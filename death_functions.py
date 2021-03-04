import tcod as libtcod

from game_states import GameStates
from render_functions import RenderOrder
from game_messages import Message


def kill_player(player):
    """
    Cette fonction est appelée lorsque le joueur n'a plus de point de vie.
    Elle retourne un message et l'état GameStates.PLAYER_DEAD
    """
    player.char = '%'
    player.color = libtcod.dark_red

    return Message('Tu es mort!', libtcod.red), GameStates.PLAYER_DEAD


def kill_monster(monster):
    """
    Cette fonction est appelée lorsqu'un monstre meurt.
    Elle retourne un message.

    """
    previousName = monster.name
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'restes de ' + monster.name
    monster.render_order = RenderOrder.CORPSE

    return Message('{0} est mort!'.format(previousName), libtcod.orange)

