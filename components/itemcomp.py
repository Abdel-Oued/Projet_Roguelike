class ItemComp:
    """
    Cette classe nous permet de définir les items et de choisir leur comportement.
    On l'utilise comme composant de la classe Item (classe fille de Entity).
    """
    def __init__(self, use_function=None, targeting=False, targeting_message=None, **kwargs):
        """
        :param use_function: nous permettra de changer librement le comportement des items
        :param kwargs: dictionnaire construit à partir des paramètres nommés : c'est du packing
        """
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.function_kwargs = kwargs
