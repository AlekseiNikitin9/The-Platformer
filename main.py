import os
import sys
import pygame
import random
from os.path import isfile, join
from os import listdir

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(16)
menu_music = pygame.mixer.Sound(join('assets', 'Music', 'Intro Theme.mp3'))
menu_music.set_volume(0.3)
first_level_track = pygame.mixer.Sound(join('assets', 'Music', 'Grasslands Theme.mp3'))
first_level_track.set_volume(0.3)
jump = pygame.mixer.Sound(join('assets', 'Music', 'jump.wav'))
jump.set_volume(1)
hit = pygame.mixer.Sound(join('assets', 'Music', 'hit.mp3'))
hit.set_volume(1)
double_jump = pygame.mixer.Sound(join('assets', 'Music', 'double_jump.wav'))
double_jump.set_volume(1)
four_lives = pygame.image.load(join('assets', 'Other', 'fulllife', 'h1.png'))
three_lives = pygame.image.load(join('assets', 'Other', 'almosthalflife', 'h1.png'))
two_lives = pygame.image.load(join('assets', 'Other', 'halflife', 'h1.png'))
one_life = pygame.image.load(join('assets', 'Other', 'onelife', 'h1.png'))
no_lives = pygame.image.load(join('assets', 'Other', 'death', 'death.png'))
hearts = [no_lives, one_life, two_lives, three_lives, four_lives]
hearts2x = [pygame.transform.scale2x(heart) for heart in hearts]


pygame.display.set_caption('Platformer')

