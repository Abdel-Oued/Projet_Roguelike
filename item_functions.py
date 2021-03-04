import tcod as libtcod

from game_messages import Message
from entity import Monster
from components.ai import ConfusedMonster


def heal(*args, **kwargs):
    """
    Cette fonction retourne les résultats de l'utilisation d'une
    potion de guérison.

    :param args: liste des arguments non nommés passés en paramètre. le premier paramètre doit être le joueur
    :param kwargs: dictionnaire des arguments nommés passés en paramètre.
    :return: liste de dictionnaires
    """
    player = args[0]  # le premier  argument passé en paramètre
    amount = kwargs.get('amount')

    results = []

    if player.fighter.hp == player.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('Vous etes deja en pleine sante!', libtcod.yellow)})
    else:
        # on augmente les points de vie
        player.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('Vos blessures commencent a aller mieux!', libtcod.green)})

    return results


def cast_lightning(*args, **kwargs):
    """
    Cette fonction accorde a l'entite qui detient l'item qui a cette fonction le pouvoir de foudroyer.
    Elle prend comme premier paramètre le foudroyeur?

    :param args: liste des arguments non nommés passés en paramètre. le premier paramètre doit être le joueur.
    :param kwargs: dictionnaire des arguments nommés passés en paramètre.
    :return: liste de dictionnaires
    """
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if isinstance(entity, Monster) and entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.distance_to(entity)

            # On cherche le monstre le plus proche
            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({'consumed': True, 'target': target, 'message': Message("Un eclair frappe le {0} avec un fort tonnerre! Les dégâts sont {1}".format(target.name, damage))})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({'consumed': False, 'target': None, 'message': Message("Aucun ennemi n'est suffisamment proche pour être frapper.", libtcod.red)})

    return results


def cast_fireball(*args, **kwargs):
    """
    Cette fonction permet au joueur de lancer une boule de feu qui brule les monstres présent dans un rayon passé en paramètre.

    :param args: liste des arguments non nommés passés en paramètre. le premier paramètre doit être le joueur
    :param kwargs: dictionnaire des arguments nommés passés en paramètre.
    :return: liste de dictionnaires
    """
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False, 'message': Message('Vous ne pouvez pas cibler une tuile en dehors de votre champ de vision!', libtcod.yellow)})
        return results

    results.append({'consumed': True, 'message': Message('La boule de feu explose, brulant tout dans un rayon de {0} tuiles!'.format(radius), libtcod.orange)})

    for entity in entities:
        # On cherche les monstres encore en vie (ceux encore capables de se battre)
        if isinstance(entity, Monster) and entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message('Le {0} a ete brule et a perdu {1} points de vie.'.format(entity.name, damage), libtcod.orange)})
            results.extend(entity.fighter.take_damage(damage))

    return results


def cast_confuse(*args, **kwargs):
    """
    Cette fonction permet au joueur de rendre un monstre cible
    étourdi en modifiant son intelligence

    :param args: liste des arguments non nommés passés en paramètre. le premier paramètre doit être le joueur
    :param kwargs: dictionnaire des arguments nommés passés en paramètre.
    :return: liste de dictionnaires
    """
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    # On verifie que la cible est dans le champ de vision
    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False, 'message': Message('Vous ne pouvez pas cibler une tuile en dehors de votre champ de vision', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedMonster(entity.ai, 10)

            confused_ai.owner = entity  # monstre cible
            entity.ai = confused_ai  # on change son intelligence

            results.append({'consumed': True, 'message': Message("Les yeux du {0} semblent vacants, alors qu'il commence a trebucher!".format(entity.name), libtcod.light_green)})

            break
    else:
        results.append({'consumed': False, 'message': Message("Il n'y a pas d'ennemi ciblable à cet endroit.", libtcod.yellow)})

    return results
