import tcod as libtcod

from game_messages import Message


class Fighter:
    """
    Composant fighter du joueur et des monstres. Cette classe sert à définir les
    caractéristiques de défense etde combat.
    """
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_damage(self, amount):
        """
        Cette méthode gère les dégats occasionnés lors d'une attaque subie.

        :param amount: points de vie en moins
        :return: liste de dictionnaires décrivant les résultats de l'attaque subie.
        """
        results = []

        self.hp -= amount

        if self.hp <= 0:
            self.hp = 0
            results.append({'dead': self.owner})

        return results

    def heal(self, amount):
        """
        Cette méthode gère les soins apportés par un item.

        :param amount: points de vie en plus
        :return: liste de dictionnaires décrivant les résultats des soins.
        """
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        """
        Cette méthode gère les dégats occasionnés à l'ennemi lorsqu'on l'attaque.

        :param target: cible
        :return: liste de dictionnaires décrivant les resultats de l'attaque menée.
        """
        results = []

        # dommages occasionnés à l'ennemi
        damage = self.power - target.fighter.defense

        if damage > 0:
            results.append({'message': Message('{0} attaque {1} pour {2} points de vie.'.format(self.owner.name, target.name, str(damage)), libtcod.white)})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({'message': Message('{0} attaque {1} mais ne fait aucun degat.'.format(self.owner.name, target.name), libtcod.white)})

        return results
