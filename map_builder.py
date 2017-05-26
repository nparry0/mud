from game_server import Map, Room
import argparse
from os import system
import curses
from curses.textpad import Textbox, rectangle
import time

parser = argparse.ArgumentParser()
parser.add_argument("--map", type=str, default="mud.map", help="Map file")

args = parser.parse_args()

map = Map(args.map)
row = 0
col = 0

def prompt(prompt_string, old_string):
    screen.clear()
    screen.border(0)
    screen.addstr(2, 2, prompt_string)
    screen.refresh()
    curses.curs_set(1)
    if old_string:
        screen.addstr(4, 2, "Old: " + old_string)
    input = screen.getstr(6, 2)
    curses.curs_set(0)
    return input

def create_room():
    name = prompt("=== Name ===", "");
    desc = prompt("=== Desc ===", "");
    return Room(name, desc, [])

char = 0

screen = curses.initscr()
curses.start_color()
curses.curs_set(0)

try:
    map.load()
except Exception, e:
    screen.addstr(1, 1, "Can't load " + args.map + " :" + str(e));
    screen.refresh()
    time.sleep(2)

while char != ord('q'):
    height,width = screen.getmaxyx()

    screen.clear()
    screen.refresh()
    screen.border(0)
    screen.addstr(1, 1, "Row:" + str(row) + " Col:" + str(col) + "  enter:new del:delete 1:name 2:desc 3:dirs s:save q:quit")

    # Print the whole map
    for x in range(2, width-2):
        for y in range(2, height-20):
            room = map.get_room(col-((width-4)/2-x), row-(y-(height-22)/2))
            if room is None:
                screen.addstr(y, x, " ")
            else:
                screen.addstr(y, x, "X")
    screen.addstr((height-22)/2, (width-4)/2, "+");

    # Print the room details
    room = map.get_room(col, row)
    if room is not None:
        screen.addstr(height-18, 1, "Room: " + room.name)
        screen.addstr(height-17, 1, "Desc: " + room.desc)
        if "n" in map.rooms[(col, row)].directions:
            screen.addstr(height-10, 10, "n")
        if "ne" in map.rooms[(col, row)].directions:
            screen.addstr(height-9, 12, "ne")
        if "e" in map.rooms[(col, row)].directions:
            screen.addstr(height-8, 14, "e")
        if "se" in map.rooms[(col, row)].directions:
            screen.addstr(height-7, 12, "se")
        if "s" in map.rooms[(col, row)].directions:
            screen.addstr(height-6, 10, "s")
        if "sw" in map.rooms[(col, row)].directions:
            screen.addstr(height-7, 8, "sw")
        if "w" in map.rooms[(col, row)].directions:
            screen.addstr(height-8, 6, "w")
        if "nw" in map.rooms[(col, row)].directions:
            screen.addstr(height-9, 8, "nw")

    # Get a character and do something about it
    char = screen.getch()

    if char == ord('s'):
        map.save()
        screen.addstr(2, 1, "Saved: " + args.map)
        screen.refresh()
        time.sleep(2)
    elif char == curses.KEY_ENTER or char == 10:
        if (col, row) not in map.rooms:
            map.rooms[(col, row)] = create_room()
    elif char == 127: # backspace
        if (col, row) in map.rooms:
            del map.rooms[(col, row)];
    elif char == ord('1'):
        if (col, row) in map.rooms:
            map.rooms[(col, row)].name = prompt("=== Name ===", map.rooms[(col, row)].name)
    elif char == ord('2'):
        if (col, row) in map.rooms:
            map.rooms[(col, row)].desc = prompt("=== Desc ===", map.rooms[(col, row)].desc)
    elif char == ord('3'):
        if (col, row) in map.rooms:
            map.rooms[(col, row)].directions = prompt("=== Directions ===", "").split(" ");
    elif char == curses.KEY_RIGHT or char == 67 or char == ord('l'):
        col = col+1
    elif char == curses.KEY_LEFT or char == 68 or char == ord('h'):
        col = col-1
    elif char == curses.KEY_UP or char == 65 or char == ord('k'):
        row = row+1
    elif char == curses.KEY_DOWN or char == 66 or char == ord('j'):
        row = row-1
    elif char == ord('q'):
        map.save()
        screen.addstr(2, 1, "Saved: " + args.map)
        screen.refresh()
        time.sleep(2)
#    else:
#        screen.addstr(2, 1, "Unknown key: " + str(char))
#        screen.refresh()
#        time.sleep(1)

curses.endwin()
