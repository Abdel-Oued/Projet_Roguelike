import tcod as libtcod

import textwrap


class Message:
    """
    Les instances de cette classe sont des textes qui ont une couleur.

    """
    def __init__(self, text, color=libtcod.white):
        self.text = text
        self.color = color


class MessageLog:
    """
    Cette classe permet de regrouper les messages à afficher dans une fenêtre
    dans une zone rectangulaire bien définie. A chaque fois que cette zone est
    pleine, les messages défilent.

    """
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message):
        """
        Cette méthode permet d'ajouter un nouveau message à la variable d'instance
        messages(liste des messages à afficher).

        :param message: objet de la classe Message
        """
        # Si nécessaire,le message est divisé en plusieurs lignes
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            # Si la zone d'affichage est pleine, supprimez le premier message pour faire de la place pour le nouveau
            if len(self.messages) == self.height:
                del self.messages[0]

            # Ajoutez la nouvelle ligne comme objet Message, avec le texte et la couleur
            self.messages.append(Message(line, message.color))