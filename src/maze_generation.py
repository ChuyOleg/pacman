import random
import sys

from settings import *

visited = []
stack = []
solution = {}
grid = []

for col in range(1, COLS + 1):
    for row in range(1, ROWS + 1):
        grid.append((col, row))


def cell_is_not_margin_wall(x, y):
    return x != 1 and x != COLS and y != 1 and y != ROWS


def cell_is_valid(x, y):
    return (x, y) in grid and (x, y) not in visited


def cell_closed_square(x_new, y_new):
    if (x_new - 1, y_new) in visited and (x_new - 1, y_new - 1) in visited and (x_new, y_new - 1) in visited:
        return True
    if (x_new - 1, y_new) in visited and (x_new - 1, y_new + 1) in visited and (x_new, y_new + 1) in visited:
        return True
    if (x_new + 1, y_new) in visited and (x_new + 1, y_new - 1) in visited and (x_new, y_new - 1) in visited:
        return True
    if (x_new + 1, y_new) in visited and (x_new + 1, y_new + 1) in visited and (x_new, y_new + 1) in visited:
        return True
    return False


def random_appending(cell, direction):
    answer = random.choice(['append', 'skip', 'skip'])
    if answer == "append":
        cell.append(direction)


def generate_stable_maze():
    if ROWS != 10:
        print("Error. You generate stable maze for 10 rows but in settings is written: ROWS = ", ROWS)
        sys.exit()
    return [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

def carve_out_maze(real_grid):
    x, y = 2, 2
    stack.append((x, y))  # place starting cell into stack
    visited.append((x, y))  # add starting cell to visited list
    previous_cell = (x, y)
    while len(stack) > 0:  # loop until stack is empty
        cells_voc = {"right": (x + 1, y), "left": (x - 1, y), "down": (x, y + 1), "up": (x, y - 1)}
        cell = []  # define cell list

        for direction in ("right", "left", "down", "up"):
            x_coor, y_coor = cells_voc[direction]
            if cell_is_valid(x_coor, y_coor) and cell_is_not_margin_wall(x_coor, y_coor) and not cell_closed_square(
                    x_coor, y_coor):
                if (direction == "right" and x - previous_cell[0] == 1) or \
                        (direction == "left" and x - previous_cell[0] == -1) or \
                        (direction == "down" and y - previous_cell[1] == 1) or \
                        (direction == "up" and y - previous_cell[1] == -1) or \
                        (x == 2 and y == 2):
                    cell.append(direction)
                else:
                    random_appending(cell, direction)

        if len(cell) > 0:  # check to see if cell list is empty
            cell_chosen = (random.choice(cell))  # select one of the cell randomly

            previous_cell = (x, y)

            if cell_chosen == "right":  # if this cell has been chosen
                solution[(x + 1, y)] = x, y  # solution = dictionary key = new cell, other = current cell
                x = x + 1  # make this cell the current cell

            elif cell_chosen == "left":
                solution[(x - 1, y)] = x, y
                x = x - 1

            elif cell_chosen == "down":
                solution[(x, y + 1)] = x, y
                y = y + 1

            elif cell_chosen == "up":
                solution[(x, y - 1)] = x, y
                y = y - 1

            visited.append((x, y))  # add to visited list
            stack.append((x, y))  # place current cell on to stack

        else:
            previous_cell = (x, y)
            x, y = stack.pop()  # if no cells are available pop one from the stack


    for (x, y) in grid:
        if (x, y) not in visited:
            real_grid[y - 1][x - 1] = 1
