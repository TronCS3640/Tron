class Player():
    def __init__(self, x, y):

        self.pos = [x, y]
        self.trail = []

    def update_pos(self):
        pass

    def update_trail(self):
        pass

    def move_ip(self, x, y):
        if len(self.trail) > 250:
            self.trail.pop(0)
        self.trail.append((self.pos[0], self.pos[1]))
        self.pos[0] += x
        self.pos[1] += y

    def get_pos(self):
        return self.pos
