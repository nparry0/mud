import cPickle
import os.path
import hashlib, uuid

# TODO: load/save should not include the player_dir
# TODO: Create Saveable class, for player, pass, and map?  include version?

class Password(object):
    def __init__(self, name, player_dir):
        self.name = name
        self.hash = ""
        self.salt = ""
        self.player_dir = player_dir

    def do_hash(self, password, salt):
        return hashlib.sha512(password + salt).hexdigest()

    def load(self):
        with open(self.player_dir + self.name + '.pwd', 'rb') as in_file:
            self.name, self.hash, self.salt = cPickle.load(in_file)

    def save(self, password):
        # TODO: Atomic save, by rotating old files?
        self.salt = uuid.uuid4().hex;
        self.hash = self.do_hash(password, self.salt)
        with open(self.player_dir + self.name + '.pwd', 'wb') as out_file:
            cPickle.dump((self.name, self.hash, self.salt), out_file, cPickle.HIGHEST_PROTOCOL)

    def check(self, password):
        return self.hash == self.do_hash(password, self.salt)


class Character(object):
    def __init__(self, name, hp, mp, location):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.location = location


class NPC(Character):

    AGGRO_FRIENDLY = 0
    AGGRO_NEUTRAL = 1
    AGGRO_HOSTILE = 2

    def __init__(self, name, hp, mp, location, aggro):
        Character.__init__(self, name, hp, mp, location)
        self.aggro = aggro


class Player(Character):
    def __init__(self, name, player_dir, net_handler):
        Character.__init__(self, name, 10, 10, (0,0,0))
        self.player_dir = player_dir
        self.net_handler = net_handler

    def serialize(self):
        return self.name, self.hp, self.mp, self.location

    def deserialize(self, data):
        self.name, self.hp, self.mp, self.location = data

    def save(self):
        # TODO: Atomic pickle, by rotating old pickle files?
        with open(self.player_dir + self.name + '.save', 'wb') as out_file:
            cPickle.dump(self.serialize(), out_file, cPickle.HIGHEST_PROTOCOL)

    def load(self):
        with open(self.player_dir + self.name + '.save', 'rb') as in_file:
            self.deserialize(cPickle.load(in_file))


def player_exists(name, player_dir):
    return os.path.isfile(player_dir + name + '.save') 
