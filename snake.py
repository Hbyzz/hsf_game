# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : 贪吃蛇—双人.py
# Time       ：2024/2/17 11:19
# Author     ：zhou zihan
# version    ：python 3.6
# Description：
"""


import random
import sys
import time
import pygame   # 第三方库
from pygame.locals import *
from collections import deque

"""
思路：父类：基类——基础设置；
    子类：蛇类——类方法：蛇的初始化、头和身体、上行、下行、左行、右行、直行、进食、摧毁预陷阱；
        屏幕类——类方法：屏幕的初始化、画格、画字、画蛇、画食物、画预陷阱、画陷阱；
        食物和陷阱类——类方法：食物和陷阱列表的初始化，得到食物的坐标、得到陷阱的坐标；
    根据游戏逻辑和各个对象的行为进行游戏

游戏规则：暂停时，回车或空格键开始或继续游戏；运行时，空格间暂停游戏；死亡时，回车键重置游戏
        方向键、英文模式下的wsad键控制方向
        得分：吃豆子+10分，摧毁预置陷阱+20分
        速度：每加10分，移动一次所用时间*0.99
        陷阱规则：三秒预置陷阱，五秒陷阱轮替（无视暂停，不是因为我不会写，是机制。机制。。。）
                预置陷阱无害，陷阱有害。
已知问题：（不会修复，谢谢） 1、回车键重新开始可能需要重新切换英文模式
                        2、摧毁预置陷阱，蛇的生长不连贯。
