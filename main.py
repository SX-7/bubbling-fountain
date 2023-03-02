from io import BytesIO
import math
import sys
import requests
from PIL import Image
from PIL import ImageDraw
from PIL import UnidentifiedImageError
from PIL import ImageSequence
import curses
import numpy
try:
    source_image = Image.open(BytesIO(requests.get(sys.argv[1]).content))

except IndexError:
    print("URL adress has not been provided")
    sys.exit(-1)
except UnidentifiedImageError:
    print("File at the URL adress is not an image file")
    sys.exit(-2)
except:
    print("Error while parsing URL, or retrieving content")
    sys.exit(-3)

pointed_position = []


def main(stdscr):
    # Setup once
    curses.curs_set(0)
    # 0th one is unchangeable, last one is reserved for marker
    color_palette_size = curses.COLORS-3
    stdscr.clear()
    stdscr.refresh()
    thumbnail = source_image.resize(
        (stdscr.getmaxyx()[1], stdscr.getmaxyx()[0])).quantize(color_palette_size)
    # ensuring that we don't create unnecesary amount of colors
    color_palette_size = len(thumbnail.getcolors())
    thumbnail_array = numpy.array(thumbnail)
    # initialize colors at positions 1-(COLORS-2) in curses
    fixed_palette = thumbnail.getpalette()[0:3*color_palette_size]
    for iterator in range(0, color_palette_size*3, 3):
        palette_iterator = int((iterator/3)+1)
        curses.init_color(palette_iterator, int(fixed_palette[iterator]/255*1000), int(
            fixed_palette[iterator+1]/255*1000), int(fixed_palette[iterator+2]/255*1000))
        curses.init_pair(palette_iterator, palette_iterator, palette_iterator)
    # cursor color set
    curses.init_color(color_palette_size+1, 1000, 0, 0)
    curses.init_color(color_palette_size+2, 0, 1000, 0)
    curses.init_pair(color_palette_size+1,
                     color_palette_size+1, color_palette_size+2)

    # Run in loop
    position_set = False
    cursor_position_y = int((thumbnail_array.shape[0]-1)/2)
    cursor_position_x = int((thumbnail_array.shape[1]-1)/2)
    while not position_set:
        stdscr.clear()
        # Draw image - yeah, I know the x and y are inverted
        for iterator_x in range(thumbnail_array.shape[0]-1):
            for iterator_y in range(thumbnail_array.shape[1]-1):
                stdscr.addstr(iterator_x, iterator_y, "#", curses.color_pair(
                    thumbnail_array[iterator_x, iterator_y]+1))
        # Draw cursor
        stdscr.addstr(cursor_position_y, cursor_position_x, "X",
                      curses.color_pair(color_palette_size+1))
        stdscr.refresh()
        # Get command
        key = stdscr.getkey()
        # Bleeding edge technology - limit at borders
        match key:
            case "KEY_LEFT":
                if not cursor_position_x == 0:
                    cursor_position_x = cursor_position_x-1
            case "KEY_RIGHT":
                if not cursor_position_x == thumbnail_array.shape[1]-2:
                    cursor_position_x = cursor_position_x+1
            case "KEY_UP":
                if not cursor_position_y == 0:
                    cursor_position_y = cursor_position_y-1
            case "KEY_DOWN":
                if not cursor_position_y == thumbnail_array.shape[0]-2:
                    cursor_position_y = cursor_position_y+1
            case " ":
                pointed_position.append(
                    cursor_position_x/(thumbnail_array.shape[1]-2))
                pointed_position.append(
                    cursor_position_y/(thumbnail_array.shape[0]-2))
                position_set = True
            case _:
                pass
    # Repeat it for direction (along top line), and height
    position_set = False
    director_position_x = int((thumbnail_array.shape[1]-1)/2)
    director_position_y = int(
        pointed_position[1]*(thumbnail_array.shape[0]-2)/2)
    while not position_set:
        stdscr.clear()
        for iterator_x in range(thumbnail_array.shape[0]-1):
            for iterator_y in range(thumbnail_array.shape[1]-1):
                stdscr.addstr(iterator_x, iterator_y, "#", curses.color_pair(
                    thumbnail_array[iterator_x, iterator_y]+1))
        # we have to draw the cursor *with* the line outgoing from the previous pos
        # make a list of coordinates that'll be used to draw, arbitrairly 10
        marker_positions = []
        marker_positions_direction_vector = ((pointed_position[1]*(thumbnail_array.shape[0]-2))/10, ((
            pointed_position[0]*(thumbnail_array.shape[1]-2))-director_position_x)/10)
        for offset_index in range(0, 11):
            marker_positions.append(
                (marker_positions_direction_vector[0]*offset_index, marker_positions_direction_vector[1]*offset_index))
        for current_marker_offset_vector in marker_positions:
            stdscr.addstr(int(current_marker_offset_vector[0]), int(current_marker_offset_vector[1]+director_position_x), "X",
                          curses.color_pair(color_palette_size+1))
        # now draw horizontal line for speechbubble height
        for line_x in range(thumbnail_array.shape[1]-1):
            stdscr.addstr(director_position_y, line_x, "X",
                          curses.color_pair(color_palette_size+1))
        stdscr.refresh()
        key = stdscr.getkey()
        match key:
            case "KEY_LEFT":
                if not director_position_x == 0:
                    director_position_x = director_position_x-1
            case "KEY_RIGHT":
                if not director_position_x == thumbnail_array.shape[1]-2:
                    director_position_x = director_position_x+1
            case "KEY_UP":
                if not director_position_y == 0:
                    director_position_y = director_position_y-1
            case "KEY_DOWN":
                if not director_position_y == int(pointed_position[1]*(thumbnail_array.shape[0]-2)):
                    director_position_y = director_position_y+1
            case " ":
                pointed_position.append(
                    director_position_x/(thumbnail_array.shape[1]-2))
                pointed_position.append(
                    director_position_y/(thumbnail_array.shape[0]-2))
                position_set = True
            case _:
                pass


