from rpilcdmenu import RpiLCDMenu

class RpiLCDSubMenu(RpiLCDMenu):
    def __init__(self, base_menu, scrolling_menu=False):
        """
        Initialize SubMenu
        """
        self.lcd = base_menu.lcd
        self.scrolling_menu = scrolling_menu
        self.lcd_queue = base_menu.lcd_queue
        self.maxWidth = base_menu.maxWidth
        self.lcdFrameRate = base_menu.lcdFrameRate

        super(RpiLCDMenu, self).__init__(base_menu)
