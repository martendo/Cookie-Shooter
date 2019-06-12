import pygame, sys, random, time
from pygame.locals import *

WINDOW_WIDTH, WINDOW_HEIGHT = 500, 600

BLACK     = ( 0 ,  0 ,  0 )
WHITE     = (255, 255, 255)
DARK_RED   = (200,  0 ,  0 )
RED       = (255,  0 ,  0 )
DARK_GREEN = ( 0 , 200,  0 )
GREEN     = ( 0 , 255,  0 )

COOKIE_MAX_SIZE = 50
COOKIE_MIN_SIZE = 20
COOKIE_MAX_SPEED_X = 2
COOKIE_MIN_SPEED_X = -2
COOKIE_MAX_SPEED_Y = 6
COOKIE_MIN_SPEED_Y = 4
COOKIE_NUM = 6

MISSILE_SPEED = 10
PLAYER_SPEED = 5
INVULN_TIME = 3

pygame.init()

def draw_text(surf, font, msg, pos, midright=False):
    FONT = pygame.font.Font(font['file'], font['size'])

    textSurf = FONT.render(msg, True, font['colour'])
    textRect = textSurf.get_rect()
    if not midright:
        textRect.center = pos
    else:
        textRect.midright = pos

    surf.blit(textSurf, textRect)

def button(surf, msg, x, y, w, h, ic, ac, func):
    mousePos = pygame.mouse.get_pos()
    mouseClick = pygame.mouse.get_pressed()

    if x + w > mousePos[0] > x and y + h > mousePos[1] > y:
        pygame.draw.rect(surf, ac, (x, y, w, h))
        if mouseClick[0] == 1:
            func()
    else:
        pygame.draw.rect(surf, ic, (x, y, w, h))

    pygame.draw.rect(surf, BLACK, (x, y, w, h), 2)

    draw_text(surf, {'file': 'ComicSansMS.ttf', 'size': 18, 'colour': BLACK},
              msg, (x + (w / 2), y + (h / 2)))

class Missle:
    def __init__(self, player):
        self.player = player
        self.image = pygame.image.load('missile.png')
        self.rect = self.image.get_rect()

class Player:
    def __init__(self):
        self.image = pygame.image.load('ship.png')
        self.rect = self.image.get_rect()
        self.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - self.rect.height)
        self.speed = 0
        self.missiles = []

    def update(self):
        self.speed = 0

        keyPress = pygame.key.get_pressed()

        if keyPress[K_LEFT]:
            self.speed = -PLAYER_SPEED
        if keyPress[K_RIGHT]:
            self.speed = PLAYER_SPEED

        self.rect.x += self.speed

        for missile in self.missiles:
            missile.rect.y -= MISSILE_SPEED

