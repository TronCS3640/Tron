class Player():
    def __init__(self, x, y):

        self.pos = [x, y]
        self.trail = []

    def update_pos(self):
        pass

    def update_trail(self):
        pass

    def move_ip(self, x, y):
        self.pos[0] += x
        self.pos[1] += y

    def get_pos(self):
        return self.pos
