import pygame
import os
import random
import cv2
import mediapipe as mp
from ultralytics import YOLO
import torch

if not torch.cuda.is_available():
    exit(1)
    pass
print(f"cuda installed. version {torch.version.cuda} {torch.__version__}")

mp_drawing = mp.solutions.drawing_utils  # mediapipe 繪圖方法
mp_drawing_styles = mp.solutions.drawing_styles  # mediapipe 繪圖樣式
mp_hands = mp.solutions.hands  # mediapipe 偵測手掌方法

# ===== Game Setup =====
player_lives = 3
score = 0
fruits = ["melon", "orange", "pomegranate", "guava", "bomb"]
bomb_immutable = False
has_skill = False
score_point = 1
object_detected = True
# initialize pygame and create window
WIDTH = 800
HEIGHT = 500
FPS = 30
pygame.init()
pygame.display.set_caption("Fruit-Ninja Game with OPENCV")
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

initial_background = pygame.image.load('images/backgound.jpg')
background = initial_background

immutable_background = pygame.image.load('images/immutable.jpg')
immutable_background = pygame.transform.scale(immutable_background, (800, 500))

increase_score_background = pygame.image.load('images/increase_score.jpg')
increase_score_background = pygame.transform.scale(increase_score_background, (800, 500))

decrease_speed_background = pygame.image.load('images/decrease_speed.jpg')
decrease_speed_background = pygame.transform.scale(decrease_speed_background, (800, 500))


#background = pygame.image.load("back.jpg")
font = pygame.font.Font(os.path.join(os.getcwd(), "comic.ttf"), 42)
score_text = font.render("Score : " + str(score), True, (255, 255, 255))
font_name = pygame.font.match_font("comic.ttf")
#explode = pygame.mixer.Sound("sound/explode.wav")
#smurf = pygame.mixer.Sound("sound/smurf.wav")
bomb_immutable = False

explode = pygame.mixer.Sound('sound/explode.wav')
smurf = pygame.mixer.Sound('sound/smurf.wav')
cave = pygame.mixer.Sound('sound/immutable.wav')
lava = pygame.mixer.Sound('sound/increase_score.wav')
space = pygame.mixer.Sound('sound/decrease_speed.wav')


data = {}


def do_nothing():
    pass


def test():
    print("test")


class Scheduler:
    do_nothing()
    timer = 10

    def __init__(self, func, timer):
        self.timer = timer
        self.func = func

    def tick(self):
        if self.timer == 0:
            self.func()
            return True
        self.timer -= 1
        return False


sch = []


def handle_scheduler():
    global sch
    next_tick_sch = []
    for index, value in enumerate(sch):
        remove_it = value.tick()
        if not remove_it:
            next_tick_sch.append(value)
    sch = next_tick_sch


def generate_random_fruits(fruit):
    fruit_path = "images/" + fruit + ".png"
    data[fruit] = {
        "img": pygame.image.load(fruit_path),
        "x": random.randint(100, 500),
        "y": 800,
        "speed_x": random.randint(-10, 10),
        "speed_y": random.randint(-65, -35),
        "throw": (random.random() >= 0.75) and True or False,
        "acceleration": 0,
        "hit": False,
    }


live_pos = [(725, 15), (760, 15), (795, 15)]

def reset_score_point():
    global score_point, has_skill, background
    score_point = 1
    has_skill = False
    background = initial_background


def increase_score_point():
    global score_point, has_skill
    if has_skill:
        return
    has_skill = True
    score_point += 1
    lava.play()
    sch.append(Scheduler(timer=5 * FPS, func=reset_score_point))

def increase_live():
    global player_lives
    if player_lives >= 3:
        print("[ERROR] max health 3")
        return
    remove_lives()
    player_lives += 1
    draw_lives()


def decrease_live():
    global player_lives
    remove_lives()
    player_lives -= 1
    draw_lives()


#
def draw_text(text, size, x, y):
    fonts = pygame.font.Font(font_name, size)
    text_surface = fonts.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    gameDisplay.blit(text_surface, text_rect)


def remove_lives():
    for i in live_pos:
        gameDisplay.blit(pygame.image.load("images/red_lives.png"), i)


# 畫生命
def draw_lives():
    for i in range(player_lives):
        img = pygame.image.load("images/red_lives.png")
        img_rect = img.get_rect()
        img_rect.x = int(690 + 35 * i)
        img_rect.y = 15
        gameDisplay.blit(img, img_rect)


def reset_speed():
    global FPS, has_skill, background
    FPS = 30
    has_skill = False
    background = initial_background


def decrease_speed():
    global FPS, has_skill
    if has_skill:
        return
    has_skill = True
    FPS = 5
    space.play()
    sch.append(Scheduler(timer=5 * FPS, func=reset_speed))

def reset_bomb_immutable():
    global bomb_immutable, has_skill, background
    bomb_immutable = False
    has_skill = False
    print(f"reset {bomb_immutable}")
    background = initial_background


