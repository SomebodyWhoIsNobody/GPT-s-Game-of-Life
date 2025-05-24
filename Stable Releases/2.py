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

# Colors
COLOR_BG = (10, 10, 10)
COLOR_GRID = (40, 40, 40)
TYPE_COLORS = {
    CELL_NORMAL: (255, 255, 255),    # White
    CELL_IMMORTAL: (0, 255, 0),      # Green
    CELL_EPHEMERAL: (255, 0, 255)    # Magenta
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
    # Draw grid lines
    for x in range(0, GRID_WIDTH * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, GRID_HEIGHT * CELL_SIZE))
    for y in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (GRID_WIDTH * CELL_SIZE, y))


def count_alive(grid, x, y):
    alive = 0
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            if not (i == 0 and j == 0):
                xi = (x + i) % GRID_WIDTH
                yj = (y + j) % GRID_HEIGHT
                if grid[yj][xi] != CELL_EMPTY:
                    alive += 1
    return alive


def update(grid):
    new = [[CELL_EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell = grid[y][x]
            neighbors = count_alive(grid, x, y)
            if cell == CELL_IMMORTAL:
                new[y][x] = CELL_IMMORTAL
            elif cell == CELL_EPHEMERAL:
                # Ephemeral always dies
                new[y][x] = CELL_EMPTY
            elif cell == CELL_NORMAL:
                # Standard life rules
                if neighbors < 2 or neighbors > 3:
                    new[y][x] = CELL_EMPTY
                else:
                    new[y][x] = CELL_NORMAL
            else:  # Dead cell
                if neighbors == 3:
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
    running = True
    placement_type = CELL_NORMAL

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid = init_grid(randomize=True)
                elif event.key == pygame.K_c:
                    grid = init_grid(randomize=False)
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_1:
                    placement_type = CELL_NORMAL
                elif event.key == pygame.K_2:
                    placement_type = CELL_IMMORTAL
                elif event.key == pygame.K_3:
                    placement_type = CELL_EPHEMERAL
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click toggles cell of current type
                    mx, my = pygame.mouse.get_pos()
                    gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                    if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                        if grid[gy][gx] == placement_type:
                            grid[gy][gx] = CELL_EMPTY
                        else:
                            grid[gy][gx] = placement_type

        draw_grid(screen, grid)
        # UI overlay
        status = f"Type: {placement_type} (1=Normal, 2=Immortal, 3=Ephemeral) | " + \
                 ("Paused" if paused else "Running")
        text = font.render(status, True, COLOR_TEXT)
        screen.blit(text, (10, 10))

        pygame.display.flip()

        if not paused:
            grid = update(grid)
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
