import gevent.server
from mud_telnet_handler import MudTelnetHandler
from game_server import GameServer
import argparse
import logging

# Set up logging
log = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser()
parser.add_argument("--playerdir", type=str, default="./players", help="Directory where all player data is kept.")
parser.add_argument("--map", type=str, default="mud.map", help="Map file")
parser.add_argument("--port", type=int, default=3000, help="Listening port.")

args = parser.parse_args()

log.info("Mud starting.  Params: %s" % args)

# Set up some class vars of MudTelnetHandler
MudTelnetHandler.player_dir = args.playerdir + "/"
MudTelnetHandler.game_server = GameServer(args.map)

server = gevent.server.StreamServer(("", args.port), MudTelnetHandler.streamserver_handle)
server.serve_forever()
