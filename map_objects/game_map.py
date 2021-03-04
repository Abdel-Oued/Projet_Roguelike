from random import randint
import tcod as libtcod


from render_functions import RenderOrder
from entity import Monster, Item
from components.fighter import Fighter
from components.ai import BasicMonster
import components.itemcomp as comp
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from game_messages import Message
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse


class GameMap:
    """
    Cette classe matérialise une carte.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        """
        Création de Tiles qui bloquent le passage et la vue sur toute la surface de la carte.
        Ces Tiles sont stockés dans une liste qu'on retourne.
        """
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room, max_items_per_room):
        """
            Cette fonction crée toutes les pièces et les relient entre elles par des tunels.

        """
        rooms = []
        num_rooms = 0

        for r in range(max_rooms):
            # largeur et hauteur aléatoires
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)

            # position aléatoire sans sortir des limites de la carte
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # Création d'une nouvelle pièce
            new_room = Rect(x, y, w, h)

            # courir à travers les autres pièces et voir si elles se croisent avec celle-ci
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # cela signifie qu'il n'y a pas d'intersections, donc cette pièce est valide

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # coordonnées du centre de la nouvelle pièce, sera utile plus tard
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    # Le joueur commence au centre de la première case
                    player.x = new_x
                    player.y = new_y
                else:
                    # Toutes les cases apres la première sont connectées à la case précédente par un tunel

                    # coordonnées du centre de la pièce précédente
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # lancer une pièce (nombre aléatoire qui est soit 0 soit 1)
                    if randint(0, 1) == 1:
                        # déplacer d'abord horizontalement, puis verticalement
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # déplacer d'abord verticalement, puis horizontalement
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities, max_monsters_per_room, max_items_per_room)

                # enfin, ajout de la nouvelle salle à la liste
                rooms.append(new_room)
                num_rooms += 1

    def create_room(self, room):
        """
        passer par les Tiles du rectangle et les rendre praticables.

        """
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        """
        Crée d'un tunel horizontal.

        """
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        """
        Crée d'un tunel vertical.

        """
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room):
        """
        Cette méthode crée et place les différentes entités autres que le joueur sur la carte.

        """

        # on génère un nombre aléatoire de monstres et d'items
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        for i in range(number_of_monsters):
            # On choisi une position aléatoire dans la chambre
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            # on verifie que cette position est libre
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            # any(...) retourne False si la liste est vide (ce qui voudra dire
            # que la position (x,y) est libre) et True sinon
                monster_chance = randint(0, 100)

                if monster_chance < 10:
                    # il ya 80% de chance que ce soit un AssassinCat
                    fighter_component = Fighter(hp=15, defense=2, power=5)
                    ai_component = BasicMonster()

                    monster = Monster(x, y, 'A', libtcod.magenta, 'AssassinCat', render_order=RenderOrder.ACTOR, blocks=True, fighter=fighter_component, ai=ai_component)
                elif monster_chance < 40:
                    # 20% de chance que ce soit un Bat
                    fighter_component = Fighter(hp=10, defense=1, power=4)
                    ai_component = BasicMonster()

                    monster = Monster(x, y, 'B', libtcod.azure, 'Bat', render_order=RenderOrder.ACTOR, blocks=True, fighter=fighter_component, ai=ai_component)
                elif monster_chance < 80:
                    # 20% de chance que ce soit un Hobgoblin
                    fighter_component = Fighter(hp=10, defense=0, power=3)
                    ai_component = BasicMonster()

                    monster = Monster(x, y, 'H', libtcod.grey, 'Hobgoblin', render_order=RenderOrder.ACTOR, blocks=True, fighter=fighter_component, ai=ai_component)
                else :
                    # 20% de chance que ce soit un Troll
                    fighter_component = Fighter(hp=10, defense=1, power=4)
                    ai_component = BasicMonster()

                    monster = Monster(x, y, 'T', libtcod.grey, 'Troll', render_order=RenderOrder.ACTOR, blocks=True, fighter=fighter_component, ai=ai_component)

                entities.append(monster)

        for i in range(number_of_items):
            # On choisi une position aléatoire dans la chambre
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            # on verifie que cette position est libre
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_chance = randint(0, 100)

                if item_chance < 60:
                    # il ya 60% de chance que ce soit une potion de guérison
                    item_component = comp.ItemComp(use_function=heal, amount=5)
                    item = Item(x, y, '!', libtcod.violet, 'Potion', render_order=RenderOrder.ITEM, item=item_component)

                elif item_chance < 70:
                    # il ya 10% de chance que ce soit une boule de feu qui a le pouvoir
                    # d'exploser dans un rayon de 3
                    message = Message('Clique-gauche sur une tuile cible pour la boule de feu ou clique-droit pour annuler.', libtcod.light_cyan)
                    item_component = comp.ItemComp(use_function=cast_fireball, targeting=True, targeting_message=message, damage=12, radius=4)
                    item = Item(x, y, '*', libtcod.red, 'Boule de feu', render_order=RenderOrder.ITEM, item=item_component)

                elif item_chance < 90:
                    # il ya 20% de chance que ce soit un étourdisseur
                    message = Message("Clique-gauche sur une tuile cible pour le vertige ou clique-droit pour annuler.", libtcod.light_cyan)
                    item_component = comp.ItemComp(use_function=cast_confuse, targeting=True, targeting_message=message)
                    item = Item(x, y, '§', libtcod.light_pink, 'Vertige', render_order=RenderOrder.ITEM, item=item_component)

                else:
                    # il ya 10% de chance que ce soit la foudre
                    item_component = comp.ItemComp(use_function=cast_lightning, damage=20, maximum_range=5)
                    item = Item(x, y, '$', libtcod.light_red, 'Foudre', render_order=RenderOrder.ITEM, item=item_component)

                entities.append(item)

    def is_blocked(self, x, y):
        """
        Cette méthode renvoie true si le Tile à la position (x,y) bloque le passage.

        """
        if self.tiles[x][y].blocked:
            return True

        return False
