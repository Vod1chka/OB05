import pygame
import random
import math
import sys


# Инициализация Pygame
pygame.init()
# Инициализация Pygame (звуки)
pygame.mixer.init()
shoot_sound = pygame.mixer.Sound(r'./sound/shoot.mp3')
shoot_sound.set_volume(0.1)
levelUP_sound = pygame.mixer.Sound(r'./sound/levelUP.mp3')

# Иконка
player_icon = pygame.image.load(r'./icons/player.png')



# Настройки экрана
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Выживание на Pygame")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Частота кадров
FPS = 60

# Шрифты для текста
font = pygame.font.SysFont(None, 36)


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_icon
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = 5
        self.velocity = pygame.math.Vector2(0, 0)
        self.last_direction = pygame.math.Vector2(1, 0)  # по умолчанию вправо
        self.health = 100

    def update(self, keys_pressed):
        self.velocity.x = 0
        self.velocity.y = 0
        if keys_pressed[pygame.K_w]:
            self.velocity.y = -self.speed
        if keys_pressed[pygame.K_s]:
            self.velocity.y = self.speed
        if keys_pressed[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys_pressed[pygame.K_d]:
            self.velocity.x = self.speed

        # Обновление позиции с учетом границ экрана
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        # Запоминаем последнее направление движения (если есть движение)
        if self.velocity.length_squared() > 0:
            self.last_direction = self.velocity.normalize()

    def shoot(self):
        # Создаем пулю в направлении last_direction
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.last_direction)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

    def shoot_with_direction(self, direction):
        bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()


# Класс врага
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(30, 50)
        self.image = pygame.Surface((size, size))
        self.image.fill(RED)

        side = random.choice(['top', 'bottom', 'left', 'right'])

        if side == 'top':
            x = random.randint(0, WIDTH)
            y = -size
        elif side == 'bottom':
            x = random.randint(0, WIDTH)
            y = HEIGHT + size
        elif side == 'left':
            x = -size
            y = random.randint(0, HEIGHT)
        else:
            x = WIDTH + size
            y = random.randint(0, HEIGHT)

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        direction_vector = pygame.math.Vector2(player.rect.centerx - self.rect.centerx,
                                               player.rect.centery - self.rect.centery).normalize()

        speed_value = random.uniform(1.5, 3.5)

        movement_vector = direction_vector * speed_value

        self.rect.x += movement_vector.x
        self.rect.y += movement_vector.y


# Класс пули (выстрелы игрока)
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        size = 10
        self.image = pygame.Surface((size, size))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        # Сохраняем направление как атрибут
        if direction.length_squared() == 0:
            direction = pygame.math.Vector2(1, 0)
        self.direction = direction

    def update(self):
        # Перемещение пули по направлению с постоянной скоростью.
        movement = self.direction * self.speed
        self.rect.x += movement.x
        self.rect.y += movement.y

        # Удаляем пулю если она вышла за границы экрана.
        if (self.rect.right < 0 or
                self.rect.left > WIDTH or
                self.rect.bottom < 0 or
                self.rect.top > HEIGHT):
            self.kill()


# Создаем группы спрайтов для удобства обработки коллизий и обновлений.
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)
shoot_cooldown = 0  # время до следующего выстрела
shoot_delay = 200  # задержка в миллисекундах

# Таймер для появления врагов каждые N миллисекунд.
ENEMY_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(ENEMY_SPAWN_EVENT, 2000)  # каждые секунду появляется новый враг

clock = pygame.time.Clock()

score = 0


def show_game_over(score):
    """Функция отображает сообщение о завершении игры и ждет нажатия любой клавиши."""
    overlay_text = f"Игра окончена! Ваш счет: {score} Нажмите любую клавишу для выхода."
    text_surface = font.render(overlay_text, True, WHITE)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

        screen.fill(BLACK)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()


running = True
triple_shot_active = False

while running:
    dt = clock.tick(FPS)  # Время между кадрами в миллисекундах
    keys_pressed = pygame.key.get_pressed()  # Получаем состояние клавиш

    # Обработка задержки для выстрелов
    if shoot_cooldown > 0:
        shoot_cooldown -= dt

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == ENEMY_SPAWN_EVENT:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

    # Обновляем игрока с учетом нажатий клавиш
    player.update(keys_pressed)

    # Автоматический выстрел через заданный интервал
    if shoot_cooldown <= 0:
        if triple_shot_active:
            # Стрелять тремя пулями одновременно
            directions = [
                player.last_direction,
                player.last_direction.rotate(10),
                player.last_direction.rotate(-10)
            ]
            for dir in directions:
                player.shoot_with_direction(dir)
        else:
            # Одиночный выстрел
            player.shoot()
        shoot_cooldown = shoot_delay

    if score >= 3 and not triple_shot_active:
        triple_shot_active = True
        levelUP_sound.play()


    # Обновляем врагов и пули
    enemies.update()
    bullets.update()

    # Проверка столкновений пуль и врагов
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 1

    # Враги наносят урон при касании с игроком
    collided_enemies = pygame.sprite.spritecollide(player, enemies, True)
    for enemy in collided_enemies:
        player.health -= 20

    # Проверка смерти игрока
    if player.health <= 0:
        show_game_over(score)  # Вызов функции отображения сообщения о конце игры.
        running = False

    # Отрисовка на экран
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Отображение здоровья и очков
    health_text = font.render(f'Здоровье: {player.health}', True, GREEN)
    score_text = font.render(f'Очки: {score}', True, GREEN)

    screen.blit(health_text, (10, 10))
    screen.blit(score_text, (10, 50))

    pygame.display.flip()

pygame.quit()