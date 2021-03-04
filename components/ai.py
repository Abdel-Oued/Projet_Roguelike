from random import randint
import tcod as libtcod
from game_messages import Message


class BasicMonster:
    """
    Cette classe défini un type d'intelligence artifielle pour les monstres.
    C'est ce composant (ai)qui est attribue aux monstres lorsqu'ils sont à l'état normal.
    """
    def take_turn(self, target, fov_map, game_map, entities):
        """
        Quand c'est au tour des monstres de faire quelque chose,
        cette méthode est appelée.

        :param target: cible, le plus souvant c'est le joueur
        :param fov_map: champ de vision
        :param game_map: carte
        :param entities: liste des entités présentes
        :return: liste de dictionnaires décrivant les resultats du tour.
        """
        results = []

        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            # Si le monstre est loin de sa cible, il avance.
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)

            # Si le monstre est proche de sa cible, il l'attaque.
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results


class ConfusedMonster:
    """
    Cette classe défini un type d'intelligence artifielle pour les monstres.
    C'est ce composant (ai) qui est attribue aux monstres lorsqu'ils sont étourdis.   .

    """
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, game_map, entities):
        """
        Quand c'est au tour des monstres de faire quelque chose,
        cette methode est appelée.

        :param target: cible, le plus souvant c'est le joueur
        :param entities: liste des entités présentes
        :return: liste de dictionnaires décrivant les résultats du tour.
        """
        results = []

        # Si le nombre de tour a l'etat etourdi n'est pas atteint
        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

            self.number_of_turns -= 1

        else:
            # On redonne au monstre sont intelligence précédente
            self.owner.ai = self.previous_ai
            results.append({'message': Message("Le {0} n'est plus confus!".format(self.owner.name), libtcod.red)})

        return results
