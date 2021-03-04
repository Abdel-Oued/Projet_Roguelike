import tcod as libtcod
from game_states import GameStates


def handle_keys(key, game_state):
    """
    En fonction de l'état du jeu, cette fonction autorise les touches correspondantes.

    """
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)

    return {}


def handle_player_turn_keys(key):
    """
    Cette fonction gère les touches lorsque le joueur est sur le terrain.

    """
    # Movement keys
    key_char = chr(key.c)  # vim keys

    if key.vk == libtcod.KEY_UP or key_char == 'k':
        return {'move': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'j':
        return {'move': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'h':
        return {'move': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'l':
        return {'move': (1, 0)}
    elif key_char == 'y':
        return {'move': (-1, -1)}
    elif key_char == 'u':
        return {'move': (1, -1)}
    elif key_char == 'b':
        return {'move': (-1, 1)}
    elif key_char == 'n':
        return {'move': (1, 1)}

    if key_char == 'g':
        return {'pickup': True}

    elif key_char == 'i':
        return {'show_inventory': True}

    elif key_char == 'd':
        return {'drop_inventory': True}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}

    # Si aucune de ces touches n'est pressée on ne retourne rien
    return {}


def handle_targeting_keys(key):
    """
    Cette fonction gère les touches lorsque le joueur vise.

    """
    if key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}

    # Si aucune de ces touches n'est pressée on ne retourne rien
    return {}


def handle_player_dead_keys(key):
    """
    Cette fonction gère les touches lorsque le joueur meurt.

    """
    key_char = chr(key.c)

    if key_char == 'i':
        return {'show_inventory': True}
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter
        return {'fullscreen': True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    # Si aucune de ces touches n'est pressée on ne retourne rien
    return {}


def handle_inventory_keys(key):
    """
    Cette fonction gère les touches lorsqu'on est au menu inventaire.

    """
    # on récupère l'indice (dans la liste inventaire) de l'item sélectionné
    index = key.c - ord('a')

    if index >= 0:
        return {'inventory_index': index}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    # Si aucune de ces touches n'est pressée on ne retourne rien
    return {}


def handle_main_menu(key):
    """
    Cette fonction gère les touches lorsqu' on est au menu principal.

    """
    key_char = chr(key.c)

    if key_char == 'a':
        return {'new_game': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c' or key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}

    # Si aucune de ces touches n'est pressée on ne retourne rien
    return {}


def handle_mouse(mouse):
    """
    Cette fonction gère la souris.
   Elle retourne un dictionnaire dont la clé
   indique la touche appuyée de la souris et
   la valeur la position du pointeur.

    """
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'right_click': (x, y)}

    # Si aucune de ces touches n'est pressée on ne retourne rien
    return {}