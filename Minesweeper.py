"""
TODO:

Optimizations (if needed)
"""


from write import write

import os
import sys

import numpy as np
import random

import time

import pygame

sys.setrecursionlimit(26194)

pyg = pygame
disp = pygame.display

pyg.init()
disp.init()

"""Colors"""
WHITE = pyg.Color('white')
BLACK = pyg.Color('black')
GREEN = pyg.Color('green')
RED = pyg.Color('red')
YELLOW = pyg.Color('yellow')
LIGHTBLUE = pyg.Color('lightblue')

bg_col = WHITE
line_col = BLACK
text_col = BLACK
btn_col = GREEN
quit_col = RED
option_col = YELLOW
change_optn_col = YELLOW
up_col = LIGHTBLUE
down_col = LIGHTBLUE

"""Screen"""
# Resolutions: 960x720, 1080x720, 1536x864
screen = disp.set_mode((1536, 864))
screen_w, screen_h = screen.get_size()
screen.fill(bg_col)
disp.flip()

disp.set_caption('Minesweeper')


"""Images"""


def load_img(name, conv_alpha=False):
    """Loads image"""
    image_name = os.path.join('img', 'Minesweeper', name)
    image = pyg.image.load(image_name)
    if conv_alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
    image_rect = image.get_rect()
    return image, image_rect
tile_1, tile_1_rect = load_img('1.bmp')  # 1 tile
tile_2, tile_2_rect = load_img('2.bmp')  # 2 tile
tile_3, tile_3_rect = load_img('3.bmp')  # 3 tile
tile_4, tile_4_rect = load_img('4.bmp')  # 4 tile
tile_5, tile_5_rect = load_img('5.bmp')  # 5 tile
tile_6, tile_6_rect = load_img('6.bmp')  # 6 tile
tile_7, tile_7_rect = load_img('7.bmp')  # 7 tile
tile_8, tile_8_rect = load_img('8.bmp')  # 8 tile
tile_blank, tile_blank_rect = load_img('Empty.bmp')  # Indented blank tile
tile_mark, tile_mark_rect = load_img('Mark.bmp')  # Marker tile
tile_mark_through, tile_mark_through_rect = load_img('Mark_Through.bmp')
tile_mine, tile_mine_rect = load_img('Mine.bmp')  # Mine tile
tile_blank_up, tile_blank_up_rect = load_img('Empty_Up.bmp')  # Blank tile
tile_blank_up_through, tile_blank_up_through_rect =\
                       load_img('Empty_Up_Through.bmp')
tile_blank_up_through2, tile_blank_up_through_rect2 =\
                        load_img('Empty_Up_Through.bmp')
tile_mark_through2, tile_mark_through_rect2 = load_img('Mark_Through.bmp')
tile_cpumark, tile_cpumark_rect = load_img('CpuMark.bmp')
tile_dot, tile_dot_rect = load_img('Dot.png', conv_alpha=True)

"""Grid size"""
size_w = 30
size_h = 30
"""Mine count"""
mines = 125

"""Options"""
show_destroy = False
cpu = False
wait = 1
mode = 1
vis_helper = True
show_time = True
"""
Modes:
1: Normal                    5: Diagonal
 XXX                          X-X
 XOX                          -O-
 XXX                          X-X
2: Knight's path             6: Far diagonal
 -X-X-                        X---X
 X---X                        -X-X-
 --O--                        --O--
 X---X                        -X-X-
 -X-X-                        X---X
3: Orthogonal
 -X-
 XOX
 -X-
4: Far orthogonal
 --X--
 --X--
 XXOXX
 --X--
 --X--
"""
around = []
modes_str = {1: 'Normal',
             2: "Knight's Path",
             3: 'Orthogonal',
             4: 'Far Orthogonal',
             5: 'Diagonal',
             6: 'Far Diagonal'}

"""Functions"""


def update():
    disp.flip()
    pyg.event.pump()


def clear():
    screen.fill(bg_col)


def ind_rel(x_d, y_d):  # Get the relative index (with diff x_d and y_d)
    return index+(x_d)+(y_d*size_w)  # Return index


def count_mines(x, y):
    c = 0
    for dx, dy in around:
        if x+dx >= size_h or y+dy >= size_w or x+dx < 0 or y+dy < 0:
            continue
        elif tiles[x+dx, y+dy] == 9:
            c += 1
    return c


def set_mode():
    global around
    if mode == 1:  # Normal
        around = ((-1, -1), ( 0, -1), ( 1, -1),
                  (-1,  0),           ( 1,  0),
                  (-1,  1), ( 0,  1), ( 1,  1))
    elif mode == 2:  # Knight's path
        around = (          (-1, -2), ( 1, -2),
                  (-2, -1),                     ( 2, -1),
                  (-2,  1),                     ( 2,  1),
                            (-1,  2), ( 1,  2))
    elif mode == 3:  # Orthogonal
        around = (         (0, -1),
                  (-1, 0),         ( 1, 0),
                           (0,  1))
    elif mode == 4:  # Far Orthogonal
        around = (                  (0, -2),
                                    (0, -1),
                  (-2, 0), (-1, 0),          ( 1, 0), ( 2, 0),
                                    (0,  1),
                                    (0,  2))
    elif mode == 5:  # Diagonal
        around = ((-1, -1), (1, -1),
                  (-1,  1), (1,  1))
    elif mode == 6:  # Far Diagonal
        around = ((-2, -2),                    (2, -2),
                            (-1, -1), (1,  -1),
                            (-1,  1), (1,   1),
                  (-2,  2),                    (2,  2))

set_mode()  # Sets around variable according to mode


def delaround(i, j):
    """Reveal tiles around a clicked tile"""
    global game_over, last_destroy
    # If the clicked tile is already revealed, do nothing.
    if tiles_cover[i, j].get_size() == (0, 0):
        return
    if tiles_cover[i, j] == tile_img_list[11]:
        return
    if tiles_cover[i, j] != tile_img_list[11]:
        tiles_cover[i, j] = pyg.Surface((0, 0))  # Reveal clicked tile
        last_destroy = (i, j)
        if tiles[i, j] == 9:  # If mine is under clicked tile
            game_over = 1
    # If the current tile is blank, check all adjacent tiles
    cycle = [(i+dx, j+dy) for dx, dy in around]
    # Cycles through surrounding tiles
    for x, y in cycle:
        if show_destroy:
            pyg.event.pump()
        # If x or y coordinates are off the grid, skip this loop
        if x >= size_h or y >= size_w or x < 0 or y < 0:
            continue
        # If the current tile is already uncovered, skip loop
        if tiles_cover[x, y].get_size() == (0, 0):
            continue
        if tiles_cover[x, y] == tile_img_list[11]:
            continue
        # If clicked tile is a number tile, uncover it
        if tiles[i, j] == 0 and tiles[x, y] in range(1, 9):
            tiles_cover[x, y] = pyg.Surface((0, 0))
            last_destroy = (i, j)
            if show_destroy:
                draw_img()
                draw_cover()
                update()
        # If clicked tile is blank, call function at the tile
        elif tiles[x, y] == 0:   # abs(x-i)+abs(y-j) != 2
            if show_destroy:
                draw_img()
                draw_cover()
                update()
            delaround(x, y)


