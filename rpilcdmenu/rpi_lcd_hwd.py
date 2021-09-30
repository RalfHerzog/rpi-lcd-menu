import queue
import threading
from RPLCD.i2c import CharLCD


class RpiLcdProcessor(threading.Thread):
    def __init__(self):
        super().__init__()

        self.lcd = CharLCD(
            i2c_expander="PCF8574",
            address=0x27,
            port=1,
            cols=16,
            rows=2,
            dotsize=8,
            auto_linebreaks=True,
        )
        self.lcd_queue = queue.Queue(maxsize=0)

    def run(self) -> None:
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


rpi_lcd_processor = RpiLcdProcessor()
rpi_lcd_processor.start()