"""


class BaseClass:
    # 基类——基础设置
    def __init__(self):
        # 屏幕的长、宽
        self.Screen_Height = 480
        self.Screen_Length = 600
        # 小方格大小
        self.Size = 20
        self.Line_Width = 1
        # 游戏区域的坐标范围，0是左边界，1是右边界
        self.Area_x = (0, self.Screen_Length // self.Size - 1)
        self.Area_y = (2, self.Screen_Height // self.Size - 1)
        # 整体颜色设置
        self.Light = (100, 100, 100)
        self.Dark = (200, 200, 200)
        self.Black = (0, 0, 0)
        self.Red = (200, 30, 30)
        self.Yellow = (255, 255, 0)
        self.Green = (0, 255, 0)
        self.Back_Ground = (40, 40, 60)
        self.Blue = (155, 155, 255)

    def get_area_x(self):
        # 返回屏幕长边范围，用于判定蛇的出界
        return self.Area_x

    def get_area_y(self):
        # 返回屏幕短边范围，用于判定蛇的出界
        return self.Area_y

    def generate_numbers(self):
        # 生成器 用于生成随机坐标（食物、陷阱、预陷阱）
        while True:
            num_x = random.randint(self.Area_x[0], self.Area_x[1])
            num_y = random.randint(self.Area_y[0], self.Area_y[1])
            yield num_x, num_y


class Snake(BaseClass):
    # 蛇类
    def __init__(self, body_list, move_to):
        # 继承基础设置并初始化一个位于左上角的长度为3的蛇
        super().__init__()
        self.move = move_to  # 蛇的移动方向
        self.snake = deque()    # 蛇的身体
        self.snake.append(body_list[0])  # 蛇的初始身体
        self.snake.append(body_list[1])
        self.snake.append(body_list[2])
        # 蛇的下一移动位置坐标
        self.next_one = (self.snake[0][0] + self.move[0], self.snake[0][1] + self.move[1])
        self.head = self.snake[0]   # 蛇的头
        self.snake_body = deque(list(self.snake)[1:])
        self.last_body = self.snake[-1]
        self.snake_long = 3

    def get_snake(self):
        # 返回蛇的除头外的身体
        self.snake_body = deque(list(self.snake)[1:])
        return self.snake_body

    def up_move(self):
        # 蛇的上行
        self.move = (0, -1)

    def down_move(self):
        # 蛇的下行
        self.move = (0, 1)

    def left_move(self):
        # 蛇的左行
        self.move = (-1, 0)

    def right_move(self):
        # 蛇的右行
        self.move = (1, 0)

    def line_move(self):
        # 蛇的直行
        self.next_one = (self.snake[0][0] + self.move[0], self.snake[0][1] + self.move[1])
        self.snake.appendleft(self.next_one)
        self.snake.pop()
        self.last_body = self.snake[-1]
        return self.snake

    def eat(self):
        # 蛇的进食
        self.snake.append(self.last_body)
        self.snake_long += 1
        return self.snake

    def consume(self):
        # 蛇的加速技能消耗
        self.snake.pop()
        self.snake_long -= 1
        return self.snake

    def get_head(self):
        # 返回蛇的头 用于判定死亡
        return self.snake[0]

    def get_next_one(self):
        # 返回蛇的头 用于判定死亡
        self.next_one = (self.snake[0][0] + self.move[0], self.snake[0][1] + self.move[1])
        return self.next_one


class FoodTrap(BaseClass):
    # 食物和陷阱类
    def __init__(self):
        # 初始化一个食物坐标以及一个空白的陷阱列表
        super().__init__()
        self.food = None
        self.traps = []

    def created_food(self, snake_1, snake_2=None):
        # 创建一个不与蛇身冲突的食物
        generate = self.generate_numbers()
        self.food = next(generate)
        while self.food in snake_1.snake:
            self.food = next(generate)
            while self.food in snake_2.snake:
                self.food = next(generate)
        return self.food

    def created_pre_trap(self, snake_1, snake_2=None):
        # 创建一个不与蛇身冲突的预陷阱列表，里面有五个预陷阱
        generate = self.generate_numbers()
        self.traps = []
        for i in range(5):
            i = next(generate)
            while i in snake_1.snake:
                i = next(generate)
                while i in snake_2.snake:
                    i = next(generate)
            self.traps.append(i)
        return self.traps

    def created_trap(self):
        # 预陷阱转换为陷阱
        return self.traps


class Screen(BaseClass):
    # 屏幕类
    def __init__(self):
        # 继承基础设置，初始化一个名为贪吃蛇的窗口
        super().__init__()
        pygame.init()
        self.screen = pygame.display.set_mode((self.Screen_Length, self.Screen_Height))  # 初始化一个准备显示的窗口或屏幕
        pygame.display.set_caption('贪吃蛇')

    def screen_paint(self):
        # 填充背景，画网格线
        self.screen.fill(self.Back_Ground)
        # 画网格线、竖线
        for x in range(self.Size, self.Screen_Length, self.Size):
            pygame.draw.line(self.screen, self.Black,
                             (x, self.Area_y[0] * self.Size), (x, self.Screen_Height), self.Line_Width)
        # 画网格线、横线
        for y in range(self.Area_y[0] * self.Size, self.Screen_Height, self.Size):
            pygame.draw.line(self.screen, self.Black, (0, y), (self.Screen_Length, y), self.Line_Width)

    def draw_grid(self, color, grid):
        pygame.draw.rect(self.screen,
                         color,
                         (
                             grid[0] * self.Size + self.Line_Width,
                             grid[1] * self.Size + self.Line_Width,
                             self.Size - self.Line_Width * 2,
                             self.Size - self.Line_Width * 2),
                         0)

    def draw_screen(self, snake_1, snake_2=None):
        # 画蛇
        head1 = snake_1.get_head()
        body1 = snake_1.get_snake()
        head2 = snake_2.get_head()
        body2 = snake_2.get_snake()
        for s in body1:
            self.draw_grid(self.Dark, s)
        self.draw_grid(self.Blue, head1)
        for s in body2:
            self.draw_grid(self.Dark, s)
        self.draw_grid(self.Blue, head2)

    def draw_food(self, c_food):
        # 画食物
        pygame.draw.rect(self.screen,
                         self.Yellow,
                         (
                             c_food[0] * self.Size + self.Line_Width,
                             c_food[1] * self.Size + self.Line_Width,
                             self.Size - self.Line_Width * 2,
                             self.Size - self.Line_Width * 2),
                         0)

    def draw_pre_trap(self, traps):
        # 画预陷阱
        for c_trap in traps:
            pygame.draw.rect(self.screen,
                             self.Green,
                             (
                                 c_trap[0] * self.Size + self.Line_Width,
                                 c_trap[1] * self.Size + self.Line_Width,
                                 self.Size - self.Line_Width * 2,
                                 self.Size - self.Line_Width * 2),
                             0)

    def draw_trap(self, traps):
        # 画预陷阱
        for c_trap in traps:
            pygame.draw.rect(self.screen,
                             self.Red,
                             (
                                 c_trap[0] * self.Size + self.Line_Width,
                                 c_trap[1] * self.Size + self.Line_Width,
                                 self.Size - self.Line_Width * 2,
                                 self.Size - self.Line_Width * 2),
                             0)

    def print_txt(self, font, x, y, text, fcolor=(255, 255, 255)):
        # font.render参数意义：.render（内容，是否抗锯齿，字体颜色，字体背景颜色）
        text = font.render(text, True, fcolor)
        self.screen.blit(text, (x, y))

    def print_over(self, text, fcolor=(255, 255, 255)):
        # font.render参数意义：.render（内容，是否抗锯齿，字体颜色，字体背景颜色）
        font = pygame.font.SysFont("Arial", 72)
        size_x, size_y = font.size(text)
        text = font.render(text, True, fcolor)
        self.screen.blit(text, ((self.Screen_Length-size_x)//2, (self.Screen_Height-size_y)//2))


# 初始化
pygame.init()
screen = Screen()   # 屏幕
BaseClass = BaseClass()
Area_X = BaseClass.get_area_x()
Area_Y = BaseClass.get_area_y()
body_list1 = [(2, Area_Y[0]), (1, Area_Y[0]), (0, Area_Y[0])]
body_list2 = [(Area_X[1]-2, Area_Y[1]), (Area_X[1]-1, Area_Y[1]), (Area_X[1], Area_Y[1])]
snake1 = Snake(body_list1, (1, 0))     # 蛇1
snake2 = Snake(body_list2, (-1, 0))     # 蛇2
Food = FoodTrap()   # 食物
food = Food.created_food(snake1, snake2)
Trap = FoodTrap()   # 陷阱
pre_trap = Trap.created_pre_trap(snake1, snake2)  # 创建预陷阱
trap = []   # 创建陷阱空字典
# 游戏设置
start = False   # 游戏的开始
pause = True   # 游戏的暂停
die = False     # 死亡与暂停的分别变量
move = False    # 是否允许蛇的移动
up_down = False     # 蛇的状态：垂直移动中
left_right = True   # 蛇的状态：水平移动中
eat_pre_trap = False     # 上次移动是否破坏预陷阱
change = False      # 是否允许陷阱更替
# 速度、时间设置
now_time = time.time()  # 当前时间
last_move_time = now_time  # 最后一次移动的时间
speed = 0.3     # 蛇的速度
score = 0   # 分数设置
max_score = 0   # 历史最高分
trap_time = time.time()     # 陷阱的计时器
change_time = trap_time     # 上一次更替陷阱的时间
speed_time = time.time()
speeding = 0
word = "等待开始"

while True:
    now_time = time.time()  # 当前时间
    trap_time = time.time()

    # 机制设置（事件反馈）
    for event in pygame.event.get():
        # 接受指令，各类进行反馈
        if event.type == pygame.QUIT:
            sys.exit()  # 程序的出口

        elif event.type == KEYDOWN:
            if start:
                if eat_pre_trap is True:
                    snake1.eat()
                    snake2.eat()
                    eat_pre_trap = False
                if event.key == K_SPACE and start:
                    # 在运行中按下空格，游戏暂停
                    pause = True
                    start = False
                    event.key = None
                    word = "按下:空格"
                elif event.key in (K_UP, K_w):
                    if left_right and move:
                        # 水平移动中才可上行
                        snake1.up_move()
                        snake2.down_move()
                        left_right = False
                        up_down = True
                        move = False
                        word = "按下:w/上键"
                elif event.key in (K_DOWN, K_s):
                    if left_right and move:
                        # 水平移动中才可下行
                        snake1.down_move()
                        snake2.up_move()
                        left_right = False
                        up_down = True
                        move = False
                        word = "按下:s/下键"
                elif event.key in (K_LEFT, K_a):
                    if up_down and move:
                        # 垂直移动中才可左行
                        snake1.left_move()
                        snake2.right_move()
                        left_right = True
                        up_down = False
                        move = False
                        word = "按下:a/左键"
                elif event.key in (K_RIGHT, K_d):
                    if up_down and move:
                        # 垂直移动中才可右行
                        snake1.right_move()
                        snake2.left_move()
                        left_right = True
                        up_down = False
                        word = "按下:d/右键"
                if event.key == K_e and snake1.snake_long > 3:
                    speed = speed*0.6
                    speeding = 1
                    speed_time = now_time
                    snake1.consume()
                    snake2.consume()
                    word = "按下:e（加速）键"

            if pause is True:

                if die is True:
                    screen.print_over("GAME OVER!")
                else:
                    screen.print_over("GAME PAUSE!")

                if event.key == K_RETURN and die:
                    word = "按下:回车键"
                    # 在蛇死亡后，回车重置游戏
                    screen = Screen()
                    body_list1 = [(2, Area_Y[0]), (1, Area_Y[0]), (0, Area_Y[0])]
                    body_list2 = [(Area_X[1] - 2, Area_Y[1]), (Area_X[1] - 1, Area_Y[1]), (Area_X[1], Area_Y[1])]
                    snake1 = Snake(body_list1, (1, 0))  # 蛇1
                    snake2 = Snake(body_list2, (-1, 0))  # 蛇2
                    Food = FoodTrap()
                    Trap = FoodTrap()
                    pre_trap = Trap.created_pre_trap(snake1, snake2)
                    trap = []
                    speed = 0.3
                    score = 0
                    last_move_time = now_time
                    left_right = True
                    up_down = False
                    die = False
                    move = False
                    speed_time = time.time()

                elif event.key == K_RETURN and not die:
                    # 暂停但未死亡时回车，开始游戏或继续游戏
                    word = "按下:回车键"
                    start = True
                    pause = False
                    last_move_time = now_time
                elif event.key == K_SPACE and not die:
                    # 这个空格貌似很多余。。。
                    word = "按下:空格键"
                    start = True
                    pause = False
                    last_move_time = now_time
        elif event.type == KEYUP and snake1.snake_long > 3:
            if event.key == K_e and now_time - speed_time < 5:
                speed = speed / 0.6
                speeding = 0
                speed_time = time.time()
                word = "松开:e（加速）键"
            elif event.key == K_e and now_time - speed_time >= 5:
                speed_time = time.time()
                word = "加速失效"
        if now_time - speed_time >= 5 and snake1.snake_long > 3 and speeding:
            speed = speed / 0.6
            speeding = 0
            word = "加速失效"

    if now_time-last_move_time > speed:
        # 是否允许移动
        if not die and not pause:
            move = True
            snake1.line_move()
            snake2.line_move()
            if eat_pre_trap is True:
                snake1.eat()
                snake2.eat()
                eat_pre_trap = False
            last_move_time = now_time

    # 陷阱的更替
    if trap_time-change_time > 3 and pre_trap != []:
        # 预陷阱转换为陷阱
        trap = Trap.created_trap()
        change_time = trap_time
        pre_trap = []
    elif trap_time-change_time > 5 and trap != []:
        # 陷阱摧毁。重新随机布置预陷阱
        pre_trap = Trap.created_pre_trap(snake1, snake2)
        change_time = trap_time
        trap = []

    # 速度、得分与死亡判定
    next_move1 = snake1.get_next_one()
    get_head1 = snake1.get_head()
    snake_body1 = snake1.get_snake()
    next_move2 = snake2.get_next_one()
    get_head2 = snake2.get_head()
    snake_body2 = snake2.get_snake()
    if get_head1 == food or get_head2 == food:
        # 蛇的头碰到食物，得分
        snake1.eat()
        snake2.eat()
        food = Food.created_food(snake1, snake2)
        score += 10
        speed = speed*0.95
    elif get_head1 in pre_trap or get_head2 in pre_trap:
        # 蛇摧毁预陷阱，得分*2
        if get_head1 in pre_trap:
            pre_trap.remove(get_head1)
        else:
            pre_trap.remove(get_head2)
        snake1.eat()
        snake2.eat()
        eat_pre_trap = True
        score += 20
        speed = speed*0.95*0.95
    elif get_head1 in trap or get_head2 in trap:
        # 落入陷阱，死亡，游戏结束
        die = True
        pause = True
        start = False
    elif get_head1 in snake_body1 or get_head1 in snake_body2:
        # 很明显蛇吃了自己，所以叫贪吃蛇
        die = True
        pause = True
        start = False
    elif (get_head1[0] < Area_X[0] or get_head1[0] > Area_X[1] or
          get_head1[1] < Area_Y[0] or get_head1[1] > Area_Y[1]):
        # 不仅贪吃，而且眼瞎，出界了
        die = True
        pause = True
        start = False
    if score >= max_score:
        max_score = score

    # 接下来画屏幕上显示的所有内容，并刷新屏幕
    screen.screen_paint()
    screen.draw_screen(snake1, snake2)
    screen.draw_food(food)
    screen.draw_pre_trap(pre_trap)
    screen.draw_trap(trap)
    # 得分字体设置
    font1 = pygame.font.SysFont('SimHei', 24)
    screen.print_txt(font1, 30, 7, f'速度: {speed:.2f}')
    screen.print_txt(font1, 240, 7, word)
    screen.print_txt(font1, 450, 7, f'得分: {score}')
    if die and pause:
        screen.print_over("GAME OVER!")
    elif not die and pause:
        screen.print_over("WAITING!")
    pygame.display.flip()
