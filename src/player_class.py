from queue import PriorityQueue
import heapq
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

        self.grid_pos[0] = (self.pix_pos[0] - TOP_BOTTOM_BUFFER // 2 -
                            self.app.cell_width // 2) // self.app.cell_width
        self.grid_pos[1] = (self.pix_pos[1] - TOP_BOTTOM_BUFFER // 2 -
                            self.app.cell_height // 2) // self.app.cell_height

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
                    if next_cell not in visited and self.app.game_field[int(next_cell[1])][int(next_cell[0])] != 1:
                        queue.put((current[0] + 1, next_cell))
                        path.append({"Current": current_node, "Next": next_cell})

        real_path = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    real_path.insert(0, step["Current"])

        return real_path

    def a_star(self, start_vert_vec, end_vert_vec):
        price_matrix = self.define_price_matrix()
        table = {}

        self.refill_price_matrix(price_matrix, table)

        closed_vertex = []
        opened_vertex = []
        start_vertex = (start_vert_vec.x, start_vert_vec.y)
        end_vertex = (end_vert_vec.x, end_vert_vec.y)

        # self.calculate_h(price_matrix, table, "manhattan", end_vertex)
        self.calculate_h(price_matrix, table, "greedy", end_vertex)

        heapq.heappush(opened_vertex, (1, start_vertex))

        while opened_vertex:

            current_vertex = heapq.heappop(opened_vertex)[1]

            for move in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                next_vertex = (current_vertex[0] + move[0], current_vertex[1] + move[1])

                if next_vertex not in closed_vertex and next_vertex not in self.app.walls:
                    if table[next_vertex]["g"] is not None:
                        old_previous = table[next_vertex]["previous"]
                        table[next_vertex]["previous"] = current_vertex
                        old_g = table[next_vertex]["g"]
                        new_g = self.calculate_g(table, price_matrix, next_vertex)
                        if new_g < old_g:
                            table[next_vertex]["g"] = new_g
                            table[next_vertex]["f"] = new_g + table[next_vertex]["h"]
                        else:
                            table[next_vertex]["previous"] = old_previous
                    else:
                        table[next_vertex]["previous"] = current_vertex
                        table[next_vertex]["g"] = self.calculate_g(table, price_matrix, next_vertex)
                        table[next_vertex]["f"] = table[next_vertex]["g"] + table[next_vertex]["h"]

                    if (next_vertex == end_vertex):
                        self.show_path(table, next_vertex)
                        return

                    heapq.heappush(opened_vertex, ((table[next_vertex]["f"]), next_vertex))

            closed_vertex.append(current_vertex)

        self.show_path(table, end_vertex)


    def show_path(self, table, vertex):
        if table[vertex]["previous"] is None:
            return
        else:
            pygame.draw.rect(self.app.screen, RED, (vertex[0] * self.app.cell_width + TOP_BOTTOM_BUFFER // 2,
                                                    vertex[1] * self.app.cell_height + TOP_BOTTOM_BUFFER // 2,
                                                    self.app.cell_width, self.app.cell_height), 0)
            self.show_path(table, table[vertex]["previous"])

    def calculate_manhattan_distance(self, start_vert, end_vert):
        return abs(end_vert[0] - start_vert[0]) + abs(end_vert[1] - start_vert[1])


    def greedy_heuristic(self, price_matrix, start_ver, end_vert):
        current_vertex = start_ver
        closed_vertex = []
        vertex_queue = []
        path = []
        overall_price = 0

        while (True):
            best_move = None
            min_price = 1000

            for move in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                next_vertex = (current_vertex[0] + move[0], current_vertex[1] + move[1])

                if next_vertex == end_vert:
                    path.append(current_vertex)
                    return overall_price

                if next_vertex not in closed_vertex and next_vertex not in self.app.walls:
                    move_price = price_matrix[int(current_vertex[1])][int(current_vertex[0])]

                    if move_price < min_price:
                        best_move = move
                        min_price = move_price

            if best_move is None:
                closed_vertex.append(current_vertex)
                if (len(path) == 0):
                    return 100
                previous_vertex = path.pop(len(path) - 1)
                current_vertex = previous_vertex
                continue

            closed_vertex.append(current_vertex)
            vertex_queue.append(current_vertex)
            if current_vertex != start_ver:
                path.append(current_vertex)
                overall_price += min_price
            current_vertex = (current_vertex[0] + best_move[0], current_vertex[1] + best_move[1])

    def define_price_matrix(self):
        return [[VOID_PRICE for x in range(COLS)] for x in range(ROWS)]

    def refill_price_matrix(self, matrix, table):
        for yidx, row in enumerate(matrix):
            for xidx, cell in enumerate(row):
                if vec(xidx, yidx) in self.app.coins:
                    matrix[yidx][xidx] = 0
                    table[(xidx, yidx)] = {"g": None, "h": None, "f": None, "previous": None}
                elif vec(xidx, yidx) in self.app.walls:
                    matrix[yidx][xidx] = 1000
                else:
                    table[(xidx, yidx)] = {"g": None, "h": None, "f": None, "previous": None}

    def calculate_h(self, price_matrix, table, heuristic_type, end_pos):
        for yidx, row in enumerate(price_matrix):
            for xidx, cell in enumerate(row):
                if vec(xidx, yidx) not in self.app.walls:
                    if heuristic_type == "manhattan":
                        table[(xidx, yidx)]["h"] = self.calculate_manhattan_distance((xidx, yidx), end_pos)
                    elif heuristic_type == "greedy":
                        table[(xidx, yidx)]["h"] = self.greedy_heuristic(price_matrix, (xidx, yidx), end_pos)

    def calculate_g(self, table, price_matrix, vertex):
        if table[vertex]["previous"] is None:
            return 0
        elif table[vertex]["previous"] is not None:
            return price_matrix[int(vertex[1])][int(vertex[0])] + self.calculate_g(table, price_matrix, table[vertex]["previous"])
