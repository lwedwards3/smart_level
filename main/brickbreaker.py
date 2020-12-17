from random import randint
from time import sleep

class Piece:
    
    def __init__(self, pos=[0, 0], size=(0, 0), velo=[0, 0]):
        self.pos = pos
        self.size = size
        self.velo = velo
        self.update_rect()
        
    
    def update_rect(self):
        self.rect = [self.pos[0], self.pos[1], self.size[0], self.size[1]]
        self.lower_right = [self.pos[0]+self.size[0]-1, self.pos[1]+self.size[1]-1]
    
        
    def move(self, velo=None):
        if not velo:
            self.pos[0] += (self.velo[0])
            self.pos[1] += (self.velo[1])
        else:
            self.pos[0] += (velo[0])
            self.pos[1] += (velo[1])
        self.update_rect()
        
        
    def is_touching(self, other):

        def is_inside(point, box):
            return (point[0] >= box.pos[0] and point[0] <= box.lower_right[0]) and (point[1] >= box.pos[1] and point[1] <= box.lower_right[1])
        
        return is_inside(self.pos, other) or is_inside(self.lower_right, other)
    
    
    def four_corners(self, square):
        return ((square.rect[0], square.rect[1]),
                (square.rect[0], square.pos[1] + square.size[1]-1),
               (square.pos[0] + square.size[0]-1, square.pos[1]),
                (square.pos[0]+ square.size[0]-1 , square.pos[1] + square.size[1]-1))


class Brick(Piece):
    
    def __init__(self, pos=[0, 0], size=(3, 6), velo=[0, 0], points=1, hits_left=0):
        Piece.__init__(self, pos, size, velo)
        self.points = points
        self.hits_left = hits_left
        
        
        
class Ball(Piece):
    
    def __init__(self, pos=[0, 0], size=(0, 0), velo=[0, 0], speed=1):
        Piece.__init__(self, pos, size, velo)
        self.speed=speed


    def move(self, velo=None):
        if not velo:
            self.pos[0] += (self.velo[0] * self.speed)
            self.pos[1] += (self.velo[1] * self.speed)
        else:
            self.pos[0] += (velo[0] * self.speed)
            self.pos[1] += (velo[1] * self.speed)
        self.update_rect()



