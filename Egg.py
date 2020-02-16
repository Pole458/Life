import random


class Egg:

    def __init__(self, mother):

        self.mother = mother

        self.world = mother.world

        self.x = mother.x
        self.y = mother.y

        self.r = self.mother.r
        self.g = self.mother.g
        self.b = self.mother.g

        self.tick = int((50 * random.random())) + 50

        self.size = 20

        self.father = None

    def draw(self):
        # Draw body
        self.world.canvas.create_oval(self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size,
                                      fill=from_r_g_b(self.r, self.g, self.b))

        if self.father:
            self.world.canvas.create_text(self.x, self.y, fill="green", text="Egg: " + str(self.tick))
        else:
            self.world.canvas.create_text(self.x, self.y, fill="red", text="Egg: " + str(self.tick))

    def update(self):
        if self.tick == 0:
            self.hatch()
        else:
            self.tick -= 1

    def fecundate(self, father):

        self.father = father

    def hatch(self):

        if self.father:

            self.mother.mate(self.father)

        self.world.eggs.remove(self)


def from_r_g_b(r, g, b):
    return from_rgb((int(r), int(g), int(b)))


def from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb
