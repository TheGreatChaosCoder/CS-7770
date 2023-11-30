import pygame
import time
import math
import numpy as np
from memberships import Membership, GaussianMembership, TrapizoidalMembership
from fis import Rule

def scale_image(img: pygame.Surface, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blit_rotate_center(win, image, top_left, angle):
    # This rotates around top left (distortion)
    rotated_image = pygame.transform.rotate(image, angle)
    # Take rotated image and put it at center of old image
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft = top_left).center)
    win.blit(rotated_image, new_rect.topleft)

DESERT = scale_image(pygame.image.load("imgs/desert.png"), 2)
TRACK_SCALE_FACTOR = 0.7
TRACK = scale_image(pygame.image.load("imgs/track.png"), TRACK_SCALE_FACTOR)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), TRACK_SCALE_FACTOR)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

INNER_TRACK_BORDER = scale_image(pygame.image.load("imgs/inner-track-border.png"), TRACK_SCALE_FACTOR)
INNER_TRACK_BORDER_MASK = pygame.mask.from_surface(INNER_TRACK_BORDER)

OUTER_TRACK_BORDER = scale_image(pygame.image.load("imgs/outer-track-border.png"), TRACK_SCALE_FACTOR)
OUTER_TRACK_BORDER_MASK = pygame.mask.from_surface(OUTER_TRACK_BORDER)

FINISH = pygame.image.load("imgs/finish.png")
FINISHMASK = pygame.mask.from_surface(FINISH)

CAR_SCALE_FACTOR = 0.5
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), CAR_SCALE_FACTOR)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

FPS = 60

