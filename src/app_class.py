import pygame.draw

from player_class import *
from enemy_class import *
from db.postgre_sql import load_data_to_db
from maze_generation import carve_out_maze
from maze_generation import generate_stable_maze

pygame.init()
vec = pygame.math.Vector2


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.start_time = None
        self.current_time = None
        self.running = True
        self.state = 'start'
        self.cell_width = MAZE_WIDTH // COLS
        self.cell_height = MAZE_HEIGHT // ROWS
        self.walls = []
        self.coins = []
        self.game_field = [[0 for x in range(COLS)] for x in range(ROWS)]
        self.enemies = []
        self.e_pos = []
        self.p_pos = None
        self.result_is_saved = False
        self.load()
        self.player = Player(self, vec(self.p_pos))
        self.make_enemies()
        self.pressed_cells = []
        self.minimax = Minimax(self.player, self.enemies, 6, "alpha-beta")

    def run(self):
        while self.running:
            if self.state == 'start':
                self.start_events()
                self.start_update()
                self.start_draw()
            elif self.state == 'playing':
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == "pause":
                self.pause_events()
                self.pause_draw()
            elif self.state == 'game over':
                self.game_over_events()
                self.game_over_update()
                self.game_over_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    ############################ HELPER FUNCTIONS ##################################

    def draw_path(self, path, color):
        for cell_pos in path:
            pix_pos = self.player.get_pix_pos_from_grid_pos_for_rect(cell_pos[0], cell_pos[1])
            pygame.draw.rect(self.screen, color,
                             (pix_pos[0], pix_pos[1], self.cell_width, self.cell_height))

    def draw_pressed_cells(self):
        for cell in self.pressed_cells:
            cell_pix = self.player.get_pix_pos_from_grid_pos_for_rect(cell[0], cell[1])
            pygame.draw.rect(self.screen, RED, (cell_pix[0], cell_pix[1], self.cell_width, self.cell_height), 0)

    def pos_is_in_field(self, pos):
        return 0 <= pos[0] < COLS and 0 <= pos[1] < ROWS

    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0] - text_size[0] // 2
            pos[1] = pos[1] - text_size[1] // 2
        screen.blit(text, pos)

    def load(self):
        # random
        # carve_out_maze(self.game_field)

        # stable
        self.game_field = generate_stable_maze()

        for yidx, row in enumerate(self.game_field):
            for xidx, cell in enumerate(row):
                if cell == 1:
                    self.walls.append(vec(xidx, yidx))
                elif cell == 0:
                    self.coins.append(vec(xidx, yidx))

        self.coins.remove(vec(1, 1))
        self.p_pos = (vec(1, 1))

        self.add_enemies(2)

    def add_enemies(self, count):
        for enemy_num in range(0, count):
            self.e_pos.append(
                [self.coins[len(self.coins) - (enemy_num + 1)].x, self.coins[len(self.coins) - (enemy_num + 1)].y])

    def update_time(self):
        self.current_time = (pygame.time.get_ticks() - self.start_time) // 1000

    def make_enemies(self):
        for idx, pos in enumerate(self.e_pos):
            enemy_type = "default"
            if idx == 1:
                enemy_type = "bfs"
            self.enemies.append(Enemy(self, vec(pos), enemy_type))

    def check_death(self):
        for enemy in self.enemies:
            diff = [enemy.pix_pos.x - self.player.pix_pos.x, enemy.pix_pos.y - self.player.pix_pos.y]
            if abs(diff[0]) < (self.cell_width // 4) and abs(diff[1]) < (self.cell_width // 4):
                return True
        return False

    def reset(self):
        self.player.lives = LIVES
        self.player.current_score = 0
        self.player.grid_pos = vec(self.player.starting_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        self.start_time = pygame.time.get_ticks()
        for enemy in self.enemies:
            enemy.grid_pos = vec(enemy.starting_pos)
            enemy.pix_pos = enemy.get_pix_pos()
            enemy.direction *= 0

        self.coins = []
        for yidx, row in enumerate(self.game_field):
            for xidx, cell in enumerate(row):
                if cell == 0:
                    self.coins.append(vec(xidx, yidx))

        self.state = "playing"

    ########################### INTRO FUNCTIONS ####################################

    def start_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = 'playing'
                self.start_time = pygame.time.get_ticks()

    def start_update(self):
        pass

    def start_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('PUSH SPACE BAR', self.screen, [
            WIDTH // 2, HEIGHT // 2 - 50], START_TEXT_SIZE, (170, 132, 58), START_FONT, centered=True)
        self.draw_text('1 PLAYER ONLY', self.screen, [
            WIDTH // 2, HEIGHT // 2 + 50], START_TEXT_SIZE, (44, 167, 198), START_FONT, centered=True)
        self.draw_text('HIGH SCORE', self.screen, [4, 0],
                       START_TEXT_SIZE, (255, 255, 255), START_FONT)
        pygame.display.update()

    ########################### PLAYING FUNCTIONS ##################################

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0, 1))
                if event.key == pygame.K_p:
                    self.state = "pause"

    def playing_update(self):

        self.update_time()

        if self.player.time_to_move():
            best_move = self.minimax.run()
            self.player.move(best_move)
            self.player.direction = best_move

        self.player.update("yes")
        for enemy in self.enemies:
            enemy.update()

        if self.check_death():
            self.remove_life()

        if len(self.coins) == 0:
            self.state = "game over"

    def playing_draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.screen, (TOP_BOTTOM_BUFFER // 2, TOP_BOTTOM_BUFFER // 2))
        self.draw_coins()
        for wall in self.walls:
            xidx, yidx = wall
            pygame.draw.rect(self.screen, GREY, (
            TOP_BOTTOM_BUFFER // 2 + xidx * self.cell_width, TOP_BOTTOM_BUFFER // 2 + yidx * self.cell_height,
            self.cell_width, self.cell_height))

        self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score),
                       self.screen, [60, 0], 18, WHITE, START_FONT)
        self.draw_text('TIME: {}'.format(self.current_time),
                       self.screen, [WIDTH // 2 + 90, 0], 18, WHITE, START_FONT)

        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        pygame.display.update()

    def remove_life(self):
        self.player.lives -= 1
        if self.player.lives == 0:
            self.state = "game over"
        else:
            self.player.grid_pos = vec(self.player.starting_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            for enemy in self.enemies:
                enemy.grid_pos = vec(enemy.starting_pos)
                enemy.pix_pos = enemy.get_pix_pos()
                enemy.direction *= 0

    def draw_coins(self):
        for coin in self.coins:
            pygame.draw.circle(self.screen, (124, 123, 7),
                               (int(coin.x * self.cell_width) + self.cell_width // 2 + TOP_BOTTOM_BUFFER // 2,
                                int(coin.y * self.cell_height) + self.cell_height // 2 + TOP_BOTTOM_BUFFER // 2), 5)

    ########################### PAUSE ################################

    def pause_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.state = 'playing'

    def pause_draw(self):
        self.draw_text('PAUSE', self.screen, [
            WIDTH // 2, HEIGHT // 2 - 20], 24, WHITE, START_FONT, centered=True)
        self.draw_text('PUSH SPACE BAR TO CONTINUE', self.screen, [
            WIDTH // 2, HEIGHT - 15], 14, WHITE, START_FONT, centered=True)
        pygame.display.update()

    ########################### GAME OVER FUNCTIONS ################################

    def game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                if not self.result_is_saved:
                    load_data_to_db([self.player.current_score, self.current_time, self.player.search_type])
                    self.result_is_saved = True

    def game_over_update(self):
        pass

    def game_over_draw(self):
        self.screen.fill(BLACK)
        quit_text = "Press the escape button to QUIT"
        again_text = "Press SPACE bar to PLAY AGAIN"
        save_result_text = "Press S button to save your result"

        if len(self.coins):
            self.draw_text("GAME OVER", self.screen, [WIDTH // 2, 100], 52, RED, "arial", centered=True)
        else:
            self.draw_text("VICTORY", self.screen, [WIDTH // 2, 100], 52, GREEN, "arial", centered=True)

        self.draw_text('SCORE: {}'.format(self.player.current_score),
                       self.screen, [80, 10], 18, WHITE, START_FONT)
        self.draw_text('TIME: {}'.format(self.current_time),
                       self.screen, [WIDTH // 2 + 90, 10], 18, WHITE, START_FONT)
        self.draw_text(save_result_text, self.screen, [WIDTH // 2, HEIGHT // 3], 32, GOLD, "arial", centered=True)

        if self.result_is_saved:
            self.draw_text("YOUR RESULT HAS BEEN SAVED", self.screen, [
                WIDTH // 2, HEIGHT // 2.5], 24, GREEN, "arial", centered=True)

        self.draw_text(again_text, self.screen, [
            WIDTH // 2, HEIGHT // 1.7], 36, (190, 190, 190), "arial", centered=True)
        self.draw_text(quit_text, self.screen, [
            WIDTH // 2, HEIGHT // 1.4], 36, (190, 190, 190), "arial", centered=True)

        pygame.display.update()
