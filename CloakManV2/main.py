import pygame
from pygame.locals import *
import sys
from sprites import *

clock = pygame.time.Clock()

pygame.init()
pygame.display.set_caption("CloackMan")

WIN_WIDTH = 640
WIN_HEIGHT = 480
BACKGROUND = 1280,960
TILE_SIZE = 32
WINDOW_SIZE = (WIN_WIDTH, WIN_HEIGHT)

#player=transformsprites("heroidle/tile000.png")
grass=transformsprites("blocks/tile001.png")
dirt=transformsprites("blocks/tile013.png")
scene = pygame.image.load("spritesheets/background/background.png")

screen = pygame.display.set_mode(WINDOW_SIZE,0,32)
display = pygame.Surface((320, 240))
#screen.blit(display, (0,0))
#proofing that the display is 300,200

display2=pygame.transform.scale(display, WINDOW_SIZE)
screen.blit(display2, (0,0))
#scaling the display to window size

scene2=pygame.transform.scale(scene, BACKGROUND)

moving_right = False
moving_left = False
jumping = False
falling = False
vertical_momentum = 0
air_timer=0

true_scroll = [0,0]

def load_map(path):
    f = open(path + '.txt','r')
    data = f.read()
    f.close()
    data = data.split('\n')
    tilemap = []
    for row in data:
        tilemap.append(list(row))
    return tilemap

tilemap = load_map('tilemap')

global animation_frames
animation_frames = {}

def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        # player_animations/idle/idle_0.png
        animation_image = transformsprites(img_loc).convert()
        animation_image.set_colorkey((255,255,255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame
        

animation_database = {}

animation_database['run'] = load_animation('player_animations/run',[7,7,7,7,7,7])
animation_database['idle'] = load_animation('player_animations/idle',[7,7,7,7])
animation_database['jump'] = load_animation('player_animations/jump',[4,4,4])
#animation_database['jumpup'] = load_animation('player_animations/jumpup',[7,7,7])
animation_database['jumpdown'] = load_animation('player_animations/jumpdown',[4,4,4])

player_action = 'idle'
player_frame = 0
player_flip = False

player_rect = pygame.Rect(100,100,32,32)
test_rect = pygame.Rect(100,100,100,50)
#tilemap = []
def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list
def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types
#Game Loop
while True:
    player=transformsprites("player_animations/idle/idle_0.png")
    screen.blit(scene2, (0,-480))
    #screen.blit(player,playerLocation) # render player
    tile_rects = []
    #Below is the scrolling feaature within the game that allows the screen to essentially follow the player.
    #true scroll is
    true_scroll[0] += (player_rect.x-true_scroll[0]-222)/20
    true_scroll[1] += (player_rect.y-true_scroll[1]-212)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    y = 0
    for row in tilemap:
        x = 0
        for tile in row:
            if tile == '2':
                screen.blit(grass, (x * TILE_SIZE - true_scroll[0], y * TILE_SIZE - true_scroll[1]))
            if tile == '1':
                screen.blit(dirt, (x * TILE_SIZE - true_scroll[0], y * TILE_SIZE - true_scroll[1]))
            if tile != '0':
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1

    player_movement = [0,0]
    if moving_right == True:
        player_movement[0] += 4
    if moving_left == True:
        player_movement[0] -= 4
    player_movement[1] += vertical_momentum
    vertical_momentum += 0.2
    if vertical_momentum > 4:
        vertical_momentum = 4


    if player_movement[0] == 0:
        player_action,player_frame = change_action(player_action,player_frame,'idle')
    if player_movement[0] > 0 and collisions['bottom']==True:
        player_flip = False
        player_action,player_frame = change_action(player_action,player_frame,'run')
    if player_movement[0] < 0 and collisions['bottom']==True:
        player_flip = True
        player_action,player_frame = change_action(player_action,player_frame,'run')
    if player_movement[0] > 0:
        if vertical_momentum < 0 :
            player_flip = False
            player_action,player_frame = change_action(player_action,player_frame,'jump')
    if player_movement[0] < 0:
        if vertical_momentum < 0 :
            player_flip = True
            player_action,player_frame = change_action(player_action,player_frame,'jump')
    #if player_movement[1] > 0:
        #falling = True
        #jumping = False
        #player_flip = False
        #player_action,player_frame = change_action(player_action,player_frame,'jumpdown')
        
    player_rect, collisions = move(player_rect, player_movement, tile_rects)

        

    if collisions['bottom']:
        air_timer = 0
        vertical_momentum = 0
        jumping = False
    else:
        air_timer += 1
        #falling = True
    
    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player = animation_frames[player_img_id]
    screen.blit(pygame.transform.flip(player,player_flip,False),(player_rect.x-scroll[0],player_rect.y-scroll[1]))

    #screen.blit(player, (player_rect.x-scroll[0],player_rect.y-scroll[1]))
 
    # test rect for collisions
    #if player_rect.colliderect(test_rect):
    #    pygame.draw.rect(screen,(255,0,0),test_rect)
    #else:
    #    pygame.draw.rect(screen,(0,0,0),test_rect)

    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            #if event.key == K_UP:
             #   jumping = True
             #   if air_timer < 6:
             #       vertical_momentum = -6
            if event.key == K_UP:
                if (air_timer < 6):
                    jumping=True
                    falling=False
                    vertical_momentum = -6
                    player_movement[1] = -5.2
                    #if vertical_momentum == -6:
                        #falling = True
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
            if event.key == K_UP:
                jumping = False
    #display2=pygame.transform.scale(display, WINDOW_SIZE)
    #screen.blit(display2, (0,0))
    #scene2=pygame.transform.scale(scene, BACKGROUND)
    #screen.blit(scene2, (0,-480))

    pygame.display.update()
    clock.tick(60)
