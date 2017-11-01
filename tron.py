#!/usr/bin/env python3

# Board is 128x72 cells
# Cells are 10px*10px
# Window size is 1280x720

# Trail queue is 250? TBD

import pyglet
from pyglet.window import key

import player

CELLSIZE = 10
BOARDWIDTH = 128
BOARDHEIGHT = 72

RED = (255, 0, 0)
LIGHTRED = (255, 125, 125)
BLUE = (0, 0, 255)
LIGHTBLUE = (125, 125, 255)
GREEN = (0, 255, 0)
LIGHTGREEN = (125, 255, 125)
PURPLE = (255, 0, 255)
LIGHTPURPLE = (255, 125, 255)
BLACK = (0, 0, 0)

class TronWindow(pyglet.window.Window):
    def __init__(self):
        super(TronWindow, self).__init__(width=BOARDWIDTH*CELLSIZE, height=BOARDHEIGHT*CELLSIZE,
                                         resizable=False, fullscreen=False)

	# stores image from previous branch
        self.prev_frame = None

        self.running = True

        self.players = [player.Player(int(BOARDWIDTH/4),   int(BOARDHEIGHT/4)),
                        player.Player(int(BOARDWIDTH/4*3), int(BOARDHEIGHT/4))]
#                        player.Player(int(BOARDWIDTH/4),   int(BOARDHEIGHT/4*3)),
#                        player.Player(int(BOARDWIDTH/4*3), int(BOARDHEIGHT/4*3))]

        self.movement1 = "up"
        self.movement2 = "up"

        pyglet.clock.schedule_interval(self.update, .03)

        #pyglet.clock.set_fps_limit(60)
        #self.map = Map()

        self.label = pyglet.text.Label('Hello, world!', x=self.width/2, y=self.height/2)

    def update(self, dt):
        if not self.running:
            exit()

        # Player 1
        # WASD
        if self.movement1 == "up":
            self.players[0].move_ip(0, 1)
        elif self.movement1 == "left":
            self.players[0].move_ip(-1, 0)
        elif self.movement1 == "right":
            self.players[0].move_ip(1, 0)
        elif self.movement1 == "down":
            self.players[0].move_ip(0, -1)

        # Player 2
        # Arrow keys
        if self.movement2 == "up":
            self.players[1].move_ip(0, 1)
        elif self.movement2 == "left":
            self.players[1].move_ip(-1, 0)
        elif self.movement2 == "right":
            self.players[1].move_ip(1, 0)
        elif self.movement2 == "down":
            self.players[1].move_ip(0, -1)

#        # Player 3
#        # WASD
#        if self.movement1 == "up":
#            self.players[2].move_ip(0, 1)
#        elif self.movement1 == "left":
#            self.players[2].move_ip(-1, 0)
#        elif self.movement1 == "right":
#            self.players[2].move_ip(1, 0)
#        elif self.movement1 == "down":
#            self.players[2].move_ip(0, -1)

#        # Player 4
#        # Arrow keys
#        if self.movement2 == "up":
#            self.players[3].move_ip(0, 1)
#        elif self.movement2 == "left":
#            self.players[3].move_ip(-1, 0)
#        elif self.movement2 == "right":
#            self.players[3].move_ip(1, 0)
#        elif self.movement2 == "down":
#            self.players[3].move_ip(0, -1)

    def check_players_collide_wall(self):

        for pnum in range(len(self.players)):
            curpos = tuple(self.players[pnum].pos)
            if curpos[0] < 0 or curpos[0] >= BOARDWIDTH or\
               curpos[1] < 0 or curpos[1] >= BOARDHEIGHT:
                print("Collides")
                return True


    def check_players_collide_players(self):

        for pnum in range(len(self.players)):
            curpos = tuple(self.players[pnum].pos)
            for pnum2 in range(len(self.players)):
                if curpos in self.players[pnum2].trail:
                    print("Collides")
                    return True

    def create_quad_vertex_list(self, x, y):
        return (x*CELLSIZE,            y*CELLSIZE,
                x*CELLSIZE + CELLSIZE, y*CELLSIZE,
                x*CELLSIZE + CELLSIZE, y*CELLSIZE + CELLSIZE,
                x*CELLSIZE,            y*CELLSIZE + CELLSIZE)

    def create_quad_color_list(self, color):
        return color*4

    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.movement1 = "up"
        elif symbol == key.A:
            self.movement1 = "left"
        elif symbol == key.D:
            self.movement1 = "right"
        elif symbol == key.S:
            self.movement1 = "down"

        elif symbol == key.UP:
            self.movement2 = "up"
        elif symbol == key.LEFT:
            self.movement2 = "left"
        elif symbol == key.RIGHT:
            self.movement2 = "right"
        elif symbol == key.DOWN:
            self.movement2 = "down"
        elif symbol == key.ESCAPE:
            self.running = False

    def on_draw(self):
        # Save time by drawing black quad over removed trail cells
        # This way all trail cells do not need to be drawn every step

        # draw previous frame buffer to screen
        if self.prev_frame != None:
            self.prev_frame.blit(0,0)

        for pnum in range(len(self.players)):

            if pnum==0:
                color1=RED
                color2=LIGHTRED
            elif pnum==1:
                color1=BLUE
                color2=LIGHTBLUE
            elif pnum==2:
                color1=GREEN
                color2=LIGHTGREEN
            elif pnum==3:
                color1=PURPLE
                color2=LIGHTPURPLE

            # Draw player
            vertex_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(
                                                            self.players[pnum].pos[0],
                                                            self.players[pnum].pos[1])),
                                                        ('c3B', self.create_quad_color_list(color1)))
            vertex_list.draw(pyglet.gl.GL_QUADS)

            # Draw trail
            if len(self.players[pnum].trail) > 0:
                if len(self.players[pnum].trail) > 250:
                    del_x, del_y = self.players[pnum].trail.pop(0)
                    trail_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(del_x, del_y)),
                                                                    ('c3B', self.create_quad_color_list(BLACK)))
                    trail_list.draw(pyglet.gl.GL_QUADS)
                new_x = self.players[pnum].trail[-1][0]
                new_y = self.players[pnum].trail[-1][1]
                trail_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(new_x, new_y)),
                                                                ('c3B', self.create_quad_color_list(color2)))
                trail_list.draw(pyglet.gl.GL_QUADS)

        # saves current framebuffer image
        self.prev_frame = pyglet.image.get_buffer_manager().get_color_buffer().get_image_data()

        if self.check_players_collide_players() or self.check_players_collide_wall():
            exit()

if __name__ == "__main__":

    tronwindow = TronWindow()
    pyglet.app.run()
