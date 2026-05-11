import cv2
import pyautogui
import math
import mediapipe as mp

# Пробуем достать модули разными путями
try:
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
except AttributeError:
    # Запасной путь для специфических сборок
    import mediapipe.python.solutions.hands as mp_hands
    import mediapipe.python.solutions.drawing_utils as mp_draw

pyautogui.FAILSAFE = False

cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_h, img_w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
            
            # Точка 8 - кончик указательного, точка 4 - кончик большого
            lm8 = hand_lms.landmark[8]
            lm4 = hand_lms.landmark[4]
            
            x8, y8 = int(lm8.x * img_w), int(lm8.y * img_h)
            x4, y4 = int(lm4.x * img_w), int(lm4.y * img_h)
            
            # Масштабируем под размер экрана
            # Умножаем на 1.2 для более легкого достижения углов
            screen_x = screen_w * lm8.x
            screen_y = screen_h * lm8.y
            
            pyautogui.moveTo(screen_x, screen_y, _pause=False)
            
            # Считаем расстояние для клика
            dist = math.hypot(x8 - x4, y8 - y4)
            
            if dist < 35:
                pyautogui.click()
                cv2.circle(img, (x8, y8), 15, (0, 255, 0), cv2.FILLED)

    cv2.imshow("Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
              