WIDTH = 800
HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.mouse.set_visible(False)  # Hide the default cursor


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_font_spritesheet(filename, scale=2):
    # Load the entire spritesheet
    spritesheet = pygame.image.load(filename).convert_alpha()

    # Dimensions of each character
    char_width = 8 * scale
    char_height = 10 * scale

    # Number of characters per row and column
    chars_per_row = 10
    rows = 5

    # Mapping of characters to their ASCII values
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.:?!()+-"

    # Dictionary to hold the surfaces for each character
    font_dict = {}

    # Extract and scale each character's image
    for row in range(rows):
        for col in range(chars_per_row):
            # Calculate the position of the character in the spritesheet
            x = col * 8  # original character width
            y = row * 10  # original character height

            # Get the specific character for current position
            char_index = row * chars_per_row + col
            if char_index < len(characters):
                char = characters[char_index]
                # Create a subsurface for this character and scale it
                char_surface = spritesheet.subsurface((x, y, 8, 10))
                scaled_char_surface = pygame.transform.scale(char_surface, (char_width, char_height))
                # Store the character's surface in the dictionary
                font_dict[char] = scaled_char_surface

    return font_dict

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join('assets', dir1, dir2)
    images  = [file for file in listdir(path) if isfile(join(path,file))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()

        sprites =[]    
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i*width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", '')] = sprites

    return all_sprites        



def blit_text(surface, text, pos, font_images, char_width=16, char_height=20):  # New default sizes after scaling
    x, y = pos
    for char in text:
        if char in font_images:
            surface.blit(font_images[char], (x, y))
            x += char_width  # Move x position by scaled character width
        else:
            x += char_width  # Space for unknown characters

def load_block(size):
    path = join('assets', 'Terrain', 'Terrain.png')
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    COLOR = (255,0,0)
    SPRITES = load_sprite_sheets('MainCharacters', 'MaskDude', 32, 32, True)
    ANIMATION_DELAY = 3
    COOLDOWN_TIME = 1000

    def __init__(self, x, y, width, height, lives = 4):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.x_v = 0
        self.y_v = 0
        self.mask = None
        self.direction = 'left'
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.lives = lives
        self.hit = False
        self.hit_count = 0
        self.cool_down_timer = 0  # No cooldown initially
        

    def jump(self):
        jump.play()
        self.y_v = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1    
        if self.jump_count == 1:
            double_jump.play()
            self.fall_count = 0

    def make_hit(self, current_time):
        if current_time - self.cool_down_timer > self.COOLDOWN_TIME:
            self.lives -= 1
            hit.play()
            self.cool_down_timer = current_time
            if self.lives <= 0:
                self.die()

    def die(self):
        menu(WINDOW)
        

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy 

    def move_left(self, vel):
        self.x_v = -vel
        if self.direction != 'left':
            self.direction = 'left'
            self.animation_count = 0


    def move_right(self, vel):
        self.x_v = vel
        if self.direction != 'right':
            self.direction = 'right'
            self.animation_count = 0

    def loop(self, fps):
        self.y_v += min(1, (self.fall_count/fps) * self.GRAVITY)
        self.move(self.x_v, self.y_v)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps*2:
            self.hit = False    
            self.hit_count = 0
        self.fall_count += 1
        self.update_sprite()

    def draw(self, window, offset_x, offset_y):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

    def update_sprite(self):
        sprite_sheet = 'idle'
        if self.hit:
            sprite_sheet = 'hit'
        if self.y_v < 0:
            if self.jump_count == 1:
                sprite_sheet = 'jump'
            elif self.jump_count == 2:
                sprite_sheet = 'double_jump' 
        elif self.y_v > self.GRAVITY * 2:
                sprite_sheet = 'fall'       
        elif self.x_v != 0:
            sprite_sheet = 'run'
        sprite_sheet_name = sprite_sheet + '_' + self.direction   
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1 
        self.update()

    def landed(self):
        self.y_v = 0
        self.fall_count = 0
        self.jump_count = 0

    def bump_head(self):
        self.count = 0
        self.y_v *= -1

    def update_cooldown(self, current_time):
        if self.cool_down_timer > 0:
            self.cool_down_timer -= current_time - self.last_hit_time
            self.last_hit_time = current_time
        if self.cool_down_timer < 0:
            self.cool_down_timer = 0  # Ensure timer doesn't go negative

    def update_hit(self, current_time):
        if current_time - self.cool_down_timer < self.COOLDOWN_TIME:
            # Player is in cooldown, cannot be hit
            self.hit = True
        else:
            self.hit = False
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)    

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name = 'none'):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window, offset_x, offset_y):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    
    ANIMATION_DELAY = 3


    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, 'fire')
        self.fire = load_sprite_sheets('Traps', 'Fire', width, height)
        self.image = self.fire['off'][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = 'off'
    
    def on(self):
        self.animation_name = 'on'
    
    def off(self):
        self.animation_name = 'off'
    
    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1 
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        if self.animation_count // self.ANIMATION_DELAY == len(sprites):
            self.animation_count = 0

def get_bg(name):
    #load image based off its name (Blue, Brown ... whatever)
    image = pygame.image.load(join('assets','Background', name))
    _, _, width, height = image.get_rect()

    #2d list storing position of each tile
    tiles = []

    for i in range (WIDTH//width+1):
        for j in range (HEIGHT//height+1):
            position_tile = (i*width, j*height)
            tiles.append(position_tile)

    #returns the image and the list with all tiles needed
    return tiles, image

def draw(window, bg, bg_image, player, objects, offset_x, offset_y):
    

    for tile in bg:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)



def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_objects.append(obj)
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.bump_head()
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
    
    player.x_v = 0
    collide_left = collide(player, objects, -PLAYER_SPEED*2) #multiplying by 2 to make sure the player is not touching the object
    collide_right = collide(player, objects, PLAYER_SPEED*2) #multiplying by 2 to make sure the player is not touching the object
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_SPEED)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_SPEED)
    elif player.rect.left < 0:
        player.x_v = 0    
      
    vertical_collide = handle_vertical_collision(player, objects, player.y_v)
    to_check = [collide_left, collide_right, *vertical_collide]
    current_time = pygame.time.get_ticks()
    player.update()
    for obj in to_check:
        if obj and obj.name == 'fire' and not player.hit:
            player.make_hit(pygame.time.get_ticks())

