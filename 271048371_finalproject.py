# MUHAMMAD BIN MUHAMMAD SALEEM

import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# images
background_image = pygame.image.load('background.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
chicken_image = pygame.image.load('chicken.png')
chicken_image = pygame.transform.scale(chicken_image, (60, 60))
player_image = pygame.image.load('player.png')
player_image = pygame.transform.scale(player_image, (50, 50))
heart_image = pygame.image.load('heart.png')
heart_image = pygame.transform.scale(heart_image, (30, 30))
beam_image = pygame.image.load('beam.png')
beam_image = pygame.transform.scale(beam_image, (5, 30))
egg_image = pygame.image.load('egg.png')
egg_image = pygame.transform.scale(egg_image, (20, 30))
chicken_leg_image = pygame.image.load('chicken_leg.png')
chicken_leg_image = pygame.transform.scale(chicken_leg_image, (40, 40))
flash_image = pygame.image.load('flash.png')
flash_image = pygame.transform.scale(flash_image, (50, 50))
slowmo_image = pygame.image.load('slowmo.png')
slowmo_image = pygame.transform.scale(slowmo_image, (50, 50))

# sounds
laser_sound = pygame.mixer.Sound('laser.mp3')
chicken_sound = pygame.mixer.Sound('chicken.mp3')
pygame.mixer.music.load('bgmusic.mp3')

# arcade font
font_path = 'pixelfont.otf'
font = pygame.font.Font(font_path, 30)  # Reduced font size

# High score file
HIGH_SCORE_FILE = "high_scores.txt"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# FPS 
FPS = 60

# Speed of the falling eggs fine tuned 
EGG_SPEED = 4

# Base class
class Game:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.chickens = pygame.sprite.Group()
        self.eggs = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.spawn_chickens(20) # spawns 20 chickens as Level 1 to familiarise player and start
        self.level = 1
        self.last_powerup_spawn_time = pygame.time.get_ticks()
        self.slowmo_active = False
        self.load_high_scores()

    def spawn_chickens(self, num_chickens): # screen positioning and pattern
        for _ in range(num_chickens):
            x = random.randint(0, SCREEN_WIDTH - 50)
            y = random.randint(0, SCREEN_HEIGHT // 2)
            pattern = random.choice(['horizontal', 'zigzag', 'complex'])
            chicken = Chicken(x, y, pattern)
            self.all_sprites.add(chicken)
            self.chickens.add(chicken)

    def spawn_powerup(self):
        now = pygame.time.get_ticks()
        if now - self.last_powerup_spawn_time > 3000:  # Spawn a powerup every 3 seconds
            x = random.randint(0, SCREEN_WIDTH - 30)
            y = 0
            powerup_type = random.choice(['chicken_leg', 'flash', 'slowmo'])
            if powerup_type == 'chicken_leg':
                powerup = Powerup(x, y, chicken_leg_image, 'chicken_leg')
            elif powerup_type == 'flash':
                powerup = Powerup(x, y, flash_image, 'flash')
            else:
                powerup = Powerup(x, y, slowmo_image, 'slowmo')
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)
            self.last_powerup_spawn_time = now

    def update(self):
        self.all_sprites.update()
        self.check_collisions()
        self.spawn_powerup()

        if len(self.chickens) < 3:
            self.level += 1
            self.spawn_chickens(40) #40 chickens as the level progresses 

    def check_collisions(self):
        hits = pygame.sprite.spritecollide(self.player, self.chickens, True)
        for hit in hits:
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.game_over()

        egg_hits = pygame.sprite.spritecollide(self.player, self.eggs, True)
        for egg in egg_hits:
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.game_over()

        bullet_hits = pygame.sprite.groupcollide(self.chickens, self.bullets, True, True)
        for hit in bullet_hits:
            Score.increment()
            chicken_sound.play()

        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            if powerup.type == 'chicken_leg':
                self.player.lives += 1
            elif powerup.type == 'flash':
                self.player.beam_count += 1
            elif powerup.type == 'slowmo':
                self.slow_down_chickens()
            Score.increment()

    def slow_down_chickens(self):
        for chicken in self.chickens:
            chicken.speedx *= 0.5
        self.slowmo_active = True
        pygame.time.set_timer(pygame.USEREVENT, 5000)  # Slow down for 5 seconds

    def game_over(self):
        Score.check_high_score()
        self.save_high_score()
        self.show_game_over_screen()

# Ending Screen 
    def show_game_over_screen(self):
        screen.blit(background_image, (0, 0))
        text = font.render("GAME OVER!", True, WHITE)
        score_text = font.render(f"Your Score: {Score.score}", True, WHITE)
        high_score_text = font.render(f"High Score: {Score.high_score}", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80)) 
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 120))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting = False
                        Score.reset()
                        main()

