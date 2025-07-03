import pygame
import sys
import time
import random

# Constants
TILE_SIZE = 48
GRID_WIDTH, GRID_HEIGHT = 13, 11
WIDTH = TILE_SIZE * GRID_WIDTH
HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 60

# Colors
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
BLUE = (0, 150, 255)

# Map
MAP = [
    "#############",
    "#..x..#..x..#",
    "#.#.#.#.#.#.#",
    "#x..x..x..x.#",
    "#.#.#.#.#.#.#",
    "#..x..#..x..#",
    "#.#.#.#.#.#.#",
    "#x..x..x..x.#",
    "#.#.#.#.#.#.#",
    "#..x..#..x..#",
    "#############",
]

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomberman Clone")
clock = pygame.time.Clock()

player_pos = [1, 1]
player_speed = 5
bomb_range = 1

bombs = []
explosions = []
enemies = [{'x': 11, 'y': 9, 'last_move': time.time()}]

power_ups = [{'x': 3, 'y': 1, 'type': 'range'}, {'x': 9, 'y': 5, 'type': 'speed'}]

def draw_map():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile = MAP[y][x]
            if tile == '#':
                pygame.draw.rect(win, GRAY, rect)
            elif tile == 'x':
                pygame.draw.rect(win, ORANGE, rect)
            else:
                pygame.draw.rect(win, BLACK, rect, 1)

def draw_player():
    pygame.draw.rect(win, WHITE, (player_pos[0]*TILE_SIZE+8, player_pos[1]*TILE_SIZE+8, 32, 32))

def draw_bombs():
    for bomb in bombs:
        pygame.draw.circle(win, RED, (bomb['x']*TILE_SIZE+TILE_SIZE//2, bomb['y']*TILE_SIZE+TILE_SIZE//2), 10)

def draw_explosions():
    for ex in explosions:
        pygame.draw.rect(win, RED, (ex[0]*TILE_SIZE, ex[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_enemies():
    for e in enemies:
        pygame.draw.rect(win, BLUE, (e['x']*TILE_SIZE+10, e['y']*TILE_SIZE+10, 28, 28))

def draw_powerups():
    for p in power_ups:
        color = GREEN if p['type'] == 'range' else BLUE
        pygame.draw.circle(win, color, (p['x']*TILE_SIZE+TILE_SIZE//2, p['y']*TILE_SIZE+TILE_SIZE//2), 8)

def is_walkable(x, y):
    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
        return False
    return MAP[y][x] in ['.', 'x']

def explode_bombs():
    now = time.time()
    for bomb in bombs[:]:
        if now - bomb['time'] >= 2:
            affected = []
            for dx, dy in [(0,0), (1,0), (-1,0), (0,1), (0,-1)]:
                for r in range(bomb['range']+1):
                    tx = bomb['x'] + dx*r
                    ty = bomb['y'] + dy*r
                    if not (0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT):
                        break
                    tile = MAP[ty][tx]
                    affected.append((tx, ty))
                    if tile == '#':
                        break
                    elif tile == 'x':
                        MAP[ty] = MAP[ty][:tx] + '.' + MAP[ty][tx+1:]
                        break
            explosions.extend(affected)
            bombs.remove(bomb)

def cleanup_explosions():
    if explosions:
        time.sleep(0.1)
        explosions.clear()

def move_enemies():
    now = time.time()
    for enemy in enemies:
        if now - enemy['last_move'] > 1:
            dirs = [(0,1), (0,-1), (1,0), (-1,0)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx = enemy['x'] + dx
                ny = enemy['y'] + dy
                if is_walkable(nx, ny):
                    enemy['x'] = nx
                    enemy['y'] = ny
                    enemy['last_move'] = now
                    break

def check_collisions():
    global bomb_range, player_speed
    for p in power_ups[:]:
        if player_pos[0] == p['x'] and player_pos[1] == p['y']:
            if p['type'] == 'range':
                bomb_range += 1
            elif p['type'] == 'speed':
                player_speed += 1
            power_ups.remove(p)

    for e in enemies:
        if e['x'] == player_pos[0] and e['y'] == player_pos[1]:
            print("💀 You got caught!")
            pygame.quit()
            sys.exit()

    for ex in explosions:
        if (player_pos[0], player_pos[1]) == ex:
            print("🔥 Burned!")
            pygame.quit()
            sys.exit()

        for e in enemies[:]:
            if (e['x'], e['y']) == ex:
                enemies.remove(e)

def game_loop():
    global player_pos
    while True:
        clock.tick(FPS)
        win.fill(BLACK)
        draw_map()
        draw_powerups()
        draw_player()
        draw_enemies()
        draw_bombs()
        draw_explosions()
        pygame.display.update()

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]: dx = -1
        elif keys[pygame.K_RIGHT]: dx = 1
        elif keys[pygame.K_UP]: dy = -1
        elif keys[pygame.K_DOWN]: dy = 1
        elif keys[pygame.K_SPACE]:
            already = any(b['x']==player_pos[0] and b['y']==player_pos[1] for b in bombs)
            if not already:
                bombs.append({'x': player_pos[0], 'y': player_pos[1], 'time': time.time(), 'range': bomb_range})
            time.sleep(0.2)

        new_x = player_pos[0] + dx
        new_y = player_pos[1] + dy
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and is_walkable(new_x, new_y):
            player_pos = [new_x, new_y]

        explode_bombs()
        cleanup_explosions()
        move_enemies()
        check_collisions()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

game_loop()
