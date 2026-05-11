import cv2
import os

# 1. Набор символов от темного к светлому (можно менять)
# Для эффекта "Матрицы" лучше использовать более плотные символы
ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-+_~<>i!lI;:,\"^`'. "
# Альтернативный простой набор: ASCII_CHARS = "@#*+=-:. " 

# Разрешение вывода (чем меньше, тем крупнее символы и быстрее работает)
# Подбери под размер своего экрана терминала
output_width = 120 

# 2. Функция для очистки консоли (чтобы ASCII-кадры не дублировались)
def clear_console():
    # Для Windows используется cls, для Linux/Mac - clear
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# 3. Основная функция преобразования
def main():
    # Открываем веб-камеру
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Ошибка: Не удалось открыть веб-камеру.")
        return

    num_chars = len(ASCII_CHARS)

    print("Подготовка... Нажмите 'q' для выхода.")
    
    # Немного ждем, чтобы камера стабилизировалась
    import time
    time.sleep(2)

    while True:
        # Считываем кадр
        ret, frame = cap.read()
        if not ret:
            break

        # Зеркально отражаем (чтобы было привычно, как в зеркале)
        frame = cv2.flip(frame, 1)

        # Преобразуем в черно-белое изображение
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Изменяем размер кадра, чтобы он влезал в терминал
        h, w = gray_frame.shape
        aspect_ratio = h / w
        # Корректировка высоты, так как символы терминала вытянутые
        output_height = int(output_width * aspect_ratio * 0.5)
        resized_frame = cv2.resize(gray_frame, (output_width, output_height))

        # 4. Самое важное: магия замены пикселей на символы
        ascii_frame = ""
        for row in resized_frame:
            for pixel_value in row:
                # Маппим яркость пикселя (0-255) на индекс в строке символов
                char_index = int(pixel_value * (num_chars - 1) / 255)
                ascii_frame += ASCII_CHARS[char_index]
            ascii_frame += "\n" # Переход на новую строку

        # 5. Вывод в консоль
        clear_console()
        # Выводим кадр и сразу добавляем сброс курсора (опционально для скорости)
        print(ascii_frame, end="")

        # Выход по кнопке Q (придется нажать в консоли, т.к. окна CV2 нет)
        # На школьных ПК этот метод может работать нестабильно, 
        # поэтому лучше прерывать Ctrl+C в консоли, если Q не срабатывает.
        # В этом коде мы не создаем окно imshow для максимальной производительности,
        # поэтому стандартный метод waitKey не работает.
        
        # Для простоты завершения на школьном ПК добавим небольшой imshow, 
        # чтобы можно было нажать Q.
        cv2.imshow('Camera (Press Q to exit)', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Освобождаем ресурсы
    cap.release()
    cv2.destroyAllWindows()
    clear_console()
    print("Программа завершена.")

if __name__ == "__main__":
    main()
  
