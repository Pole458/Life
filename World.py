import random
import time
import tkinter

from Biing import Biing, Scent, DirectionScent
from Food import Food
from Hazard import Hazard

FOOD_NUMBER = 35
POPULATION_SIZE = 50
HAZARD_NUMBER = 10


def order_for_fitness(biing):
    return biing.fitness


# Stochastic universal sampling
def sus(population):

    population.sort(key=order_for_fitness, reverse=True)

    # F := total fitness of Population
    total_fitness = 0

    for biing in population:
        total_fitness += biing.fitness

    # N := number of offspring to keep
    n = int(len(population) / 2)

    # P := distance between the pointers (F/N)
    p = int(total_fitness / n)

    # Start := random number between 0 and P
    start = random.randrange(0, p)

    # Pointers := [Start + i*P | i in [0..(N-1)]]

    pointers = []
    for i in range(n):
        pointers.append(start + i * p)

    return rws(population, pointers)


# roulette wheel selection
def rws(population, pointers):

    new_population = []

    for p in pointers:
        i = 0
        while sum(individual.fitness for individual in population[0:i+1]) < p:
            i += 1
        new_population.append(population[i])

    return new_population


class World:

    def __init__(self):

        self.WIDTH = 700
        self.HEIGHT = 700
        self.name = "World"

        self.delta_time = 1 / 25

        self.root = tkinter.Tk()

        self.canvas = tkinter.Canvas(self.root, bg="black", width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack()

        self.biings = []
        self.death_biings = []
        self.eggs = []
        self.food = []

        self.hazards = []

        self.elapsed_time = 0

        for i in range(POPULATION_SIZE):
            self.biings.append(Biing(self))

        for i in range(FOOD_NUMBER):
            self.food.append(Food(self))

        for i in range(HAZARD_NUMBER):
            self.hazards.append(Hazard(self))

        self.root.after(int(1000 / 24), self.on_draw)
        self.root.after(int(1000 * self.delta_time), self.on_update)

        self.age = 0
        self.generation = 1
        self.avg_fitness = 0

        self.root.mainloop()

    def on_draw(self):

        # start_time = time.time()

        self.canvas.delete("all")

        for h in self.hazards:
            h.draw()

        for f in self.food:
            f.draw()

        for e in self.eggs:
            e.draw()

        for s in self.biings:
            s.draw()

        # for i in range(int(self.WIDTH / 100)):
        #     arcade.draw_text(str(i*100) + ", " + str(i*100), i*100, i*100, (255, 0, 0))

        # self.canvas.create_text(25, 25, fill="red", text=str(int(self.elapsed_time * 1000) / 1000))
        # self.canvas.create_text(75, 25, fill="red", text=str(int((time.time() - start_time) * 1000) / 1000))

        # self.canvas.create_text(25, 25, fill="red", text="Biings: " + str(len(self.biings)))
        # self.canvas.create_text(25, 75, fill="red", text="Eggs: " + str(len(self.eggs)))

        self.canvas.create_text(self.WIDTH / 2,  50, fill="red",
                                text="Gen: " + str(self.generation) + ", Avg. Fitness: " + str(int(self.avg_fitness)) + ", Time: " + str(self.age))

        self.root.after(int(1000 / 24), self.on_draw)

    def on_update(self):

        self.age += 1

        self.root.title = "Generation: " + str(self.generation) + ":" + str(self.age)

        start_time = time.time()

        for e in self.eggs:
            e.update()

        # for f in self.food:
        #     if f.health < 0:
        #         self.food.remove(f)
        #     else:
        #         f.update()

        if len(self.food) < FOOD_NUMBER:
            for i in range(len(self.food), FOOD_NUMBER):
                self.food.append(Food(self))

        # Reset generation
        if len(self.biings) == 0:
            self.generation += 1
            self.age = 0

            self.death_biings += self.biings
            self.biings = []

            for b in self.death_biings:
                self.avg_fitness += b.fitness

            self.avg_fitness /= len(self.death_biings)

            # Apply natural selection
            self.death_biings = sus(self.death_biings)

            # Make new egg
            while len(self.death_biings) > 1:

                parent1 = random.choice(self.death_biings)
                self.death_biings.remove(parent1)
                parent1.reset()

                parent2 = random.choice(self.death_biings)
                self.death_biings.remove(parent2)
                parent2.reset()

                self.biings += [parent1, parent2]

                parent1.mate(parent2)
                parent2.mate(parent1)

            if len(self.death_biings) == 1:
                parent1 = self.death_biings[0]
                self.death_biings.remove(parent1)
                parent1.reset()
                parent1.mate(random.choice(self.biings))
                self.biings.append(parent1)

            # Regenerate food
            self.food = []
            for i in range(FOOD_NUMBER):
                self.food.append(Food(self))

            # Regenerate hazards
            self.hazards = []
            for i in range(HAZARD_NUMBER):
                self.hazards.append(Hazard(self))

        else:

            for biing in self.biings:
                if biing.health <= 0:
                    self.biings.remove(biing)
                    self.death_biings.append(biing)
                else:
                    # Screen borders
                    if biing.x < biing.size or biing.x > self.WIDTH - biing.size or biing.y < biing.size or biing.y > self.HEIGHT - biing.size:
                        biing.touch_hazard()

                    # Screen border scent
                    if biing.x < 200:
                        biing.scents.append(DirectionScent(255, 0, 0, biing, x=0))
                    if biing.x > self.WIDTH - 200:
                        biing.scents.append(DirectionScent(255, 0, 0, biing, x=self.WIDTH))
                    if biing.y < 200 - biing.size:
                        biing.scents.append(DirectionScent(255, 0, 0, biing, y=0))
                    if biing.y > self.HEIGHT - 200:
                        biing.scents.append(DirectionScent(255, 0, 0, biing, y=self.HEIGHT))

                    # for receiver in self.biings:
                    #     if biing is not receiver and biing.is_in_range(receiver, 200):
                    #         receiver.scents.append(Scent(biing, receiver))

                    # Apply scents
                    for e in self.eggs:
                        if biing.is_in_range(e, 200):
                            biing.scents.append(Scent(e, biing))

                    for f in self.food:
                        if biing.is_in_range(f, 200):
                            if biing.is_touching(f):
                                biing.eat(f)
                            else:
                                biing.scents.append(Scent(f, biing))

                    for h in self.hazards:
                        if biing.is_in_range(h, 200):
                            biing.scents.append(Scent(h, biing))
                            if biing.is_touching(h):
                                biing.touch_hazard()

            for biing in self.biings:
                biing.update()

        # if len(self.biings) + len(self.eggs) < 20:
        #     for i in range(len(self.biings) + len(self.eggs), 20):
        #         # sorted_biings = self.biings.sort(key=lambda b: b.health)
        #         if len(self.biings) < 2 or random.random() < 0.5:
        #             self.biings.append(Biing(self))
        #         else:
        #             parents = random.sample(self.biings, 2)
        #             parents[0].mate(parents[1])

        self.elapsed_time = time.time() - start_time

        self.root.after(int(1000 * self.delta_time), self.on_update)


if __name__ == "__main__":
    world = World()
