from rpilcdmenu import RpiLCDMenu

class RpiLCDSubMenu(RpiLCDMenu):
    def __init__(self, base_menu, scrolling_menu=False):
        """
        Initialize SubMenu
        """
        self.scrolling_menu = scrolling_menu
        self.rpi_lcd_processor = base_menu.rpi_lcd_processor
        self.max_width = base_menu.max_width
        self.lcd_framerate = base_menu.lcd_framerate
        self.cursor_char = base_menu.cursor_char

        super().__init__(base_menu)
