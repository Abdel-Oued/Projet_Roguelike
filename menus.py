import tcod as libtcod


def menu(con, header, options, width, screen_width, screen_height):
    """Cette fonction cree une console qui présente les fonctions du menu.

    :param con:
    :param header: chaine de caractère représentant le texte d'entête
    :param options: options de menu
    :param width: largueur maximale des lignes de texte
    :param screen_width: largeur de la fenetre principale
    :param screen_height: hauteur de la fenetre principale
    """
    if len(options) > 26: raise ValueError("Impossible d'avoir un menu avec plus de 26 options.")

    # Hauteur de l'entête calculée automatiquement en fonction de la longueur du texte d'entête
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, header)

    # la hauteur de la console du menu
    height = len(options) + header_height

    # création de la console du menu
    window = libtcod.console_new(width, height)

    # Affichage du texte d'entête
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # Affichage des options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # superposition de la console window à la console principale
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)


def main_menu(con, background_image, screen_width, screen_height):
    """Menu principal
       Une image est affichée en arrière plan

    """
    libtcod.image_blit_2x(background_image, 0, 0, 0)

    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    # On centre les écritures
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4, libtcod.BKGND_NONE, libtcod.CENTER, 'TOMBES DES ANCIENS ROIS')
    #libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2), libtcod.BKGND_NONE, libtcod.CENTER, 'By (Your name here)')

    menu(con, '', ['Nouvelle partie', 'Continuer', 'Quitter'], 24, screen_width, screen_height)


def inventory_menu(con, header, inventory, inventory_width, screen_width, screen_height):
    """
    Affichage d'un menu avec chaque élément de l'inventaire en option.

    :param con:
    :param header: chaine de caractère représentant le texte d'entête
    :param inventory: liste d'items (à ne pas prendre pour un dictionnaire)
    :param inventory_width: largueur maximale des lignes de texte
    :param screen_width: largeur de la fenêtre principale
    :param screen_height: hauteur de la fenêtre principale
    """
    if len(inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory.items]

    menu(con, header, options, inventory_width, screen_width, screen_height)


def message_box(con, header, width, screen_width, screen_height):
    """

    :param con: console sur laquelle écrire
    :param header: chaine de caractère représentant le texte d'entête
    :param width: largueur maximale des lignes de texte
    :param screen_width: largeur de la fenetre principale
    :param screen_height: hauteur de la fenetre principale
    """
    menu(con, header, [], width, screen_width, screen_height)