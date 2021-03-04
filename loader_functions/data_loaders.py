import os
import shelve


def save_game(player, entities, game_map, message_log, game_state):
    """
    Cette fonction creer le fichier savegame.dat qui va contenir les donnees de sauvegarde du jeu.

    """
    with shelve.open('savegame.dat', 'n') as data_file:
        # data_file est un dictionnaire
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        data_file['game_map'] = game_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state


def load_game():
    """
    Cette fonction ouvre (s'il existe) le fichier savegame.dat qui va contient les données de sauvegarde du jeu et
    récupère les données sauvegardées

    """
    # on vérifie qu'il existe un fichier de sauvegarde
    if not os.path.isfile('savegame.dat.dat'):
        raise FileNotFoundError

    with shelve.open('savegame.dat', 'r') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        game_map = data_file['game_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']

    player = entities[player_index]

    return player, entities, game_map, message_log, game_state
