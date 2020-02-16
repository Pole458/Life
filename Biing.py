import random

import math
import numpy as np
from keras import Input, Model
from keras.layers import Dense
from keras.models import load_model

from Egg import from_r_g_b
from Thing import Thing

MAX_SIZE = 25
MIN_SIZE = 10

MAX_SPEED = 6
MIN_SPEED = 2

MAX_HEALTH = 100
AGE_FACTOR = 0.005


class Biing(Thing):

    def __init__(self, world, load=None):

        super().__init__(world)

        # Genotypes
        self.mass = random.random()
        self.aggressiveness = random.random()
        self.r = int(255 * random.random())
        self.g = int(255 * random.random())
        self.b = int(255 * random.random())

        # Phenotypes
        self.size = int((MAX_SIZE - MIN_SIZE) * self.mass + MIN_SIZE)
        self.speed = int((MAX_SPEED - MIN_SPEED) * (1 - self.mass) + MIN_SPEED)

        self.model = None

        # Brain
        if load:
            try:
                self.model = load_model("models/" + load + ".h5")
            except OSError:
                print("Could not find model in: models/" + load + ".h5")

        if not self.model:
            # inputs 15
            # health -> 1
            # mass -> 1
            # olfaction -> avg_intensity, avg_r, avg_g, avg_b, r.x, r.y, g.x, g.y, b.x, b.y -> 10
            # tact -> avg_r, avg_g, avg_b

            inputs = Input(shape=(12,))

            dense = Dense(16, activation='relu')
            x = dense(inputs)

            x = Dense(8, activation='relu')(x)

            # outputs 2
            #   0 delta position -> 2

            # output_cry_color = Dense(3, activation="sigmoid")(x)
            output_delta_x = Dense(2, activation="softmax")(x)
            output_delta_y = Dense(2, activation="softmax")(x)
            # output_bite = Dense(1, activation='sigmoid')(x)
            # output_lay_egg = Dense(1, activation='sigmoid')(x)

            self.model = Model(inputs=inputs,
                               outputs=[output_delta_x, output_delta_y],
                               name="Spidey model")

            # self.model.summary()
            # keras.utils.plot_model(self.model, self.model.name + ".png", show_shapes=True)

            # Logic
            self.health = MAX_HEALTH

            self.delta_x = 0
            self.delta_y = 0

            self.noises = []
            self.scents = []

            self.fitness = 0

            # Senses
            self.avg_r = 0
            self.avg_g = 0
            self.avg_b = 0
            self.avg_intensity = 0
            self.rx = 0
            self.ry = 0
            self.gx = 0
            self.gy = 0
            self.bx = 0
            self.by = 0

    def reset(self):

        super().reset()
        self.health = MAX_HEALTH

        self.delta_x = 0
        self.delta_y = 0

        self.noises = []
        self.scents = []

        self.fitness = 0

    def draw(self):
        # Draw body
        self.world.canvas.create_oval(self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size,
                                      fill=from_r_g_b(self.r, self.g, self.b))

        # self.world.canvas.create_text(self.x, self.y, fill="red", text=str(int(self.health)))

        # Avg color I am seeing
        self.world.canvas.create_oval(self.x - self.size / 3, self.y - self.size / 3, self.x + self.size / 3, self.y + self.size / 3,
                                      fill=from_r_g_b(self.avg_r, self.avg_g, self.avg_b))
        # Color directions
        self.world.canvas.create_line(self.x, self.y, self.x + self.rx * self.size, self.y + self.ry * self.size, fill="red")
        self.world.canvas.create_line(self.x, self.y, self.x + self.gx * self.size, self.y + self.gy * self.size, fill="green")
        self.world.canvas.create_line(self.x, self.y, self.x + self.bx * self.size, self.y + self.by * self.size, fill="blue")

    def get_input_data(self):

        model_input = [self.health / MAX_HEALTH, self.mass]

        # Nostrils
        self.avg_intensity = 0
        self.avg_r = 0
        self.avg_g = 0
        self.avg_b = 0
        self.rx = 0
        self.ry = 0
        self.gx = 0
        self.gy = 0
        self.bx = 0
        self.by = 0

        # Nostril
        if len(self.scents) > 0:
            for scent in self.scents:
                self.avg_intensity += scent.intensity
                self.avg_r += abs(scent.r * scent.intensity)
                self.avg_g += abs(scent.g * scent.intensity)
                self.avg_b += abs(scent.b * scent.intensity)
                self.rx += scent.r / 255 * scent.intensity * scent.x
                self.ry += scent.r / 255 * scent.intensity * scent.y
                self.gx += scent.g / 255 * scent.intensity * scent.x
                self.gy += scent.g / 255 * scent.intensity * scent.y
                self.bx += scent.b / 255 * scent.intensity * scent.x
                self.by += scent.b / 255 * scent.intensity * scent.y

            self.avg_r /= self.avg_intensity
            self.avg_g /= self.avg_intensity
            self.avg_b /= self.avg_intensity
            self.rx /= self.avg_intensity
            self.ry /= self.avg_intensity
            self.gx /= self.avg_intensity
            self.gy /= self.avg_intensity
            self.bx /= self.avg_intensity
            self.by /= self.avg_intensity

            self.avg_intensity /= len(self.scents)

        # if len(self.scents) == 3:
        #     for scent in self.scents:
        #         print("Scent:")
        #         print(" Intensity: " + str(scent.intensity))
        #         print(" R        : " + str(scent.r))
        #         print(" G        : " + str(scent.g))
        #         print(" B        : " + str(scent.b))
        #         print(" (x,y)  : " + str((scent.x, scent.y)))
        #
        #     print("\n\nData:")
        #     print(" Intensity: " + str(self.avg_intensity))
        #     print(" R        : " + str(self.avg_r))
        #     print(" G        : " + str(self.avg_g))
        #     print(" B        : " + str(self.avg_b))
        #     print(" R (x,y)  : " + str((self.rx, self.ry)))
        #     print(" G (x,y)  : " + str((self.gx, self.gy)))
        #     print(" B (x,y)  : " + str((self.bx, self.by)))
        #
        #     sys.exit()

        model_input += [self.avg_intensity,
                        self.avg_r, self.avg_g, self.avg_b,
                        self.rx, self.ry, self.gx, self.gy, self.bx, self.by]

        self.scents = []

        return model_input

    def update(self):

        input_data = self.get_input_data()

        out_put_data = self.model.predict(np.array([input_data]))

        self.scents = []
        self.noises = []

        # outputs 2
        #   0 delta position -> 2
        #   1 bite 1 -> 1

        self.delta_x = (out_put_data[0][0][0] - out_put_data[0][0][1]) * self.speed
        self.delta_y = (out_put_data[1][0][0] - out_put_data[1][0][1]) * self.speed

        self.x += self.delta_x
        self.y += self.delta_y

        self.health -= MAX_HEALTH * AGE_FACTOR
        self.fitness += 1

    def get_dna(self):

        vector = [
            self.mass,
            self.aggressiveness,
            self.r,
            self.g,
            self.b
        ]

        return vector

    def eat(self, food):
        if self.is_touching(food):
            self.world.food.remove(food)
            self.health += MAX_HEALTH * 0.5
            # self.fitness += MAX_HEALTH * 0.25

        self.health = min(self.health, MAX_HEALTH)

    # def bite(self):
    #
    #     # for b in self.world.biings:
    #     #     if b is not self and self.is_touching(b):
    #     #         b.health -= 400
    #     #         self.health += 500
    #
    #     for f in self.world.food:
    #         if self.is_touching(f):
    #             self.world.food.remove(f)
    #             self.health += MAX_HEALTH * 0.25
    #             self.fitness += MAX_HEALTH * 0.25
    #             break
    #
    #     self.health = min(self.health, MAX_HEALTH)
    #
    #     # self.health -= MAX_HEALTH * 0.01
    #
    # def lay_egg(self):
    #     found = False
    #
    #     for e in self.world.eggs:
    #         if not e.father and e.mother is not self and self.is_touching(e):
    #             e.fecundate(self)
    #             found = True
    #             break
    #
    #     if not found:
    #         self.world.eggs.append(Egg(self))

    def mate(self, father):

        # Brain
        w1 = self.model.get_weights()
        w2 = father.model.get_weights()

        genome1 = model_to_list(w1)
        genome2 = model_to_list(w2)

        i = random.randrange(len(genome1) - 1)

        child_genome = genome1[:i] + genome2[i:]

        child_w = list_to_model(child_genome, w1)

        # Dna
        r = random.random()
        father_dna = father.get_dna()

        child_dna = []
        mother_dna = self.get_dna()
        for i in range(len(mother_dna)):
            if mother_dna[i] + father_dna[i] > 0:
                child_dna.append(mother_dna[i] * r + father_dna[i] * (1 - r))
            else:
                child_dna.append(0)

        genome = model_to_list(self.model.get_weights())

        # Mutation
        if random.random() < 0.1:

            # Mutate one component of dna
            m = random.choice((0, 1, 2, 3, 4))
            child_dna[m] = (0.5 + random.random()) * child_dna[m]
            if m < 3:
                child_dna[m] = max(0, min(child_dna[m], 1))
            else:
                child_dna[m] = int(max(0, min(child_dna[m], 255)))

            # mutate up to 10% of genome
            m = random.randrange(int(len(genome) * 0.1))

            for i in range(m):
                i = random.randrange(len(genome))
                genome[i] = (0.5 + random.random()) * genome[i]

        hatchling = Biing(self.world)
        hatchling.model.set_weights(child_w)
        # hatchling.x = self.x
        # hatchling.y = self.y

        hatchling.mass = child_dna[0]
        hatchling.aggressiveness = child_dna[1]
        hatchling.r = int(child_dna[2])
        hatchling.g = int(child_dna[3])
        hatchling.b = int(child_dna[4])

        self.world.biings.append(hatchling)

    def touch_hazard(self):
        # self.fitness = max(0, self.fitness - self.health)
        self.health = 0
        # self.fitness = max(0, self.fitness - MAX_HEALTH)
        # self.health -= MAX_HEALTH * 0.1
        # self.fitness = max(0, self.fitness - MAX_HEALTH * 0.1)


