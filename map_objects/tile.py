class Tile:
    """
    Une tuile sur une carte. Il peut être bloqué (dans ce cas elle bloque le passage) ou non, et peut ou non bloquer la vue.
    """

    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        #
        # Par défaut, si une tuile est bloquée, elle bloque également la vue
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight

        self.explored = False
