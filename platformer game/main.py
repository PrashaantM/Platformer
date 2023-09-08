import os
import random
import math
import pygame
from pygame import mixer
from pygame.locals import *
from os import listdir
from os.path import isfile, join
pygame.init()


pygame.display.set_caption("Ninja Frog Obby")

black = (0,0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
WIDTH, HEIGHT = 1000, 600
FPS = 60
PLAYER_VEL = 5
font = pygame.font.SysFont(None, 25)


window = pygame.display.set_mode((WIDTH, HEIGHT))
mixer.init()

mixer.music.load('05. Nightmare king.mp3')
repeat = 0
while repeat < 100:
    mixer.music.play()
    repeat += 1

#05. Nightmare king.mp3 
#IMG_5153.mp3
#y2mate.com_-_Candyland_But_it_is_low_quality.mp3


def show_text( msg, color, x, y):
    global window
    text = font.render( msg, True, color)
    window.blit(text, ( x, y ) )


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    #x increment 96 and y increment 64
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def get_spikes(size):
    path = join("assets", "Traps", "Spikes", "idle.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    #x increment 96 and y increment 64
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def get_enemy(size):
    path = join("assets", "MainCharacters", "MaskDude", "idle.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    #x increment 96 and y increment 64
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = .9
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.health = 200

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
            self.health -= 1
        if self.hit_count > fps:
            self.hit = False
            self.hit_count = 0
        if self.health == 0:
            main(window)
        
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Enemy(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, "enemy")

        enemy = get_enemy(size)
        self.image.blit(enemy, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Spikes(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, "spikes")

        spikes = get_spikes(size)
        self.image.blit(spikes, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    keys = pygame.key.get_pressed()
    show_text("Hold p for controls                       4 lives total", white, 470, 30)
    if keys[pygame.K_p]:
        show_text("Controls: WASD or arrows (up arrow or space for jump)", white, 370, 100)
        show_text("There is double jump but it is very small.", white, 370, 130)
        show_text("Press R if you want to respawn like when you fall off the map", white, 370, 160)
        show_text("NOTE: PLAYER MAY RANDOMLY DISAPPEAR WHEN HE JUMPS.", white, 370, 200)
        show_text("OR THEY MAY YEET ACROSS THE VERTICAL SURFACE OF A BLOCK.", white, 370, 220)
    

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_a] or keys[pygame.K_LEFT] :
        if not collide_left:
            player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        if not collide_right:
            player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
        if obj and obj.name == "enemy":
            player.make_hit()
        if obj and obj.name == "spikes":
            player.make_hit()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Black.png")

    block_size = 96
    
    i = 0
    floor1 = [] 
    while i < 21*block_size:
        floor1.append(Block(block_size*3.8+ i, HEIGHT - block_size * 0.4, block_size))
        i+=block_size
    i = 0
    stairs = []
    while i < 11*block_size:
        stairs.append(Spikes(block_size*24.5, HEIGHT - block_size-32, block_size))
        stairs.append(Spikes(block_size*24.67, HEIGHT - block_size-32, block_size))
        stairs.append(Block(block_size*23.8+ i, HEIGHT - block_size, block_size))
        i+=block_size
    i = 0
    stairs2 = []
    while i < 9*block_size:
        stairs2.append(Spikes(block_size*26.5, HEIGHT - block_size*2-32, block_size))
        stairs2.append(Spikes(block_size*26.67, HEIGHT - block_size*2-32, block_size))
        stairs2.append(Block(block_size*25.8+ i, HEIGHT - block_size*2, block_size))
        i+=block_size
    i = 0
    stairs3 = []
    while i < 7*block_size:
        stairs3.append(Spikes(block_size*28.5, HEIGHT - block_size*3-32, block_size))
        stairs3.append(Spikes(block_size*28.67, HEIGHT - block_size*3-32, block_size))
        stairs3.append(Block(block_size*27.8+ i, HEIGHT - block_size*3, block_size))
        i+=block_size
    i = 0
    stairs4 = []
    while i < 5*block_size:
        stairs4.append(Spikes(block_size*30.5, HEIGHT - block_size*4-32, block_size))
        stairs4.append(Spikes(block_size*30.67, HEIGHT - block_size*4-32, block_size))
        stairs4.append(Block(block_size*29.8+ i, HEIGHT - block_size*4, block_size))
        i+=block_size
    i = 0
    stairs5 = []
    while i < 3*block_size:
        stairs5.append(Spikes(block_size*32.5, HEIGHT - block_size*5-32, block_size))
        stairs5.append(Spikes(block_size*32.67, HEIGHT - block_size*5-32, block_size))
        stairs5.append(Block(block_size*31.8+ i, HEIGHT - block_size*5, block_size))
        i+=block_size
    i = 0
    tunnel_floor1 = []
    while i < 8*block_size:
        tunnel_floor1.append(Block(block_size*36+ i, HEIGHT - block_size, block_size))
        
        i+=block_size
    i = 0
    tunnel_roof1 = []
    tunnel_roof1.append(Block(block_size*43.5, HEIGHT - block_size*3.8, block_size))
    tunnel_roof1.append(Block(block_size*44, HEIGHT - block_size*4.8, block_size))
    tunnel_roof1.append(Block(block_size*35.8, HEIGHT - block_size*3.8, block_size))
    tunnel_roof1.append(Block(block_size*35.8, HEIGHT - block_size*4.8, block_size))
    tunnel_roof1.append(Block(block_size*35.8, HEIGHT - block_size*5.8, block_size))
    tunnel_roof1.append(Block(block_size*35.8, HEIGHT - block_size*6.8, block_size))
    tunnel_roof1.append(Block(block_size*35.8, HEIGHT - block_size*7.8, block_size))
    while i < 8*block_size:
        tunnel_roof1.append(Block(block_size*35.8+ i, HEIGHT - block_size*2.8, block_size))
        i+=block_size
    i = 0
    tunnel_floor2 = []
    while i < 16*block_size:
        tunnel_floor2.append(Block(block_size*44.8+ i, HEIGHT - block_size*2, block_size))
        i+=block_size
    i = 0
    tunnel_roof2 = []
    tunnel_roof2.append(Block(block_size*59.8, HEIGHT - block_size*3, block_size))
    tunnel_roof2.append(Block(block_size*64, HEIGHT - block_size*5.5, block_size))
    tunnel_roof2.append(Block(block_size*66, HEIGHT - block_size*5.5, block_size))
    while i < 16*block_size:
        tunnel_roof2.append(Block(block_size*44.8+ i, HEIGHT - block_size*4.8, block_size))
        i+=block_size
    
    i = 0
    end_floor = []
    end_floor.append(Block(block_size*68, HEIGHT - block_size*4.5, block_size))
    end_floor.append(Spikes(block_size*68, HEIGHT - block_size*4.5-27, block_size))
    end_floor.append(Block(block_size*70, HEIGHT - block_size*3.5, block_size))
    end_floor.append(Spikes(block_size*70, HEIGHT - block_size*3.5-27, block_size))
    end_floor.append(Block(block_size*94, HEIGHT - block_size*3, block_size))
    end_floor.append(Block(block_size*96.5, HEIGHT - block_size*4.5, block_size))
    end_floor.append(Block(block_size*99, HEIGHT - block_size*2, block_size))
    end_floor.append(Block(block_size*100.5, HEIGHT - block_size*3.9, block_size))
    end_floor.append(Block(block_size*104, HEIGHT - block_size, block_size))
    end_floor.append(Block(block_size*105, HEIGHT - block_size, block_size))
    end_floor.append(Block(block_size*106, HEIGHT - block_size, block_size))
    end_floor.append(Block(block_size*107, HEIGHT - block_size, block_size))
    end_floor.append(Block(block_size*108, HEIGHT - block_size, block_size))
    while i < 20*block_size:
        end_floor.append(Block(block_size*72+ i, HEIGHT - block_size*2.5, block_size))
        
        i += block_size
    i = 0
    end_wall = []
    while i < 8:
        end_wall.append(Block(block_size*109, HEIGHT - block_size*i, block_size))
        i+= 1

    player = Player(90, 90, 50, 50)

    fire1 = Fire(220, HEIGHT - block_size-140, 16, 32)
    fire1.on()
    fire2= Fire(block_size*57.8+100, HEIGHT - block_size-305, 16, 32)
    
    fire3= Fire(block_size*95.5, HEIGHT - block_size*4, 16, 32)
    fire3.on()
    fire4= Fire(block_size*97.9, HEIGHT - block_size*3.15, 16, 32)
    fire4.on()
    fire5= Fire(block_size*100, HEIGHT - block_size*3.4, 16, 32)
    fire5.on()

    spikes1 = []
    j = 0
    while j <6.5*41:
        spikes1.append(Spikes(900+j, HEIGHT - block_size+27, block_size))
        j+=45
    spikes2 = []
    j = 0
    while j <6.5*41:
        spikes2.append(Spikes(1400+j, HEIGHT - block_size+27, block_size))
        j+=45
    spikes3 = []
    j = 0
    while j <6.5*41:
        spikes3.append(Spikes(1900+j, HEIGHT - block_size+27, block_size))
        j+=45
    spikes4 = []
    j = 0
    while j <5*125:
        spikes4.append(Spikes(block_size*46+ j, HEIGHT - block_size-125, block_size))
        j+=115
    spikes5 = []
    j = 0
    while j < 20*block_size:
        spikes5.append(Spikes(block_size*72+j, HEIGHT - block_size*2.5-27, block_size))
        j += (2.5* block_size)
    #+27 above block height for spike placement

    enemy = Enemy(500, HEIGHT - block_size-37, block_size)
    objects = [
               #jump on to the block by avoiding the candle
               Block(0, HEIGHT - block_size * 2, block_size),
               Block(0, HEIGHT - block_size * 7, block_size), 
               Block(0, HEIGHT - block_size * 6, block_size), 
               Block(0, HEIGHT - block_size * 5, block_size), 
               Block(block_size, HEIGHT - block_size * 5, block_size),
               Block(block_size*2.8, HEIGHT - block_size * 5, block_size),
               Block(block_size*2.8, HEIGHT - block_size * 6, block_size), 
               Block(block_size*2.8, HEIGHT - block_size * 7, block_size),
               Block(block_size*1.4, HEIGHT - block_size * 7, block_size),
               Block(block_size*0.7, HEIGHT - block_size * 7, block_size),
               Block(block_size*2.1, HEIGHT - block_size * 7, block_size),
               Block(block_size*2.8, HEIGHT - block_size * 4, block_size),
               Block(block_size*2.8, HEIGHT - block_size * 3, block_size),
               #parkour under the candle
               Block(block_size*2.8, HEIGHT - block_size * 0.4, block_size),
               #floors
               *floor1, *end_floor,
               #stairs
               *stairs, *stairs2, *stairs3, *stairs4, *stairs5,
               #tunnels
               *tunnel_floor1, *tunnel_roof1, *tunnel_floor2, *tunnel_roof2,
               #fires
               fire1, fire2, fire3, fire4, fire5,
               #spikes
               *spikes1, *spikes2, *spikes3, *spikes4, *spikes5,
               *end_wall, 
               enemy
               ]

    offset_x = 0
    scroll_area_width = 500

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    if player.jump_count < 2:
                        player.jump()
                if event.key == pygame.K_r:
                    main(window)

        player.loop(FPS)
        fire1.loop()
        fire3.loop()
        fire4.loop()
        fire5.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)
        
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)