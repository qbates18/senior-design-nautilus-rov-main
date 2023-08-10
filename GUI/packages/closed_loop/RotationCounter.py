from imports import *
import threading

class rotationCounter:
    def __init__(self):
        self.previous = 0
        self.current = 0
        self.starting_heading = 0
        self.rotations = 0
        self.counter = 0
        self.total_angle = 0
        self.initial_read_bool = False

    def calculate_rotation(self, read_compass):
        if self.initial_read_bool == False:
            self.starting_heading = float(read_compass)
            self.previous = self.starting_heading
            self.initial_read_bool = True

        # #check if rotation was clockwise or counter clockwise
        # #this determines if the current should be added to or subtracted from total

        self.current = float(read_compass)
        if self.current-self.previous > 180:
            self.counter = self.counter-1
        if self.current - self.previous < -180:
            self.counter = self.counter+1
        
        self.previous = self.current
        self.rotations = self.counter + ((self.current-self.starting_heading)/360)
        return self.rotations

        # self.total_angle += self.current
        # self.rotations = self.total_angle/360
        # self.current = float(read_compass)
        # if self.current > 345:
        #     if self.previous < 15:
        #         self.counter = self.counter - 1
        # if self.current < 15:
        #     if self.previous > 345:
        #         self.counter = self.counter + 1
        # self.previous = self.current
        # self.rotations = self.counter + ((self.current - self.starting_heading)/360)
        # #print(self.rotations)
        # return self.rotations




    # def check_rotation_direction(self):
    #     if self.current > self.previous and self.current < :
    #         return 1
    #     if self.current < self.previous and self.current >:
    #         return -1