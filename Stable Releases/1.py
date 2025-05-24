import pygame
import sys
import random

# Configuration
CELL_SIZE = 10       # Size of each cell in pixels
GRID_WIDTH = 80      # Number of cells horizontally
GRID_HEIGHT = 60     # Number of cells vertically
FPS = 10             # Frames per second (simulation speed)

# Colors
COLOR_BG = (10, 10, 10)
COLOR_GRID = (40, 40, 40)
COLOR_DIE_NEXT = (170, 170, 170)
COLOR_ALIVE_NEXT = (255, 255, 255)
COLOR_TEXT = (255, 0, 0)


def init_grid(randomize=True):
    """Initialize the game grid."""
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    if randomize:
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                grid[y][x] = random.choice([0, 1])
    return grid


def draw_grid(surface, grid):
    """Draws the grid lines and live cells."""
    surface.fill(COLOR_BG)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == 1:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, COLOR_ALIVE_NEXT, rect)
    # draw grid lines
    for x in range(0, GRID_WIDTH * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, GRID_HEIGHT * CELL_SIZE))
    for y in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (GRID_WIDTH * CELL_SIZE, y))


def get_neighbors(grid, x, y):
    """Count alive neighbors for a cell at (x, y)."""
    neighbors = 0
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            if not (i == 0 and j == 0):
                xi = (x + i) % GRID_WIDTH
                yj = (y + j) % GRID_HEIGHT
                neighbors += grid[yj][xi]
    return neighbors


def update(grid):
    """Compute the next generation grid."""
    new_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            alive = grid[y][x] == 1
            neighbors = get_neighbors(grid, x, y)
            if alive:
                if neighbors < 2 or neighbors > 3:
                    new_grid[y][x] = 0
                else:
                    new_grid[y][x] = 1
            else:
                if neighbors == 3:
                    new_grid[y][x] = 1
    return new_grid


def main():
    """Main loop to run the Game of Life with pause and cell toggle."""
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    grid = init_grid(randomize=True)
    paused = False
    running = True

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                gx = mx // CELL_SIZE
                gy = my // CELL_SIZE
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                    grid[gy][gx] = 1 - grid[gy][gx]

        draw_grid(screen, grid)
        if paused:
            text = font.render("Paused (Space to toggle)", True, COLOR_TEXT)
            screen.blit(text, (10, 10))
        pygame.display.flip()

        if not paused:
            grid = update(grid)
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