class Cookie:
    def __init__(self, size, speed, x):
        self.size = size
        self.speed = speed
        self.image = pygame.transform.scale(pygame.image.load('cookie.png'),
                                            (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.y = -COOKIE_MAX_SIZE
        self.rect.x = x

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

class Game:
    def __init__(self):
        self.WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Cookie Shooter')
        self.FPS = 60
        self.CLOCK = pygame.time.Clock()

    def terminate(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def new_game(self):
        self.player = Player()

        self.lives = 3
        self.score = 0
        self.frames = 0
        self.time = [0, 0]

        self.invulnStartTime = 0
        self.invulnMode = False

        self.blasted = 0

        self.cookies = []

        self.run()

    def run(self):
        self.playing = True

        while self.playing:
            self.events()
            self.update()
            self.draw()
            self.CLOCK.tick(self.FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.terminate()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.terminate()

                if event.key == K_SPACE:
                    if self.score < 1000:
                        self.player.missiles.append(Missle(self.player))
                        self.player.missiles[len(self.player.missiles) - 1].rect.center = self.player.rect.center
                    elif self.score >= 1000 and self.score < 5000:
                        self.player.missiles.append(Missle(self.player))
                        self.player.missiles[len(self.player.missiles) - 1].rect.midleft = (self.player.rect.midleft[0] + 5,
                                                                                          self.player.rect.midleft[1])
                        self.player.missiles.append(Missle(self.player))
                        self.player.missiles[len(self.player.missiles) - 1].rect.midright = (self.player.rect.midright[0] - 5,
                                                                                          self.player.rect.midright[1])
                    else:
                        self.player.missiles.append(Missle(self.player))
                        self.player.missiles[len(self.player.missiles) - 1].rect.midleft = (self.player.rect.midleft[0] + 5,
                                                                                          self.player.rect.midleft[1])
                        self.player.missiles.append(Missle(self.player))
                        self.player.missiles[len(self.player.missiles) - 1].rect.midright = (self.player.rect.midright[0] - 5,
                                                                                          self.player.rect.midright[1])
                        self.player.missiles.append(Missle(self.player))
                        self.player.missiles[len(self.player.missiles) - 1].rect.center = (self.player.rect.center[0],
                                                                                         self.player.rect.center[1] - 7)

                if event.key == K_p:
                    self.pause()

    def update(self):
        self.player.update()

        if self.invulnMode and time.time() - self.invulnStartTime > INVULN_TIME:
            self.invulnMode = False
        
        for cookie in self.cookies:
            cookie.update()
            
            if cookie.rect.bottom >= self.player.rect.top and cookie.rect.top <= self.player.rect.bottom:
                if cookie.rect.left <= self.player.rect.right and cookie.rect.right >= self.player.rect.left:
                    if not self.invulnMode:
                        self.lives -= 1
                        self.invulnMode = True
                        self.invulnStartTime = time.time()
                        if self.lives <= 0:
                            self.playing = False

            if cookie.rect.top > WINDOW_HEIGHT:
                if cookie in self.cookies:
                    self.cookies.remove(cookie)

            for missile in self.player.missiles:
                if missile.rect.top <= cookie.rect.bottom and missile.rect.bottom >= cookie.rect.top:
                    if missile.rect.right >= cookie.rect.left and missile.rect.left <= cookie.rect.right:
                        if cookie in self.cookies:
                            self.cookies.remove(cookie)
                        self.player.missiles.remove(missile)
                        self.score += (-cookie.size + 50)
                        self.blasted += 1

                if missile.rect.bottom <= 0:
                    self.player.missiles.remove(missile)

        if len(self.cookies) < COOKIE_NUM:
            self.cookies.append(Cookie(random.randrange(COOKIE_MIN_SIZE, COOKIE_MAX_SIZE + 1),
                                       (random.randrange(COOKIE_MIN_SPEED_X, COOKIE_MAX_SPEED_X + 1),
                                        random.randrange(COOKIE_MIN_SPEED_Y, COOKIE_MAX_SPEED_Y + 1)),
                                       random.randrange(0, WINDOW_WIDTH - 40)))

        if self.player.rect.left <= 0: self.player.rect.left = 0
        elif self.player.rect.right >= WINDOW_WIDTH: self.player.rect.right = WINDOW_WIDTH

        self.frames += 1

        self.time[0] = (self.frames // self.FPS) % 60
        self.time[1] = (self.frames // self.FPS) // 60
            
    def draw(self):
        self.WINDOW.fill(BLACK)

        for cookie in self.cookies:
            self.WINDOW.blit(cookie.image, cookie.rect)
        for missile in self.player.missiles:
            self.WINDOW.blit(missile.image, missile.rect)
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not (self.invulnMode and flashIsOn):
            self.WINDOW.blit(self.player.image, self.player.rect)

        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': WHITE},
                  'Points: {}'.format(self.score), (WINDOW_WIDTH / 2, 20))
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': WHITE},
                  'Time: {:02}:{:02}'.format(self.time[1], self.time[0]), (WINDOW_WIDTH - 10, 20), True)
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': WHITE},
                  'Lives:', (35, 10))
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': WHITE},
                  'Blasted: {}'.format(self.blasted), (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 20))

        lifey = 30
        for life in range(self.lives):
            pygame.draw.rect(self.WINDOW, RED, (10, lifey, 50, 25))
            pygame.draw.rect(self.WINDOW, WHITE, (10, lifey, 50, 25), 2)
            lifey += 25

        pygame.display.update()

    def start_screen(self):
        self.gameStarted = False

        self.WINDOW.fill(WHITE)

        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 50, 'colour': BLACK},
                  'Cookie Shooter', (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4))

        while not self.gameStarted:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.terminate()

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.terminate()

            button(self.WINDOW, 'PLAY', WINDOW_WIDTH / 2 - 200, (WINDOW_HEIGHT / 4) * 3, 100, 50, DARK_GREEN, GREEN, self.start)
            button(self.WINDOW, 'QUIT', WINDOW_WIDTH / 2 + 100, (WINDOW_HEIGHT / 4) * 3, 100, 50, DARK_RED, RED, self.terminate)

            pygame.display.update()
            self.CLOCK.tick(15)

    def pause(self):
        self.paused = True

        self.WINDOW.fill(WHITE)

        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 50, 'colour': BLACK},
                  'PAUSED', (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4))
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': BLACK},
                  'Press P to unpause', (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4 + 100))
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': BLACK},
                  'Points: {}'.format(self.score), (WINDOW_WIDTH / 2, 20))
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': BLACK},
                  'Time: {:02}:{:02}'.format(self.time[1], self.time[0]), (WINDOW_WIDTH - 10, 20), True)
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': BLACK},
                  'Lives:', (35, 10))
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': BLACK},
                  'Blasted: {}'.format(self.blasted), (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 20))
        lifey = 30
        for life in range(self.lives):
            pygame.draw.rect(self.WINDOW, RED, (10, lifey, 50, 25))
            pygame.draw.rect(self.WINDOW, BLACK, (10, lifey, 50, 25), 2)
            lifey += 25

        while self.paused:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.terminate()

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.terminate()
                    if event.key == K_p:
                        for x in range(3):
                            self.WINDOW.fill(WHITE)
                            draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 75, 'colour': BLACK},
                                      str(-x + 3), (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
                            pygame.display.update()
                            pygame.time.wait(1000)
                        self.paused = False

            button(self.WINDOW, 'QUIT', WINDOW_WIDTH / 2 - 50, (WINDOW_HEIGHT / 4) * 3, 100, 50, DARK_RED, RED, self.terminate)

            pygame.display.update()
            self.CLOCK.tick(15)

    def game_over_screen(self):
        self.gameOver = True
        
        self.WINDOW.fill(WHITE)

        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 50, 'colour': BLACK},
                  'GAME OVER', (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4))
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': BLACK},
                  'Points: {}'.format(self.score), (WINDOW_WIDTH / 2 - 100, 20))
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': BLACK},
                  'Time: {:02}:{:02}'.format(self.time[1], self.time[0]), (WINDOW_WIDTH / 2 + 100, 20))
        draw_text(self.WINDOW, {'file': 'ComicSansMS.ttf', 'size': 20, 'colour': BLACK},
                  'Blasted: {}'.format(self.blasted), (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 20))

        while self.gameOver:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.terminate()

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.terminate()

            button(self.WINDOW, 'PLAY AGAIN', WINDOW_WIDTH / 2 - 213, (WINDOW_HEIGHT / 4) * 3, 125, 50, DARK_GREEN,
                   GREEN, self.restart)
            button(self.WINDOW, 'QUIT', WINDOW_WIDTH / 2 + 100, (WINDOW_HEIGHT / 4) * 3, 100, 50, DARK_RED, RED, self.terminate)

            pygame.display.update()
            self.CLOCK.tick(15)

    def restart(self): self.gameOver = False
    def start(self): self.gameStarted = True

game = Game()

game.start_screen()

while True:
    game.new_game()
    game.game_over_screen()
