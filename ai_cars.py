import pygame
import math
import random
import numpy as np

WIDTH, HEIGHT = 1000, 700
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Навчання ШІ: Автопілот")
clock = pygame.time.Clock()

class Network:
    def __init__(self):
        self.weights1 = np.random.rand(5, 8) - 0.5
        self.weights2 = np.random.rand(8, 2) - 0.5

    def predict(self, inputs):
        h = np.dot(inputs, self.weights1)
        h = np.tanh(h)
        o = np.dot(h, self.weights2)
        return np.tanh(o)

class Car:
    def __init__(self, brain=None):
        self.pos = pygame.math.Vector2(100, 350)
        self.angle = 0
        self.speed = 4
        self.alive = True
        self.brain = brain if brain else Network()
        self.distance = 0
        self.sensors = [0, 0, 0, 0, 0]

    def get_data(self, track):
        for i, angle_off in enumerate([-45, -22, 0, 22, 45]):
            ray_angle = math.radians(self.angle + angle_off)
            dist = 0
            while dist < 200:
                dist += 2
                x = int(self.pos.x + math.cos(ray_angle) * dist)
                y = int(self.pos.y + math.sin(ray_angle) * dist)
                if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT or track.get_at((x, y))[0] < 50:
                    break
            self.sensors[i] = dist / 200.0

    def update(self):
        output = self.brain.predict(np.array(self.sensors))
        self.angle += output[0] * 10
        self.pos.x += math.cos(math.radians(self.angle)) * self.speed
        self.pos.y += math.sin(math.radians(self.angle)) * self.speed
        self.distance += self.speed

    def draw(self, screen):
        color = (0, 255, 0) if self.alive else (255, 0, 0)
        pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), 10)

def create_track():
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((30, 30, 30))
    points = [(100, 350), (200, 150), (500, 100), (800, 200), (900, 400), (700, 600), (300, 550), (100, 350)]
    pygame.draw.lines(surf, (200, 200, 200), True, points, 80)
    return surf

def mutate(parent_brain):
    child = Network()
    child.weights1 = parent_brain.weights1 + (np.random.rand(5, 8) - 0.5) * 0.2
    child.weights2 = parent_brain.weights2 + (np.random.rand(8, 2) - 0.5) * 0.2
    return child

track = create_track()
cars = [Car() for _ in range(25)]
gen = 1

run = True
while run:
    screen.blit(track, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False

    alive_cars = [c for c in cars if c.alive]
    
    if not alive_cars:
        cars.sort(key=lambda x: x.distance, reverse=True)
        best_brain = cars[0].brain
        cars = [Car(mutate(best_brain)) for _ in range(24)] + [Car(best_brain)]
        gen += 1
        continue

    for car in alive_cars:
        car.get_data(track)
        car.update()
        if track.get_at((int(car.pos.x), int(car.pos.y)))[0] < 50:
            car.alive = False
        car.draw(screen)

    font = pygame.font.SysFont("Arial", 24)
    screen.blit(font.render(f"Покоління: {gen}", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Живих: {len(alive_cars)}", True, (255, 255, 255)), (10, 40))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
                        
