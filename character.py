import cPickle
import os.path
import hashlib
import uuid

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


class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description


class Equipment(Item):

    # Wear slots
    HEAD = 0
    TORSO = 1
    LEFT_HAND = 2
    RIGHT_HAND = 3
    LEGS = 4
    BACK = 5
    MAX_WEAR = 6

    # Name of wear slots
    wear_names = {
        HEAD: "Head",
        TORSO: "Torso",
        LEFT_HAND: "Left Hand",
        RIGHT_HAND: "Right Hand",
        LEGS: "Legs",
        BACK: "Back"
    }

    def __init__(self, name, description, wear=[], mods=[]):
        Item.__init__(self, name, description)
        self.wear = wear
        self.mods = mods

    def to_string(self):
        mod_strs = []
        for mod in self.mods:
            if mod.value < 0:
                if mod.is_percent:
                    mod_strs.append('{} {}%'.format(Stat.names[mod.stat], int(mod.value*100)))
                else:
                    mod_strs.append('{} {}'.format(Stat.names[mod.stat], mod.value))
            else:
                if mod.is_percent:
                    mod_strs.append('{} +{}%'.format(Stat.names[mod.stat], int(mod.value*100)))
                else:
                    mod_strs.append('{} +{}'.format(Stat.names[mod.stat], mod.value))
        return '{} ({})'.format(self.name, ', '.join(mod_strs))


class Character(object):
    def __init__(self, name, hp, mp, location):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.stats = StatTable(stats={Stat.STRENGTH: 11, Stat.SPEED: 8, Stat.INTELLIGENCE: 5, Stat.MELEE: 4})
        self.location = location
        self.wear = []

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
            self.game_server.add_action(AttackAction(actor=self, target_character=self.engaged))

        # 2) If not engaged, find someone to fight if hostile
        #elif self.AGGRO_HOSTILE:


class Player(Character):
    def __init__(self, name, player_dir, net_handler):
        # TODO: This is all test stuff
        Character.__init__(self, name, 10, 10, (0,0,0))
        self.player_dir = player_dir
        self.net_handler = net_handler
        self.inventory = [
            Equipment(
                'Iron Longsword',
                'Sturdy sword made of iron.  Might be useful in a fight',
                wear=[Equipment.RIGHT_HAND, Equipment.LEFT_HAND],
                mods=[StatMod(Stat.MELEE, 2, False)]
            ),
            Equipment(
                'Staff of Healing',
                'Smooth maple staff that emits a dim yellow aura',
                wear=[Equipment.RIGHT_HAND, Equipment.LEFT_HAND],
                mods=[StatMod(Stat.INTELLIGENCE, 2, False), StatMod(Stat.CAST_HEAL, .25, True)]
            ),
            Equipment(
                'Berserker Helmet',
                'Helmet that enrages the wearer',
                wear=[Equipment.HEAD],
                mods=[StatMod(Stat.ARMOR, 3, False), StatMod(Stat.MELEE, 5, False), StatMod(Stat.INTELLIGENCE, -5, False)]
            ),
            Equipment(
                'Heavy Chainmail',
                'Thick coat of chainmail.  Offers excellent protection from physical damage.',
                wear=[Equipment.TORSO],
                mods=[StatMod(Stat.ARMOR, 7, False), StatMod(Stat.SPEED, -.5, True)]
            )
        ]

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
    def __init__(self, actor, target=None, target_character=None, kwargs={}):
        self.actor = actor
        self.target = target
        self.target_character = target_character
        self.location = actor.location
        self.kwargs = kwargs
        self.pre_msg_str = None
        self.zero_target_error_msg_str = None

    def pre_msg(self):
        if self.time > 0 and self.pre_msg_str is not None:
            return self.pre_msg_str.format(self.actor.name)
        return None

    def zero_target_error_msg(self):
        if self.zero_target_error_msg_str is not None:
            return self.zero_target_error_msg_str.format(self.target)
        return None


class SayAction(Action):
    def __init__(self, actor, target=None, target_character=None, kwargs={}):
        super(SayAction, self).__init__(actor, target, target_character, kwargs)
        self.time = 0
        self.pre_msg_str = '{} prepares to speak...'

    def execute(self):
        return '{} says \"{}\"'.format(self.actor.name, self.kwargs["msg"])


class AttackAction(Action):
    def __init__(self, actor, target=None, target_character=None, kwargs={}):
        super(AttackAction, self).__init__(actor, target, target_character, kwargs)
        self.time = 1.0  # TODO: Make the time actually dependent on the actor (e.g. actor.get_attack_speed())
        self.pre_msg_str = '{} makes ready their weapon...'

    def execute(self):
        damage = 1
        self.target_character.mod_hp(-damage)

        if isinstance(self.target_character, Player):
            self.target_character.save()

        if isinstance(self.target_character, NPC) and self.target_character.hp > 0:
            self.target_character.aggro = NPC.AGGRO_HOSTILE
            self.target_character.engaged = self.actor

        msg = '{} strikes {} for {} damage'.format(self.actor.name, self.target_character.name, damage)
        if self.target_character.hp <= 0:
            msg += '...and {} is slain.'.format(self.target_character.name)
        return msg


