# Board is 128x72 cells
# Cells are 10px*10px
# Window size is 1280x720

# Trail queue is 250? TBD

import pyglet

CELLSIZE = 10

RED = (255, 0, 0)
LIGHTRED = (128, 0, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (0, 0, 128)


class TronWindow(pyglet.window.Window):
    def __init__ (self):
        super(TronWindow, self).__init__(width=1280, height=720,
                                         resizable=False, fullscreen=False)

        self.map = Map()

        self.label = pyglet.text.Label('Hello, world!', x=self.width/2, y=self.height/2)

    def create_quad_vertex_list(self, x, y):
        return (x*CELLSIZE,            y*CELLSIZE,
                x*CELLSIZE + CELLSIZE, y*CELLSIZE,
                x*CELLSIZE + CELLSIZE, y*CELLSIZE + CELLSIZE,
                x*CELLSIZE,            y*CELLSIZE + CELLSIZE)

    def create_quad_color_list(self, color):
        return color*4

    def on_draw(self):
        # Save time by drawing black quad over removed trail cells
        # This way all trail cells do not need to be drawn every step
        self.clear()

        # Example player
        vertex_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(0, 0)),
                                                     ('c3B', self.create_quad_color_list(RED)))
        vertex_list.draw(pyglet.gl.GL_QUADS)

        # Example trail
        vertex_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(1, 0)),
                                                     ('c3B', self.create_quad_color_list(LIGHTRED)))

        vertex_list.draw(pyglet.gl.GL_QUADS)
        vertex_list = pyglet.graphics.vertex_list(4, ('v2i', self.create_quad_vertex_list(2, 0)),
                                                     ('c3B', self.create_quad_color_list(LIGHTRED)))

        vertex_list.draw(pyglet.gl.GL_QUADS)

        self.label.draw()

class Player():
    def __init__(self, x, y):

        self.pos = [x, y]
        self.trail = []

    def update_pos(self):
        pass

    def update_trail(self):
        pass

    def get_pos(self):
        return self.pos

class Map():
    def __init__(self):

        self.players = [] # list of players

    def check_player_collision(self):
        pass

    def add_player(self):

        self.players.append(Player(64, 48))

    def step(self, keys):
        pass


if __name__ == "__main__":

    tronwindow = TronWindow()
    pyglet.app.run()