class Car:
    IMG = RED_CAR
    START_POS = (140, 200)

    def __init__(self, max_vel, rotation_vel) -> None:
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotational_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.rewardgate = 0
        self.gameScore = 0
    
    def reset(self):
        self.vel = 0
        self.angle = 0
        self.x, self.y = self.START_POS
        self.gameScore = 0
        
    
    def rotate(self, left=False, right=False, rotational_vel = None):
        if rotational_vel is None:
            rotational_vel = self.rotational_vel

        if left:
            self.angle += rotational_vel
        elif right:
            self.angle -= rotational_vel
        else:
            self.angle += rotational_vel
    
    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
        self.draw_rays(win,self,TRACK_BORDER_MASK,100)
    
    def move(self):
        radians = math.radians(self.angle)
        vertical = self.vel * math.cos(radians) 
        horizontal = self.vel * math.sin(radians) 
        # Weird reasons for subtracting (just trust)
        self.x -= horizontal
        self.y -= vertical
    
    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
    
    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
    
    def reduce_speed(self):
        if(self.vel >= 0):
            self.vel = max(self.vel - self.acceleration/2, 0)
        else:
            self.vel = min(self.vel + self.acceleration, 0)
    
    # Takes mask of object car could collide with (TRACK_BORDER_MASK) and its coordinates
    def car_collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        # If poi (point of intersction) is none, no collision occured
        return poi
    
    #Gets the point of intersection between the car and the track border in four directions and returns those coordinates for each direction.
    def getWallPointOfIntersection(self,mask,x=0,y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = [int(self.x - x), int(self.y - y)]
        rightpoi = None
        leftpoi = None
        frontpoi = None
        rearpoi = None
        while(rightpoi == None):
            offset[0] +=1
            rightpoi = mask.overlap(car_mask,offset)
        while(leftpoi == None):
            offset[0] -=1
            leftpoi = mask.overlap(car_mask,offset)
        while(frontpoi == None):
            offset[0] = self.x
            offset[1] -=1
            frontpoi = mask.overlap(car_mask,offset)
        while(rearpoi == None):
            offset[0] = self.x
            offset[1] +=1
            rearpoi = mask.overlap(car_mask,offset)
        return rightpoi,leftpoi,frontpoi,rearpoi

    def bounce(self):
        self.vel = -self.vel
    
    def correctDirection(self):
        ray_length = 50
        
        correct_right_ray = self.cast_ray(0,OUTER_TRACK_BORDER_MASK,ray_length)
        correct_left_ray = self.cast_ray(math.pi,INNER_TRACK_BORDER_MASK,ray_length)
        wrong_right_ray = self.cast_ray(0,INNER_TRACK_BORDER_MASK,ray_length)
        wrong_left_ray = self.cast_ray(math.pi,OUTER_TRACK_BORDER_MASK,ray_length)
        
        if not correct_right_ray and wrong_right_ray:
            return 0
        
        if not correct_left_ray and wrong_left_ray:
            return 0
        
        return 1
    
    def distance_to_point(self, point):
        return math.sqrt((self.x - point[0]) ** 2 + (self.y - point[1]) ** 2)

    def cast_ray(self, direction, mask, max_length):
        initDirection = 90
        radians = math.radians(self.angle + initDirection)
        dx = math.sin(radians + direction)
        dy = math.cos(radians + direction)
        
        x, y = self.x,self.y
        for _ in range(max_length):
            x += dx
            y += dy
            
            offset = (int(x),int(y))
            poi = mask.overlap(pygame.mask.from_surface(self.img),offset)
            
            if poi:
                distance = self.distance_to_point(offset)
                return offset, poi, distance
            
        return None
    
    def cast_rays(self, mask, max_length):
        right_ray = self.cast_ray(0, mask, max_length)
        left_ray = self.cast_ray(math.pi, mask, max_length)
        front_ray = self.cast_ray(math.pi / 2, mask, max_length)

        return right_ray, left_ray, front_ray
    
    def draw_rays(self,win, car, mask, max_length):
        rays = self.cast_rays(mask, max_length)
        i = 0
        for ray in rays:
            color = (255,0,0)
            if ray:
                # Draw the ray from the car's position to the point of intersection
                if i == 3:
                    color = (0,255,0)
                pygame.draw.line(win, color, (car.x + 10, car.y + 10), ray[0], 2)
            i += 1

    def getWallDistances(self):
        walldistancearray = np.zeros(3)
        rays = self.cast_rays(TRACK_BORDER_MASK,100)
        i = 0
        for ray in rays:
            if ray:
                walldistancearray[i] = int(ray[2])
            else:
                walldistancearray[i] = 100
            i += 1
        return walldistancearray

# Event Loop
run = True
clock = pygame.time.Clock()
images = [(DESERT, (0, 0)), (TRACK, (0, 0)), (FINISH, (88, 250))]
car = Car(3, 4)

def draw(win, images, car):
    for img, pos in images:
        win.blit(img, pos)
    
    car.draw(win)

def move_player_keyboard(car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        car.rotate(left=True)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        car.rotate(right=True)
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        moved=True
        car.move_forward()
    # Change to if for cool speed glitch (hold both up and down arrow)
    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
        moved=True
        car.move_backward()
    
    if not moved:
        car.reduce_speed()

#Define Memberships Here
#Wall-too-close-to-car Antecedents
distance_min = 0
distance_max = 100

close_to_front = TrapizoidalMembership(distance_min, distance_max, [0,0,50,60], x_step=0.5)
close_to_left = GaussianMembership(distance_min,distance_max, 0, 20)
close_to_right = GaussianMembership(distance_min,distance_max, 0, 20)

#Rotational Velocity Consequents (negative = turn right)
max_rot_vel = 10.0

turn_right = TrapizoidalMembership(-max_rot_vel, max_rot_vel, [-max_rot_vel,-max_rot_vel,-5,-0.5], x_step=0.5)
turn_left = TrapizoidalMembership(-max_rot_vel, max_rot_vel, [0.5,5,max_rot_vel,max_rot_vel], x_step=0.5)
keep_straight = GaussianMembership(-max_rot_vel, max_rot_vel, 0, 0.5)

#Rules
#Rule 1 - If close to left and close to front -> turn right
right_turn_move = Rule([close_to_left, close_to_front], turn_right)
#Rule 2 - If close to right and close to front -> turn left
left_turn_move = Rule([close_to_right, close_to_front], turn_left)
#Rule 3 - If not close to right and not close to left and not close to front -> keep straight
keep_foward_move = Rule([close_to_right.yager_compliment(), close_to_left.yager_compliment(), close_to_front.yager_compliment()], keep_straight)

def move_player_fuzzy(car):
    distances = car.getWallDistances()
    min_memberships = [right_turn_move.evaluate([distances[0], distances[2]]), 
                       left_turn_move.evaluate([distances[1],distances[2]]), 
                       keep_foward_move.evaluate([distances[0], distances[1], distances[2]])]
    
    _, result = Rule.defuzzify([right_turn_move, left_turn_move, keep_foward_move], 
                               min_memberships, aggregation_op="max_min", dx=0.1)
    print(min_memberships,distances ,result)
    if int(round(result,0)) == 0:
        car.move_forward()
    elif abs(result) >= 1.0:
        car.rotate(rotational_vel = -result)
    else:
        car.reduce_speed()

while run:
    # Clock prevents faster than 60 FPS
    clock.tick(FPS)

    # Updates new drawings/changes
    pygame.display.flip()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
    
    #move_player_keyboard(car)
    move_player_fuzzy(car)

    draw(WIN, images, car)
    
    if(car.car_collide(TRACK_BORDER_MASK) != None):
        car.bounce()
    # elif(car.collide(HORIZONTALLINEMASK, 88, 150)!=None):
    #     # car.bounce()
    # elif(car.collide((VERTICALLINEMASK), 120,120)!=None):
    #     # car.bounce()
    
    car.move()

    
    

pygame.quit()