# Storing high scores in a file:  
    def load_high_scores(self):
        try:
            with open(HIGH_SCORE_FILE, "r") as file:
                scores = file.readlines()
                Score.high_score = max([int(score.split(": ")[1]) for score in scores])
        except FileNotFoundError:
            Score.high_score = 0

    def save_high_score(self):
        with open(HIGH_SCORE_FILE, "a") as file: # append file to also keep the last scores safe
            file.write(f"{Score.name}: {Score.score}\n")

# Background class
class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = background_image
        self.rect = self.image.get_rect()
        self.y1 = 0
        self.y2 = -self.rect.height

    def update(self):
        self.y1 += 5
        self.y2 += 5
        if self.y1 >= self.rect.height:
            self.y1 = -self.rect.height
        if self.y2 >= self.rect.height:
            self.y2 = -self.rect.height

    def render(self):
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.lives = 3
        self.beam_count = 1

    def update(self):
        self.rect.centerx, self.rect.centery = pygame.mouse.get_pos()
        self.rect.centery = min(max(self.rect.centery, SCREEN_HEIGHT - 400), SCREEN_HEIGHT - 10)

    def shoot(self):
        for i in range(self.beam_count):
            bullet = Bullet(self.rect.centerx + i * 10 - (self.beam_count - 1) * 5, self.rect.top)
            game.all_sprites.add(bullet)
            game.bullets.add(bullet)
            laser_sound.play()

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = beam_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        self.rect.y -= 15
        if self.rect.bottom < 0:
            self.kill()

# Egg class
class Egg(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = egg_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

    def update(self):
        self.rect.y += EGG_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Powerup class
class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, image, powerup_type):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.type = powerup_type

    def update(self):
        self.rect.y += 2
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Chicken class
class Chicken(pygame.sprite.Sprite):
    def __init__(self, x, y, pattern='horizontal'):
        super().__init__()
        self.image = chicken_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = 2
        self.pattern = pattern
        self.direction = 1

    def update(self):
        if self.pattern == 'horizontal':
            self.rect.x += self.speedx * self.direction
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.direction *= -1
        elif self.pattern == 'zigzag':
            self.rect.x += self.speedx * self.direction
            self.rect.y += abs(self.speedx) * self.direction
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH or self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT // 2:
                self.direction *= -1
        elif self.pattern == 'complex':
            self.rect.x += self.speedx * self.direction
            self.rect.y += (self.speedx // 2) * self.direction
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH or self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT // 2:
                self.direction *= -1

        # Ensure chickens stay within the screen and do not fall below height of 400 from the bottom
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT - 300:
            self.rect.bottom = SCREEN_HEIGHT - 300

        if random.random() < 0.003:  # the rate at which the eggs drop
            self.drop_egg()

    def drop_egg(self):
        egg = Egg(self.rect.centerx, self.rect.bottom)
        game.all_sprites.add(egg)
        game.eggs.add(egg)

# Score class
class Score:
    score = 0
    high_score = 0
    name = ""

    @classmethod
    def increment(cls):
        cls.score += 1

    @classmethod
    def check_high_score(cls):
        if cls.score > cls.high_score:
            cls.high_score = cls.score

    @classmethod
    def reset(cls):
        cls.score = 0
        cls.name = ""

# Game loop
def main():
    global game
    pygame.display.set_caption('CHICKEN INVADERS BY MUHAMMAD BIN SALEEM')

    # game object
    game = Game()

    # background
    background = Background()

    clock = pygame.time.Clock()

    # Start menu loop
    start_game = False
    player_name = ""
    entering_name = True

    # Play background music
    pygame.mixer.music.play(-1)

    while entering_name:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    entering_name = False
                    Score.name = player_name
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode

        screen.blit(background_image, (0, 0))
        text = font.render("Enter your gamer name:", True, WHITE)
        name_text = font.render(player_name, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2 - 40))
        screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2 - name_text.get_height() // 2))
        pygame.display.flip()

    # game start loop
    while not start_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                start_game = True

        screen.blit(background_image, (0, 0))
        text = font.render("CHICKEN INVADERS", True, WHITE)
        sub_text = font.render("CLICK TO START", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
        screen.blit(sub_text, (SCREEN_WIDTH // 2 - sub_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        pygame.display.flip()

    # Main game loop
    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.player.shoot()
            elif event.type == pygame.USEREVENT and game.slowmo_active:
                for chicken in game.chickens:
                    chicken.speedx *= 2
                game.slowmo_active = False

        background.update()
        game.update()

        background.render()
        game.all_sprites.draw(screen)

        # drawing lives
        for i in range(game.player.lives):
            screen.blit(heart_image, (10 + i * 35, 10))

        # score display
        score_text = font.render(f"Score: {Score.score}", True, WHITE)
        high_score_text = font.render(f"High Score: {Score.high_score}", True, WHITE)
        screen.blit(score_text, (10, SCREEN_HEIGHT - 60)) 
        screen.blit(high_score_text, (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

