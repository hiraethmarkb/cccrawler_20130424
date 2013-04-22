#!/usr/bin/python
#
import os
import libtcodpy as libtcod

# set some constants
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

# check for pressed keys, and update player position
def handle_keys():
  global playerx, playery

  #key = libtcod.console_check_for_keypress()  #real-time
  key = libtcod.console_wait_for_keypress(True)  #turn-based
  if key.vk == libtcod.KEY_ENTER and key.lalt:
    # Alt+Enter: toggle fullscreen
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

  elif key.vk == libtcod.KEY_ESCAPE:
    return True # exit game

  # movement keys
  if libtcod.console_is_key_pressed(libtcod.KEY_UP):
    playery -= 1

  elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
    playery += 1

  elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
    playerx -= 1

  elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
    playerx += 1

###########################################################
# Initialization & Main Loop
###########################################################

# set font
font = os.path.join('data', 'fonts', 'arial10x10.png')
libtcod.console_set_custom_font(font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
# initialize window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'CodeCumbria Crawler', False)
# create new off-screen console, for drawing stuff
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
# we're going real-time, so limit game speed
#libtcod.sys_set_fps(LIMIT_FPS)
 
# create variables for tracking the players position
playerx = SCREEN_WIDTH/2
playery = SCREEN_WIDTH/2

# main game loop, runs until the window is closed
while not libtcod.console_is_window_closed():
  # set text colour to white
  libtcod.console_set_default_foreground(con, libtcod.white)
  # character starting position
  libtcod.console_put_char(con, 1, 1, '@', libtcod.BKGND_NONE)

  libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

  # flush console, to output to screen
  libtcod.console_flush()

  libtcod.console_put_char(con, playerx, playery, ' ', libtcod.BKGND_NONE)

  # handle keys and exit game if needed
  exit = handle_keys()
  if exit:
    break
