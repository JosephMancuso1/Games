""" Very close approximation to the google chrome dinosaur game with some additional features"""

from sprites import *
from os import path
from settings import *
import pygame as pg


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir)
        # load spritesheet
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

    def events(self):
        for events in pg.event.get():
            if events.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if events.type == pg.KEYDOWN:
                if events.key == pg.K_SPACE:
                    self.player.jump()
                if events.key == pg.K_DOWN:
                    self.player.duck()
                if events.key == pg.K_UP:
                    self.player.ducking = False
                    self.player.running = True
                    self.player.animate()
            if events.type == pg.KEYUP:
                if events.key == pg.K_SPACE:
                    self.player.jump_cut()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def new(self):
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.birds = pg.sprite.Group()
        self.cacti = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        Platforms(0, HEIGHT - 30, self)
        for cactus in CACTUS_LIST:
            Cactus(*cactus, self)
        self.bird_timer = 0
        self.cactus_timer = 0
        self.run()

    def update(self):
        self.all_sprites.update()
        now = pg.time.get_ticks()

        # spawns new bird
        if now - self.bird_timer > MOB_FREQ + random.choice([-1000, -500, 0, 500, 1000]):
            self.bird_timer = now
            Bird(self)

        # spawns new cacti if there are less than 3 in existence, their speed increases as a function of the score
        while len(self.cacti) < 3:
            Cactus(WIDTH + 400, HEIGHT - 70, self)

        # what happens when the player sprite hits the bird
        bird_hits = pg.sprite.spritecollide(self.player, self.birds, False, pg.sprite.collide_mask)
        if bird_hits:
            self.playing = False

        # what happens when the player sprite hits the floor
        floor_hits = pg.sprite.spritecollide(self.player, self.platforms, False)
        if floor_hits:
            self.player.vel.y = 0
            self.player.pos.y = floor_hits[0].rect.top

        # what happens when player hits the cactus
        cactus_hit = pg.sprite.spritecollide(self.player, self.cacti, False, pg.sprite.collide_mask)
        if cactus_hit:
            self.playing = False

        # score system when the birds and cacti leave the screen
        for bird in self.birds:
            if bird.rect.centerx < 0:
                bird.kill()
                self.score += 10
        for cactus in self.cacti:
            if cactus.rect.x < 0:
                cactus.kill()
                self.score += 10

    def show_start_screen(self):
        self.screen.fill(BLACK)
        # load background image:
        pg.mixer.music.load(BACKGROUND_MUSIC)
        BGImg = pg.image.load('Dinosaur Background.jpg')
        pg.mixer.music.play(-1)
        self.screen.blit(BGImg, (0, 0))
        self.draw_text('Dinosaur Game', 40, BLACK, WIDTH / 2, HEIGHT / 4)
        self.draw_text('Arrows to move and space to jump', 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text('Press a key to begin playing', 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_key()

    def draw(self):
        self.screen.fill(BG)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, GREEN, WIDTH/2, 15)
        # updates the entire display
        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def show_gameover_screen(self):
        if self.running == False:
            return
        game_over_bg = pg.image.load('GameOver.jpg')
        self.screen.fill(BLACK)
        self.screen.blit(game_over_bg, (0, 0))
        self.draw_text('GAME OVER', 40, RED, WIDTH/2, HEIGHT/4)
        self.draw_text('Score: ' + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text('Press a key to play again', 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for events in pg.event.get():
                if events.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if events.type == pg.KEYUP:
                    waiting = False


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_gameover_screen()
pg.quit()
