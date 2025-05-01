import pygame
import random
import heapq
import pickle
import time
import sys

# Maze dimensions and cell size
WIDTH, HEIGHT = 500, 500
CELL_SIZE = 10
cols, rows = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Generator and Solver")
clock = pygame.time.Clock()

# Initialize the grid of cells
grid = []

def init_grid():
    global grid
    grid = []
    for y in range(rows):
        grid.append([])
        for x in range(cols):
            grid[y].append({
                'x': x,
                'y': y,
                'walls': [True, True, True, True],  # [Top, Right, Bottom, Left]
                'in_maze': False
            })

def draw_cell(cell, color=(0, 0, 255), thickness=2):
    x = cell['x'] * CELL_SIZE
    y = cell['y'] * CELL_SIZE
    if cell['walls'][0]:
        pygame.draw.line(screen, color, (x, y), (x + CELL_SIZE, y), thickness)  # Top wall
    if cell['walls'][1]:
        pygame.draw.line(screen, color, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), thickness)  # Right wall
    if cell['walls'][2]:
        pygame.draw.line(screen, color, (x + CELL_SIZE, y + CELL_SIZE), (x, y + CELL_SIZE), thickness)  # Bottom wall
    if cell['walls'][3]:
        pygame.draw.line(screen, color, (x, y + CELL_SIZE), (x, y), thickness)  # Left wall

def draw_path(end_cell, color=(255, 255, 0), thickness=4):
    current = end_cell
    while 'parent' in current:
        next_cell = current['parent']
        x1 = current['x'] * CELL_SIZE + CELL_SIZE // 2
        y1 = current['y'] * CELL_SIZE + CELL_SIZE // 2
        x2 = next_cell['x'] * CELL_SIZE + CELL_SIZE // 2
        y2 = next_cell['y'] * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.line(screen, color, (x1, y1), (x2, y2), thickness)
        current = next_cell

def get_cell(x, y):
    if 0 <= x < cols and 0 <= y < rows:
        return grid[y][x]
    else:
        return None

def generate_maze():
    global grid
    init_grid()
    wall_list = []

    start_x = random.randint(0, cols - 1)
    start_y = random.randint(0, rows - 1)
    start_cell = grid[start_y][start_x]
    start_cell['in_maze'] = True

    x, y = start_cell['x'], start_cell['y']
    walls = start_cell['walls']
    if y > 0:
        wall_list.append((x, y, 0))  # Top wall
    if x < cols - 1:
        wall_list.append((x, y, 1))  # Right wall
    if y < rows - 1:
        wall_list.append((x, y, 2))  # Bottom wall
    if x > 0:
        wall_list.append((x, y, 3))  # Left wall

    while wall_list:
        wx, wy, wall = random.choice(wall_list)
        wall_list.remove((wx, wy, wall))

        current_cell = grid[wy][wx]
        opposite_cell = None
        dx, dy = 0, 0

        if wall == 0:
            dy = -1
        elif wall == 1:
            dx = 1
        elif wall == 2:
            dy = 1
        elif wall == 3:
            dx = -1

        nx, ny = wx + dx, wy + dy
        opposite_cell = get_cell(nx, ny)

        if opposite_cell and not opposite_cell['in_maze']:
            current_cell['walls'][wall] = False
            opposite_wall = (wall + 2) % 4
            opposite_cell['walls'][opposite_wall] = False

            opposite_cell['in_maze'] = True

            ox, oy = opposite_cell['x'], opposite_cell['y']
            walls = opposite_cell['walls']
            if oy > 0 and walls[0]:
                wall_list.append((ox, oy, 0))
            if ox < cols - 1 and walls[1]:
                wall_list.append((ox, oy, 1))
            if oy < rows - 1 and walls[2]:
                wall_list.append((ox, oy, 2))
            if ox > 0 and walls[3]:
                wall_list.append((ox, oy, 3))

        screen.fill((0, 0, 0))
        for row in grid:
            for cell in row:
                draw_cell(cell)
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    pygame.image.save(screen, "maze.png")

