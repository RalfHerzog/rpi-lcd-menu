class BaseMenu:
    """
    A generic menu
    """

    def __init__(self, parent=None):
        """
        Initialzie basic menu
        """
        self.items = []
        self.parent = parent
        self.current_option = 0
        self.selected_option = -1
        self.input_count = 0

    def start(self):
        """
        Start and render menu
        """
        self.current_option = 0
        self.selected_option = -1
        self.render()

        return self

    def debug(self, level=1):
        """
        print menu items in console
        """
        for item in self.items:
            if hasattr(item, "submenu") and isinstance(item.submenu, BaseMenu):
                print(("|" + "--" * (level + 1) + "[" + "%s" % (item.__str__()) + "]"))
                item.submenu.debug(level + 1)
            else:
                print(("|" + "--" * level + ">" + "%s" % (item.__str__())))
        return self

    def append_item(self, item):
        """
        Add an item to the end of the menu
        :param MenuItem item: The item to be added
        """
        item.menu = self
        self.items.append(item)
        return self

    def render(self):
        """
        Render menu
        """

    def clearDisplay(self):
        """
        Clear the screen/
        """

    def processUp(self):
        """
        User triggered up event
        """
        self.input_count += 1
        if self.current_option == 0:
            self.current_option = len(self.items) - 1
        else:
            self.current_option -= 1
        self.render()
        return self

    def processDown(self):
        """
        User triggered down event
        """
        self.input_count += 1
        if self.current_option == len(self.items) - 1:
            self.current_option = 0
        else:
            self.current_option += 1
        self.render()
        return self

    def processEnter(self):
        """
        User triggered enter event
        """
        self.input_count += 1
        item = self.items[self.current_option]
        return self._fire_action(item, item.action())

    def processAltEnter(self):
        """
        Trigger event for second item in a ContainerItem
        """
        self.input_count += 1
        item = self.items[self.current_option]
        try:
            type = item.get_classname()
        except AttributeError:
            type = None

        if type != "ContainerItem":
            return self._fire_action(item, item.action())

        return self._fire_action(item, item.alt_action())

    def _fire_action(self, item, action_result):
        """
        Method to trigger the action
        """
        if isinstance(action_result, BaseMenu):
            return action_result
        if hasattr(item, "submenu") and isinstance(item.submenu, BaseMenu):
            return action_result
        return self

    def exit(self):
        """
        exit submenu and return parent
        """
        if self.parent is not None:
            self.parent.render()
        return self.parent

    def remove_item(self, item):
        """
        Remove an item from the menu
        :param MenuItem item: The item to be removed
        """
        item.menu = self
        self.items.remove(item)
        return self
