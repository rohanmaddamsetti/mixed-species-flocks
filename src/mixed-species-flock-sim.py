#!/usr/bin/env python3

## mixed-species-flock-sim.py by Rohan Maddamsetti
## Usage: python3 mixed-species-flock-sim.py

## NOTE: units in the display and in space are all fucked up.
##       right now, just trying to get stuff to display and work.

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
        return np.array([random.uniform(0,self.xmax), random.uniform(0,self.ymax)])

    def add_species_pair(self, species,coords=None):
        '''add a pair of a given species at a random location.
        put second bird in a random nearby location.'''
        # neighborhood is radius of region around coords in which pairs appear.
        neighborhood = 20
        coords = coords or self.random_coords()
        coords1 = coords
        coords2 = np.array([i+random.choice([-1,1])*random.uniform(Bird.rad,neighborhood) for i in coords])
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
    mate_max_distance = 20
    
    def __init__(self, species, world, coords):
        self.species = species
        self.world = world
        self.coords = coords
        self.direction = np.array([0,0]) ## in x,y coordinates, don't go anywhere.
        if self.species == ANTSHRIKE:
            self.color = "purple"
            self.target_location = world.random_coords() # random target location.
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

    def calc_donut_dist(self,other_bird):
        ''' take periodic boundaries into account when calculating
        the distance between birds in the x,y coordinate system.'''
        pass
        
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
        my_dir_vec = np.array([0,0])
        if self.target_location is not None:
            dir_vec = self.target_location - self.coords
            dir_vec_length = np.linalg.norm(dir_vec)
            if dir_vec_length:
                unit_dir_vec = dir_vec/dir_vec_length
                my_dir_vec = attraction_matrix[self.species][0] * unit_dir_vec
        bird_weight = 1/len(seen_birds) if len(seen_birds) else 0
        for other_bird in seen_birds:
            ## my_dir_vec is a weighted sum of unit vectors in the direction
            ## of other birds in the flock and a desired direction.
            ## if the particular bird is too close, then move in the opposite direction.
            bird_dist_vec = other_bird.coords - self.coords
            bird_dist_vec_length = np.linalg.norm(bird_dist_vec)
            bird_unit_vec = bird_dist_vec/bird_dist_vec_length if bird_dist_vec_length > 0 else np.array([0,0])
            ## if mate is too far, go toward mate.
            if other_bird.species == bird.species and bird_dist_vec_length > bird.mate_max_distance:
                my_dir_vec = np.array(bird_dist_vec/bird_dist_vec_length)
                break # don't worry about other birds in the flock, only the mate!
            if bird_dist_vec_length < bird.rad: ## too close to the other bird.
                my_dir_vec = np.array([i - attraction_matrix[self.species][other_bird.species]*j for i,j in zip(my_dir_vec,bird_unit_vec)])
            else: # move toward each other
                my_dir_vec = np.array([i + attraction_matrix[self.species][other_bird.species]*j for i,j in zip(my_dir_vec,bird_unit_vec)])
        self.direction = my_dir_vec

    def move(self):
        self.coords = self.coords + self.direction
                
def update(i, fig, scat, world):
    '''callback function for the animation, also one step in the world '''
    for bird in world.flock:
        #print(bird.coords)
        bird.calc_direction_vec()
        bird.move()
    ## positions don't wrapped around, but the image maps to the
    ## modulus of the periodic boundaries.
    flocka_x = [bird.coords[0] % world.xmax for bird in world.flock]
    flocka_y = [bird.coords[1] % world.ymax  for bird in world.flock]
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
    #ani.save('bird.mp4', fps=15)
    plt.show()
    
main()