def reset_visited():
    global grid
    for row in grid:
        for cell in row:
            cell['visited'] = False
            cell.pop('parent', None)
            cell.pop('distance', None)
            cell.pop('g', None)
            cell.pop('h', None)
            cell.pop('f', None)

def dijkstra(start, end):
    start_time = time.time()
    queue = []
    start['distance'] = 0
    heapq.heappush(queue, (0, id(start), start))  # Add unique id to ensure comparison

    visited_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    max_queue_size = 0  # Track maximum queue size
    visited_memory = sys.getsizeof(visited_surface)  # Memory for visited visualization

    nodes_explored = 0  # Track number of nodes explored

    while queue:
        max_queue_size = max(max_queue_size, sys.getsizeof(queue))  # Track peak memory usage

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill((0, 0, 0))
        screen.blit(visited_surface, (0, 0))
        for row in grid:
            for cell_draw in row:
                draw_cell(cell_draw)
        pygame.display.flip()
        clock.tick(60)

        dist, _, current_cell = heapq.heappop(queue)
        if 'visited' in current_cell and current_cell['visited']:
            continue
        current_cell['visited'] = True
        nodes_explored += 1  # Increment the counter for each node explored

        x = current_cell['x'] * CELL_SIZE
        y = current_cell['y'] * CELL_SIZE
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(visited_surface, (34, 139, 34, 100), rect)

        if current_cell == end:
            break

        neighbors = []
        walls = current_cell['walls']
        x, y = current_cell['x'], current_cell['y']

        if not walls[0] and y > 0:
            neighbors.append(grid[y - 1][x])
        if not walls[1] and x < cols - 1:
            neighbors.append(grid[y][x + 1])
        if not walls[2] and y < rows - 1:
            neighbors.append(grid[y + 1][x])
        if not walls[3] and x > 0:
            neighbors.append(grid[y][x - 1])

        for neighbor in neighbors:
            alt = dist + 1
            if 'distance' not in neighbor or alt < neighbor['distance']:
                neighbor['distance'] = alt
                neighbor['parent'] = current_cell
                heapq.heappush(queue, (alt, id(neighbor), neighbor))

    draw_path(end)
    pygame.display.flip()

    elapsed_time = time.time() - start_time

    total_queue_memory = max_queue_size
    total_memory = visited_memory + total_queue_memory

    # Calculate path length
    path_length = 0
    current = end
    while 'parent' in current:
        path_length += 1
        current = current['parent']

    print(f"Dijkstra's Algorithm completed in {elapsed_time:.4f} seconds")
    print(f"Space complexity:")
    print(f"  Peak priority queue size: {total_queue_memory / 1024:.2f} KB")
    print(f"  Visited surface size: {visited_memory / 1024:.2f} KB")
    print(f"  Total memory usage: {total_memory / 1024:.2f} KB")
    print(f"Number of nodes explored: {nodes_explored}")
    print(f"Path length: {path_length}")


