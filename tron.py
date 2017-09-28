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
LIGHTRED = (128, 0, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (0, 0, 128)


class TronWindow(pyglet.window.Window):
    def __init__(self):
        super(TronWindow, self).__init__(width=1280, height=720,
                                         resizable=False, fullscreen=False)
        self.running = True


        self.player1 = player.Player(int(BOARDWIDTH/4), int(BOARDHEIGHT/4))

        self.movement = "up"

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
        self.clear()

        # Example player
        vertex_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(
                                                        self.player1.pos[0],
                                                        self.player1.pos[1])),
                                                     ('c3B', self.create_quad_color_list(RED)))
        vertex_list.draw(pyglet.gl.GL_QUADS)

        self.label.draw()

if __name__ == "__main__":

    tronwindow = TronWindow()
    pyglet.app.run()