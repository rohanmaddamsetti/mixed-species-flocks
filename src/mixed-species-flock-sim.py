#!/usr/bin/env python3

## mixed-species-flock-sim.py by Rohan Maddamsetti
## Usage: python3 mixed-species-flock-sim.py

## I borrowed much code from http://www.indiana.edu/~q320/Code/hw3_320.py
## to get started.

## NOTE: units in the display and in space are all fucked up.
##       right now, just trying to get stuff to display and work.

## Use numpy to implement vectors to make the math easier.


import random, math
import tkinter as tk
from time import sleep
from attraction_rules import * # the file containing edge weights for birds and target.

## Global variables which are shorthand for bird species.
## Target is defined for the attraction matrix.
TARGET = 0
ANTSHRIKE = 1
ANTWREN = 2
OTHER = 3

def vec_length(vec):
    '''return length of a vector in x,y coordinates'''
    x,y = vec
    return math.sqrt(x**2 + y**2)
    
class WorldFrame(tk.Frame):
    ''' A Frame in which to display the world. This is a subclass of the 
    Tk Frame object. Each unit is a pixel represents 1 meter, so 400mx400m world.'''

    def __init__(self, root, width=400,height=400):
        '''give the frame a canvas, a world, and dimensions and display it.'''
        tk.Frame.__init__(self,root)
        self.world = World(self,width=width,height=height)
        root.title('Amazon Donut World')
        self.grid()

### TODO: Code up territories for birds. The territory effect on direction
### is that birds drop out of the flock when the flock crosses the boundary.

### species pair territories are a voronoi tiling of the world (no overlap for
### a single species). Different species have different tilings that overlap.

class World(tk.Canvas):
    '''The arena where everything happens, including both graphics and
    bird representation. This is a subclass of a Canvas object.'''

    ## Spatial scale: 200-300 meters across for a single territory.
    ## Move like a meter per minute.
    ## Each time step is 1 minute, so each movement is 1 meter.
    ## Let's make each run last 300 minutes.
    ## Right now, this is a simulation of a single large territory.
    time_steps_per_run = 300

    def __init__(self, frame, width=400,height=400):
        '''initialize dimensions and create things'''
        tk.Canvas.__init__(self, frame, width=width,height=height)
        self.frame = frame
        self.width = width
        self.height = height
        self.flock = []
        self.graphic_objs = {}
        self.grid()

    def add_species_pair(self, species, coords=None):
        '''add a pair of a given species at a random location.
        put second bird in a random nearby location.'''

        # neighborhood is radius of region around coords in which pairs appear.
        neighborhood = 20
        coords = coords or self.random_coords()
        coords1 = coords
        coords2 = [i+random.choice([-1,1])*random.uniform(Bird.rad,neighborhood) for i in coords]
        bird1 = Bird(species, self, coords1)
        bird2 = Bird(species, self, coords2)
        self.flock.append(bird1)
        self.graphic_objs[bird1.graphic_id] = bird1
        self.flock.append(bird2)
        self.graphic_objs[bird2.graphic_id] = bird2

    def random_coords(self):
        return [random.uniform(0,self.width), random.uniform(0,self.height)]

    def adjust_coords(self,coords):
        '''adjust coordinates of bird, assuming donut world'''
        x, y = coords
        if x < 0:
            x = self.width + x
        elif x > self.width:
            x = x - self.width
        if y < 0:
            y = self.height + y
        elif y > self.height:
            y = y - self.height
        return x, y

    def step(self):
        for bird in self.flock:
            bird_image = self.graphic_obj[bird.graphic_id]
            bird.calc_direction_vec()
            bird.move() # this updates the birds coordinates.
            self.update()
            
            print(bird.coords)

    def draw_one_frame(self):
        pass

    def run(self):
        ''' Run the simulation'''
        ## First, add birds to the flock.
        self.add_species_pair(ANTSHRIKE)
        self.add_species_pair(ANTWREN)
        self.draw_one_frame()
        for s in range(World.time_steps_per_run):
            self.after(10,self.step())
            print()
            self.draw_one_frame()
            self.update_idletasks()
            
