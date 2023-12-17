import pygame
import os
import random

player_lives = 3  # keep track of lives
score = 0  # keeps track of score
fruits = ['melon', 'orange', 'pomegranate', 'guava', 'bomb']  # entities in the game

# initialize pygame and create window
WIDTH = 800
HEIGHT = 500
FPS = 30  # controls how often the gameDisplay should refresh. In our case, it will refresh every 1/5th second
pygame.init()
pygame.display.set_caption('Fruit-Ninja Game in Python -- GetProjects.org')
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))  # setting game display size
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

background = pygame.image.load('back.jpg')  # game background
font = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), 42)
score_text = font.render('Score : ' + str(score), True, (255, 255, 255))  # score display
lives_icon = pygame.image.load('images/white_lives.png')  # images that shows remaining lives

# Generic method to draw fonts on the screen
font_name = pygame.font.match_font('comic.ttf')

explode = pygame.mixer.Sound('sound/explode.wav')
smurf = pygame.mixer.Sound('sound/smurf.wav')


# Generalized structure of the fruit Dictionary
def generate_random_fruits(fruit):
    fruit_path = "images/" + fruit + ".png"
    data[fruit] = {
        'img': pygame.image.load(fruit_path),
        'x': random.randint(100, 500),  # where the fruit should be positioned on x-coordinate
        'y': 800,
        'speed_x': random.randint(-10, 10),
        # how fast the fruit should move in x direction. Controls the diagonal movement of fruits
        'speed_y': random.randint(-65, -35),  # control the speed of fruits in y-directionn ( UP )
        'throw': (random.random() >= 0.75) and True or False,
        # determines if the generated coordinate of the fruits is outside the gameDisplay or not. If outside,
        # then it will be discarded
        'acceleration': 0,
        'hit': False,
    }


def decrease_live(x, y):
    gameDisplay.blit(pygame.image.load("images/red_lives.png"), (x, y))


def draw_text(display, text, size, x, y):
    fonts = pygame.font.Font(font_name, size)
    text_surface = fonts.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    gameDisplay.blit(text_surface, text_rect)


# 畫生命
def draw_lives(display, x, y, lives, image):
    for i in range(lives):
        img = pygame.image.load(image)
        img_rect = img.get_rect()  # gets the (x,y) coordinates of the cross icons (lives on the the top rightmost side)
        img_rect.x = int(x + 35 * i)  # sets the next cross icon 35pixels awt from the previous one
        img_rect.y = y  # takes care of how many pixels the cross icon should be positioned from top of the screen
        display.blit(img, img_rect)


# show game over display & front display
def handle_gameover(game_over):
    global player_lives, score
    gameDisplay.blit(background, (0, 0))
    draw_text(gameDisplay, "TEAM WORK", 90, WIDTH / 2, HEIGHT / 4)
    if not game_over:
        draw_text(gameDisplay, "Score : " + str(score), 50, WIDTH / 2, HEIGHT / 2)

    draw_text(gameDisplay, "Press a key to begin!", 64, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
    player_lives = 3  # reset player live\
    score = 0


def handle_hit(value, key, game_over, current_position):
    global score, player_lives, score_text
    value['x'] += value['speed_x']  # moving the fruits in x-coordinates
    value['y'] += value['speed_y']  # moving the fruits in y-coordinate
    value['speed_y'] += (1 * value['acceleration'])  # increasing y-corrdinate
    value['acceleration'] += 0.3  # increasing speed_y for next loop

    if value['y'] <= 800:
        gameDisplay.blit(value['img'],
                         (value['x'], value['y']))  # displaying the fruit inside screen dynamically
    else:
        generate_random_fruits(key)

    if not value['hit'] and value['x'] < current_position[0] < value['x'] + 90 \
            and value['y'] < current_position[1] < value['y'] + 90:
        if key == 'bomb':
            explode.play()
            player_lives -= 1
            if player_lives == 0:
                decrease_live(690, 15)
            elif player_lives == 1:
                decrease_live(725, 15)
            elif player_lives == 2:
                decrease_live(760, 15)
            # if the user clicks bombs for three time, GAME OVER message should be displayed and the
            # window should be reset
            if player_lives == 0:
                handle_gameover(game_over)
                game_over = True

            half_fruit_path = "images/explosion.png"
        else:
            smurf.play()
            half_fruit_path = "images/" + "half_" + key + ".png"

        value['img'] = pygame.image.load(half_fruit_path)
        value['speed_x'] += 10
        if key != 'bomb':
            score += 1
        score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
        value['hit'] = True


def draw_point(pos):
    global gameDisplay, BLUE
    pygame.draw.circle(gameDisplay, RED, pos, 18, 5)


def run_game():
    global score, score_text, player_lives
    first_round = True
    game_over = True  # terminates the game While loop if more than 3-Bombs are cut
    game_running = True  # used to manage the game loop
    while game_running:
        if game_over:
            if first_round:
                handle_gameover(game_over)
                first_round = False
            game_over = False
            draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')

        for event in pygame.event.get():
            # checking for closing window
            if event.type == pygame.QUIT:
                game_running = False

        gameDisplay.blit(background, (0, 0))
        gameDisplay.blit(score_text, (0, 0))
        draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')

        current_position = pygame.mouse.get_pos()  # gets the current coordinate (x, y) in pixels of the mouse
        draw_point(current_position)

        for key, value in data.items():
            if value['throw']:
                handle_hit(value, key, game_over, current_position)
            else:
                generate_random_fruits(key)

        pygame.display.update()
        clock.tick(FPS)
        # keep loop running at the right speed (manages the frame/second). The loop should update
        # after every 1/12th pf the sec

    pygame.quit()


data = {}
for fruit in fruits:
    generate_random_fruits(fruit)

run_game()
