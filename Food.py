from Thing import Thing


class Food(Thing):

    def __init__(self, world):

        super().__init__(world)

        self.r = 0
        self.g = 255
        self.b = 0

        self.size = 5

    # def update(self):
    #     self.size = self.health * 5 / MAX_HEALTH

    def draw(self):
        self.world.canvas.create_oval(self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size,
                                      fill="green")
        # self.world.canvas.create_text(self.x, self.y, fill="red", text="Food")
