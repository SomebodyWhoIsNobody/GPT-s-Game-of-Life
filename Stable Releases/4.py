import pygame
import sys
import random

# Configuration
CELL_SIZE = 10
GRID_WIDTH = 80
GRID_HEIGHT = 60
FPS = 10

# Cell Types
CELL_EMPTY     = 0
CELL_NORMAL    = 1  # Standard Game of Life
CELL_IMMORTAL  = 2  # Never dies
CELL_EPHEMERAL = 3  # Dies after one gen
CELL_VIRAL     = 4  # Infects one neighbor
CELL_SHRINKER  = 5  # Kills neighbors then dies
CELL_SPREADER  = 6  # Infects *all* empty neighbors then dies
CELL_BLINKER   = 7  # Toggles each generation

# Colors
COLOR_BG   = (10, 10, 10)
COLOR_GRID = (40, 40, 40)
TYPE_COLORS = {
    CELL_NORMAL:    (200, 200, 200),
    CELL_IMMORTAL:  (0, 200,   0),
    CELL_EPHEMERAL: (200,   0, 200),
    CELL_VIRAL:     (200,  50,  50),
    CELL_SHRINKER:  ( 50,  50, 200),
    CELL_SPREADER:  (  0, 200, 200),  # Cyan
    CELL_BLINKER:   (200, 200,   0),  # Yellow
}
COLOR_TEXT = (255, 0, 0)


def init_grid(randomize=True):
    grid = [[CELL_EMPTY]*GRID_WIDTH for _ in range(GRID_HEIGHT)]
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
                color = TYPE_COLORS[cell]
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, color, rect)
    # grid lines
    for x in range(0, GRID_WIDTH*CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, GRID_HEIGHT*CELL_SIZE))
    for y in range(0, GRID_HEIGHT*CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (GRID_WIDTH*CELL_SIZE, y))


def neighbors_coords(x, y):
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            if dx!=0 or dy!=0:
                yield (x+dx)%GRID_WIDTH, (y+dy)%GRID_HEIGHT


def update(grid):
    new = [[CELL_EMPTY]*GRID_WIDTH for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell = grid[y][x]
            alive = [(nx,ny) for nx,ny in neighbors_coords(x,y) if grid[ny][nx]!=CELL_EMPTY]
            normals = sum(1 for nx,ny in neighbors_coords(x,y)
                          if grid[ny][nx] in (CELL_NORMAL, CELL_IMMORTAL))

            if cell == CELL_IMMORTAL:
                new[y][x] = CELL_IMMORTAL

            elif cell == CELL_EPHEMERAL:
                # always dies
                new[y][x] = CELL_EMPTY

            elif cell == CELL_VIRAL:
                new[y][x] = CELL_VIRAL
                # infect one random empty neighbor
                empties = [(nx,ny) for nx,ny in neighbors_coords(x,y) if grid[ny][nx]==CELL_EMPTY]
                if empties:
                    tx,ty = random.choice(empties)
                    new[ty][tx] = CELL_VIRAL

            elif cell == CELL_SHRINKER:
                # kill all neighbors then self‐destruct
                for nx,ny in neighbors_coords(x,y):
                    new[ny][nx] = CELL_EMPTY
                new[y][x] = CELL_EMPTY

            elif cell == CELL_SPREADER:
                # infect every empty neighbor then die
                for nx,ny in neighbors_coords(x,y):
                    if grid[ny][nx]==CELL_EMPTY:
                        new[ny][nx] = CELL_SPREADER
                # original dies
                new[y][x] = CELL_EMPTY

            elif cell == CELL_BLINKER:
                # simply toggle off
                new[y][x] = CELL_EMPTY

            elif cell == CELL_NORMAL:
                # classic life
                if len(alive) in (2,3):
                    new[y][x] = CELL_NORMAL
                else:
                    new[y][x] = CELL_EMPTY

            else:
                # Birth rules for all other: normals & immortals
                if normals == 3:
                    new[y][x] = CELL_NORMAL

    # Now revive blinkers: any cell that was BLINKER becomes BLINKER again next gen
    # (so they just flash off for one step and back on)
    # We need to track where they were; simple hack: we could track prev grid
    # but for demo, let's do: any cell that has 2+ live neighbors becomes BLINKER
    # (you can tweak this as you see fit)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == CELL_BLINKER:
                new[y][x] = CELL_BLINKER

    return new


def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH*CELL_SIZE, GRID_HEIGHT*CELL_SIZE))
    pygame.display.set_caption("Enhanced Game of Life")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    grid = init_grid()
    paused = False
    placement_type = CELL_NORMAL

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    grid = init_grid(True)
                elif ev.key == pygame.K_c:
                    grid = init_grid(False)
                elif ev.key == pygame.K_SPACE:
                    paused = not paused
                elif ev.key in (pygame.K_1, pygame.K_2, pygame.K_3,
                                pygame.K_4, pygame.K_5,
                                pygame.K_6, pygame.K_7):
                    placement_type = int(ev.unicode)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx,my = pygame.mouse.get_pos()
                gx,gy = mx//CELL_SIZE, my//CELL_SIZE
                if grid[gy][gx] == placement_type:
                    grid[gy][gx] = CELL_EMPTY
                else:
                    grid[gy][gx] = placement_type

        draw_grid(screen, grid)
        label = f"Type {placement_type} | {'Paused' if paused else 'Running'}"
        text = font.render(label, True, COLOR_TEXT)
        screen.blit(text, (10,10))

        pygame.display.flip()
        if not paused:
            grid = update(grid)
        clock.tick(FPS)


if __name__ == "__main__":
    main()
