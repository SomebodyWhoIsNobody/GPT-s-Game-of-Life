import pygame
import sys
import random

# Configuration
CELL_SIZE = 10       # Size of each cell in pixels
GRID_WIDTH = 80      # Number of cells horizontally
GRID_HEIGHT = 60     # Number of cells vertically
FPS = 10             # Frames per second (simulation speed)

# Cell Types
CELL_EMPTY = 0
CELL_NORMAL = 1      # Standard Game of Life rules
CELL_IMMORTAL = 2    # Never dies once placed
CELL_EPHEMERAL = 3   # Dies after one generation
CELL_VIRAL = 4       # Infects adjacent cells
CELL_SHRINKER = 5    # Kills neighbors then dies

# Colors for each type
COLOR_BG = (10, 10, 10)
COLOR_GRID = (40, 40, 40)
TYPE_COLORS = {
    CELL_NORMAL: (200, 200, 200),     # Light gray
    CELL_IMMORTAL: (0, 200, 0),       # Green
    CELL_EPHEMERAL: (200, 0, 200),    # Magenta
    CELL_VIRAL: (200, 50, 50),        # Red-tinged
    CELL_SHRINKER: (50, 50, 200)      # Blue-tinged
}
COLOR_TEXT = (255, 0, 0)


def init_grid(randomize=True):
    grid = [[CELL_EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    if randomize:
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                grid[y][x] = random.choice([CELL_EMPTY, CELL_NORMAL])
    return grid


def draw_grid(surface, grid):
    surface.fill(COLOR_BG)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell = grid[y][x]
            if cell != CELL_EMPTY:
                color = TYPE_COLORS.get(cell, TYPE_COLORS[CELL_NORMAL])
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, color, rect)
    # draw grid lines
    for x in range(0, GRID_WIDTH * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, GRID_HEIGHT * CELL_SIZE))
    for y in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (GRID_WIDTH * CELL_SIZE, y))


def neighbors_coords(x, y):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx != 0 or dy != 0:
                yield (x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT


def update(grid):
    new = [[CELL_EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell = grid[y][x]
            # count alive neighbors (not empty)
            alive_neighbors = sum(1 for nx, ny in neighbors_coords(x, y) if grid[ny][nx] != CELL_EMPTY)

            if cell == CELL_IMMORTAL:
                new[y][x] = CELL_IMMORTAL
            elif cell == CELL_EPHEMERAL:
                # ephemerals die
                new[y][x] = CELL_EMPTY
            elif cell == CELL_VIRAL:
                # remain viral and infect one random neighbor
                new[y][x] = CELL_VIRAL
                targets = [(nx, ny) for nx, ny in neighbors_coords(x, y) if grid[ny][nx] == CELL_EMPTY]
                if targets:
                    tx, ty = random.choice(targets)
                    new[ty][tx] = CELL_VIRAL
            elif cell == CELL_SHRINKER:
                # kills all neighbors then disappears
                for nx, ny in neighbors_coords(x, y):
                    if grid[ny][nx] != CELL_EMPTY:
                        new[ny][nx] = CELL_EMPTY
                # shrinker itself vanishes
                new[y][x] = CELL_EMPTY
            elif cell == CELL_NORMAL:
                # classic rules
                if alive_neighbors in (2, 3):
                    new[y][x] = CELL_NORMAL
                else:
                    new[y][x] = CELL_EMPTY
            else:
                # empty cell: birth if exactly 3 neighbors normal/immortal
                normals = sum(1 for nx, ny in neighbors_coords(x, y) if grid[ny][nx] in (CELL_NORMAL, CELL_IMMORTAL))
                if normals == 3:
                    new[y][x] = CELL_NORMAL
    return new


def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("GPT's Game of Life")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    grid = init_grid(randomize=True)
    paused = False
    placement_type = CELL_NORMAL

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid = init_grid(randomize=True)
                elif event.key == pygame.K_c:
                    grid = init_grid(randomize=False)
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3,
                                   pygame.K_4, pygame.K_5):
                    placement_type = int(event.unicode)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                    if grid[gy][gx] == placement_type:
                        grid[gy][gx] = CELL_EMPTY
                    else:
                        grid[gy][gx] = placement_type

        draw_grid(screen, grid)
        # simple overlay: type number and paused/running
        label = f"{placement_type} | {'Paused' if paused else 'Running'}"
        text = font.render(label, True, COLOR_TEXT)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        if not paused:
            grid = update(grid)
        clock.tick(FPS)

if __name__ == "__main__":
    main()
