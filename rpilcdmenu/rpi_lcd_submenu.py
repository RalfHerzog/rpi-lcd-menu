from rpilcdmenu import RpiLCDMenu
from rpilcdmenu.rpi_lcd_hwd import RpiLCDHwd

class RpiLCDSubMenu(RpiLCDMenu):
    def __init__(self, base_menu):
        """
        Initialize SubMenu
        """
        self.lcd = RpiLCDHwd()
        self.scrolling_menu = base_menu.scrolling_menu
        self.lcd_queue = base_menu.lcd_queue

        super(RpiLCDMenu, self).__init__(base_menu)
