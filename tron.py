#!/usr/bin/env python3

# Board is 128x72 cells
# Cells are 10px*10px
# Window size is 1280x720

# Trail queue is 250? TBD

import pyglet
from pyglet.window import key
import socket
import sys

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

	    # Set up connection to server
        TCP_IP = sys.argv[1]
        TCP_PORT = 1025
        self.BUFFER_SIZE = 1024

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((TCP_IP, TCP_PORT))

        self.pnum = int(self.s.recv(self.BUFFER_SIZE).decode()[1])

	    # stores image from previous branch
        self.prev_frame = None

        self.running = True
        self.sending = True

        self.movement = "u"
        self.players = [player.Player(int(BOARDWIDTH/4),   int(BOARDHEIGHT/4*3)),
                        player.Player(int(BOARDWIDTH/4*3), int(BOARDHEIGHT/4*3)),
                        player.Player(int(BOARDWIDTH/4),   int(BOARDHEIGHT/4)),
                        player.Player(int(BOARDWIDTH/4*3), int(BOARDHEIGHT/4))]
        # Players that have collided with something
        self.deadPlayers = set()
        # Players that have been been erased from the board
        self.removedPlayers = set()
        pyglet.clock.schedule_interval(self.update, .025)

        if self.pnum==0+1:
            pcolor = "RED"
        elif self.pnum==1+1:
            pcolor = "BLUE"
        elif self.pnum==2+1:
            pcolor = "GREEN"
        elif self.pnum==3+1:
            pcolor = "PURPLE"

        self.label = pyglet.text.Label('Your color is: ' + pcolor, x=self.width/2, y=self.height-20)

        # For windows: makes window not appear to be not responding
        self.flip()

        # Wait for server to notify to start
        if not self.s.recv(self.BUFFER_SIZE).decode().strip() == "s":
            print("Something went wrong...")
            exit()
        else:
            print("Starting game...")

    def update(self, dt):
        if not self.running:
            exit()

        # Send move to server
        if self.sending:
            self.s.send("{0}{1}".format(self.movement, str(self.pnum)).encode())

        movesList = self.s.recv(self.BUFFER_SIZE).decode()
        for p in range(0,4):
            if movesList[p] == "k":
                pass
            if movesList[p] == "u":
                self.players[p].move_ip(0, 1)
            elif movesList[p] == "l":
                self.players[p].move_ip(-1, 0)
            elif movesList[p] == "r":
                self.players[p].move_ip(1, 0)
            elif movesList[p] == "d":
                self.players[p].move_ip(0, -1)

    def check_players_collide_wall(self):

        deadPlayers = set()

        for pnum in range(len(self.players)):
            if pnum not in self.deadPlayers:
                curpos = tuple(self.players[pnum].pos)
                if curpos[0] < 0 or curpos[0] >= BOARDWIDTH or\
                curpos[1] < 0 or curpos[1] >= BOARDHEIGHT:
                        deadPlayers.add(pnum)

        return deadPlayers

    def check_players_collide_players(self):

        deadPlayers = set()

        for pnum in range(len(self.players)):
            if pnum not in self.deadPlayers:
                curpos = tuple(self.players[pnum].pos)
                for pnum2 in range(len(self.players)):
                    if pnum2 not in self.deadPlayers:
                        if curpos in self.players[pnum2].trail:
                            deadPlayers.add(pnum)
                            break

        return deadPlayers

    def create_quad_vertex_list(self, x, y):
        return (x*CELLSIZE,            y*CELLSIZE,
                x*CELLSIZE + CELLSIZE, y*CELLSIZE,
                x*CELLSIZE + CELLSIZE, y*CELLSIZE + CELLSIZE,
                x*CELLSIZE,            y*CELLSIZE + CELLSIZE)

    def create_quad_color_list(self, color):
        return color*4


    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.movement = "u"
        elif symbol == key.A:
            self.movement = "l"
        elif symbol == key.D:
            self.movement = "r"
        elif symbol == key.S:
            self.movement = "d"
        elif symbol == key.ESCAPE:
            self.running = False

    def on_draw(self):
        # Save time by drawing black quad over removed trail cells
        # This way all trail cells do not need to be drawn every step

        # draw previous frame buffer to screen
        if self.prev_frame != None:
            self.prev_frame.blit(0,0)

        self.label.draw()

        for pnum in range(len(self.players)):

            if pnum not in self.removedPlayers:
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

                if pnum in self.deadPlayers:
                    # Remove player
                    vertex_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(
                                                                    self.players[pnum].pos[0],
                                                                    self.players[pnum].pos[1])),
                                                                ('c3B', self.create_quad_color_list(BLACK)))
                    vertex_list.draw(pyglet.gl.GL_QUADS)

                    # Remove trail
                    for del_x,del_y in self.players[pnum].trail:
                        trail_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(del_x, del_y)),
                                                                        ('c3B', self.create_quad_color_list(BLACK)))
                        trail_list.draw(pyglet.gl.GL_QUADS)
                    self.removedPlayers.add(pnum)
                else:
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


        self.deadPlayers = self.deadPlayers.union(self.check_players_collide_players())
        self.deadPlayers = self.deadPlayers.union(self.check_players_collide_wall())

        # Stop sending and let server take control when player dies
        if (self.pnum-1) in self.deadPlayers and self.sending:
            self.s.send("{0}{1}".format("k", str(self.pnum)).encode())
            self.sending = False

        if len(self.deadPlayers) == 3:
            for pnum in range(len(self.players)):
                if pnum not in self.deadPlayers:
                    pyglet.text.Label('Player #{0} wins!!!'.format(str(pnum+1)), x=self.width/2, y=self.height/2).draw()


        # saves current framebuffer image
        self.prev_frame = pyglet.image.get_buffer_manager().get_color_buffer().get_image_data()



if __name__ == "__main__":

    tronwindow = TronWindow()
    pyglet.app.run()