class Bird:
    ''' Birds can be ANTSHRIKE (leaders),
    ANTWREN (followers that occasionally peel out),
    or integers 3 and above representing additional follower species.'''
    
    rad = 5 #each bird has a radius of space.
    percept = 2000 #each bird has a radius of perception.
    target_location = None ## antshrikes (occasionally antwrens) have a target in the world

    
    def __init__(self, species, world, coords):
        self.species = species
        self.world = world
        self.coords = coords
        self.direction = [0,0] ## in x,y coordinates, don't go anywhere.
        if self.species == ANTSHRIKE:
            self.color = "purple"
            self.target = world.random_coords() # random target location.
        elif self.species == ANTWREN:
            self.color = "green"
        else:
            self.color = "orange"
        self.make_graphical_object()
        
    def make_graphical_object(self):
        ''' Create the Canvas object for the bird: a circle.'''
        x, y = self.coords
        self.graphic_id = self.world.create_oval(x-Bird.rad,y-Bird.rad,
                                                 x+Bird.rad,y+Bird.rad,
                                                 fill=self.color,
                                                 outline="black")
    def observes(self,bird):
        '''Can I see the nearby bird?'''
        my_x,my_y = self.coords
        its_x,its_y = bird.coords
        if its_x > my_x - Bird.percept and its_x < my_x + Bird.percept and its_y > my_y - Bird.percept and its_y < my_y + Bird.percept:
            return True
        else:
            return False
    
    def calc_direction_vec(self):
        ''' the direction: weighted average of position of all birds in the 
        flock (within perception radius). 
        Leaders get more weight, and leaders also have a desired 
        direction. Antwrens might have a switch that gives them a desired 
        direction during the simulation. Also, need to provide a repulsion 
        force that gives each bird some personal space.'''
        seen_birds = []
        ## find birds within perception range.
        for bird in self.world.flock:
            if self.observes(bird):
                seen_birds.append(bird)
        my_x, my_y = self.coords
        
        my_dir_vec = [0,0]
        if self.target_location:
            dir_vec = [self.target_location[0] - my_x, self.target_location[1] - my_y]
            dir_vec_len = vec_length(dir_vec)
            if dir_vec_len > 0:
                unit_dir_vec = [i/dir_vec_len for i in dir_vec]
                my_dir_vec = [attraction_matrix[self.species][0] * i for i in unit_dir_vec]
        bird_weight = 1/len(seen_birds)
        for rel_bird in seen_birds:
            other_species = rel_bird.species
            other_coords = rel_bird.coords
            other_x, other_y = other_coords
            ## my_dir_vec is a weighted sum of unit vectors in the direction
            ## of other birds in the flock and a desired direction.
            ## if the particular bird is too close, then move in the opposite direction.
            bird_dist_vec = ([other_x - my_x, other_y - my_y])
            bird_dist_vec_length = vec_length(bird_dist_vec)
            if bird_dist_vec_length > 0:
                bird_unit_vec = [i/bird_dist_vec_length for i in bird_dist_vec]
                my_dir_vec = [i + attraction_matrix[self.species][rel_bird.species]*j for i,j in zip(my_dir_vec,bird_unit_vec)]
        self.direction = my_dir_vec

    def move(self):
        self.coords = [i+j for i,j in zip(self.coords,self.direction)]
        self.coords = self.world.adjust_coords(self.coords)
        x,y = self.coords
        self.world.coords(self.graphic_id,
                          x - Bird.rad, y - Bird.rad,
                          x+ Bird.rad, y + Bird.rad)

def main():
    root = tk.Tk()
    amazon_donut = WorldFrame(root)
    amazon_donut.world.run()
    root.mainloop()
    
main()
