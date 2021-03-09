import queue
import threading
from time import sleep
from RPLCD.i2c import CharLCD
from RPLCD.codecs import A02Codec as LCDCodec
from rpilcdmenu.base_menu import BaseMenu


class RpiLCDMenu(BaseMenu):
    """ Class to create and set up the main menu object. """

    def __init__(self, scrolling_menu=True):
        """
        Initialize the menu. Communication with the LCD hardware is
        handled by the RPLCD module. By default, if the text of the current
        menu item is longer than the display width, it will scroll right-to-
        left, pause momentarily, and then repeat. Set 'scrolling_menu' to
        False to disable this animation and simply truncate the extra
        characters.
        """
        self.lcd = CharLCD(
            i2c_expander="PCF8574",
            address=0x27,
            port=1,
            cols=16,
            rows=2,
            dotsize=8,
            auto_linebreaks=True,
        )
        self.lcd_framerate = 0.05  # Interval to listen for input during menu scrolling
        self.cursor_char = ">"  # Character for menu selector

        self.scrolling_menu = scrolling_menu
        self.lcd_queue = queue.Queue(maxsize=0)
        self.max_width = 15

        threading.Thread(target=self._lcd_queue_processor).start()

        super().__init__()

    def custom_character(self, loc, char):
        """
        Define a custom display character in LCD CG-RAM.
        loc: The CG-RAM location to which to write (e.g. '\x03')
        char: A tuple containing the bitmap representing the character
        For more info, see:
        https://rplcd.readthedocs.io/en/stable/usage.html#creating-custom-characters
        """
        self.lcd.create_char(loc, char)
        return self

    def home_lcd(self, *args):
        """ Reset LCD cursor to starting position. """
        self.lcd.home()

    def write_to_lcd(self, framebuffer):
        """
        Method to write out the formatted framebuffer to the LCD.
        framebuffer: A list whose elements are the strings to be written to the LCD
        """
        for row in framebuffer:
            self.lcd.write_string(row.ljust(16)[:16])
            self.lcd.write_string("\r\n")
        return self

    def message(self, text, clear=True):
        """
        Method to display a static message on the LCD.
        text: String containing the message text to be displayed
        clear: If false, will not clear the display first
        """
        if clear:
            self.lcd.clear()
        if isinstance(text, list):
            self.lcd_queue.put((self.write_to_lcd, text))
        else:
            self.lcd_queue.put((self.lcd.write_string, text))
            self.lcd_queue.put((self.home_lcd, ""))
        return self

    def render(self):
        """
        Pre-format the menu elements to be displayed. The elements are
        then fed either to _menu_static if the menu's 'scrolling_menu'
        attribute is False, or to _menu_scroller if True.
        """
        if len(self.items) == 0:
            self.message("Menu is empty")
            return self

        if len(self.items) <= 2:
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
            self.lcd_queue.put(
                (self._menu_scroller, text, cursor_pos, self.input_count)
            )
        else:
            self.lcd_queue.put((self._menu_static, text, cursor_pos))
        return self

    def _menu_static(self, text, cursor_pos):
        """
        Receive pre-formatted menu elements from render, generate final
        framebuffer for a fixed, non-scrolling menu with indicator cursor,
        and send it to write_to_lcd.
        """
        inactive_row = int(cursor_pos == 0 and "1" or "0")
        print("STATIC DISPLAY")
        print("cursor_pos: " + str(cursor_pos))
        print("inactive_row: " + str(inactive_row))
        framebuffer = ["", ""]
        framebuffer[cursor_pos] = self.cursor_char + text[cursor_pos][: self.max_width]
        framebuffer[inactive_row] = " " + text[inactive_row][: self.max_width]
        print(framebuffer)
        self.write_to_lcd(framebuffer)
        return self

    def _menu_scroller(self, text, cursor_pos, start_input_count):
        """
        Receive pre-formatted menu elements from render, generate frames
        to animate a scrolling menu with indicator cursor, and send each
        frame of the animated menu to write_to_lcd.
        """
        inactive_row = int(cursor_pos == 0 and "1" or "0")
        print("SCROLLING DISPLAY")
        print("cursor_pos: " + str(cursor_pos))
        print("inactive_row: " + str(inactive_row))
        if len(text[cursor_pos]) <= self.max_width:
            # Selected row of the menu fits on line; no need to scroll,
            # but we're going to truncate the bottom line if it's too long
            framebuffer = ["", ""]
            framebuffer[cursor_pos] = self.cursor_char + text[cursor_pos]
            framebuffer[inactive_row] = " " + text[inactive_row][: self.max_width]
            print(framebuffer)
            self.write_to_lcd(framebuffer)
            return self

        # top line too long.. so animate until there's another input event
        ani_pos = 0
        while start_input_count == self.input_count:
            # Render partial menu text
            ani_text = text[cursor_pos][ani_pos : ani_pos + self.max_width]
            # Prepend cursor character in front of top menu item, pad bottom item
            framebuffer = ["", ""]
            framebuffer[cursor_pos] = self.cursor_char + ani_text[: self.max_width]
            framebuffer[inactive_row] = " " + text[inactive_row][: self.max_width]
            # Send the framebuffer to the LCD
            self.write_to_lcd(framebuffer)
            # Determine next animation state
            if ani_pos in (0, len(text[cursor_pos]) - self.max_width):
                delay_frames = 25
            else:
                delay_frames = 5
            ani_pos += 1
            # Restart the animation once the whole row has been scrolled
            if ani_pos >= (len(text[cursor_pos]) - self.max_width + 1):
                ani_pos = 0

            # Watch for input during "pause" so interface remains responsive
            for _ in range(delay_frames):
                sleep(self.lcd_framerate)
                if start_input_count != self.input_count:
                    break
        return self

    def _lcd_queue_processor(self):
        """
        Process all LCD write commands through a queue to prevent
        display corruption.
        """
        self.lcd.clear()
        while True:
            items = self.lcd_queue.get()
            func = items[0]
            args = items[1:]
            func(*args)
