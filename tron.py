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
BLACK = (0, 0, 0)

# Use single buffer
# TODO Use double-buffer but copy previous frame to image and render to new frame?
config = pyglet.gl.Config(double_buffer=False)

class TronWindow(pyglet.window.Window):
    def __init__(self):
        super(TronWindow, self).__init__(width=BOARDWIDTH*CELLSIZE, height=BOARDHEIGHT*CELLSIZE,
                                         resizable=False, fullscreen=False,
                                         config=config)
        self.running = True

        self.player1 = player.Player(0, 0)

        self.movement = "up"

        #pyglet.clock.schedule_interval(self.update, .5)
        pyglet.clock.schedule_interval(self.update, .03)

        #pyglet.clock.set_fps_limit(60)
        #self.map = Map()

        self.label = pyglet.text.Label('Hello, world!', x=self.width/2, y=self.height/2)

    def update(self, dt):
        if not self.running:
            exit()

        if self.movement == "up":
            self.player1.move_ip(0, 1)
        elif self.movement == "left":
            self.player1.move_ip(-1, 0)
        elif self.movement == "right":
            self.player1.move_ip(1, 0)
        elif self.movement == "down":
            self.player1.move_ip(0, -1)

    def create_quad_vertex_list(self, x, y):
        return (x*CELLSIZE,            y*CELLSIZE,
                x*CELLSIZE + CELLSIZE, y*CELLSIZE,
                x*CELLSIZE + CELLSIZE, y*CELLSIZE + CELLSIZE,
                x*CELLSIZE,            y*CELLSIZE + CELLSIZE)

    def create_quad_color_list(self, color):
        return color*4

    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.movement = "up"
        elif symbol == key.A:
            self.movement = "left"
        elif symbol == key.D:
            self.movement = "right"
        elif symbol == key.S:
            self.movement = "down"
        elif symbol == key.ESCAPE:
            self.running = False

    def on_draw(self):
        # Save time by drawing black quad over removed trail cells
        # This way all trail cells do not need to be drawn every step

        # Example player
        vertex_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(
                                                        self.player1.pos[0],
                                                        self.player1.pos[1])),
                                                     ('c3B', self.create_quad_color_list(RED)))
        vertex_list.draw(pyglet.gl.GL_QUADS)

        # Example trail
        if len(self.player1.trail) > 0:
            if len(self.player1.trail) > 250:
                del_x, del_y = self.player1.trail.pop(0)
                trail_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(del_x, del_y)),
                                                                ('c3B', self.create_quad_color_list(BLACK)))
                trail_list.draw(pyglet.gl.GL_QUADS)
            new_x = self.player1.trail[-1][0]
            new_y = self.player1.trail[-1][1]
            trail_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(new_x, new_y)),
                                                            ('c3B', self.create_quad_color_list(LIGHTRED)))
            trail_list.draw(pyglet.gl.GL_QUADS)

        #self.label.draw()

if __name__ == "__main__":

    tronwindow = TronWindow()
    pyglet.app.run()