output_frames = []
frame_length = []

# Get positions
curses.wrapper(main)
# Edit the image in accordance to info retrieved from user
for frame in ImageSequence.Iterator(source_image):
    # higher level overview - make a speechbubble from pieslice and ellipse, but inverted - it's a mask for tranparency layer
    # 1k x 1k should be enough for most applications, it's resized later to the actual image
    bubble_mask = Image.new("RGBA", (1000, 1000), (255, 255, 255, 255))
    bubble_mask_drawable = ImageDraw.Draw(bubble_mask)
    # Make it better responsive
    # Calculate the angle
    pointer_angle = 270 + math.degrees(math.atan((pointed_position[2]-pointed_position[0])/pointed_position[1]))
    bubble_mask_drawable.pieslice(xy=(
        -1000+1000*pointed_position[0], -1000+1000*pointed_position[1], 1000+1000*pointed_position[0], 1000+1000*pointed_position[1]), start=pointer_angle-5, end=pointer_angle+5, fill=(255, 255, 255, 0))
    bubble_mask_drawable.ellipse(
        xy=(-500, -1000, 1500, 1000*pointed_position[3]), fill=(255, 255, 255, 0))
    bubble_mask = bubble_mask.resize(
        (source_image.width, source_image.height), resample=Image.Resampling.NEAREST)
    transparent = Image.new(
        "RGBA", (source_image.width, source_image.height), (255, 255, 255, 0))
    output_frames.append(Image.composite(frame, transparent, bubble_mask))
    try:
        frame_length.append(frame.info['duration'])
    except:
        frame_length.append(0)

# how to handle output? termux's an issue
output_frames[0].save("res.gif", save_all=True, append_images=output_frames[1:],
                      loop=0, duration=frame_length, optimize=True, disposal=2)
