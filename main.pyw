import tcod as libtcod

from loader_functions.initialize_new_game import get_game_constants, get_game_variables
from death_functions import kill_monster, kill_player
from entity import get_blocking_entities_at_location
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from game_states import GameStates
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from loader_functions.data_loaders import save_game, load_game
from menus import main_menu, message_box
from entity import Monster, Item


def main():
    """
    C'est la fonction qui lance la fenêtre principale au démarrage du jeu.

    """
    constants = get_game_constants()

    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    libtcod.console_init_root(constants.get('screen_width'), constants.get('screen_height'), constants.get('window_title'), False)  #False: pour le plein écran

    con = libtcod.console_new(constants.get('screen_width'), constants.get('screen_height'))
    panel = libtcod.console_new(constants.get('screen_width'), constants.get('panel_height'))

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True  # au demarrage du jeu on tombe sur le menu principal
    show_load_error_message = False  # il n'y a pas d'erreur de chargement au demarrage

    main_menu_background_image = libtcod.image_load('menu_background.png')

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            # Affichage du menu principal
            main_menu(con, main_menu_background_image, constants.get('screen_width'), constants.get('screen_height'))

            if show_load_error_message:
                # Affichage du message d'erreur de chargement
                message_box(con, 'Aucune sauvegarde', 50, constants.get('screen_width'), constants.get('screen_height'))

            # Rafraichissement de la fenêtre
            libtcod.console_flush()

            # On active les commandes du menu principal
            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
                # On ne change pas la valeur de show_main_menu : le menu reste affiche

            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(constants)
                game_state = GameStates.PLAYERS_TURN

                # On quitte le menu principal vers le jeu
                show_main_menu = False

            elif load_saved_game:
                try:
                    # On essaie de modifier les variables du jeu
                    player, entities, game_map, message_log, game_state = load_game()

                    # Si le chargement a réussi on quitte le menu principal vers le jeu
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True

            elif exit_game:
                # On quitte totalement le jeu en fermant la fenêtre principale
                break

        # if show_main_menu = false, le jeu commence
        else:
            libtcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, con, panel, constants)
            # On revient au menu principal en appuyant sur Esc
            show_main_menu = True


def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):
    """Cette fonction gère le déroulement du jeu proprement parlant. Elle lance la fenêtre
       de jeu ou l'on voit le joueur évoluer dans son environnement.

    """

    # Cette variable sert à mettre à jour le champ de vision
    fov_recompute = True

    # Initialisation du champ de vision
    fov_map = initialize_fov(game_map)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    previous_game_state = game_state

    targeting_item = None

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants.get('fov_radius'), constants.get('fov_light_walls'), constants.get('fov_algorithm'))

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, constants.get('screen_width'), constants.get('screen_height'),
                   constants.get('bar_width'), constants.get('panel_height'), constants.get('panel_y'), mouse, constants.get('colors'), game_state)

        fov_recompute = False

        # Rafraichissement de la fenêtre
        libtcod.console_flush()

        clear_all(con, entities)

        # Les touches actives lors du jeu dépendent de l'état du jeu (sommes nous en train de regarder l'inventaire,
        # viser, ...).
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        # Cette variable est une liste de dictionnaires qui contiennent les résultats de l'action effectuée par le joueur
        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)

                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                # Si on a un item et que le joueur est à la même place que l'item , il peut le ramasser
                if isinstance(entity, Item) and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break
            else:
                message_log.add_message(Message("Il n'y a rien ici a ramasser", libtcod.yellow))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        # on vérifie que l'indice correspond à une option et que le joueur est encore vivant (pour que ça est un sens)
        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map, target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit:
            # Lorsqu'on appuie sur Esc quand on est dans le menu inventaire, on revient au jeu
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            # Sinon on sauvegarde la partie et on revient au menu principal
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    # C'est un monstre
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                # on supprime l'item obtenu de la liste des entités présentes sur la carte.
                # Elle fait maintenant partie de l'inventaire du joueur
                entities.remove(item_added)

                # En ramassant un item on perd un tour
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                # Consommant un item on perd un tour
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            if item_dropped:
                # Si un item est depose par le joueur, on le rajoute a la liste des entités présentes sur la carte
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN

        if game_state == GameStates.ENEMY_TURN:
            # On s'occupe des monstres
            for entity in entities:
                # Si on a un monstre et qu'il est vivant
                if isinstance(entity, Monster) and entity.ai:
                    # Cette variable est une liste de dictionnaires qui contiennent les résultats de l'action effectuée par un monstre
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()
