import tcod as libtcod


def initialize_fov(game_map):
    """
    Cette fonction initialise le champ de vision du joueur.

    """
    fov_map = libtcod.map_new(game_map.width, game_map.height)

    for y in range(game_map.height):
        for x in range(game_map.width):
            libtcod.map_set_properties(fov_map, x, y, not game_map.tiles[x][y].block_sight, not game_map.tiles[x][y].blocked)

    return fov_map


def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):
    """
    Cette fonction met à jour le champ de vision du joueur en fonction
   de la position du joueur et du rayon de son champ de vision.
   L'algorithme FOV utilisé par défaut est le 0.

    """
    libtcod.map_compute_fov(fov_map, x, y, radius, light_walls, algorithm)
