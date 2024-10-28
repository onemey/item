import pygame
import random
import time

# Инициализация Pygame
pygame.init()

# Параметры экрана и основные цвета
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Procedural Roguelike")

# Загрузка изображений
player_image = pygame.image.load("New Piskel (3).gif")  # Укажите путь к изображению персонажа
enemy_image = pygame.image.load("New Piskel (2).gif")  # Укажите путь к изображению врага
wall_image = pygame.image.load("New Piskel (1).gif")  # Укажите путь к изображению стены
floor_image = pygame.image.load("New Piskel (4).gif")  # Укажите путь к изображению пола
item_image = pygame.image.load("New Piskel (5).gif")  # Укажите путь к изображению предмета

# Карта и положения объектов
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE
player_pos, player_health = [1, 1], 10
enemies, items = [], []
level = 1

# Флаги
has_sword = False
sword_start_time = None
sword_duration = 10  # Время действия меча в секундах
enemy_damage_interval = 0.2  # Интервал урона врага
last_damage_time = time.time()  # Время последнего урона

# Генерация карты с помощью алгоритма блуждания
def generate_map():
    game_map = [[1] * COLS for _ in range(ROWS)]
    stack = [(1, 1)]

    while stack:
        current_cell = stack[-1]
        x, y = current_cell
        game_map[y][x] = 0

        # Находим соседей
        neighbors = []
        if x > 1 and game_map[y][x - 2] == 1:
            neighbors.append((x - 2, y))
        if x < COLS - 2 and game_map[y][x + 2] == 1:
            neighbors.append((x + 2, y))
        if y > 1 and game_map[y - 2][x] == 1:
            neighbors.append((x, y - 2))
        if y < ROWS - 2 and game_map[y + 2][x] == 1:
            neighbors.append((x, y + 2))

        if neighbors:
            # Случайный выбор соседа
            neighbor = random.choice(neighbors)
            nx, ny = neighbor
            game_map[(y + ny) // 2][(x + nx) // 2] = 0  # Открываем путь к соседу
            stack.append(neighbor)
        else:
            stack.pop()

    game_map[1][1], game_map[ROWS - 2][COLS - 2] = 0, 0  # Начальная и конечная позиции
    return game_map

# Функции отрисовки
def draw_map(game_map):
    for y in range(ROWS):
        for x in range(COLS):
            if game_map[y][x] == 1:
                screen.blit(wall_image, (x * TILE_SIZE, y * TILE_SIZE))
            else:
                screen.blit(floor_image, (x * TILE_SIZE, y * TILE_SIZE))

def draw_entities():
    screen.blit(player_image, (player_pos[1] * TILE_SIZE, player_pos[0] * TILE_SIZE))
    for enemy in enemies:
        screen.blit(enemy_image, (enemy["pos"][1] * TILE_SIZE, enemy["pos"][0] * TILE_SIZE))
    for item in items:
        screen.blit(item_image, (item[1] * TILE_SIZE, item[0] * TILE_SIZE))

def draw_health():
    health_text = f"Health: {player_health}"
    font = pygame.font.SysFont("Arial", 30)
    text_surface = font.render(health_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, 20))
    screen.blit(text_surface, text_rect)

# Проверка на возможность движения
def can_move(y, x, game_map):
    return 0 <= x < COLS and 0 <= y < ROWS and game_map[y][x] == 0

# Генерация врагов и предметов
def generate_enemies(count):
    for _ in range(count):
        while True:
            pos = [random.randint(0, ROWS - 1), random.randint(0, COLS - 1)]
            if pos != player_pos and can_move(pos[0], pos[1], game_map):
                enemies.append({"pos": pos, "health": 3})
                break

def generate_items(count):
    for _ in range(count):
        while True:
            pos = [random.randint(0, ROWS - 1), random.randint(0, COLS - 1)]
            if can_move(pos[0], pos[1], game_map):
                items.append(pos)
                break

# Боевая функция
def attack_enemy():
    for enemy in enemies:
        if enemy["pos"] == player_pos:
            if has_sword:
                enemies.remove(enemy)  # Убираем врага, если есть меч
                print("Enemy defeated!")
            else:
                enemy["health"] -= 1
                if enemy["health"] <= 0:
                    enemies.remove(enemy)
                break

# Перемещение игрока
def move_player(dy, dx, game_map):
    new_y, new_x = player_pos[0] + dy, player_pos[1] + dx
    if can_move(new_y, new_x, game_map):
        player_pos[0], player_pos[1] = new_y, new_x
        for item in items:
            if item == player_pos:
                items.remove(item)  # Подбор предмета
                grant_sword()  # Даем меч
                print("Item picked up! You got a sword for 10 seconds!")

# Функция восстановления здоровья
def heal_player(amount):
    global player_health
    player_health += amount
    player_health = min(player_health, 10)  # Максимальное здоровье 10

# Функция для начала нового уровня
def new_level():
    global game_map, enemies, items, player_pos, level
    level += 1
    player_pos = [1, 1]
    game_map = generate_map()
    enemies.clear()  # Очищаем предыдущих врагов
    items.clear()  # Очищаем предыдущие предметы
    generate_enemies(5 + level)  # Генерируем врагов в зависимости от уровня
    generate_items(10 + level * 2)  # Увеличиваем количество предметов с каждым уровнем
    print(f"Welcome to Level {level}!")

# Функция для получения меча
def grant_sword():
    global has_sword, sword_start_time
    has_sword = True
    sword_start_time = time.time()  # Запоминаем время получения меча

# Игровой цикл
game_map = generate_map()
generate_enemies(5)  # Генерация врагов для первого уровня
generate_items(10)  # Увеличиваем количество предметов
clock = pygame.time.Clock()
running = True

while running:
    screen.fill((0, 0, 0))
    draw_map(game_map)
    draw_entities()
    draw_health()  # Отображаем здоровье игрока

    # Проверка истечения времени меча
    if has_sword and (time.time() - sword_start_time > sword_duration):
        has_sword = False
        print("Sword duration has ended.")

    # Проверка урона от врагов
    for enemy in enemies:
        if enemy["pos"] == player_pos:
            current_time = time.time()
            if current_time - last_damage_time >= enemy_damage_interval:
                if not has_sword:  # Игрок теряет здоровье только если нет меча
                    player_health -= 1
                    last_damage_time = current_time
                    print(f"Player health: {player_health}")
                    if player_health <= 0:
                        print("Game Over")
                        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move_player(-1, 0, game_map)
            elif event.key == pygame.K_DOWN:
                move_player(1, 0, game_map)
            elif event.key == pygame.K_LEFT:
                move_player(0, -1, game_map)
            elif event.key == pygame.K_RIGHT:
                move_player(0, 1, game_map)
            elif event.key == pygame.K_SPACE:
                attack_enemy()

    # Проверка достижения выхода
    if player_pos == [ROWS - 2, COLS - 2]:
        print("Level Completed!")
        new_level()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()

