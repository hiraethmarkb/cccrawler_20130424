# import needed libs
import libtcodpy as libtcod

# set some constants
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

# set font
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

# initialize window
libt.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'CC Crawler', False)

# we're going real-time, so limit game speed
libtcod.sys_set_fps(LIMIT_FPS)

# main game loop, runs until the window is closed
while not libtcod.console_is_window_closed():
  # set text colour to white
  libtcod.console_set_default_foreground(0, libtcod.white)
  # character starting position
  libtcod.console_put_char(0, 1, 1, '@', libtcod.BKGND_NONE)
  # flush console, to output to screen
  libtcod.console_flush()
