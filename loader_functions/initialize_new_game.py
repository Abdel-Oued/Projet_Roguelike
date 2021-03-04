import tcod as libtcod

from entity import Player
from components.fighter import Fighter
from components.inventory import Inventory
from map_objects.game_map import GameMap
from game_states import GameStates
from render_functions import RenderOrder
from game_messages import MessageLog


def get_game_constants():
    """
    Cette fonction retourne un dictionnaire qui contient les constantes du jeu.
    Elle est appele dans la fonction principale (main) du jeu.
    """
    window_title = 'Roguelike'

    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3
    max_items_per_room = 2

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50)
    }

    game_constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room,
        'colors': colors
    }

    return game_constants


def get_game_variables(constants):
    """
    Cette fonction retourne un dictionnaire qui contient les variables principales
    (joueur, entites presentes, carte, messages à afficher, état du jeu) du jeu.
    Elle est appelée dans la fonction principale (main) du jeu.

    :param constants: constantes de jeu
    :return:
    """
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)
    player = Player(0, 0, '@', libtcod.black, 'Player', render_order=RenderOrder.ACTOR, blocks=True, fighter=fighter_component, inventory=inventory_component)
    entities = [player]

    game_map = GameMap(constants.get('map_width'), constants.get('map_height'))
    game_map.make_map(constants.get('max_rooms'), constants.get('room_min_size'), constants.get('room_max_size'), constants.get('map_width'), constants.get('map_height'), player, entities, constants.get('max_monsters_per_room'), constants.get('max_items_per_room'))

    message_log = MessageLog(constants.get('message_x'), constants.get('message_width'), constants.get('message_height'))

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state