import gevent, gevent.server
from telnetsrv.green import TelnetHandler, command
from character import Password, Player, player_exists


# The TelnetHandler instance is re-created for each connection.
class MudTelnetHandler(TelnetHandler):
    #authNeedUser = True
    #authNeedPass = True
    map_dir = None
    player_dir = None
    game_server = None
    WELCOME = ''' 
 _    _ _____ _     _____ ________  ___ _____ 
| |  | |  ___| |   /  __ \  _  |  \/  ||  ___|
| |  | | |__ | |   | /  \/ | | | .  . || |__  
| |/\| |  __|| |   | |   | | | | |\/| ||  __| 
\  /\  / |___| |___| \__/\ \_/ / |  | || |___ 
 \/  \/\____/\_____/\____/\___/\_|  |_/\____/ 

This is a really cool MUD.  It doesn't have a name yet.
Or much, if any, content.  

New players, enter NEW as your name.
'''
    PROMPT="mud>"

    def update_prompt(self):
        self.PROMPT="%dhp %dmp>" % (self.player.hp, self.player.mp)


    def writeerror(self, text):
        '''Called to write any error information (like a mistyped command).
        Add a splash of color using ANSI to render the error text in red.  see http://en.wikipedia.org/wiki/ANSI_escape_code'''
        TelnetHandler.writeerror(self, "\x1b[91m%s\x1b[0m" % text )


    def write_room_desc(self):
        name, desc, directions, characters = self.game_server.get_room_info(self.player.location);
        character_list = "\n".join(characters)
        self.writeresponse("""
%s
        
%s
%s
-------
%s
""" % (name, desc, directions, character_list));


    def change_location(self, direction):
        new_location = self.game_server.change_location(self.player, direction)
        if new_location is not None:
            self.player.location = new_location
            self.player.save()
            self.write_room_desc()
        else:
            self.writeerror("You cannot go that way")



#    @command(['echo', 'copy', 'repeat'])
#    def command_echo(self, params):
#        '''<text to echo>
#        Echo text back to the console.
#
#        '''
#        self.writeresponse( ' '.join(params) )
#
#    @command('timer')
#    def command_timer(self, params):
#        '''<time> <message>
#        In <time> seconds, display <message>.
#        Send a message after a delay.
#        <time> is in seconds.
#        If <message> is more than one word, quotes are required.
#        example:
#        > TIMER 5 "hello world!"
#        '''
#        try:
#            timestr, message = params[:2]
#            time = int(timestr)
#        except ValueError:
#            self.writeerror( "Need both a time and a message" )
#            return
#        #print "time=" + str(time);
#        self.writeresponse("Waiting %d seconds..." % time)
#        gevent.spawn_later(time, self.writemessage, message)

    @command('who')
    def command_who(self, params):
        '''
        Display a list of players online
        '''
        players = self.game_server.get_players()
        players_str = "Players online:\n"
        print type(players)
        for player in players:
            players_str += "%s\n" % player
        self.writeresponse(players_str);

    # TODO: Do I need more locking around player, since even though I own him, other players in the room will be changing him?

    @command(['north', 'n'])
    def command_north(self, params):
        '''
        Go north
        '''
        self.change_location('n')

    @command(['northwest', 'nw'])
    def command_northwest(self, params):
        '''
        Go northwest
        '''
        self.change_location('nw')

    @command(['northeast', 'ne'])
    def command_northeast(self, params):
        '''
        Go northeast
        '''
        self.change_location('ne')

    @command(['south', 's'])
    def command_south(self, params):
        '''
        Go south
        '''
        self.change_location('s')

    @command(['southwest', 'sw'])
    def command_southwest(self, params):
        '''
        Go southwest
        '''
        self.change_location('sw')

    @command(['southeast', 'se'])
    def command_southeast(self, params):
        '''
        Go southeast
        '''
        self.change_location('se')

    @command(['east', 'e'])
    def command_east(self, params):
        '''
        Go east
        '''
        self.change_location('e')

    @command(['west', 'w'])
    def command_west(self, params):
        '''
        Go west
        '''
        self.change_location('w')

    @command(['up', 'u'])
    def command_up(self, params):
        '''
        Go up
        '''
        self.change_location('u')

    @command(['down', 'd'])
    def command_down(self, params):
        '''
        Go down
        '''
        self.change_location('d')

    def session_start(self):
        while True:
            name = self.readline( prompt="What is your name?", echo=True, use_history=False )
            if player_exists(name, self.player_dir) or name == "NEW":
                break
            self.writeresponse("That player does not exist!")

        if name == "NEW":
            # Create a new player
            self.writeresponse("Welcome, let's create a new player!");

            while True:
                name = self.readline( prompt="What is your player's name?", echo=True, use_history=False )
                if not name.isalnum():
                    self.writeresponse("Names must be only letters and/or numbers")
                    continue
                if player_exists(name, self.player_dir):
                    self.writeresponse("That player already exists!")
                    continue
                break

            while True:
                password = self.readline( prompt="What will be your password?", echo=False, use_history=False )
                password_dup = self.readline( prompt="Please retype password:", echo=False, use_history=False )
                if password != password_dup:
                    self.writeresponse("Passwords do not match, please try again");
                    continue
                break

            # Everything worked, save password and player
            password_object = Password(name, self.player_dir)
            password_object.save(password)
            self.player = Player(name, self.player_dir)
            self.player.save();

        else:
            # Load an old player
            while True:
                password = self.readline( prompt="Password: ", echo=False, use_history=False )
                password_object = Password(name, self.player_dir)
                password_object.load()
                if password_object.check(password):
                    break;
                self.writeresponse("Incorrect password");

            self.player = Player(name, self.player_dir)
            self.player.load()

        # We are now playing, whether the player was new or old
        self.update_prompt();
        self.game_server.add_player(self.player);
        self.write_room_desc();


#    def session_end(self):
#        self.game_server.(self.username);
