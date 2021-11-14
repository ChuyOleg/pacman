import sys

import random
import pygame
import math

vec = pygame.math.Vector2


class Minimax:
    def __init__(self, player, enemies, max_deep, algorithm_type):
        self.player = player
        self.enemies = enemies
        self.max_deep = max_deep
        self.algorithm_type = algorithm_type

    def run(self):
        if self.player.time_to_move():

            best_move = self.make_move(1, self.max_deep, -math.inf, math.inf, True)

            return best_move["direction"]

    def make_move(self, deep, max_deep, alpha, beta, maximizing_player):
        saved_player_pos = self.save_player_pos()

        saved_enemies_pos = self.save_enemies_pos()

        if maximizing_player:
            max_move = {"price": -math.inf, "direction": vec(0, 0)}
            for move in self.get_available_moves(self.player):
                self.player.grid_pos += move

                eval_val = 0
                if self.player.grid_pos in self.player.app.coins:
                    eval_val += 2
                if self.is_victory():
                    eval_val = math.inf
                if self.is_dead():
                    eval_val = -math.inf

                if deep == max_deep:
                    eval_val += self.calculate_move_price()
                else:
                    eval_val += self.make_move(deep + 1, max_deep, alpha, beta, False)["price"]

                active_move = {"price": eval_val, "direction": move}

                max_move = self.max_move(max_move, active_move)

                self.rollback_pos_changes(saved_player_pos, saved_enemies_pos)

                if self.algorithm_type == "alpha-beta":
                    alpha = max(alpha, eval_val)
                    if beta < alpha:
                        break

            return max_move
        else:
            enemy_0 = self.enemies[0]
            enemy_1 = self.enemies[1]
            enemy0_moves = self.get_available_moves(enemy_0)
            enemy1_moves = self.get_available_moves(enemy_1)
            min_move = {"price": math.inf, "direction": [enemy0_moves[0], enemy1_moves[1]]}
            for enemy0_move in enemy0_moves:
                for enemy1_move in enemy1_moves:
                    enemy_0.grid_pos += enemy0_move
                    enemy_1.grid_pos += enemy1_move

                    eval_val = 0

                    if self.is_dead():
                        if self.algorithm_type == "expectimax" and enemy_0.grid_pos == self.player.grid_pos and random.choice(range(0, 5)) != 0:
                            self.rollback_pos_changes(saved_player_pos, saved_enemies_pos)
                            continue
                        else:
                            eval_val = -math.inf

                    if deep == max_deep:
                        eval_val += self.calculate_move_price()
                    else:
                        eval_val += self.make_move(deep + 1, max_deep, alpha, beta, True)["price"]

                    active_move = {"price": eval_val, "direction": [enemy0_move, enemy1_move]}

                    min_move = self.min_move(min_move, active_move)

                    self.rollback_pos_changes(saved_player_pos, saved_enemies_pos)

                    if self.algorithm_type == "alpha-beta":
                        beta = min(beta, eval_val)
                        if beta < alpha:
                            break
                else:
                    continue
                break

            return min_move

    def calculate_move_price(self):
        move_price = 0
        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos:
                return 0
            else:
                move_price += math.sqrt(abs(self.player.grid_pos[0] - enemy.grid_pos[0]) + abs(
                    self.player.grid_pos[1] - enemy.grid_pos[1]))

        return move_price

    def select_best_move(self, min_or_max, move_list):
        best_move = move_list[0]
        for move in move_list:
            if min_or_max == "min" and move["price"] < best_move["price"]:
                best_move = move
            elif min_or_max == "max" and move["price"] > best_move["price"]:
                best_move = move
            elif min_or_max not in ("min", "max"):
                print("Incorrect min_or_max value: " + min_or_max)
                sys.exit()
        return best_move

    def get_available_moves(self, person):
        moves = []
        for move in (vec(1, 0), vec(0, 1), vec(-1, 0), vec(0, -1)):
            if (person.grid_pos + move) not in self.player.app.walls:
                moves.append(move)
        return moves

    def max_move(self, move_1, move_2):
        if move_1["price"] > move_2["price"]:
            return move_1
        else:
            return move_2

    def min_move(self, move_1, move_2):
        if move_1["price"] < move_2["price"]:
            return move_1
        else:
            return move_2

    def is_victory(self):
        if len(self.player.app.coins) == 1 and self.player.grid_pos in self.player.app.coins:
            return True
        else:
            return False

    def is_dead(self):
        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos:
                return True
        return False

    def save_player_pos(self):
        return [self.player.grid_pos.x, self.player.grid_pos.y]

    def save_enemies_pos(self):
        arr = []
        for enemy in self.enemies:
            arr.append([enemy.grid_pos.x, enemy.grid_pos.y])
        return arr

    def rollback_pos_changes(self, saved_player_pos, saved_enemies_pos):
        self.player.grid_pos = vec(saved_player_pos[0], saved_player_pos[1])
        for idx, pos in enumerate(saved_enemies_pos):
            self.enemies[idx].grid_pos = vec(pos[0], pos[1])
