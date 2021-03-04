import tcod as libtcod

from enum import Enum

from game_states import GameStates
from menus import inventory_menu


class RenderOrder(Enum):
    """
    Enumération pour geree l'ordre dans lequel les entités sont déssinées sur la carte.
    Les acteurs (Player et Monster vivants) ont la priorité sur les item (Items) et les entités mortes.
    """
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    """
    Defini une zone d'écriture où on affichechera les messages pendant qu'on joue.

    :param panel:
    :param x:
    :param y:
    :param total_width:
    :param name:
    :param value:
    :param maximum:
    :param bar_color:
    :param back_color:
    """
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER, '{0}: {1}/{2}'.format(name, value, maximum))


def get_names_under_mouse(mouse, entities, fov_map):
    """
    Cette fonction retourne le nom de l'entité pointée par la souris.

    """
    (x, y) = (mouse.cx, mouse.cy)

    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, bar_width, panel_height, panel_y, mouse, colors, game_state):
    """
    Cette fonction s'occupe de l'affichage et de la mise à jour de tout ce qui est visible pendant le déroulement du jeu.

    """
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        #libtcod.console_set_char_background(con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, libtcod.light_blue)
                        libtcod.console_put_char(con, x, y, '^', libtcod.BKGND_NONE)
                    else:
                        libtcod.console_set_char_background(con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, libtcod.white)
                        libtcod.console_put_char(con, x, y, '+', libtcod.BKGND_NONE)
                    game_map.tiles[x][y].explored = True

                elif game_map.tiles[x][y].explored:
                    if wall:
                        #libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, libtcod.light_blue)
                        libtcod.console_put_char(con, x, y, '^', libtcod.BKGND_NONE)
                    else:
                        libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, libtcod.white)
                        libtcod.console_put_char(con, x, y, '+', libtcod.BKGND_NONE)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # Ecrire les messages du jeu, une ligne à la fois
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse(mouse, entities, fov_map))

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        else:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'

        inventory_menu(con, inventory_title, player.inventory, 50, screen_width, screen_height)


def clear_all(con, entities):
    """
    Efface toute les entités d'une liste donnée.

    :param con: console dans laquelle ont veut dessiner
    :param entities: liste des entités à effacer
    """
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map):
    """
    Dessine une entité dans une console si elle est dans le champ de vision

    :param con: console dans laquelle ont veut dessiner
    :param entity: entité à dessiner
    :param fov_map: carte représentant le champ de vision
    """
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
        libtcod.console_set_default_foreground(con, entity.color)
        libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
    """
    Effacer le caractère qui représente cet objet. On remplace le caractère par un espace
    """
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)