def immutable_bomb_for_5_sec():
    global bomb_immutable, has_skill
    if has_skill:
        return
    has_skill = True
    bomb_immutable = True
    # 播放音效
    cave.play()
    sch.append(Scheduler(timer=5 * FPS, func=reset_bomb_immutable))

def show_immutable_bomb():
    global background
    if has_skill:
        # 切換背景
        background = immutable_background

def show_increase_speed():
    global background
    if has_skill:
        # 切換背景
        background = increase_score_background

def show_decrease_speed():
    global background
    if has_skill:
        # 切換背景
        background = decrease_speed_background

def pausegame():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)
        if event.type == pygame.KEYUP:
            return False
    return True
def quitgame():
    cv2.destroyAllWindows()
    pygame.quit()
    exit(0)
# func 是中止lock的條件 True代表繼續lock False代表結束lock
def lock(func):
    waiting = True
    while waiting:
        handle_scheduler()
        clock.tick(FPS)
        waiting = func()


def game_over_key_handle():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)
        if event.type == pygame.KEYUP:
            return False
    return True


def handle_game_start_end(first_round):
    global player_lives, score
    gameDisplay.blit(background, (0, 0))
    draw_text("TEAM WORK", 90, WIDTH / 2, HEIGHT / 4)
    if not first_round:
        draw_text("Score : " + str(score), 50, WIDTH / 2, HEIGHT / 2)

    draw_text("Press a key to begin!", 64, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    lock(game_over_key_handle)
    player_lives = 3  # reset player live
    score = 0
    for fruit in fruits:
        generate_random_fruits(fruit)


def handle_obj(key, value, current_position):
    global score, player_lives, score_text
    value["x"] += value["speed_x"]
    value["y"] += value["speed_y"]
    value["speed_y"] += 1 * value["acceleration"]
    value["acceleration"] += 0.3

    if value["y"] <= 800:
        gameDisplay.blit(value["img"], (value["x"], value["y"]))
    else:
        generate_random_fruits(key)

    if (
            not bomb_immutable
            and not value["hit"]
            and value["x"] < current_position[0] < value["x"] + 90
            and value["y"] < current_position[1] < value["y"] + 90
    ):
        if key == "bomb":
            explode.play()
            decrease_live()

            if player_lives == 0:
                handle_game_start_end(False)

            half_fruit_path = "images/explosion.png"
        else:
            smurf.play()
            half_fruit_path = "images/" + "half_" + key + ".png"

        value["img"] = pygame.image.load(half_fruit_path)
        value["speed_x"] += 10
        if key != "bomb":
            score += 1
        score_text = font.render("Score : " + str(score), True, (255, 255, 255))
        value["hit"] = True


def draw_point(pos):
    global gameDisplay, BLUE
    pygame.draw.circle(gameDisplay, RED, pos, 18, 5)


current_position = (0, 0)


def run_game():
    global current_position ,object_detected
    cap = cv2.VideoCapture(0)
    global score, score_text, player_lives
    first_round = True
    game_over = True
    game_running = True
    while game_running:
        if game_over or first_round:
            handle_game_start_end(first_round)
            first_round = False
            game_over = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
        gameDisplay.blit(background, (0, 0))
        gameDisplay.blit(score_text, (0, 0))
        draw_lives()

        ret, preimg = cap.read()
        img = cv2.flip(preimg, 1)
        if not ret:
            print("Cannot receive frame")
        else:
            pass
            #object_detected = True

            # Predict Picture
            results = model(img, conf=0.4)
            for result in results:
                boxes = result.boxes
                print(boxes)
                annotated_frame = result.plot()
                cv2.imshow("YOLOv8 Inference", annotated_frame)
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    # 
                    # Add functionality here
                    #
                    # {0: 'Bomb-proof', 1: 'Slowmotion', 2: 'continue', 3: 'control', 4: 'double-score', 5: 'end', 6: 'head', 7: 'heal', 8: 'stop'}
                    class_index = box.cls
                    confidence = box.conf
                    if class_index == 6:

                        current_position = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                        draw_point(current_position)
                        pass
                    elif class_index == 0:
                        # bomb-proof
                        show_immutable_bomb()
                        immutable_bomb_for_5_sec()

                    elif class_index == 1:
                        decrease_speed()
                        show_decrease_speed()
                        # slowmotion
                        pass
                    elif class_index == 2:
                        object_detected = True
                        pass
                    elif class_index == 4:
                        show_increase_speed()
                        increase_score_point()
                        pass
                    elif class_index == 5:
                        #quitgame()
                        pass
                    elif class_index == 7:
                        increase_live()
                        pass
                    elif class_index == 8:
                        object_detected = False
                        pass

                for key, value in data.items():
                    if value["throw"]:
                        handle_obj(key, value, current_position)
                    else:
                        generate_random_fruits(key)

                if object_detected == True:
                    pygame.display.update()
                handle_scheduler()
                clock.tick(FPS)

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()


# Load the YOLOv8 model
model = YOLO('best.pt')

if __name__ == "__main__":
    run_game()

# Reference: https://docs.ultralytics.com/modes/predict/
