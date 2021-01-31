import queue
import threading
import multiprocessing as mp
from time import sleep
from RPLCD.i2c import CharLCD
from RPLCD.codecs import A02Codec as LCDCodec

from rpilcdmenu.base_menu import BaseMenu

class RpiLCDMenu(BaseMenu):
    def __init__(self, scrolling_menu=False):
        """
        Initialize menu
        """
        self.lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8, auto_linebreaks=True)
        self.scrolling_menu = scrolling_menu
        self.lcd_queue = queue.Queue(maxsize=0)
        self.maxWidth = 15
        self.lcdFrameRate = 0.05

        threading.Thread(target=self.lcd_queue_processor).start()

        super(self.__class__, self).__init__()

    def write_to_lcd(self, framebuffer):
        for row in framebuffer:
            self.lcd.write_string(row.ljust(16)[:16])
            self.lcd.write_string('\r\n')

        return self

    def message(self, text, autoscroll=False):
        self.lcd.clear()
        if type(text) == list:
            self.write_to_lcd(text)
        else:
            self.lcd.write_string(text)

        return self

    def render(self):
        if len(self.items) == 0:
            self.message('Menu is empty')
            return self

        elif len(self.items) <= 2:
            text = [self.items[0].text, ""]
            cursor_pos = self.current_option
            if len(self.items) == 2:
                text[1] = self.items[1].text

        elif len(self.items) > 2:
            text = [self.items[self.current_option].text, ""]
            cursor_pos = 0
            if self.current_option + 1 < len(self.items):
                text[1] = self.items[self.current_option + 1].text
            else:
                text[1] = self.items[0].text

        if self.scrolling_menu:
            self.lcd_queue.put((self.menu_scroller, text, cursor_pos, self.current_option))
        else:
            self.lcd_queue.put((self.menu_static, text, cursor_pos))
        return self

    def menu_static(self, text, cursor_pos):
        inactive_row = int(cursor_pos == 0 and "1" or "0")
        framebuffer = ["",""]
        framebuffer[cursor_pos] = '>' + text[cursor_pos][:self.maxWidth]
        framebuffer[inactive_row] = ' ' + text[inactive_row][:self.maxWidth]
        self.write_to_lcd(framebuffer)
        return self

    def menu_scroller(self, text, cursor_pos, inputOption):
        inactive_row = int(cursor_pos == 0 and "1" or "0")

        print('cursor_pos: ' + str(cursor_pos))
        print('inactive_row: ' + str(inactive_row))
        if len(text[cursor_pos]) <= self.maxWidth:
            # Selected row of the menu fits on line; no need to scroll,
            # but we're going to truncate the bottom line if it's too long
            framebuffer = ["",""]
            framebuffer[cursor_pos] = '>' + text[cursor_pos]
            framebuffer[inactive_row] = ' ' + text[inactive_row][:self.maxWidth]
            print(framebuffer)
            self.write_to_lcd(framebuffer)
            return self

        # top line too long.. so animate until there's another input event
        aniPosition = 0
        print('inputOption is: ' + str(inputOption))
        print('self.current_option is: ' + str(self.current_option))
        while inputOption == self.current_option:
            ### render partial menu text
            aniText = text[cursor_pos][aniPosition: aniPosition + self.maxWidth]
            # prepend cursor character in front of top menu item, blank space in front of bottom
            framebuffer = ["",""]
            framebuffer[cursor_pos] = '>' + aniText[:self.maxWidth]
            framebuffer[inactive_row] = ' ' + text[1][:self.maxWidth]
            # Send the framebuffer to the LCD
            self.write_to_lcd(framebuffer)

            ### determine next state
            if aniPosition == 0 or aniPosition == len(text[0]) - self.maxWidth:
                delayFrames=25
            else:
                delayFrames=5

            aniPosition += 1
            # Restart the animation once the whole row has been scrolled
            if aniPosition >= (len(text[0]) - self.maxWidth + 1):
                aniPosition = 0

            for _ in range(delayFrames):
                sleep(self.lcdFrameRate)
                if inputOption != self.current_option:
                    break
        return self

    def lcd_queue_processor(self):
        # clear it once in case of existing corruption
        self.lcd.clear()

        # process the queue
        while True:
            items = self.lcd_queue.get()
            func = items[0]
            args = items[1:]
            func(*args)
