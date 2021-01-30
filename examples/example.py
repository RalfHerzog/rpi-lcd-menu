#!/usr/bin/python

"""
test if lcd display is connected to raspberry on default pins 
"""

from rpilcdmenu import *

def main():
	menu = RpiLCDMenu(scrolling_menu = True)
	menu.message('Hello world!')

if __name__ == "__main__":
	main()