def a_star(start, end):
    start_time = time.time()
    open_set = []
    start['g'] = 0
    start['h'] = abs(end['x'] - start['x']) + abs(end['y'] - start['y'])
    start['f'] = start['g'] + start['h']
    heapq.heappush(open_set, (start['f'], id(start), start))  # Add unique id to ensure comparison

    visited_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    max_open_set_size = 0  # Track maximum size of open_set
    visited_memory = sys.getsizeof(visited_surface)  # Memory for visited visualization

    nodes_explored = 0  # Track number of nodes explored

    while open_set:
        max_open_set_size = max(max_open_set_size, sys.getsizeof(open_set))  # Track peak memory usage

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill((0, 0, 0))
        screen.blit(visited_surface, (0, 0))
        for row in grid:
            for cell_draw in row:
                draw_cell(cell_draw)
        pygame.display.flip()
        clock.tick(60)

        _, _, current_cell = heapq.heappop(open_set)
        if 'visited' in current_cell and current_cell['visited']:
            continue
        current_cell['visited'] = True
        nodes_explored += 1  # Increment the counter for each node explored

        x = current_cell['x'] * CELL_SIZE
        y = current_cell['y'] * CELL_SIZE
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(visited_surface, (34, 139, 34, 100), rect)

        if current_cell == end:
            break

        neighbors = []
        walls = current_cell['walls']
        x, y = current_cell['x'], current_cell['y']

        if not walls[0] and y > 0:
            neighbors.append(grid[y - 1][x])
        if not walls[1] and x < cols - 1:
            neighbors.append(grid[y][x + 1])
        if not walls[2] and y < rows - 1:
            neighbors.append(grid[y + 1][x])
        if not walls[3] and x > 0:
            neighbors.append(grid[y][x - 1])

        for neighbor in neighbors:
            tentative_g = current_cell['g'] + 1
            if 'g' not in neighbor or tentative_g < neighbor['g']:
                neighbor['g'] = tentative_g
                neighbor['h'] = abs(end['x'] - neighbor['x']) + abs(end['y'] - neighbor['y'])
                neighbor['f'] = neighbor['g'] + neighbor['h']
                neighbor['parent'] = current_cell
                heapq.heappush(open_set, (neighbor['f'], id(neighbor), neighbor))

    draw_path(end)
    pygame.display.flip()

    elapsed_time = time.time() - start_time

    total_open_set_memory = max_open_set_size
    total_memory = visited_memory + total_open_set_memory

    # Calculate path length
    path_length = 0
    current = end
    while 'parent' in current:
        path_length += 1
        current = current['parent']

    print(f"A* Algorithm completed in {elapsed_time:.4f} seconds")
    print(f"Space complexity:")
    print(f"  Peak open set size: {total_open_set_memory / 1024:.2f} KB")
    print(f"  Visited surface size: {visited_memory / 1024:.2f} KB")
    print(f"  Total memory usage: {total_memory / 1024:.2f} KB")
    print(f"Number of nodes explored: {nodes_explored}")
    print(f"Path length: {path_length}")

def main():
    global grid
    init_grid()

    print("Welcome to the Maze Generator and Solver!")
    print("1. Generate a new maze using Prim's Algorithm")
    print("2. Load an existing maze")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        generate_maze()
        save_option = input("Do you want to save the generated maze? (y/n): ")
        if save_option.lower() == 'y':
            filename = input("Enter filename to save the maze (e.g., maze_data.pkl): ")
            with open(filename, 'wb') as f:
                pickle.dump(grid, f)
            print(f"Maze saved to {filename}")
    elif choice == '2':
        filename = input("Enter filename of the maze to load (e.g., maze_data.pkl): ")
        try:
            with open(filename, 'rb') as f:
                grid = pickle.load(f)
            screen.fill((0, 0, 0))
            for row in grid:
                for cell in row:
                    draw_cell(cell)
            pygame.display.flip()
        except FileNotFoundError:
            print("File not found. Exiting.")
            pygame.quit()
            exit()
    else:
        print("Invalid choice. Exiting.")
        pygame.quit()
        exit()

    while True:
        reset_visited()

        start = grid[0][0]
        end = grid[rows - 1][cols - 1]

        print("Select a maze-solving algorithm:")
        print("1. Dijkstra's Algorithm")
        print("2. A* Pathfinding Algorithm")
        choice = input("Enter the number of your choice: ")

        if choice == '1':
            dijkstra(start, end)
        elif choice == '2':
            a_star(start, end)
        else:
            print("Invalid choice.")

        again = input("Do you want to try another algorithm on the same maze? (y/n): ")
        if again.lower() != 'y':
            break

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(30)
    pygame.quit()

if __name__ == "__main__":
    main()
