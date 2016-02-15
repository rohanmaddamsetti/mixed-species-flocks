#!/usr/bin/env python3

## mixed-species-flock-sim.py by Rohan Maddamsetti
## Usage: python3 mixed-species-flock-sim.py

## I borrowed code from http://www.indiana.edu/~q320/Code/hw3_320.py
## to get started.

## NOTE: units in the display and in space are all fucked up.
##       right now, just trying to get stuff to display and work.

## TODO: Use numpy to implement vectors to make the math easier.
## make an animation with matplotlib, save a bunch of frames and stitch together.


import random, math
from attraction_rules import * # the file containing edge weights for birds and target.

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
    
### TODO: Code up territories for birds. The territory effect on direction
### is that birds drop out of the flock when the flock crosses the boundary.

### species pair territories are a voronoi tiling of the world (no overlap for
### a single species). Different species have different tilings that overlap.

class World:

    def __init__(self):
        self.flock = []
        self.xmax=400
        self.ymax=400

    def random_coords(self):
        return [random.uniform(0,self.xmax), random.uniform(0,self.ymax)]

    def add_species_pair(self, species,coords=None):
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
        self.flock.append(bird2)

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
        self.adjust_coords()
        
    def adjust_coords(self):
        '''adjust coordinates of bird, assuming donut world'''
        x, y = self.coords
        if x < 0:
            x = self.world.xmax + x
        elif x > self.world.xmax:
            x = x - self.world.xmax
        if y < 0:
            y = self.world.ymax + y
        elif y > self.world.ymax:
            y = y - self.world.ymax
        self.coords = x, y

        
def update(i, fig, scat, world):
    '''callback function for the animation, also one step in the world '''
    for bird in world.flock:
        #print(bird.coords)
        bird.calc_direction_vec()
        bird.move() # this updates the birds coordinates.
    flocka_x = [bird.coords[0] for bird in world.flock]
    flocka_y = [bird.coords[1] for bird in world.flock]
    scat = plt.scatter(flocka_x,flocka_y)
    return scat,


def main():

    ## Spatial scale: 200-300 meters across for a single territory.
    ## Move like a meter per minute.
    ## Each time step is 1 minute, so each movement is 1 meter.
    ## Let's make each run last 300 minutes.
    ## Right now, this is a simulation of a single large territory.
    time_steps = 300

    amazon_donut = World()
    ## add birds to the flock.
    amazon_donut.add_species_pair(ANTSHRIKE)
    amazon_donut.add_species_pair(ANTWREN)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid()
    ax.set_xlim([0,400])
    ax.set_ylim([0,400])
    flocka_x = [bird.coords[0] for bird in amazon_donut.flock]
    flocka_y = [bird.coords[1] for bird in amazon_donut.flock]
    scat = plt.scatter(flocka_x,flocka_y)
    scat.set_alpha(0.8)
    ani = animation.FuncAnimation(fig, update, fargs=(fig,scat,amazon_donut),
                                  frames=time_steps, interval=100)
    plt.show()
    
main()
