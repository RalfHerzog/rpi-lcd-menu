#!/usr/bin/python

"""
multi level menu
"""
import time

from rpilcdmenu import *
from rpilcdmenu.items import *


def main():
    menu = RpiLCDMenu()

    function_item1 = FunctionItem("Item 1", fooFunction, [1])
    function_item2 = FunctionItem("Item 2", fooFunction, [2])
    menu.append_item(function_item1).append_item(function_item2)

    submenu = RpiLCDSubMenu(menu)
    submenu_item = SubmenuItem("SubMenu (3)", submenu, menu)
    menu.append_item(submenu_item)

    submenu.append_item(FunctionItem("Item 31", fooFunction, [31])).append_item(
        FunctionItem("Item 32", fooFunction, [32]))
    submenu.append_item(FunctionItem("Back", exitSubMenu, [submenu]))

    menu.append_item(FunctionItem("Item 4", fooFunction, [4]))

    menu.start()
    menu.debug()
    print("----")
    # press first menu item and scroll down to third one
    menu = menu.processEnter()
    time.sleep(1)
    menu.lcd.backlight_enabled = False
    menu = menu.processDown()
    time.sleep(1)
    menu = menu.processDown()
    time.sleep(1)
    menu.lcd.backlight_enabled = True
    # enter submenu, press Item 32, press Back button
    menu = menu.processEnter()
    time.sleep(1)
    menu = menu.processDown()
    time.sleep(1)
    menu = menu.processEnter()
    time.sleep(1)
    menu = menu.processDown()
    time.sleep(1)
    menu = menu.processEnter()
    time.sleep(1)
    # press item4 back in the menu
    menu = menu.processDown()
    time.sleep(1)
    menu = menu.processEnter()
    time.sleep(1)

    # while not menu.lcd_queue.empty():
    #     time.sleep(0.1)
    # time.sleep(.5)
    # menu.clearDisplay()

    # # Show input dialog for password
    frame_buffer = ['Username:   ok-#', '']
    for char in 'Jon Doe':
        # menu.lcd_queue.put([menu._write_to_lcd, frame_buffer, False])
        menu.write_to_lcd(frame_buffer)
        frame_buffer[1] += char
        time.sleep(.5)

    # # Show input dialog for password
    frame_buffer = ['Passwort:   ok-#', '']
    for _ in range(5):
        # menu.lcd_queue.put([menu._write_to_lcd, frame_buffer, False])
        menu.write_to_lcd(frame_buffer)
        frame_buffer[1] += '*'
        time.sleep(.5)
    menu.write_to_lcd(['    Accepted!  ', 'Returning ...'])
    time.sleep(5)
    menu.start()


def fooFunction(item_index):
    """
	sample method with a parameter
	"""
    print("item %d pressed" % (item_index))


def exitSubMenu(submenu):
    return submenu.exit()


if __name__ == "__main__":
    main()
