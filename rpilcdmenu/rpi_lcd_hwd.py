import threading
import time
import queue
from queue import Empty
import signal
import threading

from RPLCD.i2c import CharLCD


class RpiLcdProcessor(threading.Thread):
    def __init__(self):
        super().__init__()

        self.lcd = CharLCD(
            i2c_expander="PCF8574", address=0x27, port=1,
            cols=16, rows=2, dotsize=8, auto_linebreaks=True,
        )
        self.lcd.clear()
        self._queue = queue.Queue(maxsize=0)

    def run(self) -> None:
        """
        Process all LCD write commands through a queue to prevent
        display corruption.
        """
        while True:
            items = self._queue.get()
            if items is None:
                break
            func = items[0]
            args = items[1:]
            func(*args)

    def stop(self):
        # self._p.terminate()
        self._queue.put(None)
        self.join()

    def put(self, *args):
        self._queue.put(*args)


if __name__ == "__main__":
    def test(*args):
        print(f"test called with arguments {args}")


    rpi_lcd_processor = RpiLcdProcessor()
    rpi_lcd_processor.start()
    rpi_lcd_processor.put([test, [1, 'Test']])

    time.sleep(1)
    print(rpi_lcd_processor)
    rpi_lcd_processor.stop()
    time.sleep(1)
    print(rpi_lcd_processor)

    print("end")
    time.sleep(5)