class Scent:

    def __init__(self, sender, receiver):

        distance = math.sqrt(receiver.get_squared_distance(sender))

        distance_from_borders = max(0, distance - sender.size - receiver.size)
        self.intensity = 1 / math.pow(distance_from_borders + 1, 2)
        # self.intensity = (distance_from_borders * distance_from_borders) / 40000 - distance_from_borders / 100 + 1

        self.x = (sender.x - receiver.x) / distance
        self.y = (sender.y - receiver.y) / distance

        self.r = sender.r
        self.g = sender.g
        self.b = sender.b


class DirectionScent:

    def __init__(self, r, g, b, receiver, x=None, y=None):

        distance = 0

        if x is not None:
            distance = abs(x - receiver.x)
        elif y is not None:
            distance = abs(y - receiver.y)

        distance_from_borders = max(0, distance - receiver.size)
        self.intensity = 1 / math.pow(distance_from_borders + 1, 2)

        if distance is not 0:

            if x is not None:
                self.x = (x - receiver.x) / distance
                self.y = 0
            elif y is not None:
                self.x = 0
                self.y = (y - receiver.y) / distance
        else:
            self.x = 0
            self.y = 0

        self.r = r
        self.g = g
        self.b = b


def model_to_list(weights):
    vector = []
    weights = np.copy(weights)
    for e in weights:
        vector += e.flatten().tolist()
    return vector


def list_to_model(weight_list, weights):

    w = []

    for e in weights:

        current_w = weight_list[:e.size]
        weight_list = weight_list[e.size:]

        a = np.array(current_w)
        a = a.reshape(e.shape)

        w.append(a)

    return w
