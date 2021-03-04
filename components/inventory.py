import tcod as libtcod

from game_messages import Message


class Inventory():
    """
    Classe du composant inventaire du Player.
    Elle contient un liste dont la taille ne doit pas depasser l'attribut capacite.
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        """
        Cette méthode ajoute un item ramasse a l'inventaire.

        :param item: objet de type Item a ajouter a l'inventaire
        :return: liste de dictionnaires décrivant les resultats de la tentative d'ajout.
        """
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                'item_added': None,
                'message': Message('Vous ne pouvez plus en transporter, votre inventaire est plein!', libtcod.yellow)
            })
        else:
            results.append({
                'item_added': item,
                'message': Message('Vous avez obtenu un {0}!'.format(item.name), libtcod.blue)
            })

            self.items.append(item)

        return results

    def use(self, item_entity, **kwargs):
        """
        Cette méthode va utiliser un item et le supprimer de l'inventaire.

        :param item_entity: instance de Entity qui a un composant item. C'est cet item qui sera utilisé
        :param kwargs:
        :return: liste de dictionnaires décrivant les resultats de la tentative d'utilisation.
        """
        results = []

        item_component = item_entity.item

        # Si l'item n'a pas d'utilité
        if item_component.use_function is None:
            results.append({'message': Message('Le {0} ne peut pas être utilisé!'.format(item_entity.name), libtcod.yellow)})

        else:
            # Si l'item a besoin d'une cible dont la position n'est pas encore connue (on aura alors besoin de passer à l'etat TARGETING)
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)
                # Dans le cas de la potion de guerison, item_component.function_kwargs = {'amount':4}

                # Apres avoir consomer un item, on le supprime de l'inventaire
                for item_use_result in item_use_results:
                    if item_use_result.get('consumed'):
                        self.remove_item(item_entity)

                results.extend(item_use_results)

        return results

    def remove_item(self, item):
        """
        Méthode de suppression d'un item de l'inventaire.

        :param item: item à supprimer
        :return: None
        """
        self.items.remove(item)

    def drop_item(self, item):
        """
        Quand on supprime un item de l'inventaire, le joueur le redépose en fait sur
        le carte, a la position ou il se trouve.
        :param item: Item à déposer
        :return: liste de dictionnaires décrivant les résultats de la suppresion.
        """
        results = []

        # la position de l'item est celle du joueur à ce moment
        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({'item_dropped': item, 'message': Message('Vous avez supprime le {0}'.format(item.name), libtcod.yellow)})

        return results

