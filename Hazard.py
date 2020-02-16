from Thing import Thing


class Hazard(Thing):

    def __init__(self, world):

        super().__init__(world)

        self.size = 5

        self.r = 255
        self.g = 0
        self.b = 0

    def draw(self):
        self.world.canvas.create_oval(self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size,
                                      fill="red")
