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

# for the dungoen generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

# fov values
FOV_ALGO = 0 # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

# 
LIMIT_FPS = 20

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110,50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

###########################################################
# Class definitions
###########################################################

class Tile:
  # a tile of the map and it's properties
  def __init__(self, blocked, block_sight = None):
    self.blocked = blocked

    # all tiles start unexplored
    self.explored = False

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

  def center(self):
    center_x = (self.x1 + self.x2) / 2
    center_y = (self.y1 + self.y2) / 2
    return (center_x, center_y)

  def intersect(self, other):
    # returns true if this rectangle intere=sects with another one
    return(self.x1 <= other.x2 and self.x2 >= other.x1 and
           self.y1 <= other.y2 and self.y2 >= other.y1)


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
    #only show if it's visible to the player
    if libtcod.map_is_in_fov(fov_map, self.x, self.y):
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

  rooms = []
  num_rooms = 0

  for r in range(MAX_ROOMS):
    # random width and height
    w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)

    # random position without going out of the boundaries of the map
    x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
    y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

    # "Rect" class makes rectangles easier to work with
    new_room = Rect(x, y, w, h)

    # run through the other ooms and see if they intersect with this one
    failed = False
    for other_room in rooms:
      if new_room.intersect(other_room):
        failed = True
        break

    if not failed:
      # this means there are no intersections, so this room is valid

      # "paint" it to the map's tiles
      create_room(new_room)

      # centre coordinates of new room, will be useful later
      (new_x, new_y) = new_room.center()

      #optional: print "room number" to see how the map drawing worked
      #          we may have more than ten rooms, so print 'A' for the first room, 'B' for the next...
      room_no = Object(new_x, new_y, chr(65+num_rooms), libtcod.white)
      objects.insert(0, room_no) #draw early, so monsters are drawn on top

      if num_rooms == 0:
        # this is the first room, where the player starts at
        player.x = new_x
        player.y = new_y
    
      else:
        # all rooms after the first:
        # connect it to the previous room with a tunnel

        # center coordinates of previous room
        (prev_x, prev_y) = rooms[num_rooms - 1].center()

        # draw a coin (random number that is either 0 or 1)
        if libtcod.random_get_int(0, 0, 1) == 1:
          # first move horizontally, then vertically
          create_h_tunnel(prev_x, new_x, prev_y)
          create_v_tunnel(prev_y, new_y, new_x)

        else:
          # first move vertically, then horizontally
          create_v_tunnel(prev_y, new_y, prev_x)
          create_h_tunnel(prev_x, new_x, new_y)

      # finally, append the new room to the list
      rooms.append(new_room)
      num_rooms += 1


#
def render_all():
  global color_dark_wall, color_light_wall
  global color_dark_ground, color_light_ground
  global fov_map, fov_recompute

  if fov_recompute:
    # recompute FOV if needed (the player moved or something)
    fov_recompute = False
    libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
 
    #go through all tiles, and set their background color
    for y in range(MAP_HEIGHT):
      for x in range(MAP_WIDTH):
        visible = libtcod.map_is_in_fov(fov_map, x, y)
        wall = ccmap[x][y].block_sight
        if not visible:
          # if it's not visible right now, the player can only see it if it's explored
          if ccmap[x][y].explored:
            # it's out of the player's FOV
            if wall:
              #libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
              libtcod.console_put_char_ex(con, x, y, '#', libtcod.white, color_dark_wall)
            else:
              #libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
              libtcod.console_put_char_ex(con, x, y, '.', libtcod.white, color_dark_ground)

        else:
          # it's visible
          if wall:
            #libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
            libtcod.console_put_char_ex(con, x, y, '#', libtcod.white, color_light_wall)
          else:
            #libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
            libtcod.console_put_char_ex(con, x, y, '.', libtcod.white, color_light_ground)
          # since it's visible, explore it
          ccmap[x][y].explored = True

  # draw all objects in the list
  for object in objects:
    object.draw()

  #blit the contents of "con" to the root console
  libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


# check for pressed keys, and update player position
def handle_keys():
  global fov_recompute

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
    fov_recompute = True

  elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
    player.move(0, 1)
    fov_recompute = True

  elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
    player.move(-1, 0)
    fov_recompute = True

  elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
    player.move(1,0)
    fov_recompute = True

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

# create the FOV map, according to the generated map
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not ccmap[x][y].block_sight, not ccmap[x][y].blocked)

# only need to recompute if the player moves, or a tile changes
fov_recompute = True

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
