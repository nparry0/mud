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

    def mod_hp(self, hp):
        self.hp += hp
        if self.hp < 0:
            self.hp = 0


class NPC(Character):

    AGGRO_FRIENDLY = 0
    AGGRO_NEUTRAL = 1
    AGGRO_HOSTILE = 2

    def __init__(self, name, hp, mp, location, aggro, game_server):
        Character.__init__(self, name, hp, mp, location)
        self.aggro = aggro
        self.engaged = None  # Character this NPC is fighting
        self.game_server = game_server

    def act(self):
        # 1) If engaged, fight that character
        if self.engaged is not None:
            self.game_server.add_action(Action(self, None, self.engaged, Action.ACTION_TYPE_ATTACK, {}))

        # 2) If not engaged, find someone to fight if hostile
        #elif self.AGGRO_HOSTILE:


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
        self.net_handler.update_prompt()

    def load(self):
        with open(self.player_dir + self.name + '.save', 'rb') as in_file:
            self.deserialize(cPickle.load(in_file))


def player_exists(name, player_dir):
    return os.path.isfile(player_dir + name + '.save') 


class Action(object):

    ACTION_TYPE_SAY = 0
    ACTION_TYPE_ATTACK = 1

    def __init__(self, actor, target, target_character, type, kwargs):
        self.actor = actor
        self.target = target
        self.target_character = target_character
        self.location = actor.location
        self.type = type
        self.kwargs = kwargs
        self.time = 0
        if self.type == self.ACTION_TYPE_ATTACK:
            self.time = 1.0  # TODO: Make the time actually dependent on the actor (e.g. actor.get_attack_speed())

    def pre_msg(self):
        if self.time <= 0:
            return None
        elif self.type == self.ACTION_TYPE_SAY:
            return "%s prepares to speak..." % self.actor.name
        elif self.type == self.ACTION_TYPE_ATTACK:
            return "%s makes ready their weapon..." % self.actor.name

    # Returns the message of what happened.  Assumes the target exists.
    def execute(self):
        if self.type == self.ACTION_TYPE_SAY:
            return "%s says '%s'" % (self.actor.name, self.kwargs["msg"])

        elif self.type == self.ACTION_TYPE_ATTACK:

            damage = 1
            self.target_character.mod_hp(-damage)

            # TODO: Put this back so that hp-- is saved
            #if isinstance(self.target_character, Player):
                #self.target_character.save()
            if isinstance(self.target_character, NPC) and self.target_character.hp > 0:
                self.target_character.aggro = NPC.AGGRO_HOSTILE
                self.target_character.engaged = self.actor

            msg = "%s strikes %s for %d damage" % (self.actor.name, self.target_character.name, damage)
            if self.target_character.hp <= 0:
                msg += "...and %s is slain." % self.target_character.name
            return msg

    def zero_target_error_msg(self):
        if self.type == self.ACTION_TYPE_ATTACK:
            return "'%s' is not something you can attack" % self.target


class Stat(object):

    # Base stats
    STAT_STRENGTH = 0
    STAT_SPEED = 1
    STAT_INTELLIGENCE = 2

    # Secondary stats
    STAT_MELEE = 10

    STAT_RANGED = 20

    STAT_CAST_FLAME = 30

    # Name of the stat
    names = {
        STAT_STRENGTH:          "Strength",
        STAT_SPEED:             "Speed",
        STAT_INTELLIGENCE:      "Intelligence",
        STAT_MELEE:             "Melee Attack",
        STAT_RANGED:            "Ranged Attack",
        STAT_CAST_FLAME:        "Cast Flame"
    }

    # Description of the stat
    descriptions = {
        STAT_STRENGTH:          "Physical strength and stamina.  Used to determine effectiveness of melee attacks and amount of HP.",
        STAT_SPEED:             "Speed and dexterity.  Used to determine effectiveness of ranged attacks and evasion.",
        STAT_INTELLIGENCE:      "Intellect and willpower.  Used to determine effectiveness of magical attacks and magical defense.",
        STAT_MELEE:             "Strike an opponent with a weapon at close range.  Usage: equip a melee weapon and type 'attack <target>'",
        STAT_RANGED:            "Fire a ranged weapon at an opponent.  Usage: equip a ranged weapon and type 'attack <target>'",
        STAT_CAST_FLAME:        "Launch a fireball about as big as a fist towards an opponent.  Usage: 'cast flame <target>'"
    }

    # Base modifiers (which base stats enhance a secondary stat)
    base_mod = {
        STAT_MELEE:             STAT_STRENGTH,
        STAT_RANGED:            STAT_SPEED,
        STAT_CAST_FLAME:        STAT_INTELLIGENCE
    }

    # Dependencies (which stats do you need to be able to access new stats?)
    deps = {

    }

    def __init__(self, value):
        self.value = value
        self.mod_value = value

        self.mod_number = 0
        self.mod_percent = 1.0
        self.modifiers = []

    def get_base(self):
        return int(self.value)

    def get_modified(self):
        mod_val = int(round((self.value + self.mod_number) * self.mod_percent))
        if mod_val < 0:
            return 0
        return mod_val

    def add_modifier(self, value, is_percent):
        self.modifiers.append([value, is_percent])
        if is_percent:
            self.mod_percent += value
        else:
            self.mod_number += value
        self.mod_value = int(round((self.value + self.mod_number) * self.mod_percent))
        if self.mod_value < 0:
            self.mod_value = 0

    def remove_modifier(self, value, is_percent):
        if [value, is_percent] in self.modifiers:
            self.modifiers.remove([value, is_percent])
            if is_percent:
                self.mod_percent -= value
            else:
                self.mod_number -= value
            self.mod_value = int(round((self.value + self.mod_number) * self.mod_percent))
            if self.mod_value < 0:
                self.mod_value = 0