class BrickBreaker:
    
    def __init__(self, gyro, display):
        self.gyro=gyro
        self.display = display
        self.bricks = []
        self.brick_size = (3, 6)
        self.brick_vel = [0, 0]
        self.bottom_brick = 0
        self.xlim = (16, 118)
        self.ylim = (0, 63)
        self.lives = 3
        self.points = 0
        self.get_hi_score()
        self.new_hi_score = False
        
       
    def setup(self):
        self.bricks = []
        for r in range(3, 8):
            for c in range(14):
                posy = self.ylim[0] + r * (self.brick_size[0] + 1)
                posx = self.xlim[0] + 2 + c * (self.brick_size[1] + 1) + ((r % 2) * (self.brick_size[1] // 2))
                
                # a certain percentage of bricks are 'high value'.
                # it takes multiple hits to break them; but you get more points.
                points=1
                hits_left=0
                if randint(1, 100) < 3:
                    points=5
                    hits_left=2
                    
                self.bricks.append(Brick(pos=[posy, posx],
                                   size=self.brick_size, 
                                   #velo=[0,0],
                                    points=points,
                                    hits_left=hits_left))
                self.bottom_brick = max(posy + self.brick_size[0], self.bottom_brick)

        self.paddle = Piece(pos=[61, 58], size=(1, 10))
        self.ball = Ball(size=(2, 2))
        self.left_wall = Piece(pos=[0, self.xlim[0]], size=(64, 1))
        self.right_wall = Piece(pos=[0, self.xlim[1]], size=(64, 1))
        self.lives = 3
        self.points = 0
        self.serve()

        
    def get_hi_score(self):
        try:
            with open('hi_score.txt','r') as fb:
                self.hi_score = int(fb.read())
        except OSError:
            self.hi_score = 0
    
    
    def map(self, raw, in_min, in_max, out_min, out_max):
        in_range = in_max - in_min
        out_range = out_max - out_min
        return (raw - in_min) * out_range / in_range + out_min
    

    def move(self):
        x_angle = self.gyro.get_angles()[0]
        self.paddle.pos[1] = int(self.map(x_angle, -30, 30, 0, 127))
        self.paddle.move()
        self.ball.move()

        
    def serve(self):
        ball_x = randint(self.xlim[0], self.xlim[1])
        self.ball.pos=[60, ball_x]
        ball_direction = 1 if randint(0,1) == 0 else -1
        directions = [-2, -1, -1, -1, 0, 1, 1, 1, 2]
        ball_direction = directions[randint(0,8)]
        self.ball.velo = [-1, ball_direction]
        
    
    def find_collisions(self):
        # ball vs brick
        if self.ball.pos[0] <= self.bottom_brick:  # only test bricks if ball is in the range
            touched=False
            for brick in self.bricks:
                if self.ball.is_touching(brick):
                    touched=True
                    if brick.hits_left == 0:
                        self.points += brick.points
                        self.bricks.remove(brick)
                    else:
                        brick.hits_left -= 1
                        self.ball.velo[1] *= -1
                    break

            if touched:  
                #print('brick')
                self.ball.velo[0] *= -1
                self.ball.speed = 1 + self.points // 25
                
        # ball vs left wall
        if self.ball.pos[1] <= self.xlim[0]:
            #print('left')
            self.ball.velo[1] *= -1
            self.ball.move()
        
        # ball vs right wall
        if self.ball.lower_right[1] >= self.xlim[1]:
            #print('right')
            self.ball.velo[1] *= -1
            self.ball.move()
            
        # ball vs ceiling
        if self.ball.pos[0] <= self.ylim[0]:
            #print('ceiling')
            self.ball.velo[0] *= -1
            
        # ball vs floor
        if self.ball.lower_right[0] >= self.ylim[1]:
            #print('floor')
            self.lives -= 1
            self.lost_life()
            self.serve()
            
        # ball vs paddle
        if self.ball.is_touching(self.paddle):
            #print('paddle')
            sign = -1 if self.ball.velo[1] < 0 else 1
            if self.ball.pos[1] <= self.paddle.pos[1] + (self.paddle.size[1] // 4):
                self.ball.velo[1] = -2  # angle ball, if hit from the extreme left side
            elif self.ball.lower_right[1] >= self.paddle.lower_right[1] - self.paddle.size[1] // 4:
                self.ball.velo[1] = 2 # angle ball, if hit from the extreme side
            elif self.ball.pos[1] + self.ball.size[1]//2 == self.paddle.pos[1] + self.paddle.size[1]//2:
                self.ball.velo[1] = 1
            else:           
                self.ball.velo[1] = -1 * sign
            self.ball.velo[0] *= -1
                
        # keep paddle in bounds
        if self.paddle.pos[1] < self.xlim[0]:
            self.paddle.pos[1] = self.xlim[0]
        if self.paddle.lower_right[1] > self.xlim[1]:
            self.paddle.pos[1] = self.xlim[1] - self.paddle.size[1]


    def lost_life(self):
        self.display.fill(0)
        self.display.text('X',64,32)
        self.display.show()
        sleep(1)
    
    
    def refresh_display(self, game_over=False):
        def draw_rect(piece, fill=False):
            #if piece.hits_left > 0:
            #    self.display.fill_rect(piece.rect[1], piece.rect[0], piece.rect[3], piece.rect[2], 1)
            #else:
            #    self.display.rect(piece.rect[1], piece.rect[0], piece.rect[3], piece.rect[2], 1)
            if fill:
                self.display.fill_rect(piece.rect[1], piece.rect[0], piece.rect[3], piece.rect[2], 1)
            else:
                self.display.rect(piece.rect[1], piece.rect[0], piece.rect[3], piece.rect[2], 1)
        
        self.display.fill(0)
        self.display.text(str(self.points), 0, 0)
        
        if not game_over:
            for brick in self.bricks:
                draw_rect(brick, brick.hits_left>0)
            draw_rect(self.left_wall)
            draw_rect(self.right_wall)
            draw_rect(self.paddle)
            draw_rect(self.ball)
            for i in range(self.lives):
                self.display.text("^", 120, 6 * i)
        
        if game_over:
            self.display.text("    Game Over", 0, 16)
            self.display.text("  High Score: "+str(self.hi_score), 0, 36)
    
        self.display.show()
        
        
    def cycle(self):
        self.move()
        self.find_collisions()
        if self.lives > 0:
            self.refresh_display()
            return True
        else:
            if self.points > self.hi_score:
                self.set_hi_score()
            self.refresh_display(game_over=True)
            return False


    def set_hi_score(self):
        self.hi_score = self.points
        with open('hi_score.txt','w') as fb:
            fb.write(str(self.hi_score))
        self.new_hi_score = True
    
    
    def play(self, lives=3):
        self.setup()
        self.lives=lives
        while self.lives > 0:
            self.cycle()

        