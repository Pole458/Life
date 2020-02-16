import random

import math

BORDER = 50


class Thing:

    def __init__(self, world):

        # World position
        self.world = world
        self.x = BORDER + (world.WIDTH - BORDER) * random.random()
        self.y = BORDER + (world.HEIGHT - BORDER) * random.random()

        self.size = 0

        self.r = 0
        self.g = 0
        self.b = 0

    def reset(self):
        self.x = BORDER + (self.world.WIDTH - BORDER) * random.random()
        self.y = BORDER + (self.world.HEIGHT - BORDER) * random.random()

    def update(self):
        pass

    def draw(self):
        pass

    def get_squared_distance(self, thing):
        return math.pow(self.x - thing.x, 2) + math.pow(self.y - thing.y, 2)

    def is_in_range(self, thing, distance):
        return self.get_squared_distance(thing) <= math.pow(distance, 2)

    def is_touching(self, thing):
        return self.is_in_range(thing, self.size + thing.size)
