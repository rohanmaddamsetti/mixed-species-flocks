#!/usr/bin/env python3

## mixed-species-flock-sim.py by Rohan Maddamsetti
## Usage: python3 mixed-species-flock-sim.py

## I borrowed much code from http://www.indiana.edu/~q320/Code/hw3_320.py
## to get started.

## NOTE: units in the display and in space are all fucked up.
##       right now, just trying to get stuff to display and work.

import random, math
import tkinter as tk

## Global variables which are shorthand for bird species.
ANTSHRIKE = 0
ANTWREN = 1

def xy_dist(angle, dist):
#    '''The x and y distances corresponding to a distance dist in angle.'''
    radian_angle = math.radians(angle)
#    ## return is x,y tuple
    return (dist * math.cos(radian_angle), dist * math.sin(radian_angle))

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
        coords = coords or self.random_bird_coords()
        coords1 = coords
        coords2 = tuple(i+random.choice([-1,1])*random.uniform(Bird.rad,neighborhood) for i in coords )
        bird1 = Bird(species, self, coords1)
        bird2 = Bird(species, self, coords2)
        self.flock.append(bird1)
        self.graphic_objs[bird1.graphic_id] = bird1
        self.flock.append(bird2)
        self.graphic_objs[bird2.graphic_id] = bird2

    def random_bird_coords(self):
        return random.uniform(0,self.width), random.uniform(0,self.height)

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
        pass
    
    def run(self):
        ''' Run the simulation'''
        ## First, add birds to the flock.
        self.add_species_pair(ANTSHRIKE)
        self.add_species_pair(ANTWREN)
        #for bird in self.flock:
        #    bird.calc_direction_vec()
        #for s in range(World.time_steps_per_run):
            # TODO: in each time step, move the flock.   
            #self.update_idletask()
            
class Bird:
    ''' Birds can be ANTSHRIKE (leaders),
    ANTWREN (followers that occasionally peel out),
    or integers 2 and above representing additional follower species.'''
    
    rad = 5 #each bird has a radius of space.
    percept = 2000 #each bird has a radius of perception.
        
    def __init__(self, species, world, coords):
        self.species = species
        self.world = world
        self.coords = coords
        ## direction is a dict with polar coordinates.
        ##initially, bird does not go anywhere.
        self.direction = {'r':0, 'theta':0}
        if self.species == ANTSHRIKE:
            self.color = "purple"
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
                seen_birds.append((bird.species,bird.coords))
       # dir_vec = [0,0]
       # for rel_bird in seen_birds:
       #     other_species,other_coords = rel_bird
       #     other_x, other_y = other_coords
       #     dir_vec = dir_vec + ## a weighted sum of this bird.

def main():
    root = tk.Tk()
    amazon_donut = WorldFrame(root)
    amazon_donut2 = WorldFrame(root)
    amazon_donut.world.run()
    root.mainloop()

main()
