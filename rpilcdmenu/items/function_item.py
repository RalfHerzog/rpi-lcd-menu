from .menu_item import MenuItem


class FunctionItem(MenuItem):
    """
    A menu item to call a Python function
    """

    def __init__(self, text, function, args=None, kwargs=None, menu=None):
        """
        :ivar function: The function to be called
        :ivar list args: An optional list of arguments to be passed to the function
        :ivar dict kwargs: An optional dictionary of keyword arguments to be passed to the function
        :ivar RpiLCDMenu menu: The menu which this item belongs to
        """
        super(FunctionItem, self).__init__(text=text, menu=menu)

        self.function = function

        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.returned_value = None

    def action(self):
        """
        This class overrides this method
        """
        self.returned_value = self.function(*self.args, **self.kwargs)
        return self.returned_value

    def get_return(self):
        """
        :return: The return value from the function call
        """
        return self.returned_value