def menu(window):
    WIDTH, HEIGHT = window.get_size()

    # Load font images
    letters = load_font_spritesheet(join('assets', 'Menu', 'Text', 'Text (White) (8x10).png'))

    bg, bg_image = get_bg('Gray.png')
    first_level_track.stop()
    menu_music.play(-1)
    
    # Load cursor image
    cursor_image = pygame.image.load(join('assets', 'Other', 'cursor.png')).convert_alpha()

    # Load button images
    normal_button = pygame.image.load(join('other_assets', 'png@0.5x', 'Buttons', 
                                           'Rect', 'PlayText', 'Default@0.5x.png'))
    hover_button = pygame.image.load(join('other_assets', 'png@0.5x', 'Buttons', 
                                          'Rect', 'PlayText', 'Hover@0.5x.png'))
    scaled_normal_button = pygame.transform.scale2x(normal_button)
    scaled_hover_button = pygame.transform.scale2x(hover_button)

    # Load sound button images
    sound_on = pygame.image.load(join('other_assets', 'png@0.5x', 'Buttons', 'Square', 'SoundOn', 'Default@0.5x.png'))
    sound_on_hover = pygame.image.load(join('other_assets', 'png@0.5x', 'Buttons', 'Square', 'SoundOn', 'Hover@0.5x.png'))
    sound_off = pygame.image.load(join('other_assets', 'png@0.5x', 'Buttons', 'Square', 'SoundOff', 'Default@0.5x.png'))
    sound_off_hover = pygame.image.load(join('other_assets', 'png@0.5x', 'Buttons', 'Square', 'SoundOff', 'Hover@0.5x.png'))
    scaled_sound_on = pygame.transform.scale2x(sound_on)
    scaled_sound_on_hover = pygame.transform.scale2x(sound_on_hover)
    scaled_sound_off = pygame.transform.scale2x(sound_off)
    scaled_sound_off_hover = pygame.transform.scale2x(sound_off_hover)

    sound_button_image = scaled_sound_on
    sound_button_hover_image = scaled_sound_on_hover
    sound_button_rect = sound_button_image.get_rect(topleft=(20, HEIGHT - 20 - sound_button_image.get_height()))
    sound_enabled = True

    button_rect = scaled_normal_button.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Draw "Click or press Enter" below the play button
    info_text = "CLICK OR PRESS ENTER"
    info_text_pos = (WIDTH // 2 - len(info_text) * 8, HEIGHT // 2 + 60)


    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    menu_music.stop()
                    first_level_track.play(-1)
                    main(window, sound_enabled)  # Call the main function if clicked on button
                if sound_button_rect.collidepoint(event.pos):
                    sound_enabled = not sound_enabled  # Toggle sound state
                    if sound_enabled:
                        pygame.mixer.unpause()
                        sound_button_image = scaled_sound_on
                        sound_button_hover_image = scaled_sound_on_hover
                    else:
                        pygame.mixer.pause()
                        sound_button_image = scaled_sound_off
                        sound_button_hover_image = scaled_sound_off_hover
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False
                elif event.key == pygame.K_RETURN:
                    menu_music.stop()
                    first_level_track.play(-1)
                    main(window, sound_enabled)  # Call the main function if Enter is pressed

        mouse_x, mouse_y = pygame.mouse.get_pos()
        if button_rect.collidepoint((mouse_x, mouse_y)):
            button_image = scaled_hover_button
        else:
            button_image = scaled_normal_button

        if sound_button_rect.collidepoint((mouse_x, mouse_y)):
            sound_button_current = sound_button_hover_image
        else:
            sound_button_current = sound_button_image

        # Draw the background and buttons
        window.fill((0, 0, 0))  # Optional: Fill window with black before drawing everything else
        for tile in bg:
            window.blit(bg_image, tile)
        window.blit(button_image, button_rect)
        window.blit(sound_button_current, sound_button_rect)
        blit_text(window, info_text, info_text_pos, letters)
        window.blit(cursor_image, (mouse_x, mouse_y))

        pygame.display.update()

    pygame.quit()
    sys.exit()

def pause():
    pass

def generate_level(size):
    level_blocks = []
    
    
    # Elevated platforms
    #level_blocks.append(Block(5 * size, HEIGHT - size * 3, size))
    #level_blocks.append(Block(6 * size, HEIGHT - size * 3, size))
    level_blocks.append(Block(10 * size, HEIGHT - size * 5, size))
    level_blocks.append(Block(15 * size, HEIGHT - size * 2, size))
    level_blocks.append(Block(16 * size, HEIGHT - size * 2, size))
    level_blocks.append(Block(17 * size, HEIGHT - size * 2, size))

    # Challenging gaps
    level_blocks.append(Block(20 * size, HEIGHT - size * 4, size))
    level_blocks.append(Block(24 * size, HEIGHT - size * 4, size))

    # High platform
    for i in range(25, 30):
        level_blocks.append(Block(i * size, HEIGHT - size * 6, size))

    # Stair-like ascending platforms
    for i in range(5):
        level_blocks.append(Block((2 + i) * size, HEIGHT - size * (2 + i), size))

    # Isolated platforms requiring precise jumps
    level_blocks.append(Block(8 * size, HEIGHT - size * 7, size))
    level_blocks.append(Block(22 * size, HEIGHT - size * 5, size))
    level_blocks.append(Block(23 * size, HEIGHT - size * 5, size))

    # A tricky gap that requires a longer jump
    level_blocks.append(Block(13 * size, HEIGHT - size * 3, size))
    level_blocks.append(Block(19 * size, HEIGHT - size * 3, size))  # Landing platform after the gap

    # Elevated platforms for advanced navigation
    level_blocks.append(Block(28 * size, HEIGHT - size * 7, size))
    level_blocks.append(Block(29 * size, HEIGHT - size * 8, size))  # Highest point in the level

    # Additional complex structures
    # Zig-zag platforms for complex jumping puzzles
    level_blocks.append(Block(12 * size, HEIGHT - size * 6, size))
    level_blocks.append(Block(13 * size, HEIGHT - size * 7, size))
    level_blocks.append(Block(14 * size, HEIGHT - size * 8, size))

    # A series of small platforms that act as a maze
    for j in range(1, 5):
        level_blocks.append(Block((30 - j) * size, HEIGHT - size * (2 + j), size))
        level_blocks.append(Block((25 - j) * size, HEIGHT - size * (3 + j), size))

    return level_blocks



def main(window, sound_enabled=True):
    clock = pygame.time.Clock()
    bg, bg_image = get_bg('Blue.png')
    block_size = 96
    pause_button = pygame.image.load(join('other_assets', 'png@0.5x', 'Buttons', 'Square', 'Pause', 'Default@0.5x.png')).convert_alpha()
    pause_button_hover = pygame.image.load(join('other_assets', 'png@0.5x', 'Buttons', 'Square', 'Pause', 'Hover@0.5x.png')).convert_alpha()
    player = Player(100, 100, 50, 50)
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, (WIDTH * 10) // block_size)]
    #multiplying and dividing by 3 because there are three fire widths in one block size
    fire = [Fire(i*block_size/3, HEIGHT - block_size - 64, 16, 32) for i in range (3*3,15*3)]

    objects = [*floor, *generate_level(96), *fire]
    scroll_area_width = 200
    scroll_area_height = 150
    offset_x = 0
    offset_y = 0

    pause_button_rect = pause_button.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    pause_button_image = None

    cursor_image = pygame.image.load(join('assets','Other', 'cursor.png')).convert_alpha()  # Load your cursor image
    run = True
    while run:
        current_time = pygame.time.get_ticks()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_q]:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count <= 1:
                    player.jump()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause_button_rect.collidepoint(event.pos):
                    pause()         
        player.update_hit(current_time)
        player.loop(FPS)
        for obj in fire:
            obj.loop()
            obj.on()
        handle_move(player, objects)
        draw(WINDOW, bg, bg_image, player, objects, offset_x, offset_y)
        if pause_button_rect.collidepoint((mouse_x, mouse_y)):
            pause_button_image = pause_button_hover
        else:
            pause_button_image = pause_button    


        window.blit(pause_button_image, (20, 20))

        if player.lives > 0:
            window.blit(hearts2x[player.lives], (WIDTH - 150, 20))
        else:
            window.blit(hearts2x[0], (WIDTH - 150, 20))
            player.die()    
        window.blit(cursor_image, (mouse_x, mouse_y))

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_v > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_v < 0):
            offset_x += player.x_v
            
        if (player.rect.top - offset_y) <= scroll_area_height and player.y_v < 0:
            offset_y += player.y_v
        elif (player.rect.bottom - offset_y) >= (HEIGHT - scroll_area_height - player.height) and player.y_v > 0.7:
            offset_y += player.y_v
        
        pygame.display.update()
if __name__ == '__main__':
    menu(WINDOW)
