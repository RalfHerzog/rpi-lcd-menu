from rpilcdmenu import RpiLCDMenu

class RpiLCDSubMenu(RpiLCDMenu):
    def __init__(self, base_menu, scrolling_menu=False):
        """
        Initialize SubMenu
        """
        self.lcd = base_menu.lcd
        self.scrolling_menu = scrolling_menu
        self.lcd_queue = base_menu.lcd_queue
        self.max_width = base_menu.max_width
        self.lcd_framerate = base_menu.lcd_framerate
        self.cursor_char = base_menu.cursor_char

        super().__init__(base_menu)
