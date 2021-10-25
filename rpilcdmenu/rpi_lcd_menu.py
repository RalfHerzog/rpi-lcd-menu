from time import sleep
from rpilcdmenu.base_menu import BaseMenu
from rpilcdmenu.rpi_lcd_hwd import RpiLcdProcessor
import logging


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
        super().__init__()
        self.logger = logging

        self.lcd_framerate = 0.05  # Interval to listen for input during menu scrolling
        self.cursor_char = ">"  # Character for menu selector

        try:
            self.rpi_lcd_processor
        except AttributeError:
            self.rpi_lcd_processor = RpiLcdProcessor()
            self.rpi_lcd_processor.start()

        self.lcd = self.rpi_lcd_processor.lcd

        self.scrolling_menu = scrolling_menu
        self.max_width = 15

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

    def write_to_lcd(self, frame_buffer, clear=False):
        self.rpi_lcd_processor.put([self._write_to_lcd, frame_buffer, clear])

    def _write_to_lcd(self, framebuffer, clear=False):
        """
        Method to write out the formatted framebuffer to the LCD.
        framebuffer: A list whose elements are the strings to be written to the LCD
        """
        if clear:
            self.lcd.clear()
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
        if isinstance(text, list):
            self.rpi_lcd_processor.put([self._write_to_lcd, text, clear])
        else:
            self.rpi_lcd_processor.put([self.lcd.write_string, text])
            self.rpi_lcd_processor.put([self.lcd.home])
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
            text = [self.items[0].text]
            cursor_pos = self.current_option
            if len(self.items) == 2:
                text.append(self.items[1].text)

        else:
            text = [self.items[self.current_option].text]
            cursor_pos = 0
            if self.current_option + 1 < len(self.items):
                text.append(self.items[self.current_option + 1].text)
            else:
                text.append(self.items[0].text)

        if len(text[cursor_pos]) <= self.max_width:
            return self._menu_static(text, cursor_pos)

        if self.scrolling_menu:
            self.rpi_lcd_processor.put([self._menu_scroller, text, cursor_pos, self.input_count])
            return self

        return self._menu_static(text, cursor_pos)

    def _menu_static(self, text, cursor_pos):
        """
        Receive pre-formatted menu elements from render, generate final
        framebuffer for a fixed, non-scrolling menu with indicator cursor,
        and send it to write_to_lcd.
        """
        inactive_row = int(cursor_pos == 0 and "1" or "0")
        self.logger.debug("STATIC DISPLAY")
        self.logger.debug("cursor_pos: " + str(cursor_pos))
        self.logger.debug("inactive_row: " + str(inactive_row))
        framebuffer = ["", ""]
        framebuffer[cursor_pos] = self.cursor_char + text[cursor_pos][: self.max_width]
        framebuffer[inactive_row] = " " + text[inactive_row][: self.max_width]
        self.logger.debug(framebuffer)
        self.rpi_lcd_processor.put([self._write_to_lcd, framebuffer])
        return self

    def _menu_scroller(self, text, cursor_pos, start_input_count):
        """
        Receive pre-formatted menu elements from render, generate frames
        to animate a scrolling menu with indicator cursor, and send each
        frame of the animated menu to write_to_lcd.
        """
        inactive_row = int(cursor_pos == 0 and "1" or "0")
        self.logger.debug("SCROLLING DISPLAY")
        self.logger.debug("cursor_pos: " + str(cursor_pos))
        self.logger.debug("inactive_row: " + str(inactive_row))
        # top line too long.. so animate until there's another input event
        ani_pos = 0
        while start_input_count == self.input_count and self.scrolling_menu:
            # Render partial menu text
            ani_text = text[cursor_pos][ani_pos: ani_pos + self.max_width]
            # Prepend cursor character in front of top menu item, pad bottom item
            framebuffer = ["", ""]
            framebuffer[cursor_pos] = self.cursor_char + ani_text[: self.max_width]
            framebuffer[inactive_row] = " " + text[inactive_row][: self.max_width]
            # Send the framebuffer to the LCD
            self._write_to_lcd(framebuffer)
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

    def stop(self):
        self.rpi_lcd_processor.stop()