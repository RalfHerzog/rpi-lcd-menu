class ContainerItem:
    """
    An item to contain two other items
    """

    def __init__(self, text, menu=None):
        """
        :ivar str text: The text shown for this menu item
        :ivar RpiLCDMenu menu: The menu which this item belongs to
        """

        self.items = list()
        self.text = text
        self.menu = menu

    def __str__(self):
        return "%s" % self.text

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def show(self, index):
        """
        How this item should be displayed in the menu. Can be overridden, but should keep the same pattern
        Default is:
            1 - Item 1
            2 - Another Item
        :param int index: The index of the item in the items list of the menu
        :return: The representation of the item to be shown in a menu
        :rtype: str
        """
        return "%d - %s" % (index + 1, self.text)

    def set_up(self):
        """
        Override to add any setup actions necessary for the item
        """

    def append_item(self, item):
        """
        Add an item to the container.
        :param MenuItem item: The item to be added
        """
        if len(self.items) >= 2:
            raise Exception("Error: Container already full.")

        item.menu = self
        self.items.append(item)
        return self

    def action(self):
        """
        Override to carry out the main action for this item.
        """
        if not self.items:
            raise Exception("Error: Container is empty!")

        return self._fire_action(self.items[0])

    def alt_action(self):
        """
        Override to carry out the alternate action for this item.
        """
        if len(self.items) == 1:
            return self.action()

        return self._fire_action(self.items[1])

    def _fire_action(self, item):
        """
        Method to trigger the action of item.
        """
        action_result = item.action()
        if isinstance(action_result, ContainerItem):
            return action_result
        if hasattr(item, "submenu") and isinstance(item.submenu, ContainerItem):
            return action_result
        return self

    def clean_up(self):
        """
        Override to add any cleanup actions necessary for the item
        """
        pass

    def get_return(self):
        """
        Override to change what the item returns.
        Otherwise just returns the same value the last selected item did.
        """
        return self.menu is not None and self.menu.get_return() or None