def draw_all():
    clear()
    draw_img()
    draw_cover()
    draw_time()
    draw_mines_left()
    update()


def draw_cover():
    dest_x = screen_w//2 - (size_w*tile_w)//2
    dest_y = screen_h//2 - (size_h*tile_h)//2

    for y in tiles_cover:
        for x in y:
            screen.blit(x, (dest_x, dest_y))
            dest_x += tile_w
        dest_y += tile_h
        dest_x = screen_w//2 - (size_w*tile_w)//2


def draw_img():
    dest_x = screen_w//2 - (size_w*tile_w)//2
    dest_y = screen_h//2 - (size_h*tile_h)//2

    for y in tiles_img:
        for x in y:
            screen.blit(x, (dest_x, dest_y))
            dest_x += tile_w
        dest_y += tile_h
        dest_x = screen_w//2 - (size_w*tile_w)//2


def draw_time():
    if time_start:
        cur_time = time.time()-time_start
        write(screen,
              'Time: ' + str(int(cur_time)//60) + ':' +
              str(int(cur_time) % 60).zfill(2) + '.' +
              str(round(cur_time-int(cur_time), 2))[2:],
              text_col, None, 28, screen_w//2-60, screen_h-50,
              centered=False)


def draw_mines_left():
    write(screen, 'Mines Left: '+str(mines_left),
          text_col, None, 28, screen_w//2, 50)


"""Mark Tile"""


def mark(i, j):
    global mines_left
    if tiles_cover[i, j] == tile_img_list[11]:
        tiles_cover[i, j] = tile_img_list[10]
        mines_left += 1
    elif tiles_cover[i, j] == tile_img_list[10]:
        tiles_cover[i, j] = tile_img_list[11]
        mines_left -= 1


def clear_tiles(i, j):
    cycle = [(i+dx, j+dy) for dx, dy in around]
    if tiles_img[i, j] in tile_img_list[1:9]:
        count = 0
        for x, y in cycle:
            if x < 0 or y < 0 or x >= size_h or y >= size_w:
                continue
            if tiles_cover[x, y] == tile_img_list[11]:
                count += 1
        if count == tiles[i, j]:
            for x, y in cycle:
                if x < 0 or y < 0 or x >= size_h or y >= size_w:
                    continue
                delaround(x, y)


def show_mines():
    for x, y in mine_indices:
        if tiles_cover[x, y] == tile_img_list[10]:
            tiles_cover[x, y] = tile_img_list[12]
        elif tiles_cover[x, y] == tile_img_list[11]:
            tiles_cover[x, y] = tile_img_list[13]

    for a in range(255, 100, -1):
        tile_img_list[12].set_alpha(a)
        tile_img_list[13].set_alpha(a)

        draw_img()
        draw_cover()

        update()
        pyg.event.pump()
        pyg.time.delay(20)


def explode_mines():
    b = False
    index_coords = last_destroy
    tile_img_list[14].set_alpha(100)
    tile_img_list[15].set_alpha(100)
    mine_distance = []
    for x, y in mine_indices:
        mine_distance.append(
            (
                ((index_coords[0]-x)**2 + (index_coords[1]-y)**2)**0.5,
                mine_indices.index((x, y)))
            )

    mine_distance.sort()

    for dist, mine_index in mine_distance:
        x, y = mine_indices[mine_index]
        cur_tile_img = tiles_cover[x, y]
        if tiles_cover[x, y] == tile_img_list[10]:
            tiles_cover[x, y] = tile_img_list[12]
        elif tiles_cover[x, y] == tile_img_list[11]:
            tiles_cover[x, y] = tile_img_list[13]
        for a in range(255, 100, -15):
            tile_img_list[12].set_alpha(a)
            tile_img_list[13].set_alpha(a)

            draw_img()
            draw_cover()

            update()
            event = pyg.event.get()
            if event:
                event = event[0]
            else:
                event = pyg.event.Event(-1)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2 and event.dict['key'] == 27:
                for x, y in mine_indices:
                    if tiles_cover[x, y] == tile_img_list[10] or\
                            tiles_cover[x, y] == tile_img_list[12]:
                        tiles_cover[x, y] = tile_img_list[14]
                    elif tiles_cover[x, y] == tile_img_list[11] or\
                            tiles_cover[x, y] == tile_img_list[13]:
                        tiles_cover[x, y] = tile_img_list[15]
                draw_img()
                draw_cover()
                update()
                b = True
                break
        if b:
            break

        if tiles_cover[x, y] == tile_img_list[12]:
            tiles_cover[x, y] = tile_img_list[14]
        elif tiles_cover[x, y] == tile_img_list[13]:
            tiles_cover[x, y] = tile_img_list[15]


def show_all():
    for a in range(255, 200, -1):
        tile_img_list[10].set_alpha(a)
        tile_img_list[11].set_alpha(a)
        draw_img()
        draw_cover()
        update()
        pyg.event.pump()
        pyg.time.delay(20)


def resize_tiles():
    global tile_h, tile_w, tile_ratio, tile_img_list, tile_rect_list
    global tile_1, tile_1_rect, tile_2, tile_2_rect,\
        tile_3, tile_3_rect, tile_4, tile_4_rect,\
        tile_5, tile_5_rect, tile_6, tile_6_rect,\
        tile_7, tile_7_rect, tile_8, tile_8_rect,\
        tile_blank, tile_blank_rect, tile_mark, tile_mark_rect,\
        tile_mark_through, tile_mark_through_rect,\
        tile_mark_through2, tile_mark_through_rect2,\
        tile_mine, tile_mine_rect, tile_blank_up, tile_blank_up_rect,\
        tile_blank_up_through, tile_blank_up_through_rect,\
        tile_blank_up_through2, tile_blank_up_through_rect2,\
        tile_cpumark, tile_cpumark_rect, tile_dot, tile_dot_rect

    tile_img_list = [
        tile_blank, tile_1, tile_2, tile_3, tile_4, tile_5,
        tile_6, tile_7, tile_8, tile_mine,
        tile_blank_up, tile_mark, tile_blank_up_through, tile_mark_through,
        tile_blank_up_through2, tile_mark_through2, tile_cpumark, tile_dot
        ]  # List of tile images

    for i in [x for x in tile_img_list if x != tile_dot]:
        i.set_alpha(255)
    tile_dot.set_alpha(64)

    tile_h = (screen_h-150)//size_h  # Tile height (resized)
    tile_w = tile_h  # Tile width is equal to the tile height (resized)
    if tile_w*size_w >= screen_w-500:
        tile_w = (screen_w-500)//size_w
        tile_h = tile_w

    tile_ratio = 50/tile_h  # Tile ratio

    tile_img_list = [
        pyg.transform.scale(img, (tile_h, tile_w)) for img in tile_img_list
        ]  # Scaled images for tile images
    tile_rect_list = [
        img.get_rect() for img in tile_img_list
        ]  # Scaled image rects for tile images

    (tile_blank_rect,
     tile_1_rect, tile_2_rect, tile_3_rect, tile_4_rect,
     tile_5_rect, tile_6_rect, tile_7_rect, tile_8_rect,
     tile_mine_rect,
     tile_blank_up_rect,
     tile_mark_rect,
     tile_blank_up_through_rect,
     tile_mark_through_rect,
     tile_blank_up_through_rect2,
     tile_mark_through_rect2,
     tile_cpumark_rect,
     tile_dot_rect
     ) = tile_rect_list  # Set rect variables

    (tile_blank,
     tile_1, tile_2, tile_3, tile_4,
     tile_5, tile_6, tile_7, tile_8,
     tile_mine,
     tile_blank_up,
     tile_mark,
     tile_blank_up_through,
     tile_mark_through,
     tile_blank_up_through2,
     tile_mark_through2,
     tile_cpumark,
     tile_dot
     ) = tile_img_list  # Set image variables


def main():
    global record_time, cur_time, time_start, end_time,\
        index, game_over, mines_left, mine_indices,\
        index_coords
    global tile_1, tile_1_rect, tile_2, tile_2_rect,\
        tile_3, tile_3_rect, tile_4, tile_4_rect,\
        tile_5, tile_5_rect, tile_6, tile_6_rect,\
        tile_7, tile_7_rect, tile_8, tile_8_rect,\
        tile_blank, tile_blank_rect, tile_mark, tile_mark_rect,\
        tile_mark_through, tile_mark_through_rect,\
        tile_mine, tile_mine_rect, tile_blank_up, tile_blank_up_rect,\
        tile_blank_up_through, tile_blank_up_through_rect,\
        tile_dot, tile_dot_rect
    global tiles, tiles_img, tile_img_list,\
        tile_h, tile_w, tile_rect_list, tiles_cover

    game_over = 0
    cur_time = None
    time_start = None
    end_time = 2**1000
    set_mode()

    mines_left = int(mines)

    """Variables/Tiles"""

    tiles = np.array([[0]*size_w]*size_h)  # Tiles (numbers)

    tile_img_list = [
        tile_blank, tile_1, tile_2, tile_3, tile_4, tile_5,
        tile_6, tile_7, tile_8, tile_mine,
        tile_blank_up, tile_mark, tile_blank_up_through, tile_mark_through,
        tile_blank_up_through2, tile_mark_through2
        ]  # List of tile images

    resize_tiles()

    # Board tile images
    tiles_img = np.array([[tile_img_list[0]]*size_w]*size_h)
    # Overlay tile images
    tiles_cover = np.array([[tile_blank_up]*size_w]*size_h)

    tiles_rect = []  # Initialize tile_rect list for checking clicks

    i = 0  # Initialize i and j coordinates of tile list
    j = 0

    dest_x = screen_w//2 - (size_w*tile_w)//2  # Destination of tiles
    dest_y = screen_h//2 - (size_h*tile_h)//2  # (Centered around middle)

    clear()

    if record_time:
        write(screen,
              'Record Time: ' + str(int(record_time)//60) + ':' +
              str(int(record_time) % 60).zfill(2) + '.' +
              str(round(record_time-int(record_time), 2))[2:].zfill(2),
              text_col, None, 28, 25, screen_h-50,
              centered=False)

    """Draw tiles"""
    for y in tiles_cover:  # Go through the tiles vertically
        for x in y:  # Go through each tile in the lists
            blitrect = screen.blit(x, (dest_x, dest_y))  # Draw tile
            tiles_rect.append(blitrect)  # Append tile rect for click detection
            dest_x += tile_w  # Move the destination x-coord to the right
        dest_y += tile_h  # Move the destination y-coord downwards
        dest_x = screen_w//2 - (size_w*tile_w)//2  # Reset x-coord

    update()  # Update screen

    area = pyg.Surface((screen_w, 70))
    area.fill(WHITE)
    screen.blit(area, (0, 0))
    write(screen, 'Start by clicking a tile.',
          text_col, None, 28, screen_w//2, 35)
    update()

    """Get first click"""
    running = True
    while running:
        event = pyg.event.get()  # Get eventlist
        if event:  # If something happens,
            event = event[0]  # Get the event itself
        else:  # Otherwise,
            event = pyg.event.Event(-1)  # Set event to something else
        if event.type == pyg.QUIT:
            running = False
            break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.dict['button'] == 1:  # Left click
            print("click registered")
            click = pyg.Rect(event.dict['pos'], (1, 1))  # Record pos as rect
            index = click.collidelist(tiles_rect)  # Get index of rect clicked
            if index == -1:
                continue
            i = index // size_h  # Get y-coord of rect clicked
            j = index % size_w  # Get x-coord of rect clicked
            index_coords = (i, j)  # Format as ordered pair
            break  # Exit loop
    if not running:
        pyg.quit()
        return

    """Set up board"""
    """No-mine locations"""
    no_mines = [
        ind_rel(-2, -2), ind_rel(-1, -2),
        ind_rel(+0, -2), ind_rel(+1, -2), ind_rel(+2, -2),
        ind_rel(-2, -1), ind_rel(-1, -1),
        ind_rel(+0, -1), ind_rel(+1, -1), ind_rel(+2, -1),
        ind_rel(-2, +0), ind_rel(-1, +0),
        ind_rel(+0, +0), ind_rel(+1, +0), ind_rel(+2, +0),
        ind_rel(-2, +1), ind_rel(-1, +1),
        ind_rel(+0, +1), ind_rel(+1, +1), ind_rel(+2, +1),
        ind_rel(-2, +2), ind_rel(-1, +2),
        ind_rel(+0, +2), ind_rel(+1, +2), ind_rel(+2, +2)
        ]  # List of places where there should be no mines at first click

    mine_indices = [index]  # Initialize mine indices
    while True:
        for i in no_mines:  # Cycle through places where no mines should be
            if i in mine_indices:  # If one of the mines is in that place,
                mine_indices = random.sample(
                    range(0, size_w*size_h), mines
                    )  # Randomize mine placement
                break  # Exit inner loop
        else:  # When there are no mines in the place where they shouldn't be,
            break  # Exit loop

    for mine_index in range(len(mine_indices)):  # Loop though each mine
        index = mine_indices[mine_index]  # Record the index
        i = index // size_w  # Get the y-coordinate of the index
        j = index % size_h  # Get the x-coordinate of the index
        mine_indices[mine_index] = (i, j)  # Format as ordered pair
        tiles[i, j] = 9  # Set the tile number to 9 (denotes mine)

    """Number of mines surrounding a tile"""
    for x in range(size_h):  # Loop though the vertical coordinates
        for y in range(size_w):  # Loop through the horizontal coordinates
            if tiles[x, y] == 9:  # If the tile is a mine,
                continue  # Skip this loop

            tiles[x, y] = count_mines(x, y)

    # Changes tile numbers to tile images with the corresponding numbers
    for i in range(len(tiles)):
        for j in range(len(tiles[i])):
            tiles_img[i, j] = tile_img_list[tiles[i, j]]

    index_coords_marker = (-1, -1)
    index_coords_clear = (-1, -1)
    mark_around = False
    running = True
    while running:
        if index_coords != (-1, -1):
            delaround(*index_coords)
        if game_over != 1:
            index_coords = (-1, -1)

        if time_start is None:
            time_start = time.time()

        if index_coords_marker != (-1, -1):
            i, j = index_coords_marker
            if mark_around:
                for di, dj in around:
                    if i+di < 0 or j+dj < 0 or\
                       i+di >= size_h or j+dj >= size_w:
                        continue
                    if tiles_cover[i+di, j+dj] in (tile_blank_up,
                                                   tile_cpumark):
                        mark(i + di, j + dj)
                mark_around = False
            else:
                mark(*index_coords_marker)
        index_coords_marker = (-1, -1)

        if index_coords_clear != (-1, -1):
            clear_tiles(*index_coords_clear)
        index_coords_clear = (-1, -1)

        for i in range(len(tiles)):
            for j in range(len(tiles[i])):
                tiles_img[i, j] = tile_img_list[tiles[i, j]]

        draw_img()
        draw_cover()
        update()

        b = False
        for x in range(len(tiles_img)):
            for y in range(len(tiles_img[x])):
                if tiles_img[x, y] != tile_img_list[9] and\
                   tiles_cover[x, y] == tile_img_list[10] and\
                   tiles_cover[x, y] != tile_img_list[11]:
                    b = True
                    break
            if b:
                break
        else:
            cur_time = time.time()-time_start
            end_time = cur_time
            clear()
            write(screen, 'You win!!!',
                  text_col, None, 36, screen_w//2, 35)
            write(screen,
                  'Time: ' + str(int(cur_time)//60) + ':' +
                  str(int(cur_time) % 60).zfill(2) + '.' +
                  str(round(cur_time-int(cur_time), 2))[2:],
                  text_col, None, 28, screen_w//2-60, screen_h-50,
                  centered=False)
            show_mines()
            draw_img()
            draw_cover()
            update()
            break

        if game_over == 1:
            clear()
            cur_time = time.time()-time_start
            write(screen, 'Game Over.',
                  text_col, None, 36, screen_w//2, 35)
            write(screen,
                  'Time: ' + str(int(cur_time)//60) + ':' +
                  str(int(cur_time) % 60).zfill(2) + '.' +
                  str(round(cur_time-int(cur_time), 2))[2:],
                  text_col, None, 28, screen_w//2-60, screen_h-50,
                  centered=False)
            explode_mines()
            show_all()
            draw_img()
            draw_cover()
            update()
            break

        while running:
            event = pyg.event.get()
            pressed = pyg.key.get_pressed()
            if event:
                event = event[0]
            else:
                event = pyg.event.Event(-1)
            if event.type == pyg.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.dict['button'] == 1:
                click = pyg.Rect(event.dict['pos'], (1, 1))
                index = click.collidelist(tiles_rect)
                if index == -1:
                    continue
                i = index // size_w
                j = index % size_h
                index_coords = (i, j)
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.dict['button'] == 3:
                click = pyg.Rect(event.dict['pos'], (1, 1))
                index_marker = click.collidelist(tiles_rect)
                if index_marker == -1:
                    continue
                i = index_marker // size_h
                j = index_marker % size_w
                index_coords_marker = (i, j)
                if pressed[pyg.K_LSHIFT] or pressed[pyg.K_RSHIFT]:
                    empty_up_count = 0
                    for di, dj in around:
                        if i+di < 0 or j+dj < 0 or\
                           i+di >= size_h or j+dj >= size_w:
                            continue
                        if tiles_cover[i+di, j+dj] in tile_img_list[10:12]:
                            empty_up_count += 1
                    if empty_up_count == count_mines(i, j):
                        mark_around = True
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.dict['button'] == 2:
                click = pyg.Rect(event.dict['pos'], (1, 1))
                index_clear = click.collidelist(tiles_rect)
                if index_clear == -1:
                    continue
                i = index_clear // size_h
                j = index_clear % size_w
                index_coords_clear = (i, j)
                break
            elif vis_helper and event.type == pyg.MOUSEMOTION:
                mouse = pyg.Rect(event.dict['pos'], (1, 1))
                hover_index = mouse.collidelist(tiles_rect)
                if hover_index == -1:
                    continue
                h_i = hover_index // size_h
                h_j = hover_index % size_w
                draw_img()
                draw_cover()
                if tiles[h_i, h_j] not in range(1, 9) or\
                   tiles_cover[h_i, h_j] in [tile_mark, tile_blank_up]:
                    continue
                for dx, dy in around:  # Draw dot at each of coords
                    n_i, n_j = h_i+dx, h_j+dy
                    if n_i >= size_h or n_j >= size_w or n_i < 0 or n_j < 0:
                        continue
                    elif tiles_cover[n_i, n_j] not in (tile_mark,
                                                       tile_blank_up):
                        continue
                    screen.blit(tile_dot,
                                tiles_rect[hover_index+size_w*dx+dy])
            area = pyg.Surface((screen_w, 70))
            area.fill(WHITE)
            screen.blit(area, (0, 0))
            screen.blit(area, (0, screen_h-70))
            write(screen, 'Mines Left: '+str(mines_left),
                  text_col, None, 28, screen_w//2, 50, antialias=False)
            cur_time = time.time()-time_start
            if show_time:
                write(screen,
                      'Time: ' + str(int(cur_time)//60) + ':' +
                      str(int(cur_time) % 60).zfill(2) + '.' +
                      str(round(cur_time-int(cur_time), 2))[2:].zfill(2),
                      text_col, None, 28, screen_w//2-60, screen_h-50,
                      centered=False)
            if record_time is not None:
                write(screen,
                      'Record Time: ' + str(int(record_time)//60) + ':' +
                      str(int(record_time) % 60).zfill(2) + '.' +
                      str(round(record_time-int(record_time), 2))[2:].zfill(2),
                      text_col, None, 28, 25, screen_h-50,
                      centered=False)
            update()
    if not running:
        pyg.quit()
        return
    
    button = pyg.Surface((100, 50))
    button_rect = pyg.Rect(screen_w-162, screen_h//2-75, 100, 50)
    button.fill(btn_col)
    screen.blit(button, (screen_w-162, screen_h//2-75))
    text_x = screen_w-162+button.get_width()//2
    text_y = screen_h//2-75+button.get_height()//2
    write(screen, 'Again?', text_col, None, 28, text_x, text_y)

    quit_btn = pyg.Surface((75, 50))
    quit_btn_rect = pyg.Rect(screen_w-150, screen_h//2+100, 75, 50)
    quit_btn.fill(quit_col)
    screen.blit(quit_btn, (screen_w-150, screen_h//2+100))
    quit_txt_x = screen_w-150+quit_btn.get_width()//2
    quit_txt_y = screen_h//2+100+quit_btn.get_height()//2
    write(screen, 'Quit?', text_col, None, 24, quit_txt_x, quit_txt_y)

    option_btn = pyg.Surface((100, 50))
    option_btn_rect = pyg.Rect(50, screen_h//2-25, 100, 50)
    option_btn.fill(option_col)
    screen.blit(option_btn, (50, screen_h//2-25))
    option_txt_x = 50+option_btn.get_width()//2
    option_txt_y = screen_h//2-25+option_btn.get_height()//2
    write(screen, 'Options', text_col, None, 26, option_txt_x, option_txt_y)
    update()
    while True:
        event = pyg.event.get()
        if event:
            event = event[0]
        else:
            event = pyg.event.Event(-1)
        if event.type == pyg.QUIT:
            pyg.quit()
            break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.dict['button'] == 1:
            pos = event.dict['pos']
            click = pyg.Rect(pos, (1, 1))
            if button_rect.colliderect(click):
                if record_time and end_time and end_time < record_time:
                    record_time = end_time
                elif record_time is None and end_time:
                    record_time = end_time
                main()
                break
            elif quit_btn_rect.colliderect(click):
                pyg.quit()
                break
            elif option_btn_rect.colliderect(click):
                options()
                break


"""AI/CPU"""


def pick_rand_tile():
    global index, index_coords
    index = random.randint(0, size_w*size_h-1)
    i = index // size_h
    j = index % size_w
    index_coords = (i, j)


def mark_click(i, j):
    tiles_cover[i, j] = tile_cpumark


def count_covered(i, j, mark=True):
    cycle = [(i+dx, j+dy) for dx, dy in around]

    c = 0
    if mark:
        tiles_to_test = (tile_mark, tile_blank_up)
    else:
        tiles_to_test = (tile_blank_up,)
    for x, y in cycle:
        if y >= size_w or y < 0 or\
           x >= size_h or x < 0:
            continue
        if tiles_cover[x, y] in tiles_to_test:
            c += 1
    return c


def mark_around(i, j):
    global mines_left
    cycle = [(i+dx, j+dy) for dx, dy in around]
    for x, y in cycle:
        if y >= size_w or y < 0 or\
           x >= size_h or x < 0:
            continue
        if tiles_cover[x, y] == tile_blank_up:
            tiles_cover[x, y] = tile_mark

    mines_left = mines-list(tiles_cover.flatten()).count(tile_mark)


"""Cpu Main"""


def cpu_main():
    global record_time, cur_time, time_start, end_time,\
        index, game_over, mines_left, mine_indices, index_coords
    global tile_1, tile_1_rect, tile_2, tile_2_rect,\
        tile_3, tile_3_rect, tile_4, tile_4_rect,\
        tile_5, tile_5_rect, tile_6, tile_6_rect,\
        tile_7, tile_7_rect, tile_8, tile_8_rect,\
        tile_blank, tile_blank_rect, tile_mark, tile_mark_rect,\
        tile_mark_through, tile_mark_through_rect,\
        tile_mine, tile_mine_rect, tile_blank_up, tile_blank_up_rect,\
        tile_blank_up_through, tile_blank_up_through_rect, tile_cpumark,\
        tile_cpumark_rect
    global tiles, tiles_img, tile_img_list,\
        tile_h, tile_w, tile_rect_list, tiles_cover, prev_tiles_cover
    global times_done, loop

    game_over = 0
    cur_time = None
    time_start = None
    end_time = 2**1000

    mines_left = int(mines)

    """Variables/Tiles"""
    tiles = np.array([[0]*size_w]*size_h)  # Tiles (numbers)

    resize_tiles()

    # Board tile images
    tiles_img = np.array([[tile_img_list[0]]*size_w]*size_h)
    # Overlay tile images
    tiles_cover = np.array([[tile_blank_up]*size_w]*size_h)

    dest_x = screen_w//2 - (size_w*tile_w)//2  # Destination of tiles
    dest_y = screen_h//2 - (size_h*tile_h)//2  # (Centered around middle)

    clear()

    if record_time:
        write(screen,
              'Record Time: ' + str(int(record_time)//60) + ':' +
              str(int(record_time) % 60).zfill(2) + '.' +
              str(round(record_time-int(record_time), 2))[2:].zfill(2),
              text_col, None, 28, 25, screen_h-50,
              centered=False)

    """Draw tiles"""
    for y in tiles_cover:  # Go through the tiles vertically
        for x in y:  # Go through each tile in the lists
            blitrect = screen.blit(x, (dest_x, dest_y))  # Draw tile
            dest_x += tile_w  # Move the destination x-coord to the right
        dest_y += tile_h  # Move the destination y-coord downwards
        dest_x = screen_w//2 - (size_w*tile_w)//2  # Reset x-coord

    update()  # Update screen

    area = pyg.Surface((screen_w, 70))
    area.fill(WHITE)
    screen.blit(area, (0, 0))

    pick_rand_tile()

    """Set up board"""
    """No-mine locations"""
    no_mines = [
        ind_rel(-2, -2), ind_rel(-1, -2),
        ind_rel(+0, -2), ind_rel(+1, -2), ind_rel(+2, -2),
        ind_rel(-2, -1), ind_rel(-1, -1),
        ind_rel(+0, -1), ind_rel(+1, -1), ind_rel(+2, -1),
        ind_rel(-2, +0), ind_rel(-1, +0),
        ind_rel(+0, +0), ind_rel(+1, +0), ind_rel(+2, +0),
        ind_rel(-2, +1), ind_rel(-1, +1),
        ind_rel(+0, +1), ind_rel(+1, +1), ind_rel(+2, +1),
        ind_rel(-2, +2), ind_rel(-1, +2),
        ind_rel(+0, +2), ind_rel(+1, +2), ind_rel(+2, +2)
        ]  # List of places where there should be no mines at first click

    mine_indices = [index]  # Initialize mine indices
    while True:
        for i in no_mines:  # Cycle through places where no mines should be
            if i in mine_indices:  # If one of the mines is in that place,
                mine_indices = random.sample(
                    range(1, size_w*size_h+1), mines
                    )  # Randomize mine placement
                break  # Exit inner loop
        else:  # When there are no mines in the place where they shouldn't be,
            break  # Exit loop

    for mine_index in range(len(mine_indices)):  # Loop though each mine
        index = mine_indices[mine_index]  # Record the index
        i = (index-1)//size_w  # Get the y-coordinate of the index
        j = (index-1) % size_h  # Get the x-coordinate of the index
        mine_indices[mine_index] = (i, j)  # Format as ordered pair
        tiles[i, j] = 9  # Set the tile number to 9 (denotes mine)

    """Number of mines surrounding a tile"""
    for x in range(size_h):  # Loop though the vertical coordinates
        for y in range(size_w):  # Loop through the horizontal coordinates
            if tiles[x, y] == 9:  # If the tile is a mine,
                continue  # Skip this loop

            tiles[x, y] = count_mines(x, y)

    # Changes tile numbers to tile images with the corresponding numbers
    for i in range(len(tiles)):
        for j in range(len(tiles[i])):
            tiles_img[i, j] = tile_img_list[tiles[i, j]]

    time_start = time.time()

    delaround(*index_coords)
    mines_left = int(mines)
    cycles = 0
    paused = False
    no_update = True
    while True:
        if paused:
            event = pyg.event.get()
            if event:
                event = event[-1]
            else:
                event = pyg.event.Event(-1)
            if event.type == pyg.KEYDOWN and\
               event.dict['key'] in (pyg.K_p, pyg.K_SPACE):
                paused = not paused
            continue
        prev_tiles_cover = np.array(tiles_cover)

        # Optimization; reduces time spent

        rows_to_check = set()
        cols_to_check = set()

        for row in range(0, size_h):
            if list(tiles_cover[row]).count(tile_blank_up) > 0:
                rows_to_check = rows_to_check.union({row-1, row, row+1})

        transposed_tiles_cover = tiles_cover.transpose()
        for col in range(0, size_w):
            if list(transposed_tiles_cover[col]).count(tile_blank_up) > 0:
                cols_to_check = cols_to_check.union({col-1, col, col+1})

        # Goes through each uncovered tile
        for i in range(0, size_h):
            for j in range(0, size_w):
                if tiles_cover[i, j] not in (tile_blank_up, tile_mark):
                    if count_covered(i, j, mark=False) == 0:
                        continue
                    """Event setup"""
                    event_list = pyg.event.get()
                    if not event_list:
                        event_list = [pyg.event.Event(-1)]
                    for event in event_list:
                        if event.type == pyg.QUIT:
                            try:
                                pyg.quit()
                            except:
                                pass
                        elif wait > 0 and event.type == pyg.KEYDOWN and\
                                event.dict['key'] in (pyg.K_p, pyg.K_SPACE):
                            paused = not paused

                    """Cpu Marker"""
                    if wait > 0:
                        tiles_cover[i, j] = tile_cpumark
                        draw_cover()

                    """Count tiles around (i, j). If = tile  #, mark."""
                    if count_covered(i, j) == tiles[i, j]:
                        mark_around(i, j)
                    clear_tiles(i, j)

                    """Special Case 1"""
                    # testcase_1(i, j)

                    """Test Game Over"""
                    tiles_cover_list = list(tiles_cover.flatten())
                    blank_c = tiles_cover_list.count(tile_blank_up)
                    if blank_c == 0:
                        game_over = 2
                        tiles_cover[i, j] = pyg.Surface((0, 0))
                        break

                    if wait > 0:
                        if tiles_img[i, j] in tile_img_list[1:9]:
                            draw_img()
                            draw_cover()
                            update()
                            pyg.time.wait(wait)
                        area = pyg.Surface((screen_w, 70))
                        area.fill(WHITE)
                        screen.blit(area, (0, 0))
                        screen.blit(area, (0, screen_h-70))

                        cur_time = time.time()-time_start
                        write(screen,
                              'Time: '+str(int(cur_time)//60) + ':' +
                              str(int(cur_time) % 60).zfill(2) + '.' +
                              str(round(
                                  cur_time-int(cur_time), 2))[2:].zfill(2),
                              text_col, None, 28, screen_w//2-60, screen_h-50,
                              centered=False)

                        draw_mines_left()

                        tiles_cover[i, j] = pyg.Surface((0, 0))

            if game_over:
                break
        if not no_update:
            draw_img()
            draw_cover()
            update()
        same = True
        for row in range(0, len(tiles_cover)):
            for col in range(0, len(tiles_cover[0])):
                if tiles_cover[row, col] in (tile_blank_up, tile_mark):
                    if tiles_cover[row, col] != prev_tiles_cover[row, col]:
                        same = False
                else:
                    if prev_tiles_cover[row, col] in\
                       (tile_blank_up, tile_mark):
                        same = False
                if not same:
                    break
            if not same:
                break
        if game_over == 2:
            draw_img()
            draw_cover()
            write(screen, "Done.", BLACK, None, 28, screen_w//2, 35)
            update()
            break
        elif same:
            draw_img()
            draw_cover()
            write(screen,
                  "The CPU could not solve this Minesweeper." +
                  " Guessing or advanced deduction is needed.",
                  BLACK, None, 28, screen_w//2, 35)
            update()
            break

    button = pyg.Surface((100, 50))
    button_rect = pyg.Rect(screen_w-162, screen_h//2-75, 100, 50)
    button.fill(btn_col)
    screen.blit(button, (screen_w-162, screen_h//2-75))
    text_x = screen_w-162+button.get_width()//2
    text_y = screen_h//2-75+button.get_height()//2
    write(screen, 'Again?', text_col, None, 28, text_x, text_y)

    quit_btn = pyg.Surface((75, 50))
    quit_btn_rect = pyg.Rect(screen_w-150, screen_h//2+100, 75, 50)
    quit_btn.fill(quit_col)
    screen.blit(quit_btn, (screen_w-150, screen_h//2+100))
    quit_txt_x = screen_w-150+quit_btn.get_width()//2
    quit_txt_y = screen_h//2+100+quit_btn.get_height()//2
    write(screen, 'Quit?', text_col, None, 24, quit_txt_x, quit_txt_y)

    option_btn = pyg.Surface((100, 50))
    option_btn_rect = pyg.Rect(50, screen_h//2-25, 100, 50)
    option_btn.fill(option_col)
    screen.blit(option_btn, (50, screen_h//2-25))
    option_txt_x = 50+option_btn.get_width()//2
    option_txt_y = screen_h//2-25+option_btn.get_height()//2
    write(screen, 'Options', text_col, None, 26, option_txt_x, option_txt_y)
    update()
    while True:
        event = pyg.event.get()
        if event:
            event = event[0]
        else:
            event = pyg.event.Event(-1)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.dict['button'] == 1:
            pos = event.dict['pos']
            click = pyg.Rect(pos, (1, 1))
            if button_rect.colliderect(click):
                if record_time and end_time and end_time < record_time:
                    record_time = end_time
                elif record_time is None and end_time:
                    record_time = end_time
                cpu_main()
                break
            elif quit_btn_rect.colliderect(click):
                pyg.quit()
                break
            elif option_btn_rect.colliderect(click):
                options()
                break
        elif event.type == pyg.KEYDOWN and\
                event.dict['key'] in (pyg.K_r, pyg.K_RETURN):
            cpu_main()
        if loop > 0:
            if game_over == 2:
                times_done['Done'] += 1
                res = 'Done'
            elif same:
                times_done['Break'] += 1
                res = 'Break'
            print(res, 'Done:', times_done['Done'],
                  'Break:', times_done['Break'])
            pyg.time.wait(loop)
            cpu_main()


"""Options Menu"""


def opt_draw_tiles_cover():
    global size_w, size_h, tile_w, tile_h, opt_tiles_cover_img
    dest_x = screen_w//2 - (size_w*tile_w)//2
    dest_y = screen_h//2 - (size_h*tile_h)//2

    for y in opt_tiles_cover_img:
        for x in y:
            screen.blit(x, (dest_x, dest_y))
            dest_x += tile_w
        dest_y += tile_h
        dest_x = screen_w//2 - (size_w*tile_w)//2


def options():
    global size_w, size_h, tile_w, tile_h, mines,\
           opt_tiles_cover_img, show_destroy, cpu, wait,\
           mode, around, show_time

    def count_mines(x, y):
        global size_w, size_h, tiles2, around
        c = 0
        for dx, dy in around:
            if x+dx >= size_h or y+dy >= size_w or x+dx < 0 or y+dy < 0:
                continue
            elif tiles2[x+dx, y+dy] == 9:
                c += 1
        return c

    def set_mines():
        global size_w, size_h, tiles2, mines

        tiles2 = np.array([[0]*size_w]*size_h)

        mine_indices = random.sample(
            range(0, size_w*size_h), mines
            )  # Randomize mine placement

        """Mine placement"""
        for mine_index in range(len(mine_indices)):  # Loop though each mine
            index = mine_indices[mine_index]  # Record the index
            i = (index)//(size_w)  # Get the y-coordinate of the index
            j = (index) % size_w   # Get the x-coordinate of the index
            mine_indices[mine_index] = (i, j)  # Format as ordered pair
            tiles2[i, j] = 9  # Set the tile number to 9 (denotes mine)

        """Number of mines surrounding a tile"""
        for x in range(size_h):  # Loop though the vertical coordinates
            for y in range(size_w):  # Loop through the horizontal coordinates
                if tiles2[x, y] == 9:  # If the tile is a mine,
                    continue  # Skip this loop
                tiles2[x, y] = count_mines(x, y)
        pyg.event.pump()

    option = 1

    set_mines()

    # Board tile images
    opt_tiles_cover_img = np.array([[tile_img_list[0]]*size_w]*size_h)

    # Changes tile numbers to tile images with the corresponding numbers
    for i in range(len(tiles)):
        for j in range(len(tiles[i])):
            opt_tiles_cover_img[i, j] = tile_img_list[tiles2[i, j]]

    d = tile_img_list[17]
    o = tile_img_list[0]
    m = tile_img_list[16]
    running = True
    while running:
        clear()
        # Board tile images
        opt_tiles_cover_img = np.array([[tile_img_list[0]]*size_w]*size_h)

        # Changes tile numbers to tile images with the corresponding numbers
        for i in range(len(tiles2)):
            for j in range(len(tiles2[i])):
                opt_tiles_cover_img[i, j] = tile_img_list[tiles2[i, j]]

        # Mode explanation images
        mode_expl_back = np.array([[tile_img_list[0]]*5]*5)
        if mode == 1: # Normal
            mode_expl_img = np.array([[o, o, o, o, o],
                                      [o, d, d, d, o],
                                      [o, d, m, d, o],
                                      [o, d, d, d, o],
                                      [o, o, o, o, o]])
        elif mode == 2: # Knight's path
            mode_expl_img = np.array([[o, d, o, d, o],
                                      [d, o, o, o, d],
                                      [o, o, m, o, o],
                                      [d, o, o, o, d],
                                      [o, d, o, d, o]])
        elif mode == 3: # Orthogonal
            mode_expl_img = np.array([[o, o, o, o, o],
                                      [o, o, d, o, o],
                                      [o, d, m, d, o],
                                      [o, o, d, o, o],
                                      [o, o, o, o, o]])
        elif mode == 4: # Far orthogonal
            mode_expl_img = np.array([[o, o, d, o, o],
                                      [o, o, d, o, o],
                                      [d, d, m, d, d],
                                      [o, o, d, o, o],
                                      [o, o, d, o, o]])
        elif mode == 5: # Diagonal
            mode_expl_img = np.array([[o, o, o, o, o],
                                      [o, d, o, d, o],
                                      [o, o, m, o, o],
                                      [o, d, o, d, o],
                                      [o, o, o, o, o]])
        elif mode == 6: # Far diagonal
            mode_expl_img = np.array([[d, o, o, o, d],
                                      [o, d, o, d, o],
                                      [o, o, m, o, o],
                                      [o, d, o, d, o],
                                      [d, o, o, o, d]])

        resize_tiles()
        opt_draw_tiles_cover()
        write(screen, 'Options', text_col, None, 28, screen_w//2, 50)

        change_optn = pyg.Surface((150, 50))
        change_optn_rect = pyg.Rect(150, screen_h//2-75, 150, 50)
        change_optn.fill(change_optn_col)
        screen.blit(change_optn, (100, screen_h//2-75))
        text_x = 100+change_optn.get_width()//2
        text_y = screen_h//2-75+change_optn.get_height()//2
        write(screen, 'Change Option:', text_col, None, 26, text_x, text_y-50)

        again_optn = pyg.Surface((150, 50))
        again_optn_rect = pyg.Rect(150, screen_h//2+75, 150, 50)
        again_optn.fill(btn_col)
        screen.blit(again_optn, (100, screen_h//2+75))
        again_text_x = 100+again_optn.get_width()//2
        again_text_y = screen_h//2+75+again_optn.get_height()//2
        write(screen, 'Back', text_col, None, 26, again_text_x, again_text_y)

        up = pyg.Surface((25, 25))
        up_rect = pyg.Rect(screen_w-150, screen_h//2-38, 25, 25)
        up.fill(up_col)
        screen.blit(up, (screen_w-150, screen_h//2-38))
        up_text_x = screen_w-150+up.get_width()//2
        up_text_y = screen_h//2-38+up.get_height()//2
        write(screen, '+', text_col, None, 20, up_text_x, up_text_y)

        down = pyg.Surface((25, 25))
        down_rect = pyg.Rect(screen_w-150, screen_h//2+38, 25, 25)
        down.fill(up_col)
        screen.blit(down, (screen_w-150, screen_h//2+38))
        down_text_x = screen_w-150+down.get_width()//2
        down_text_y = screen_h//2+38+down.get_height()//2
        write(screen, '-', text_col, None, 20, down_text_x, down_text_y)

        if option == 1:
            write(screen, 'Grid width', text_col, None, 26, text_x, text_y)
            write(screen, str(size_w),
                  text_col, None, 28, screen_w-140, screen_h//2+10)
        elif option == 2:
            write(screen, 'Grid height', text_col, None, 26, text_x, text_y)
            write(screen, str(size_h),
                  text_col, None, 28, screen_w-140, screen_h//2+10)
        elif option == 3:
            write(screen, 'Mine number', text_col, None, 26, text_x, text_y)
            write(screen, str(mines),
                  text_col, None, 28, screen_w-140, screen_h//2+10)
        elif option == 4:
            write(screen, 'Show destroy', text_col, None, 26, text_x, text_y)
            write(screen, str(show_destroy),
                  text_col, None, 28, screen_w-140, screen_h//2+10)
        elif option == 5:
            write(screen, 'CPU', text_col, None, 26, text_x, text_y)
            write(screen, str(cpu),
                  text_col, None, 28, screen_w-140, screen_h//2+10)
        elif cpu and option == 6:
            write(screen, 'Wait', text_col, None, 26, text_x, text_y)
            write(screen, str(wait),
                  text_col, None, 28, screen_w-140, screen_h//2+10)
        elif option == 7:
            write(screen, 'Mode', text_col, None, 26, text_x, text_y)
            write(screen, modes_str[mode],
                  text_col, None, 28, screen_w-140, screen_h//2+10)

            # Draw mode explanation picture
            dest_x = screen_w-140-2.5*tile_w
            dest_y = screen_h//2-150-2.5*tile_h
            for i in range(5):
                for j in range(5):
                    screen.blit(mode_expl_back[j, i], (dest_x, dest_y))
                    screen.blit(mode_expl_img[j, i], (dest_x, dest_y))
                    dest_x += tile_w
                dest_y += tile_h
                dest_x = screen_w-140-2.5*tile_w
        elif option == 8:
            write(screen, 'Show Time', text_col, None, 26, text_x, text_y)
            write(screen, str(show_time),
                  text_col, None, 28, screen_w-140, screen_h//2+10)
        else:
            option = 1

        event = pyg.event.get()
        if event:
            event = event[0]
        else:
            event = pyg.event.Event(-1)

        if event.type == pyg.QUIT:
            running = False
            break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.dict['button'] == 1:
            pos = event.dict['pos']
            click = pyg.Rect(pos, (1, 1))
            if change_optn_rect.colliderect(click):
                option += 1
                if not cpu and option == 6:  # Skip wait option if cpu enabled
                    option = 7
                elif option == 9:  # Loop around
                    option = 1
            elif up_rect.colliderect(click):
                if option == 1:  # Width
                    if (size_w+1)*size_h > mines-25:
                        size_w += 1
                        set_mines()
                elif option == 2:  # Height
                    if size_w*(size_h+1) > mines-25:
                        size_h += 1
                        set_mines()
                elif option == 3:  # Mines
                    if size_w*size_h > mines-24:
                        mines += 1
                        set_mines()
                elif option == 4:  # Show Destroy
                    show_destroy = not show_destroy
                elif option == 5:  # CPU
                    cpu = not cpu
                elif cpu and option == 6:  # Wait
                    wait += 1
                elif option == 7:  # Mode
                    mode += 1
                    if mode > max(modes_str):
                        mode = 1
                elif option == 8:
                    show_time = not show_time
            elif down_rect.colliderect(click):
                if option == 1:
                    if size_w-1 > 0 and (size_w-1)*size_h > mines+25:
                        size_w -= 1
                        set_mines()
                elif option == 2:
                    if size_h-1 > 0 and size_w*(size_h-1) > mines+25:
                        size_h -= 1
                        set_mines()
                elif option == 3:
                    if mines-1 > 0 and size_w*size_h > mines+24:
                        mines -= 1
                        set_mines()
                elif option == 4:
                    show_destroy = not show_destroy
                elif option == 5:
                    cpu = not cpu
                elif cpu and option == 6:
                    if wait > 0:
                        wait -= 1
                elif option == 7:
                    mode -= 1
                    if mode < 1:
                        mode = max(modes_str)
                elif option == 8:
                    show_time = not show_time
            elif again_optn_rect.colliderect(click):
                if cpu:
                    cpu_main()
                elif not cpu:
                    main()
                return

        keys_pressed = pyg.key.get_pressed()
        if keys_pressed[pyg.K_UP]:
            if option == 1:
                if (size_w+1)*size_h > mines+25:
                    size_w += 1
                    set_mines()
            elif option == 2:
                if size_w*(size_h+1) > mines+25:
                    size_h += 1
                    set_mines()
            elif option == 3:
                if size_w*size_h > mines+26:
                    mines += 1
                    set_mines()
            elif option == 4:
                show_destroy = not show_destroy
            elif option == 5:
                cpu = not cpu
            elif option == 6:
                wait += 1
            elif option == 7:
                mode += 1
                if mode > max(modes_str):
                    mode = 1
                set_mode()
            elif option == 8:
                show_time = not show_time
        elif keys_pressed[pyg.K_DOWN]:
            if option == 1:
                if size_w-1 > 0 and (size_w-1)*size_h > mines+25:
                    size_w -= 1
                    set_mines()
            elif option == 2:
                if size_h-1 > 0 and size_w*(size_h-1) > mines+25:
                    size_h -= 1
                    set_mines()
            elif option == 3:
                if mines-1 > 0 and size_w*size_h > mines+24:
                    mines -= 1
                    set_mines()
            elif option == 4:
                show_destroy = not show_destroy
            elif option == 5:
                cpu = not cpu
            elif option == 6:
                if wait > 0:
                    wait -= 1
            elif option == 7:
                mode -= 1
                if mode < 1:
                    mode = max(modes_str)
                set_mode()
            elif option == 8:
                show_time = not show_time
        update()
    if not running:
        pyg.quit()


record_time = None
times_done = {'Done': 0, 'Break': 0}
loop = 0
if not cpu:
    main()
elif cpu:
    cpu_main()
