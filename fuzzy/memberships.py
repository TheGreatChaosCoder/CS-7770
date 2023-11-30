import numpy as np
import matplotlib.pyplot as plt
import util
from math import sqrt, exp, pi

class Membership:
    def __init__(self, x_min, x_max, x_step=1, mem_func=None, init_membership=True):
        self.x_min = x_min
        self.x_max = x_max
        self.x_step = x_step
        self.x_qual = np.arange(x_min, x_max+x_step, x_step)
        self.membership = np.zeros(len(self.x_qual))

        if(init_membership and mem_func is not None):
            for i in range(len(self.x_qual)):
                self.membership[i] = util.into_range(0,1,mem_func(self.x_qual[i]))

    def interp(self, x):
        #assume anything outside of the domain of x has a membership of zero
        if x<self.x_min or x>self.x_max:
            return 0
        
        #get index of value that is closet to x and less than or equal to than x
        i = np.where(self.x_qual == util.get_closest_value(self.x_qual, x))[0][0]

        if(x==self.x_qual[i]):
            return self.membership[i]

        #interpolation time baby
        return self.membership[i] + (self.membership[i+1]-self.membership[i])/(self.x_qual[i+1]-self.x_qual[i])*(x-self.x_qual[i])

    def alpha_cut(self, alpha:float, x=None):
        if x == None:
            #return all values from x_qual that sastify the alpha cut
            cut_x = []
            for i in range(len(self.x_qual)):
                if self.membership[i]>=alpha:
                    cut_x.append(self.x_qual[i])
            return cut_x
        else:
            #return if x sastify the alpha cut
            return self.interp(x)>=alpha
        
    def get_input_range(self):
        return self.x_qual
    
    #x_value has to be in x_qual
    def set_membership_output(self, x_value, output_value):
        #get index of value that is closet to x and less than or equal to than x
        i = np.where(self.x_qual == util.get_closest_value(self.x_qual, x_value))[0][0]
        self.membership[i] = output_value
    
    def yager_compliment(self, w = 1.0): #Returns a membership function
        negated_membership = Membership(self.x_min, self.x_max, self.x_step, init_membership=False)
        for i in range(len(self.x_qual)):
            negated_membership.set_membership_output(self.x_qual[i], (1.0-(self.membership[i])**(w))**(1.0/w))
        return negated_membership
    
    def graph(self, x_qual = None, title = None, x_label = None):
        if x_qual is None:
            x_qual = self.x_qual
            membership = self.membership
        else:
            membership = np.zeros(len(x_qual))
            for i in range(len(x_qual)):
                membership[i] = self.interp(x_qual[i])

        fig, ax0 = plt.subplots(nrows=1, figsize=(8, 4))

        if title is not None:
            plt.title(label=title)
        if x_label is not None:
            plt.xlabel(x_label)

        ax0.plot(x_qual, membership, 'b', linewidth=1.5)
    
    #assume real-valued domain if dx>0, assume discrete domain otherwise
    #left rienmann sum time fellas
    def centroid(self, dx = 0.01) -> float:
        numerator = 0
        demoninator = 0

        if dx <= 0:
            for i in range(len(self.x_qual)):
                numerator += self.x_qual[i] * self.membership[i]
                demoninator += self.membership[i]
            
        else:
            x_array = np.arange(self.x_min, self.x_max,dx)

            for x in x_array:
                numerator += x * self.interp(x) * dx
                demoninator += self.interp(x) * dx

        return numerator/demoninator

class TriangleMembership(Membership):
     #points - [min value, middle point, max value]
     def __init__(self, x_min, x_max, points:list, x_step=1, max_value = 1.0):
        super().__init__(x_min, x_max, x_step=x_step, mem_func=None, init_membership=False)

        points_reached = [False, False, False]

        if points[1] == points[0]:
            left_line = lambda x: max_value
        else:
            left_line = lambda x : max_value/(points[1]-points[0]) * (x-points[0])
        
        if points[2] == points[1]:
            right_line = lambda x: max_value
        else:
            right_line = lambda x: -max_value/(points[2]-points[1]) * (x-points[2]) 

        for i in range(len(self.x_qual)):
            if self.x_qual[i]==points[0]:
                points_reached[0] = True

            if points_reached[0] and not points_reached[1]:
                if self.x_qual[i]==points[1]:
                    points_reached[1] = True
                self.membership[i] = left_line(self.x_qual[i])

            if points_reached[1] and not points_reached[2]:
                if self.x_qual[i]==points[2]:
                    points_reached[2] = True
                self.membership[i] = right_line(self.x_qual[i])
            
            if self.x_qual[i] > points[2]:
                break

class TrapizoidalMembership(Membership):
    #points - [min value, left corner, right corner, max value]
    def __init__(self, x_min, x_max, points:list, x_step=1, max_value = 1.0):
        super().__init__(x_min, x_max, x_step=x_step, mem_func=None, init_membership=False)

        points_reached = [False, False, False, False]

        if points[1] == points[0]:
            left_line = lambda x : max_value 
        else:
            left_line = lambda x : max_value/(points[1]-points[0]) * (x-points[0])
        
        if points[3] == points[2]:
            right_line = lambda x : max_value 
        else:
            right_line = lambda x : -max_value/(points[3]-points[2]) * (x-points[3]) 

        for i in range(len(self.x_qual)):
            if self.x_qual[i]==points[0]:
                points_reached[0] = True
            
            if points_reached[0] and not points_reached[1]:
                if self.x_qual[i]==points[1]:
                    points_reached[1] = True
                self.membership[i] = left_line(self.x_qual[i])

            if points_reached[1] and not points_reached[2]:
                if self.x_qual[i]==points[2]:
                    points_reached[2] = True
                self.membership[i] = max_value

            if points_reached[2] and not points_reached[3]:
                if self.x_qual[i]==points[3]:
                    points_reached[3] = True
                self.membership[i] = right_line(self.x_qual[i])
            
            if self.x_qual[i] > points[3]:
                break

class GaussianMembership(Membership):
    #points - [min value, left corner, right corner, max value]
    #have max_value = 1/sqrt(2pi*stddeviation^2) for a normal distribution
    def __init__(self, x_min, x_max, mean, stddeviation, x_step=0.1, max_value = 1.0):
        self.membership_func = lambda x: max_value*exp(-(x-mean)**2/(2*stddeviation**2))
        super().__init__(x_min, x_max, x_step=x_step, mem_func=self.membership_func, init_membership=True)

    def interp(self, x):
        #assume anything outside of the domain of x has a membership of zero
        if x<self.x_min or x>self.x_max:
            return 0
        
        #technically its not interpolation, however the gaussian is already created so its better to use that
        return self.membership_func(x)

def test():
    print("test")
    x_qual = np.arange(0,11,1)
    membership = GaussianMembership(0,10,5,2)
    qual = membership.membership
    print(qual)
    print(membership.interp(6.3))
    fig, ax0 = plt.subplots(nrows=1, figsize=(8, 4))

    ax0.plot(x_qual, qual, 'b', linewidth=1.5)
            

