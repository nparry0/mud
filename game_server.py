import threading
import json
import os
import mud_utils
from pprint import pprint
from scipy.sparse import coo_matrix
import cPickle
import logging

class Room(object):
    def __init__(self, name, desc, directions):
        self.name = name
        self.desc = desc
        self.directions = directions
        self.lock = threading.Lock()
        self.characters = {}

    def add_character(self, character):
        with self.lock:
            self.characters[character.name] = character

    def remove_character(self, character):
        with self.lock:
            del self.characters[character.name]

    def serialize(self):
        return (self.name, self.desc, self.directions)

    def deserialize(self, data):
        self.name, self.desc, self.directions = data

    def get_info(self):
        with self.lock:
            return (self.name, self.desc, self.directions, self.characters.keys())


class Map(object):
    def __init__(self, map_file):
        self.rooms = {}
        self.map_file = map_file

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
                    self.rooms[location] = room
            except EOFError: 
                pass

    def get_room(self, x, y):
        if (x,y) in self.rooms:
            return self.rooms[(x,y)]
        return None

    def add_character(self, character, location):
        if location in self.rooms:
            self.rooms[location].add_character(character)

    def remove_character(self, character):
        if character.location in self.rooms:
            self.rooms[character.location].remove_character(character)



class GameServer(object):
    def __init__(self, map):
        self.players = {};
        self.players_lock = threading.Lock()
        self.map = Map(map)
        self.map.load()
        log = logging.getLogger()
        log.info("Map initialized from '" + self.map.map_file + "'.  Loaded " + str(len(self.map.rooms)) + " rooms")

    def add_player(self, player):
        with self.players_lock:
            self.players[player.name] = player
        self.map.add_character(player, player.location)

    def remove_player(self, player):
        with self.players_lock:
            del self.players[player.name]

    def get_players(self):
        with self.players_lock:
            list = self.players.keys()
        return list

    def get_room_info(self, location):
        if location in self.map.rooms:
            room = self.map.rooms[location];
            return room.get_info()

    def change_location(self, player, direction):
        if direction in self.map.rooms[player.location].directions:
            if direction == 'n':  
                new_location = (player.location[0], player.location[1]+1)
            elif direction == 's':  
                new_location = (player.location[0], player.location[1]-1)
            elif direction == 'e':  
                new_location = (player.location[0]+1, player.location[1])
            elif direction == 'w':  
                new_location = (player.location[0]-1, player.location[1])

            if new_location in self.map.rooms:
                self.map.remove_character(player)
                self.map.add_character(player, new_location)
                return new_location
        return None
