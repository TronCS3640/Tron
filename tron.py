import pyglet

class TronWindow(pyglet.window.Window):
    def __init__ (self):
        super(TronWindow, self).__init__(width=1280, height=768, fullscreen=False)

        self.label = pyglet.text.Label('Hello, world!', x=self.width/2, y=self.height/2)

    def on_draw(self):
        self.clear()
        self.label.draw()

if __name__ == "__main__":

    tronwindow = TronWindow()
    pyglet.app.run()