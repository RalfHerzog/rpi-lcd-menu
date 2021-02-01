import queue
import threading
from time import sleep
from RPLCD.i2c import CharLCD
from RPLCD.codecs import A02Codec as LCDCodec

from rpilcdmenu.base_menu import BaseMenu

class RpiLCDMenu(BaseMenu):
    def __init__(self, scrolling_menu=True):
        """
        Initialize menu
        """
        self.lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8, auto_linebreaks=True)
        self.scrolling_menu = scrolling_menu
        self.lcd_queue = queue.Queue(maxsize=0)
        self.maxWidth = 15
        self.lcdFrameRate = 0.05
        self.cursor_char = '\x07'

        threading.Thread(target=self.lcd_queue_processor).start()

        super(self.__class__, self).__init__()

    def custom_character(self, loc, char):
        self.lcd.create_char(loc, char)
        return self

    def home_lcd(self, var=None):
        self.lcd.home()
        return

    def write_to_lcd(self, framebuffer):
        for row in framebuffer:
#            self.lcd_queue.put((self.lcd.write_string, row.ljust(16)[:16]))
#            self.lcd_queue.put((self.lcd.write_string, '\r\n'))
            self.lcd.write_string(row.ljust(16)[:16])
            self.lcd.write_string('\r\n')

        return self

    def message(self, text, autoscroll=False, clear=True):
        if clear:
            self.lcd.clear()
        if type(text) == list:
            self.lcd_queue.put((self.write_to_lcd, text))
#            self.write_to_lcd(text)
        else:
            self.lcd_queue.put((self.lcd.write_string, text))
            self.lcd_queue.put((self.home_lcd,'None'))
#            self.lcd_queue.put((self.lcd.write_string, '\r\n'))
#            self.lcd_queue.put((self.lcd.write_string, '\r\n'))
#            self.lcd.write_string(text)

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
#            self.menu_scroller(text, cursor_pos, self.input_count)
            self.lcd_queue.put((self.menu_scroller, text, cursor_pos, self.input_count))
        else:
#            self.menu_static(text, cursor_pos)
            self.lcd_queue.put((self.menu_static, text, cursor_pos))
        return self

    def menu_static(self, text, cursor_pos):
        inactive_row = int(cursor_pos == 0 and "1" or "0")
        print('STATIC DISPLAY')
        print('cursor_pos: ' + str(cursor_pos))
        print('inactive_row: ' + str(inactive_row))
        framebuffer = ["",""]
        framebuffer[cursor_pos] = self.cursor_char + text[cursor_pos][:self.maxWidth]
        framebuffer[inactive_row] = ' ' + text[inactive_row][:self.maxWidth]
        print(framebuffer)
        self.write_to_lcd(framebuffer)
        return self

    def menu_scroller(self, text, cursor_pos, startInputCount):
        inactive_row = int(cursor_pos == 0 and "1" or "0")
        print('SCROLLING DISPLAY')
        print('cursor_pos: ' + str(cursor_pos))
        print('inactive_row: ' + str(inactive_row))
        if len(text[cursor_pos]) <= self.maxWidth:
            # Selected row of the menu fits on line; no need to scroll,
            # but we're going to truncate the bottom line if it's too long
            framebuffer = ["",""]
            framebuffer[cursor_pos] = self.cursor_char + text[cursor_pos]
            framebuffer[inactive_row] = ' ' + text[inactive_row][:self.maxWidth]
            print(framebuffer)
            self.write_to_lcd(framebuffer)
            return self

        # top line too long.. so animate until there's another input event
        aniPosition = 0
        while startInputCount == self.input_count:
            ### render partial menu text
            aniText = text[cursor_pos][aniPosition: aniPosition + self.maxWidth]
            # prepend cursor character in front of top menu item, blank space in front of bottom
            framebuffer = ["",""]
            framebuffer[cursor_pos] = self.cursor_char + aniText[:self.maxWidth]
            framebuffer[inactive_row] = ' ' + text[inactive_row][:self.maxWidth]
            # Send the framebuffer to the LCD
            self.write_to_lcd(framebuffer)
            print(framebuffer)
            ### determine next state
            if aniPosition == 0 or aniPosition == len(text[cursor_pos]) - self.maxWidth:
                delayFrames=25
            else:
                delayFrames=5

            aniPosition += 1
            # Restart the animation once the whole row has been scrolled
            if aniPosition >= (len(text[cursor_pos]) - self.maxWidth + 1):
                aniPosition = 0

            for _ in range(delayFrames):
                sleep(self.lcdFrameRate)
                if startInputCount != self.input_count:
                    break
#        self.lcd.clear()
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
