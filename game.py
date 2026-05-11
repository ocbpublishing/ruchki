import pygame
import random
import os

WIDTH, HEIGHT = 800, 600
FPS = 60

COLORS = {
    'grass': (50, 200, 50),
    'rabbit': (200, 200, 200),
    'sheep': (255, 255, 255),
    'wolf': (100, 100, 100)
}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Екосистема: Еволюція та Харчовий ланцюг")
clock = pygame.time.Clock()

def load_animation(prefix, state, fallback_color, size, frame_count=3):
    frames = []
    for i in range(1, frame_count + 1):
        filename = f"{prefix}_{state}_{i}.png"
        if os.path.exists(filename):
            img = pygame.image.load(filename).convert_alpha()
            frames.append(pygame.transform.scale(img, (size, size)))
        else:
            surf = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
            if state == 'action':
                radius = size // 2 + (i * 2)
            else:
                radius = size // 2 if i % 2 != 0 else (size // 2) - 2
            pygame.draw.circle(surf, fallback_color, ((size+20)//2, (size+20)//2), radius)
            frames.append(surf)
    return frames

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, animations, start_state):
        super().__init__()
        self.animations = animations
        self.state = start_state
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0
            if self.state == 'action':
                self.state = 'move'
        self.image = self.animations[self.state][int(self.frame_index)]
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

class Animal(Entity):
    def __init__(self, x, y, animations, speed, max_energy):
        super().__init__(x, y, animations, 'move')
        self.speed = speed
        self.energy = max_energy
        self.max_energy = max_energy
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.velocity.length() > 0:
            self.velocity.scale_to_length(self.speed)

    def move(self):
        self.pos += self.velocity
        if self.pos.x < 0 or self.pos.x > WIDTH:
            self.velocity.x *= -1
            self.pos.x = max(0, min(self.pos.x, WIDTH))
        if self.pos.y < 0 or self.pos.y > HEIGHT:
            self.velocity.y *= -1
            self.pos.y = max(0, min(self.pos.y, HEIGHT))
        
        self.energy -= 0.1

    def seek_target(self, target_group):
        nearest_target = None
        min_dist = float('inf')
        for target in target_group:
            dist = self.pos.distance_to(target.pos)
            if dist < min_dist and dist < 150:
                min_dist = dist
                nearest_target = target
        
        if nearest_target:
            direction = nearest_target.pos - self.pos
            if direction.length() > 0:
                self.velocity = direction.normalize() * self.speed

class Grass(Entity):
    def __init__(self, x, y):
        anims = {'idle': load_animation('grass', 'idle', COLORS['grass'], 10, 3)}
        super().__init__(x, y, anims, 'idle')

    def update(self, *args):
        self.animate()

class Rabbit(Animal):
    def __init__(self, x, y):
        anims = {
            'move': load_animation('rabbit', 'move', COLORS['rabbit'], 20, 3),
            'action': load_animation('rabbit', 'action', COLORS['rabbit'], 20, 3)
        }
        super().__init__(x, y, anims, speed=2.5, max_energy=100)

    def update(self, grasses):
        self.seek_target(grasses)
        self.move()
        self.animate()
        eaten = pygame.sprite.spritecollide(self, grasses, True)
        if eaten:
            self.state = 'action'
            self.frame_index = 0
            self.energy = min(self.energy + 30, self.max_energy)

class Sheep(Animal):
    def __init__(self, x, y):
        anims = {
            'move': load_animation('sheep', 'move', COLORS['sheep'], 30, 3),
            'action': load_animation('sheep', 'action', COLORS['sheep'], 30, 3)
        }
        super().__init__(x, y, anims, speed=1.5, max_energy=150)

    def update(self, grasses):
        self.seek_target(grasses)
        self.move()
        self.animate()
        eaten = pygame.sprite.spritecollide(self, grasses, True)
        if eaten:
            self.state = 'action'
            self.frame_index = 0
            self.energy = min(self.energy + 40, self.max_energy)

class Wolf(Animal):
    def __init__(self, x, y):
        anims = {
            'move': load_animation('wolf', 'move', COLORS['wolf'], 40, 3),
            'action': load_animation('wolf', 'action', COLORS['wolf'], 40, 3)
        }
        super().__init__(x, y, anims, speed=3.0, max_energy=200)

    def update(self, herbivores):
        self.seek_target(herbivores)
        self.move()
        self.animate()
        eaten = pygame.sprite.spritecollide(self, herbivores, True)
        if eaten:
            self.state = 'action'
            self.frame_index = 0
            self.energy = min(self.energy + 80, self.max_energy)

grasses = pygame.sprite.Group()
rabbits = pygame.sprite.Group()
sheeps = pygame.sprite.Group()
wolves = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

def spawn_entity(GroupClass, group, count):
    for _ in range(count):
        x, y = random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)
        entity = GroupClass(x, y)
        group.add(entity)
        all_sprites.add(entity)

spawn_entity(Grass, grasses, 50)
spawn_entity(Rabbit, rabbits, 15)
spawn_entity(Sheep, sheeps, 10)
spawn_entity(Wolf, wolves, 3)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if random.random() < 0.05 and len(grasses) < 150:
        spawn_entity(Grass, grasses, 1)

    grasses.update()

    for r in list(rabbits):
        r.update(grasses)
        if r.energy <= 0:
            r.kill()
        elif r.energy > 90 and random.random() < 0.01:
            r.energy -= 40
            spawn_entity(Rabbit, rabbits, 1)

    for s in list(sheeps):
        s.update(grasses)
        if s.energy <= 0:
            s.kill()
        elif s.energy > 130 and random.random() < 0.005:
            s.energy -= 60
            spawn_entity(Sheep, sheeps, 1)

    for w in list(wolves):
        w.update(pygame.sprite.Group(rabbits.sprites() + sheeps.sprites()))
        if w.energy <= 0:
            w.kill()
        elif w.energy > 180 and random.random() < 0.005:
            w.energy -= 100
            spawn_entity(Wolf, wolves, 1)

    screen.fill((30, 30, 30))
    all_sprites.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
              
