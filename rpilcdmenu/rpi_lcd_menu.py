import queue
import threading
import multiprocessing as mp
from time import sleep
from RPLCD.i2c import CharLCD
from RPLCD.codecs import A02Codec as LCDCodec

from rpilcdmenu.base_menu import BaseMenu

all_processes = []

class RpiLCDMenu(BaseMenu):
    def __init__(self, scrolling_menu=False):
        """
        Initialize menu
        """
        self.lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8, auto_linebreaks=True)
        self.scrolling_menu = scrolling_menu
        self.lcd_queue = queue.Queue(maxsize=0)

        threading.Thread(target=self.reader_proc).start()

        self.lcd.clear()

        super(self.__class__, self).__init__()

        self.event_handler.link(self.exit_loop, 'onInput')

    def exit_loop(self, msg=None):
        if self.scrolling_menu:
            for process in all_processes:
                process.terminate()
            all_processes.clear()
        return self

    def write_to_lcd(self, framebuffer):
        for row in framebuffer:
            self.lcd.write_string(row.ljust(16)[:16])
            self.lcd.write_string('\r\n')

        return self

    def loop_string(self, display_items, row_to_scroll):
        framebuffer = [
            display_items[0],
            display_items[1],
        ]
        if len(display_items[int(row_to_scroll)]) > 16:
            if self.scrolling_menu:
                framebuffer[int(0 == 0 and "1" or "0")] = display_items[int(0 == 0 and "1" or "0")][:16]
                s = display_items[row_to_scroll][1:]
                while True:
                    for i in range(len(s) - 15 + 1):
                        framebuffer[row_to_scroll] = '>' + s[i:i+15]
                        self.write_to_lcd(framebuffer)
                        print(framebuffer)
                        print(i)
                        if i == 0 or i == len(s) - 15:
                            print('slow')
                            delay=1.5
                        else:
                            print('fast')
                            delay=0.15
                        sleep(delay)
            else:
                framebuffer = [display_items[0][:16], display_items[1][:16]]
                self.write_to_lcd(framebuffer)
                return self
        else:
            self.write_to_lcd(framebuffer)
        return self

    def scroller(self, text):
        self.lcd.clear()
        while True:
            self.loop_string(text, 0)
        return self

    def message(self, text, autoscroll=False):
        self.lcd.clear()
        if type(text) == list:
            self.write_to_lcd(text)
        else:
            self.lcd.write_string(text)

        return self

    def render(self):
        """
        Render menu
        """
        self.exit_loop()
        self.lcd.clear()

        if len(self.items) == 0:
            self.lcd.write_string('Menu is empty')
            return self

        if len(self.items) <= 2:
            display_items = [(self.current_option == 0 and ">" or " ") + self.items[0].text, ""]
            cursor_pos = self.current_option
            if len(self.items) == 2:
                display_items[1] = (self.current_option == 1 and ">" or " ") + self.items[1].text

        if len(self.items) > 2:
            display_items = [">" + self.items[self.current_option].text, ""]
            cursor_pos = 0
            if self.current_option + 1 < len(self.items):
                display_items[1] = " " + self.items[self.current_option + 1].text[:15]
            else:
                display_items[1] = " " + self.items[0].text[:15]

        process=[self.loop_string, display_items, cursor_pos]
        self.lcd_queue_processor(process)

        return self

    def lcd_queue_processor(self, process):
        func = process[0]
        args = process[1:]
        clear = mp.Process(target=self.lcd.clear())
        enqueue = mp.Process(target=func, args=(args))
        self.lcd_queue.put(clear)
        self.lcd_queue.put(enqueue)
        all_processes.append(enqueue)

        return self

    def reader_proc(self):
        print('[2] reader_proc executed...')
        while True:
            process = self.lcd_queue.get()
            process.start()
            all_processes.append(process)
            process.join()
