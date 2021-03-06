from game_server import Map, Room
import argparse
import curses
import time
from character import NPC

parser = argparse.ArgumentParser()
parser.add_argument("--map", type=str, default="mud.map", help="Map file")

args = parser.parse_args()

map = Map(args.map, None)
row = 0
col = 0
level = 0

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

def create_spawn():
    spawn_points = []
    num = int(prompt("=== How many spawn points? ===", ""))
    for x in range(0, num):
        type = int(prompt("=== Spawn Point %d: Type (%d=npc) ===" % (x+1, Room.SPAWN_POINT_TYPE_NPC), ""))
        if type == Room.SPAWN_POINT_TYPE_NPC:
            spawn_point = {}
            spawn_point['type'] = type
            spawn_point['name'] = prompt("=== Spawn Point %d: NPC Name ===" % (x+1), "")
            spawn_point['hp'] = int(prompt("=== Spawn Point %d: NPC HP ===" % (x+1), ""))
            spawn_point['mp'] = int(prompt("=== Spawn Point %d: NPC MP ===" % (x+1), ""))
            spawn_point['aggro'] = \
                int(prompt("=== Spawn Point %d: NPC Aggro (%d=friend, %d=neutral %d=hostile) ===" %
                           (x+1, NPC.AGGRO_FRIENDLY, NPC.AGGRO_NEUTRAL, NPC.AGGRO_HOSTILE), ""))
            spawn_point['time'] = int(prompt("=== Spawn Point %d: Respawn time (seconds) ===" % (x+1), ""))
        spawn_points.append(spawn_point)
    return spawn_points

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
    screen.addstr(1, 1, "Row:%d Col:%d Level:%d | hjkl/arrows:move u:up d:down enter:new del:delete 1:name 2:desc 3:dirs 4:addspawn 5:delspawn s:save q:quit" % (row, col, level))

    # Print the whole map
    for x in range(2, width-2):
        for y in range(2, height-20):
            room = map.get_room(col-((width-4)/2-x), row-(y-(height-22)/2), level)
            if room is None:
                screen.addstr(y, x, " ")
            else:
                screen.addstr(y, x, "X")
    screen.addstr((height-22)/2, (width-4)/2, "+");

    # Print the room details
    room = map.get_room(col, row, level)
    if room is not None:
        screen.addstr(height-18, 1, "Room: " + room.name)
        screen.addstr(height-17, 1, "Desc: " + room.desc)
        if "u" in map.rooms[(col, row, level)].directions:
            screen.addstr(height-11, 10, "u")
        if "n" in map.rooms[(col, row, level)].directions:
            screen.addstr(height-10, 10, "n")
        if "ne" in map.rooms[(col, row, level)].directions:
            screen.addstr(height-9, 12, "ne")
        if "e" in map.rooms[(col, row, level)].directions:
            screen.addstr(height-8, 14, "e")
        if "se" in map.rooms[(col, row, level)].directions:
            screen.addstr(height-7, 12, "se")
        if "s" in map.rooms[(col, row, level)].directions:
            screen.addstr(height-6, 10, "s")
        if "d" in map.rooms[(col, row, level)].directions:
            screen.addstr(height-5, 10, "d")
        if "sw" in map.rooms[(col, row, level)].directions:
            screen.addstr(height-7, 8, "sw")
        if "w" in map.rooms[(col, row, level)].directions:
            screen.addstr(height-8, 6, "w")
        if "nw" in map.rooms[(col, row, level)].directions:
            screen.addstr(height-9, 8, "nw")

        i=0
        for spawn_point in room.spawn_points:
            i += 1
            if spawn_point["type"] == Room.SPAWN_POINT_TYPE_NPC:
                msg = "NPC Spawn:%s HP:%d MP:%d Aggro:%d time:%d" % \
                      (spawn_point["name"], spawn_point["hp"], spawn_point["mp"], spawn_point["aggro"], spawn_point["time"])
            screen.addstr(height-11+i, 30, msg)


    # Get a character and do something about it
    char = screen.getch()

    if char == ord('s'):
        map.save()
        screen.addstr(2, 1, "Saved: " + args.map)
        screen.refresh()
        time.sleep(2)
    elif char == curses.KEY_ENTER or char == 10:
        if (col, row, level) not in map.rooms:
            map.rooms[(col, row, level)] = create_room()
    elif char == 127: # backspace
        if prompt("=== Delete room, are you sure? ===", "") == "yes" and (col, row, level) in map.rooms:
            del map.rooms[(col, row, level)];
    elif char == ord('1'):
        if (col, row, level) in map.rooms:
            map.rooms[(col, row, level)].name = prompt("=== Name ===", map.rooms[(col, row, level)].name)
    elif char == ord('2'):
        if (col, row, level) in map.rooms:
            map.rooms[(col, row, level)].desc = prompt("=== Desc ===", map.rooms[(col, row, level)].desc)
    elif char == ord('3'):
        if (col, row, level) in map.rooms:
            map.rooms[(col, row, level)].directions = prompt("=== Directions ===", "").split(" ");
    elif char == ord('4'):
        if (col, row, level) in map.rooms:
            map.rooms[(col, row, level)].spawn_points = create_spawn()
    elif char == ord('5'):
        if prompt("=== Delete spawn points, are you sure? ===", "") == "yes" and (col, row, level) in map.rooms:
            map.rooms[(col, row, level)].spawn_points = []
    elif char == curses.KEY_RIGHT or char == 67 or char == ord('l'):
        col = col+1
    elif char == curses.KEY_LEFT or char == 68 or char == ord('h'):
        col = col-1
    elif char == curses.KEY_UP or char == 65 or char == ord('k'):
        row = row+1
    elif char == curses.KEY_DOWN or char == 66 or char == ord('j'):
        row = row-1
    elif char == ord('u'):
        level = level+1
    elif char == ord('d'):
        level = level-1
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
