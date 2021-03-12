import queue
import threading
from RPLCD.i2c import CharLCD

lcd = CharLCD(
    i2c_expander="PCF8574",
    address=0x27,
    port=1,
    cols=16,
    rows=2,
    dotsize=8,
    auto_linebreaks=True,
)

lcd_queue = queue.Queue(maxsize=0)

def _lcd_queue_processor():
    """
    Process all LCD write commands through a queue to prevent
    display corruption.
    """
    lcd.clear()
    while True:
        items = lcd_queue.get()
        func = items[0]
        args = items[1:]
        func(*args)

threading.Thread(target=_lcd_queue_processor).start()
