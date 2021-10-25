import pygame
import random
from settings import *

vec = pygame.math.Vector2


class Enemy:
    def __init__(self, app, pos, number):
        self.app = app
        self.grid_pos = pos
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.radius = int(self.app.cell_width // 2.3)
        self.number = number
        self.colour = (255, 5, 5)
        self.direction = vec(0, 0)
        self.speed = 2

    def update(self):
        self.pix_pos += self.direction * self.speed

        self.grid_pos[0] = (self.pix_pos[0] - TOP_BOTTOM_BUFFER +
                            self.app.cell_width // 2) // self.app.cell_width
        self.grid_pos[1] = (self.pix_pos[1] - TOP_BOTTOM_BUFFER +
                            self.app.cell_height // 2) // self.app.cell_height

        if self.time_to_move():
            self.change_direction_if_possible()

    def draw(self):
        pygame.draw.circle(self.app.screen, self.colour,
                           (int(self.pix_pos.x), int(self.pix_pos.y)), self.radius)

    def time_to_move(self):
        if (self.pix_pos.x - TOP_BOTTOM_BUFFER // 2 - self.app.cell_width // 2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True

        if (self.pix_pos.y - TOP_BOTTOM_BUFFER // 2 - self.app.cell_height // 2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True


    def change_direction_if_possible(self):
        if ((self.grid_pos + self.direction) in self.app.walls) or (self.direction == vec(0, 0)):
            self.direction = self.get_random_direction()

        if self.direction in [vec(1, 0), vec(-1, 0)]:
            if self.grid_pos + vec(0, 1) not in self.app.walls or self.grid_pos + vec(0, -1) not in self.app.walls:
                while True:
                    new_direction = self.get_random_direction()
                    if new_direction != vec(self.direction.x * -1, self.direction.y):
                        self.direction = new_direction
                        return

        if self.direction in [vec(0, 1), vec(0, -1)]:
            if self.grid_pos + vec(1, 0) not in self.app.walls or self.grid_pos + vec(-1, 0) not in self.app.walls:
                while True:
                    new_direction = self.get_random_direction()
                    if new_direction != vec(self.direction.x, self.direction.y * -1):
                        self.direction = new_direction
                        return

    def get_random_direction(self):
        while True:
            number = random.randint(-2, 1)
            if number == -2:
                x_dir, y_dir = 1, 0
            elif number == -1:
                x_dir, y_dir = 0, 1
            elif number == 0:
                x_dir, y_dir = -1, 0
            else:
                x_dir, y_dir = 0, -1
            next_pos = vec(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            if next_pos not in self.app.walls:
                break
        return vec(x_dir, y_dir)

    def get_pix_pos(self):
        return vec((self.grid_pos.x * self.app.cell_width) + TOP_BOTTOM_BUFFER // 2 + self.app.cell_width // 2,
                   (self.grid_pos.y * self.app.cell_height) + TOP_BOTTOM_BUFFER // 2 +
                   self.app.cell_height // 2)
