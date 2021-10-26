from queue import PriorityQueue
from time import sleep

import pygame
from settings import *

vec = pygame.math.Vector2


class Player:
    def __init__(self, app, pos):
        self.app = app
        self.starting_pos = [pos.x, pos.y]
        self.grid_pos = pos
        self.pix_pos = self.get_pix_pos()
        self.direction = vec(0, 0)
        self.search_type = "Standard"
        self.stored_direction = None
        self.able_to_move = True
        self.current_score = 0
        self.speed = SPEED
        self.lives = LIVES
        self.search_time = {"bfs": 0, "dfs": 0, "ucs": 0}

    def update(self):

        if self.able_to_move:
            self.pix_pos += self.direction * self.speed

        self.grid_pos = self.get_grid_pos_from_pix_pos(self.pix_pos)

        if self.time_to_move():
            self.change_direction_if_possible()

        if self.on_coin():
            self.eat_coin()

    def draw(self):
        pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (int(self.pix_pos.x),
                                                            int(self.pix_pos.y)), self.app.cell_width // 2 - 2)

        # Drawing player lives
        for x in range(self.lives):
            pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (30 + 20 * x, HEIGHT - 15), 7)

    def on_coin(self):
        if self.grid_pos in self.app.coins:
            if int(self.pix_pos.x - TOP_BOTTOM_BUFFER // 2 - self.app.cell_width // 2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y - TOP_BOTTOM_BUFFER // 2 - self.app.cell_height // 2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def eat_coin(self):
        self.app.coins.remove(self.grid_pos)
        self.current_score += 1

    def move(self, direction):
        self.stored_direction = direction

    def get_grid_pos_from_pix_pos(self, pix_pos):
        return vec((pix_pos[0] - TOP_BOTTOM_BUFFER // 2 - self.app.cell_width // 2) // self.app.cell_width,
                (pix_pos[1] - TOP_BOTTOM_BUFFER // 2 - self.app.cell_height // 2) // self.app.cell_height)

    def get_pix_pos(self):
        return vec((self.grid_pos[0] * self.app.cell_width) + TOP_BOTTOM_BUFFER // 2 + self.app.cell_width // 2,
                   (self.grid_pos[1] * self.app.cell_height) +
                   TOP_BOTTOM_BUFFER // 2 + self.app.cell_height // 2)

    def get_pix_pos_from_grid_pos(self, x, y):
        return vec(int((x * self.app.cell_width) + TOP_BOTTOM_BUFFER // 2),
                   int((y * self.app.cell_height) + TOP_BOTTOM_BUFFER // 2))

    def get_pix_pis_on_grid(self, x, y):
        return vec(int(self.pix_pos.x - TOP_BOTTOM_BUFFER // 2 - self.app.cell_width // 2),
                   self.pix_pos.y - TOP_BOTTOM_BUFFER // 2 - self.app.cell_height // 2)

    def time_to_move(self):
        if (self.pix_pos.x - TOP_BOTTOM_BUFFER // 2 - self.app.cell_width // 2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True

        if (self.pix_pos.y - TOP_BOTTOM_BUFFER // 2 - self.app.cell_height // 2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def change_direction_if_possible(self):
        if self.stored_direction is not None and (self.grid_pos + self.stored_direction) not in self.app.walls:
            self.direction = self.stored_direction
            self.able_to_move = True
        elif (self.grid_pos + self.direction) not in self.app.walls:
            self.able_to_move = True
        else:
            self.able_to_move = False

    def bfs(self, start, target):
        queue = [start]
        path = []
        visited = []

        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                    if next_cell not in visited and self.app.game_field[int(next_cell[1])][int(next_cell[0])] != 1:
                        queue.append(next_cell)
                        path.append({"Current": current, "Next": next_cell})

        real_path = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    real_path.insert(0, step["Current"])

        return real_path

    def dfs(self, start_node, target):
        visited = []
        path = []

        def real_dfs(current):

            visited.append(current)

            if current == target:
                return True

            neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
            for neighbour in neighbours:
                next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                if next_cell not in visited and self.app.game_field[int(next_cell[1])][int(next_cell[0])] != 1:
                    path.append({"Current": current, "Next": next_cell})
                    result_bool = real_dfs(next_cell)
                    if result_bool:
                        return True
            return False

        real_dfs(start_node)

        real_path = [target]
        while target != start_node:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    real_path.insert(0, step["Current"])

        return real_path

    def ucs(self, start, target):

        price_matrix = self.create_price_matrix()
        queue = PriorityQueue()
        queue.put((0, start))
        visited = []
        path = []

        while queue:
            current = queue.get()
            current_node = current[1]
            visited.append(current_node)
            if current_node == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    next_cell = [int(neighbour[0] + current_node[0]), int(neighbour[1] + current_node[1])]
                    if next_cell not in visited and next_cell not in self.app.walls:
                        queue.put((current[0] + price_matrix[int(next_cell[1])][(int(next_cell[0]))], next_cell))
                        path.append({"Current": current_node, "Next": next_cell})

        real_path = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    real_path.insert(0, step["Current"])

        return real_path

    def a_star(self, start_vert_vec, end_vert_vec, heuristic_type):
        price_matrix = self.create_price_matrix()
        table = {}

        closed_vertex = []
        opened_vertex = PriorityQueue()

        current_vertex = (start_vert_vec.x, start_vert_vec.y)
        end_vertex = (end_vert_vec.x, end_vert_vec.y)

        self.fill_h_matrix(table, end_vert_vec, heuristic_type)

        opened_vertex.put((1, current_vertex))

        while opened_vertex and current_vertex != end_vertex:

            current_vertex = opened_vertex.get()[1]

            for move in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                next_vertex = (current_vertex[0] + move[0], current_vertex[1] + move[1])

                if next_vertex not in closed_vertex and next_vertex not in self.app.walls:
                    if table[next_vertex]["g"] is not None:
                        old_previous = table[next_vertex]["previous"]
                        table[next_vertex]["previous"] = current_vertex
                        old_g = table[next_vertex]["g"]
                        new_g = self.calculate_g(table, price_matrix, next_vertex)
                        if new_g >= old_g:
                            table[next_vertex]["g"] = new_g
                            table[next_vertex]["f"] = new_g + table[next_vertex]["h"]
                        else:
                            table[next_vertex]["previous"] = old_previous
                    else:
                        table[next_vertex]["previous"] = current_vertex
                        table[next_vertex]["g"] = self.calculate_g(table, price_matrix, next_vertex)
                        table[next_vertex]["f"] = table[next_vertex]["g"] + table[next_vertex]["h"]

                    opened_vertex.put((table[next_vertex]["f"], next_vertex))

                    if next_vertex == end_vertex:
                        break

            closed_vertex.append(current_vertex)

        real_path = [end_vertex]
        while table[end_vertex]["previous"] is not None:
            real_path.insert(0, table[end_vertex]["previous"])
            end_vertex = table[end_vertex]["previous"]

        return real_path

    def greedy_search(self, start_ver, end_vert):

        price_matrix = self.create_price_matrix()

        current_vertex = start_ver
        end_vertex = (end_vert.x, end_vert.y)
        closed_vertex = []
        path = []

        while True and current_vertex != end_vertex:

            best_move = None
            min_price = 1000

            for move in ((1, 0), (-1, 0), (0, 1), [0, -1]):
                next_vertex = (current_vertex[0] + move[0], current_vertex[1] + move[1])

                if next_vertex == end_vert:
                    best_move = move
                    break

                if next_vertex not in closed_vertex and next_vertex not in self.app.walls:
                    move_price = price_matrix[int(next_vertex[1])][int(next_vertex[0])]

                    if move_price < min_price:
                        best_move = move
                        min_price = move_price

            if best_move is None:
                closed_vertex.append(current_vertex)
                current_vertex = path.pop(len(path) - 1)
                continue

            closed_vertex.append(current_vertex)
            path.append(current_vertex)
            current_vertex = (current_vertex[0] + best_move[0], current_vertex[1] + best_move[1])

        path.append(end_vertex)
        return path

    def create_price_matrix(self):
        price_matrix = [[VOID_PRICE for x in range(COLS)] for x in range(ROWS)]
        for yidx, row in enumerate(price_matrix):
            for xidx, cell in enumerate(row):
                if vec(xidx, yidx) in self.app.coins:
                    price_matrix[yidx][xidx] = 0
                elif vec(xidx, yidx) in self.app.walls:
                    price_matrix[yidx][xidx] = 1000
        return price_matrix

    def fill_h_matrix(self, table, end_pos, heuristic_type):
        for yidx, row in enumerate(self.app.game_field):
            for xidx, cell in enumerate(row):
                if (vec(xidx, yidx)) not in self.app.walls:
                    table[(xidx, yidx)] = {"g": None, "h": None, "f": None, "previous": None}
                    if heuristic_type == "manhattan":
                        table[(xidx, yidx)]["h"] = self.calculate_manhattan_distance((xidx, yidx), end_pos)
                    elif heuristic_type == "bfs":
                        table[(xidx, yidx)]["h"] = self.calculate_bfs_distance(vec(xidx, yidx), end_pos)
                    else:
                        print("Incorrect name of heuristic function")
                        exit()

    def follow_path(self, path):
        self.app.draw_path(path, WHITE)
        pygame.display.update()
        sleep(2)

        for cell in path:
            move = (vec(cell) - self.grid_pos)

            if (move == vec(0, 0)): continue

            self.stored_direction = None
            self.direction = move

            for i in range(0, int(self.app.cell_width / SPEED)):
                if self.able_to_move:
                    self.pix_pos += self.direction * self.speed

                self.grid_pos = self.get_grid_pos_from_pix_pos(self.pix_pos)

                if self.on_coin():
                    self.eat_coin()

                if self.time_to_move():
                    break

            self.draw()
            self.app.playing_draw()
            self.app.draw_pressed_cells()
            pygame.display.update()
            sleep(0.2)


    def use_a_star_for_4_points(self):
        for cell in self.app.pressed_cells:
            path = self.a_star(self.grid_pos, vec(cell), "manhattan")
            self.follow_path(path)
        self.app.pressed_cells = []
        self.direction = vec(0, 0)


    def calculate_manhattan_distance(self, start_vert, end_vert):
        return abs(end_vert[0] - start_vert[0]) + abs(end_vert[1] - start_vert[1])

    def calculate_bfs_distance(self, start_vert, end_vert):
        path = self.bfs(start_vert, end_vert)
        return len(path)

    def calculate_g(self, table, price_matrix, vertex):
        if table[vertex]["previous"] is None:
            return 0
        elif table[vertex]["previous"] is not None:
            return price_matrix[int(vertex[1])][int(vertex[0])] + self.calculate_g(table, price_matrix, table[vertex]["previous"])
