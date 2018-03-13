import threading
import cPickle
import logging
from character import NPC, Player
import re


class Room(object):

    SPAWN_POINT_TYPE_NPC = 0
    # Add more types of spawn points.  Equipment, etc

    def __init__(self, name, desc, directions):
        self.name = name
        self.desc = desc
        self.directions = directions
        self.spawn_points = []
        self.lock = threading.RLock()
        self.characters = {}

    def add_character(self, character):
        with self.lock:
            self.characters[character.name] = character

    def remove_character(self, character):
        with self.lock:
            del self.characters[character.name]

    def serialize(self):
        return self.name, self.desc, self.directions, self.spawn_points

    def deserialize(self, data):
        self.name, self.desc, self.directions, self.spawn_points = data

    def get_info(self):
        with self.lock:
            return self.name, self.desc, self.directions, self.characters

    def broadcast_to_players(self, actor, msg):
        for name, character in self.characters.iteritems():
            if isinstance(character, Player):
                if actor is None or name != actor.name:
                    character.net_handler.writemessage(msg)
                else:
                    character.net_handler.writeresponse(msg)

    def add_action(self, action):
        # If there's a target, make sure that target is there first
        if action.target is not None:
            targets = {name: value for name, value in self.characters.iteritems() if re.match(action.target, name, re.I)}
            if len(targets) >= 1:  # TODO: Select the 2nd one by adding a "2" to the target
                action.target_character = targets.itervalues().next()
            else:
                action.actor.net_handler.writemessage(action.zero_target_error_msg())
                return

        # Broadcast pre-msg to tell players what is about to happen
        pre_msg = action.pre_msg()
        if pre_msg is not None:
            self.broadcast_to_players(action.actor, pre_msg)

        # If this action will happen in the future, set a timer.  Otherwise, do it now
        if action.time > 0:
            t = threading.Timer(action.time, self.exec_action, [action.actor, action], {})
            t.start()
        else:
            self.exec_action(action.actor, action)

    def exec_action(self, actor, action):
        with self.lock:
            # Skip if the target has left the room
            if action.target_character and action.target_character.name not in self.characters:
                return
            # Skip if the actor was killed between starting and executing this action
            if actor.hp <= 0:
                return

            # Do it
            post_msg = action.execute()

            # See if anyone died
            if action.target_character and action.target_character.hp <= 0:
                self.characters.pop(action.target_character.name, None)

            # TODO: could this hold the lock for too long?
            if post_msg is not None:
                self.broadcast_to_players(actor, post_msg)

            # If the action target is an NPC, their aggro will have been inc'd in action.execute().
            # This gives the NPC the ability to react
            # TODO: Not sure this is the best place for an NPC reaction.  It assumes the player is attacking
            if action.target_character and action.target_character.hp > 0 and isinstance(action.target_character, NPC):
                action.target_character.act()


class Map(object):
    def __init__(self, map_file, game_server):
        self.rooms = {}
        self.map_file = map_file
        self.num_spawn_points = 0
        self.game_server = game_server

    def save(self):
        with open(self.map_file, 'wb') as out_file:
            for location, room in self.rooms.iteritems():
                cPickle.dump((location, room.serialize()), out_file, cPickle.HIGHEST_PROTOCOL)

    def load(self):
        with open(self.map_file, 'rb') as in_file:
            try:
                while 1:
                    location, room_data = cPickle.load(in_file)
                    room = Room(None, None, None)
                    room.deserialize(room_data)
                    for spawn_point in room.spawn_points:
                        if spawn_point["type"] == Room.SPAWN_POINT_TYPE_NPC:
                            npc = NPC(spawn_point["name"],
                                      spawn_point["hp"],
                                      spawn_point["mp"],
                                      location,
                                      spawn_point["aggro"],
                                      self.game_server)
                            room.add_character(npc)
                        self.num_spawn_points += 1
                    self.rooms[location] = room
            except EOFError: 
                pass

    def get_room(self, x, y, z):
        if (x,y,z) in self.rooms:
            return self.rooms[(x,y,z)]
        return None

    def add_character(self, character, location):
        if location in self.rooms:
            self.rooms[location].add_character(character)

    def remove_character(self, character):
        if character.location in self.rooms:
            self.rooms[character.location].remove_character(character)

    def add_action(self, action):
        if action.location in self.rooms:
            self.rooms[action.location].add_action(action)


class GameServer(object):
    def __init__(self, map):
        self.players = {}
        self.players_lock = threading.Lock()
        self.map = Map(map, self)
        self.map.load()
        log = logging.getLogger()
        log.info("Map initialized from '%s'.  Loaded %d rooms with %d spawn points" % (self.map.map_file, len(self.map.rooms), self.map.num_spawn_points))

    def add_player(self, player):
        with self.players_lock:
            self.players[player.name] = player
        self.map.add_character(player, player.location)

    def remove_player(self, player):
        with self.players_lock:
            del self.players[player.name]

    def get_players(self):
        with self.players_lock:
            players = self.players.keys()
        return players

    def get_room_info(self, location):
        if location in self.map.rooms:
            room = self.map.rooms[location];
            return room.get_info()

    def change_location(self, player, direction):
        if direction in self.map.rooms[player.location].directions:
            if direction == 'n':  
                new_location = (player.location[0],     player.location[1]+1,   player.location[2])
            if direction == 'ne':
                new_location = (player.location[0]+1,   player.location[1]+1,   player.location[2])
            if direction == 'nw':
                new_location = (player.location[0]-1,   player.location[1]+1,   player.location[2])
            elif direction == 's':
                new_location = (player.location[0],     player.location[1]-1,   player.location[2])
            elif direction == 'se':
                new_location = (player.location[0]+1,   player.location[1]-1,   player.location[2])
            elif direction == 'sw':
                new_location = (player.location[0]-1,   player.location[1]-1,   player.location[2])
            elif direction == 'e':
                new_location = (player.location[0]+1,   player.location[1],     player.location[2])
            elif direction == 'w':  
                new_location = (player.location[0]-1,   player.location[1],     player.location[2])
            elif direction == 'u':
                new_location = (player.location[0],     player.location[1],     player.location[2]+1)
            elif direction == 'd':
                new_location = (player.location[0],     player.location[1],     player.location[2]-1)

            if new_location in self.map.rooms:
                self.map.remove_character(player)
                self.map.add_character(player, new_location)
                return new_location
        return None

    def add_action(self, action):
        self.map.add_action(action)
