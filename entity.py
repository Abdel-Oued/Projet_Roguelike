import math
import tcod as libtcod

from render_functions import RenderOrder


class Entity:
    """
    Toutes les entités (objets à rammaser, joueur et monstres) sont des instances de cette classe.

    """
    def __init__(self, x, y, char, color, name, render_order=RenderOrder.CORPSE, blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order

    def move(self, dx, dy):
        """
        Cette méthode déplace l'entité.

        """
        self.x += dx
        self.y += dy

    def distance(self, x, y):
        """
        Cette méthode retourne la distance entre l'entité et une position donnée.

        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        """
        Cette méthode retourne la distance entre l'entité et une autre entité donnée.

        :param other: Entity
        :return: float
        """
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)


class Player(Entity):
    """
    Un Player est une entité pouvant se battre. Il possède en plus un composant Inventaire et un score.

    """
    def __init__(self, x, y, char, color, name, render_order, blocks, fighter, inventory):
        super().__init__(x, y, char, color, name, render_order, blocks)
        self.score = 0
        self.fighter = fighter
        self.inventory = inventory

        self.fighter.owner = self
        self.inventory.owner = self


class Item(Entity):
    """
    Un Item est une entité à ramasser.

    """
    def __init__(self, x, y, char, color, name, render_order, item):
        super().__init__(x, y, char, color, name, render_order)
        self.item = item
        self.item.owner = self


class Monster(Entity):
    """
    Un Monster est une entité doté d'une intelligence et pouvant se battre.

    """
    def __init__(self, x, y, char, color, name, render_order, blocks, fighter, ai):
        super().__init__(x, y, char, color, name, render_order, blocks)
        self.fighter = fighter
        self.ai = ai

        self.fighter.owner = self
        self.ai.owner = self

    def move_towards(self, target_x, target_y, game_map, entities):
        """
        Cette fonction est utilisée par les monstres pour se rapprocher de leur cible.
        Le monstre se déplace horizontalement d'un pixel si la cible a la même ordonnee y
        et verticalement d'un pixel si la cible a la même abscisse.
        Dans le cas contraire ils ne bouge pas.

        """
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Si dx=distance alors dx devient 1 et on se rapproche horizontalement d'un pixel, sinon dx devient nul
        # Si dy=distance alors dy devient 1 et on se rapproche verticalement d'un pixel, sinon dy devient nul
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def move_astar(self, target, entities, game_map):
        """
        Cette fonction permet aux monstres d'avoir des déplacements plus sophistiqués.
        Ils peuvent se déplacer en diagonal.

        """
        # Créer une carte FOV qui a les dimensions de la carte
        fov = libtcod.map_new(game_map.width, game_map.height)

        # On scanne la carte actuelle à chaque tour et on définit tous les murs comme inviolables
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                libtcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight, not game_map.tiles[x1][y1].blocked)

        # On Scanne tous les objets pour voir s'il y a des objets qui doivent être parcourus
        # On Vérifie également que l'objet n'est pas lui-même ou la cible (pour que les points de départ et d'arrivée soient libres)
        # La classe AI gère la situation si le self est à côté de la cible, de sorte qu'elle n'utilisera pas cette fonction A * de toute façon
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov, entity.x, entity.y, True, False)

        # Allouer un chemin A *
        # Le 1,41 (racine carré de 2)  est le coût diagonal normal du déplacement, il peut être réglé sur 0,0 si les déplacements diagonaux sont interdits
        my_path = libtcod.path_new_using_map(fov, 1.41)

        # Calculer le chemin entre les coordonnées de self et les coordonnées de la cible
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Vérifiez si le chemin existe, et dans ce cas, si le chemin est également plus court que 25 tuiles
        # La taille du chemin est importante si vous voulez que le monstre utilise d'autres chemins plus longs (par exemple à travers d'autres pièces) si par exemple le joueur est dans un couloir
        # Il est logique de garder la taille du chemin relativement faible pour empêcher les monstres de courir sur la carte s'il y a un chemin alternatif très loin
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            # Trouver les coordonnées suivantes dans le chemin complet calculé
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                # On attribue ces coordonnées à self
                self.x = x
                self.y = y
        else:
            # Conservez l'ancienne fonction de déplacement comme sauvegarde afin que s'il n'y a pas de chemin (par exemple, un autre monstre bloque un couloir)
            # il essaiera toujours de se déplacer vers le joueur (plus près de l'ouverture du couloir)
            self.move_towards(target.x, target.y, game_map, entities)

            # Supprimer le chemin pour libérer de la mémoire
        libtcod.path_delete(my_path)


def get_blocking_entities_at_location(entities, destination_x, destination_y):
    """
    La fonction parcourt les entités, et si l'une d'elles "bloque" et se trouve
    à l'emplacement x et y que nous avons spécifié, nous la renvoyons.

    """
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None
