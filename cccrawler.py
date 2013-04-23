#!/usr/bin/python
#
import os
import libtcodpy as libtcod

###########################################################
# Constant definitions
###########################################################

# screen size
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

# map size
MAP_WIDTH = 80
MAP_HEIGHT = 45

# 
LIMIT_FPS = 20

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

###########################################################
# Class definitions
###########################################################

class Tile:
  # a tile of the map and it's properties
  def __init__(self, blocked, block_sight = None):
    self.blocked = blocked

    # by default, if a tile is blocked, it also blocks sight
    if block_sight is None: block_sight = blocked
    self.block_sight = block_sight


class Rect:
  # a rectangle on the map. used to characterize a room.
  def __init__(self, x, y, w, h):
    self.x1 = x
    self.y1 = y
    self.x2 = x + w
    self.y2 = y + h


class Object:
  #this is a generic object: the player, a monster, an item, the stairs...
  #it's always represented by a character on screen.
  def __init__(self, x, y, char, color):
    self.x = x
    self.y = y
    self.char = char
    self.color = color
 
  def move(self, dx, dy):
    #check we're not trying to walk into something, like a pillar
    if not ccmap[self.x + dx][self.y + dy].blocked:
      #move by the given amount
      self.x += dx
      self.y += dy
 
  def draw(self):
    #set the color and then draw the character that represents this object at its position
    libtcod.console_set_default_foreground(con, self.color)
    libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
 
  def clear(self):
    #erase the character that represents this object
    libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

###########################################################
# Function definitions
###########################################################

#
def create_room(room):
  global ccmap
  
  # go through the tiles in the rectangle and make them passable
  for x in range(room.x1 + 1, room.x2):
    for y in range(room.y1 + 1, room.y2):
      ccmap[x][y].blocked = False
      ccmap[x][y].block_sight = False


#
def create_h_tunnel(x1, x2, y):
  global ccmap
  
  # horizontal tunnel. min() and max() are used in case x1>x2
  for x in range(min(x1, x2), max(x1, x2) + 1):
    ccmap[x][y].blocked = False
    ccmap[x][y].block_sight = False


#
def create_v_tunnel(y1, y2, x):
  global ccmap
  
  # vertical tunnel
  for y in range(min(y1, y2), max(y1, y2) + 1):
    ccmap[x][y].blocked = False
    ccmap[x][y].block_sight = False


#
def make_map():
  global ccmap

  # fill map with "blocked" tiles
  ccmap = [[ Tile(True)
    for y in range(MAP_HEIGHT) ]
      for x in range(MAP_WIDTH) ]

  #create two rooms
  room1 = Rect(20, 15, 10, 15)
  room2 = Rect(50, 15, 10, 15)
  create_room(room1)
  create_room(room2)

  # create a tunnel to join the two rooms
  create_h_tunnel(25, 55, 23)
  
  # place in center of first room
  player.x = 25
  player.y = 23


#
def render_all():
  global color_light_wall
  global color_light_ground
 
  #go through all tiles, and set their background color
  for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
      wall = ccmap[x][y].block_sight
      if wall:
        #libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
        libtcod.console_put_char_ex(con, x, y, '#', libtcod.white, color_dark_wall)
      else:
        #libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
        libtcod.console_put_char_ex(con, x, y, '.', libtcod.white, color_dark_ground)

  # draw all objects in the list
  for object in objects:
    object.draw()

  #blit the contents of "con" to the root console
  libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


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
    player.move(0, -1)

  elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
    player.move(0, 1)

  elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
    player.move(-1, 0)

  elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
    player.move(1,0)

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
libtcod.sys_set_fps(LIMIT_FPS)
 
#create object representing the player
player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white)
 
#create an NPC
npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', libtcod.yellow)
 
#the list of objects with those two
objects = [npc, player]

#generate map (at this point it's not drawn to the screen)
make_map()

# main game loop, runs until the window is closed
while not libtcod.console_is_window_closed():
  
  #render the screen
  render_all()
  
  libtcod.console_flush()
 
  #erase all objects at their old locations, before they move
  for object in objects:
    object.clear()
  
  # handle keys and exit game if needed
  exit = handle_keys()
  if exit:
    break