class Stat(object):

    # TODO: Are these class variables??

    # Base stats
    STRENGTH = 0
    SPEED = 1
    INTELLIGENCE = 2

    # Secondary stats
    MELEE = 10
    ARMOR = 11
    RANGED = 20
    EVASION = 21


    WILLPOWER = 30
    CAST_FLAME = 31
    CAST_HEAL = 32
    CAST_CHILL = 33
    CAST_FLAMING_SWORD = 34

    # Name of the stat
    names = {
        STRENGTH: "Strength",
        SPEED: "Speed",
        INTELLIGENCE: "Intelligence",
        MELEE: "Melee Attack",
        ARMOR: "Armor",
        RANGED: "Ranged Attack",
        EVASION: "Evasion",
        WILLPOWER: "Willpower",
        CAST_FLAME: "Cast Flame",
        CAST_HEAL: "Cast Heal",
        CAST_CHILL: "Cast Chill",
        CAST_FLAMING_SWORD: "Cast Flaming Sword"
    }

    # Description of the stat
    # TODO: Descriptions like this should be in some sort of documentation resource file
    descriptions = {
        STRENGTH: "Physical strength and stamina.  Used to determine effectiveness of melee attacks and amount of HP.",
        SPEED: "Speed and dexterity.  Used to determine effectiveness of ranged attacks and evasion.",
        INTELLIGENCE: "Intellect and willpower.  Used to determine effectiveness of magical attacks and magical defense.",
        MELEE: "Strike an opponent with a weapon at close range.  Usage: equip a melee weapon and type 'attack <target>'",
        ARMOR: "Physical defense due to armor, physical constitution, or both.  Damage from melee and ranged attacks is reduced",
        RANGED: "Fire a ranged weapon at an opponent.  Usage: equip a ranged weapon and type 'attack <target>'",
        EVASION: "Ability to dodge melee and ranged attacks",
        WILLPOWER: "Damaged is reduced from magic attacks",
        CAST_FLAME: "Launch a fireball about as big as a fist towards an opponent.  Usage: 'cast flame <target>'",
        CAST_HEAL: "TBD",
        CAST_CHILL: "TBD",
        CAST_FLAMING_SWORD: "TBD"
    }

    def __init__(self, value):
        self._value = value
        self._mod_value = value

        self._mod_number = 0
        self._mod_percent = 1.0
        self._modifiers = []

    @property
    def base(self):
        return int(self._value)

    @property
    def modified(self):
        mod_val = int(round((self._value + self._mod_number) * self._mod_percent))
        if mod_val < 0:
            return 0
        return mod_val

    def add_modifier(self, value, is_percent):
        self._modifiers.append([value, is_percent])
        if is_percent:
            self._mod_percent += value
        else:
            self._mod_number += value

    def remove_modifier(self, value, is_percent):
        if [value, is_percent] in self._modifiers:
            self._modifiers.remove([value, is_percent])
            if is_percent:
                self._mod_percent -= value
            else:
                self._mod_number -= value


class StatTable(object):

    # Base modifiers (which base stats enhance a secondary stat)
    base_mod = {
        Stat.MELEE:                Stat.STRENGTH,
        Stat.ARMOR:                Stat.STRENGTH,
        Stat.RANGED:               Stat.SPEED,
        Stat.EVASION:              Stat.SPEED,
        Stat.WILLPOWER:            Stat.INTELLIGENCE,
        Stat.CAST_FLAME:           Stat.INTELLIGENCE,
        Stat.CAST_HEAL:            Stat.INTELLIGENCE,
        Stat.CAST_CHILL:           Stat.INTELLIGENCE,
        Stat.CAST_FLAMING_SWORD:   Stat.INTELLIGENCE
    }

    # Dependencies (which stats do you need to be able to access new stats?)
    deps = {
        Stat.STRENGTH: [],
        Stat.SPEED: [],
        Stat.INTELLIGENCE: [],
        Stat.MELEE: [],
        Stat.ARMOR: [],
        Stat.RANGED: [],
        Stat.EVASION: [],
        Stat.WILLPOWER: [],
        Stat.CAST_FLAME: [],
        Stat.CAST_HEAL: [
            {'stat': Stat.CAST_FLAME, 'level': 5}
        ],
        Stat.CAST_CHILL: [
            {'stat': Stat.CAST_HEAL, 'level': 5}
        ],
        Stat.CAST_FLAMING_SWORD: [
            {'stat': Stat.CAST_FLAME, 'level': 5},
            {'stat': Stat.MELEE, 'level': 10}
        ]
    }

    # Initialize with {stat_enum: int, stat_enum: int}
    def __init__(self, stats={}):
        self._stats = {}
        for stat in StatTable.deps:
            if stat in stats:
                self._stats[stat] = Stat(stats[stat])
            else:
                self._stats[stat] = Stat(0)

    def get_combined_modified(self, stat):
        modified = self._stats[stat].modified
        if modified <= 0:
            return 0  # Base mods should not buff stats that are 0 to begin with
        if stat in StatTable.base_mod:
            return self._stats[stat].modified + self._stats[StatTable.base_mod[stat]].modified
        else:
            return self._stats[stat].modified

    # Get a list of all stats where deps have been met
    def get_available_stats(self):
        ret = []
        for stat in StatTable.deps:
            should_add = True
            for dep in StatTable.deps[stat]:
                if self._stats[dep['stat']].base < dep['level']:
                    should_add = False
                    break
            if should_add:
                ret.append(stat)
        return ret

    def to_string(self):
        display_stats = []
        for s in self._stats:
            combined_modified = self.get_combined_modified(s)
            if combined_modified > 0:
                display_stats.append('{}:\t{} ({})'.format(Stat.names[s], combined_modified, self._stats[s].base))
        return '\n'.join(display_stats)


class StatMod(object):
    def __init__(self, stat, value, is_percent, time=0):
        self.stat = stat
        self.value = value
        self.is_percent = is_percent
        self.time = time

