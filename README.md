# MUD
This is a game server for a multi-user dungeon (MUD) written in Python 2
## Running
### Map Builder
Before you run the game server, you need a map.  To build a map, run 

    python map_builder.py

Basic instructions to create your map are shown on screen.  Press "s" to save, or "q" to save and quit after you have created your map.  By default, map builder saves the map to "./mud.map".  This can be changed with the "--map" option

    $ python map_builder.py -h
    usage: map_builder.py [-h] [--map MAP]

    optional arguments:
      -h, --help  show this help message and exit
      --map MAP   Map file
      
### MUD Server
Once the map is generated, you can start the server as follows  

    $ python mud.py
    [2017-06-02 23:45:36,570] [INFO] Mud starting.  Params: Namespace(map='mud.map', playerdir='./players', port=3000)
    [2017-06-02 23:45:36,575] [INFO] Map initialized from 'mud.map'.  Loaded 2 rooms with 3 spawn points

On startup, it reads the map from the map file supplied on the command line.  The default map is "./mud.map", which is the default map file generated by the map builder.  The player directory is used to keep player character information (stats, current location, etc), as well as the user's salted SHA512 password hash.

    $ python mud.py -h
    usage: mud.py [-h] [--playerdir PLAYERDIR] [--map MAP] [--port PORT]

    optional arguments:
      -h, --help            show this help message and exit
      --playerdir PLAYERDIR
                        Directory where all player data is kept.
      --map MAP             Map file
      --port PORT           Listening port.

## Storyline
TBD

## TODO
- [X] Map builder to generate maps
- [X] MUD server consumes map and generates world
- [X] Users can register new PCs and log in with old ones
- [X] PCs can move from room to room
- [X] Spawn points can be generated with map builder and create NPCs on map load
- [ ] Combat interaction with NPCs (attacking them, being attacked in return)
- [ ] Stat system and decide how the stats affect the mechanics of combat
- [ ] Spawn points generate equipment.  PCs can obtain equipment, and wear it, modifying their stats.
- [ ] Talk to friendly NPCs.  Shop in stores to purchase equipment and items.
- [ ] Complete stat system, implementing every attack and spell, as well as side effects (e.g. flame spell burns target)
- [ ] Questing system
- [ ] Settings system to allow users to change personal settings (e.g. screen width, terminal colors on/off, etc)
