import random
import time
import pygame
from pygame import mixer
import serial
import serial.tools.list_ports


device_name = ""
port_name = ""
ports = list(serial.tools.list_ports.comports())
port_name = ports[0].device
ser = serial.Serial(port_name, baudrate=9600, timeout=0.1, bytesize=8, parity=serial.PARITY_ODD, stopbits=1)
time.sleep(2)


# initialization list
pygame.init()
mixer.init()


# Create the mainScreen
class Screen:

    def __init__(self, width=800, height=600, title="New Window", icon="NULL"):
        # Basic Parameters
        self.Width = width
        self.Height = height
        self.Surface = pygame.display.set_mode((self.Width, self.Height))  # return a surface object

        # Title
        pygame.display.set_caption(title)

        # Icon
        if icon != "NULL":
            self.icon = pygame.image.load(icon)
            pygame.display.set_icon(self.icon)


# create screens
myMainScreen = Screen(800, 720, "Space Invaders", "Pictures\\icon.png")

# set a motion upper limit for the player
UpperLimit = 0.5 * myMainScreen.Height


class Img:
    def __init__(self, source="NULL", width=0, height=0):
        self.source = source
        self.width = width
        self.height = height
        self.surface = pygame.image.load(self.source)

    def transformation(self, new_x, new_y):
        self.surface = pygame.image.load(self.source)
        self.surface = pygame.transform.scale(self.surface, (new_x, new_y))


# define images
bulletImg = [Img("Pictures\\bullet.png", 32, 32), Img("Pictures\\bullet2.png", 32, 32)]
enemyImg = Img("Pictures\\enemy.png", 64, 64)
playerImg = [Img("Pictures\\player.png", 64, 64), Img("Pictures\\player2.png", 64, 64)]
BackgroundImg = Img("Pictures\\logo.jpg", int(0.5 * myMainScreen.Width), int(0.5 * myMainScreen.Height))
HeartImg = Img("Pictures\\heart.png", 32, 32)
LaserImg = Img("Pictures\\laser.png", 32, 32)
BackgroundImg.surface.set_alpha(0)

BackgroundImg.transformation(int(0.5 * myMainScreen.Width), int(0.5 * myMainScreen.Height))
# enemyImg.transformation(128,128)
HeartImg.transformation(32, 32)

# define colours (R, G, B, alpha)
black = (0, 0, 0)
white = (255, 255, 255)  # input is a Tuple
Green = (0, 255, 0)
Red = (255, 0, 0)
Blue = (0, 0, 255)
DarkRed = (200, 0, 0)
DarkGreen = (0, 200, 0)
DarkBlue = (0, 0, 200)
Yellow = (255, 255, 0)

# Maneging Frames per seconds (FBS)
clock = pygame.time.Clock()  # returns a pygame clock object
FBS = 60

mixer.music.load("Audio\\Background.mp3")
mixer.music.play(-1)

Number_of_Players = 1


class BasicMovements:
    def __init__(self):
        self.Change_Right = 0
        self.Change_Left = 0
        self.Change_Up = 0
        self.Change_Down = 0
        self.MoveSpeedX = 8
        self.MoveSpeedY = 8

    def display(self, image, x, y):
        myMainScreen.Surface.blit(image, [x, y])  # input is a list


# =============================================== Player ===============================================================
class Player(BasicMovements):

    def __init__(self):
        BasicMovements.__init__(self)
        # Center the x and y coordinates of the player
        self.X = (myMainScreen.Width - playerImg[0].width) / 2
        self.Y = myMainScreen.Height - playerImg[0].height

        # Score
        self.Score = 0
        self.Life = 3
        self.Laser = 0

        self.Counter = 0
        self.invincible = False
        self.invincibleTime = 3

        self.t0 = 0

    def boundary_check(self):
        for i in range(Number_of_Players):
            if i in Players:
                if Players[i].X > (myMainScreen.Width - playerImg[i].width):  # Right Boundary
                    Players[i].X = myMainScreen.Width - playerImg[i].width

                if Players[i].X < 0:  # Left Boundary
                    Players[i].X = 0

                if Players[i].Y > (myMainScreen.Height - playerImg[i].height):  # Down Boundary
                    Players[i].Y = myMainScreen.Height - playerImg[i].height

                if Players[i].Y < UpperLimit:  # Up Boundary
                    Players[i].Y = UpperLimit


# =============================================== Enemy ===============================================================
class Enemy(BasicMovements):
    def __init__(self):
        BasicMovements.__init__(self)
        self.Health = 10

        # initial position is out of the screen
        self.X = random.uniform(-myMainScreen.Width - enemyImg.width, 2 * myMainScreen.Width)
        self.Y = - enemyImg.height

        self.MoveSpeedX /= 2
        self.MoveSpeedY /= 2

        self.time_per_enemy = 4
        self.t0 = time.time()

        self.score_per_hit = 15
        self.score_per_kill = 50

    def move(self):
        self.X += self.Change_Right + self.Change_Left
        self.Y += self.Change_Up + self.Change_Down

        if self.X > (myMainScreen.Width - enemyImg.width):  # exceed Right Boundary
            self.Change_Right = 0
            self.Change_Left = -self.MoveSpeedX

        elif self.X < 0:  # exceed Left Boundary
            self.Change_Right = self.MoveSpeedX
            self.Change_Left = 0

        if self.Y > (myMainScreen.Height - enemyImg.height):  # exceed lower Boundary
            self.Change_Down = 0
            self.Change_Up = -self.MoveSpeedY

        elif self.Y < 0:  # exceed upper Boundary
            self.Change_Down = self.MoveSpeedY
            self.Change_Up = 0

    def HealthBar(self):
        if self.X < 0:
            myMainScreen.Surface.fill(Green,
                                      rect=[self.X, int(self.Y - 10), (self.Health / 10) * enemyImg.width + self.X, 5])
        else:
            myMainScreen.Surface.fill(Green, rect=[self.X, int(self.Y - 10), (self.Health / 10) * enemyImg.width, 5])


# =============================================== Bullet ===============================================================
class Bullet(BasicMovements):
    def __init__(self, i):
        self.X = Players[i].X + random.randrange(0, int(playerImg[i].width / 2))
        self.Y = Players[i].Y
        BasicMovements.__init__(self)
        self.Damage = 2.5
        if i == 0:
            mixer.Sound("Audio\\Bullet.mp3").play()
        else:
            mixer.Sound("Audio\\Bullet2.mp3").play()
        self.MoveSpeedY *= 1.5
        self.Change_Up = - self.MoveSpeedY


Players = {}  # Creating a player object dictionary
myEnemy = Enemy()
Bullets = [[], []]
Enemies = []


# ==================================================== Laser ==========================================================
class Laser:
    def __init__(self):
        self.state = False
        self.Duration = 4  # Lasts for 3 seconds
        self.score_to_gain = 1000
        self.first_color = Red
        self.second_color = DarkRed
        self.t0 = 0

    def fire(self, i):
        if i == 1:
            self.first_color = Green
            self.second_color = DarkGreen
        myMainScreen.Surface.fill(self.first_color,
                                  rect=[int(Players[i].X), 0, int(playerImg[i].width), int(Players[i].Y)])
        myMainScreen.Surface.fill(self.second_color,
                                  rect=[int(Players[i].X + 0.25 * playerImg[i].width), 0, int(0.5 * playerImg[i].width),
                                        int(Players[i].Y)])


laser = []

for i in range(Number_of_Players):
    laser.append(Laser())
    Players[i] = Player()

# ============================================== other functions =======================================================
pt_to_px = 0.23
Font_Size = int(0.2 * pt_to_px * myMainScreen.Width)  # size = 20% of the screen width
scoreFont = pygame.font.SysFont(None, Font_Size)


def display_Data(message, data, x, y):
    message = scoreFont.render(message + str(data), True, white)
    myMainScreen.Surface.blit(message, [x, y])


def frame(object, img, color):
    if img.width > img.height:
        r = img.width
    else:
        r = img.height
    pygame.draw.circle(myMainScreen.Surface, color, (object.X + 0.5 * img.width, object.Y + 0.5 * img.height), r, 10)


Frame_Color = [Yellow, Blue]


def reset():
    for i in range(Number_of_Players):
        laser.append(Laser())
        Players[i] = Player()
        laser[i].__init__()
        Bullets[i].clear()
    Enemies.clear()


def game_over():
    gameover = True
    while gameover:
        myMainScreen.Surface.fill(black)
        display_Data("You Lose..Press U to try again", "", 0.20 * myMainScreen.Width,
                     0.20 * myMainScreen.Height)

        for event in pygame.event.get():
            # Ending the game
            if event.type == pygame.QUIT:
                running = False
                gameover = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    reset()
                    gameover = False

        pygame.display.update()
        clock.tick(5)


# ====================================================== Heart ======================================================
class Heart_Drop(BasicMovements):
    def __init__(self):
        self.X = random.randrange(0, int(myMainScreen.Width - HeartImg.width))
        self.Y = - 50
        BasicMovements.__init__(self)
        self.lives = 1
        self.Change_Up = self.MoveSpeedY * random.uniform(0.2, 1)
        self.t0 = 0
        self.time_per_drop = 30


myHeart = Heart_Drop()

Hearts_Drop = []


# ====================================================== Laser_Drops ============================================
class Laser_Drop(BasicMovements):
    def __init__(self):
        self.X = random.randrange(0, int(myMainScreen.Width - LaserImg.width))
        self.Y = - 50
        BasicMovements.__init__(self)
        self.laser = 1
        self.Change_Up = self.MoveSpeedY * random.uniform(0.2, 1)
        self.t0 = 5
        self.time_per_drop = 30


myLaser = Laser_Drop()

Lasers_Drop = []
LEFT = 1
RIGHT = 3
pos = [0, 0]

c = -1
countl=0
countr=0
x=''
#  *******************************************************Game Loop ****************************************************
def game_loop():
    running = True
    global c
    global x
    global countl
    global countr
    while running:

        if ser.in_waiting:
            c = int.from_bytes(ser.read(1),"big")

            print(c)
            if c==2:
                Players[0].Change_Right = Players[0].MoveSpeedX  # Move right
            elif c==1:
                Players[0].Change_Left = -Players[0].MoveSpeedX  # Move left
            elif c==0:
                Players[0].Change_Right = 0
                Players[0].Change_Left = 0
                #laser[0].state = False

            if c == 3:
                Bullets[0].append(Bullet(0))


            elif c == 4:
                Players[0].Change_Left = -Players[0].MoveSpeedX  # Move left
                if countl >5:
                    countl=0
                    Bullets[0].append(Bullet(0))
                else:
                    countl+=1
            elif c == 5:
                Players[0].Change_Right = Players[0].MoveSpeedX  # Move right
                if countr >5:
                    countr=0
                    Bullets[0].append(Bullet(0))
                else:
                    countr+=1

            '''elif c == 5:
                if Players[0].Laser >= 1:
                    laser[0].t0 = time.time()
                    Players[0].Laser -= 1
                    laser[0].state = True'''

        # =============================================== Event loop ===================================================
        for event in pygame.event.get():

            if 1 in Players:
                pos = pygame.mouse.get_pos()
                Players[1].X = pos[0]
                Players[1].Y = pos[1]

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == RIGHT:
                        if Players[1].Laser >= 1:
                            laser[1].t0 = time.time()
                            Players[1].Laser -= 1
                            laser[1].state = True
                    elif event.button == LEFT:
                        Bullets[1].append(Bullet(1))

            if 0 in Players:
                '''
                # Checks to see if a button is pressed
                if event.type == pygame.KEYDOWN :


                    # if the pressed key is the right key
                    if event.key == pygame.K_RIGHT :
                        Players[0].Change_Right = Players[0].MoveSpeedX  # Move right

                    # if the pressed key is the left key
                    elif event.key == pygame.K_LEFT:
                        Players[0].Change_Left = -Players[0].MoveSpeedX  # Move left

                    # if the pressed key is the up key
                    elif event.key == pygame.K_UP:
                        Players[0].Change_Up = -Players[0].MoveSpeedY  # Move up

                    # if the pressed key is the down key
                    elif event.key == pygame.K_DOWN:
                        Players[0].Change_Down = Players[0].MoveSpeedY  # Move down

                    # if the pressed key is the space bar
                    elif event.key == pygame.K_SPACE:
                        Bullets[0].append(Bullet(0))

                    elif event.key == pygame.K_LCTRL:
                        if Players[0].Laser >= 1:
                            laser[0].t0 = time.time()
                            Players[0].Laser -= 1
                            laser[0].state = True
                        

                # Checks to see if a button is Released
                if event.type == pygame.KEYUP:

                    if event.key == pygame.K_RIGHT:  # if right button is Released
                        Players[0].Change_Right = 0

                    elif event.key == pygame.K_LEFT:  # if left button is Released
                        Players[0].Change_Left = 0

                    elif event.key == pygame.K_UP:  # if up button is Released
                        Players[0].Change_Up = 0

                    elif event.key == pygame.K_DOWN:  # if down button is Released
                        Players[0].Change_Down = 0
            '''
            # Ending the game
            if event.type == pygame.QUIT:
                running = False
                gameover = True

        # =============================================== Background ===============================================
        # Fill the background
        myMainScreen.Surface.fill((40, 40, 60))  # Red, Green, Blue

        # Display a Background
        myMainScreen.Surface.blit(BackgroundImg.surface, (0.25 * myMainScreen.Width, 0.25 * myMainScreen.Height))
        BackgroundImg.surface.set_alpha(50)

        # Draw a line (surface, colour, [pos_x, pos_y, width, Height]) using fill "Graphically accelerated..."
        myMainScreen.Surface.fill(white, rect=[0, int(UpperLimit - 5), int(myMainScreen.Width), 5])

        # ============================================= Player =====================================================
        for j in range(Number_of_Players):
            if j in Players:
                Players[j].X += Players[j].Change_Right + Players[j].Change_Left
                Players[j].Y += Players[j].Change_Up + Players[j].Change_Down
                Players[j].boundary_check()
                Players[j].display(playerImg[j].surface, Players[j].X, Players[j].Y)

        # ============================================= Heart_Gained =================================================
        if (time.time() - myHeart.t0) > myHeart.time_per_drop:
            Hearts_Drop.append(Heart_Drop())
            myHeart.t0 = time.time()

        for HeartObj in Hearts_Drop:
            HeartObj.display(HeartImg.surface, HeartObj.X, HeartObj.Y)  # Display the Hearts_Drop[i]
            HeartObj.Y += HeartObj.Change_Up
            if HeartObj.Y > myMainScreen.Height:
                if HeartObj in Hearts_Drop:
                    Hearts_Drop.remove(HeartObj)

            # Loop through Players Positions
            for j in range(Number_of_Players):
                if j in Players:
                    # if a Heart hits a player
                    if Players[j].X <= HeartObj.X <= Players[j].X + playerImg[0].width \
                            and Players[j].Y <= HeartObj.Y <= Players[j].Y + playerImg[0].height:
                        mixer.Sound("Audio\\Heart_Gained.mp3").play()
                        Players[j].Life += myHeart.lives
                        if HeartObj in Hearts_Drop:
                            Hearts_Drop.remove(HeartObj)
        # ============================================= Laser_gained =================================================
        if (time.time() - myLaser.t0) > myLaser.time_per_drop:
            Lasers_Drop.append(Laser_Drop())
            myLaser.t0 = time.time()

        for LaserObj in Lasers_Drop:
            LaserObj.display(LaserImg.surface, LaserObj.X, LaserObj.Y)  # Display the Lasers_Drop[i]
            LaserObj.Y += LaserObj.Change_Up
            if LaserObj.Y > myMainScreen.Height:
                if LaserObj in Lasers_Drop:
                    Lasers_Drop.remove(LaserObj)

            # Loop through Players Positions
            for j in range(Number_of_Players):
                if j in Players:
                    # if a Laser hits a player
                    if Players[j].X <= LaserObj.X <= Players[j].X + playerImg[0].width \
                            and Players[j].Y <= LaserObj.Y <= Players[j].Y + playerImg[0].height:
                        mixer.Sound("Audio\\Laser_Gained.mp3").play()
                        Players[j].Laser += myLaser.laser
                        if LaserObj in Lasers_Drop:
                            Lasers_Drop.remove(LaserObj)

        # ============================================= Bullets ====================================================
        # Loop through active bullet
        for j in range(Number_of_Players):
            if j in Players:
                for BulletObj in Bullets[j]:
                    BulletObj.display(bulletImg[j].surface, BulletObj.X, BulletObj.Y)  # Display the Bullets[i]
                    BulletObj.Y += BulletObj.Change_Up
                    if BulletObj.Y < 0:
                        if BulletObj in Bullets[j]:
                            Bullets[j].remove(BulletObj)

                    # Loop through Enemies Positions
                    for EnemyObj in Enemies:

                        # if a bullet hits an enemy
                        if EnemyObj.X <= BulletObj.X <= EnemyObj.X + enemyImg.width \
                                and EnemyObj.Y <= BulletObj.Y <= EnemyObj.Y + enemyImg.height:

                            mixer.Sound("Audio\\Hit_Enemy.mp3").play()
                            EnemyObj.Health -= BulletObj.Damage
                            Players[j].Score += EnemyObj.score_per_hit

                            # if an enemy dies
                            if EnemyObj.Health <= 0:
                                if EnemyObj in Enemies:
                                    mixer.Sound("Audio\\Death_Enemy.mp3").play()
                                    Enemies.remove(EnemyObj)

                                    # when you kill an enemy maybe or maybe not another one will appear
                                    if random.randint(0, 1):
                                        Enemies.append(Enemy())

                                Players[j].Score += EnemyObj.score_per_kill

                            if BulletObj in Bullets[j]:
                                Bullets[j].remove(BulletObj)

        # ================================================== Enemies ===============================================

        # Create a new enemy every fixed duration
        if (time.time() - myEnemy.t0) > myEnemy.time_per_enemy:
            Enemies.append(Enemy())
            myEnemy.t0 = time.time()

        # loop through active enemies Enemy
        for EnemyObj in Enemies:
            EnemyObj.move()  # Move the enemy
            EnemyObj.display(enemyImg.surface, EnemyObj.X, EnemyObj.Y)
            EnemyObj.HealthBar()

            # Enemies-Player collision check
            for j in range(Number_of_Players):
                if j in Players:  # if this Player exists
                    if not Players[j].invincible:
                        if ((Players[j].X <= EnemyObj.X <= playerImg[j].width + Players[j].X) or
                            (Players[j].X <= EnemyObj.X + enemyImg.width <= playerImg[j].width + Players[j].X)) and \
                                ((Players[j].Y <= EnemyObj.Y <= playerImg[j].height + Players[j].Y) or
                                 (Players[j].Y <= EnemyObj.Y + enemyImg.height <= playerImg[j].height + Players[j].Y)):
                            Players[j].invincible = True
                            Players[j].t0 = time.time()

                            Players[j].Life -= 1
                            if Players[j].Life <= 0:
                                Players.pop(j)
                                if len(Players) == 0:
                                    game_over()

                    # Player after collision
                    else:
                        frame(Players[j], playerImg[j], Frame_Color[j])
                        if (time.time() - Players[j].t0) >= Players[j].invincibleTime:
                            Players[j].invincible = False

        # ================================================ Laser ===================================================
        for j in range(Number_of_Players):
            if j in Players:
                if laser[j].state:
                    mixer.Sound("Audio\\Laser.mp3").play()
                    if time.time() - laser[j].t0 < laser[j].Duration:
                        laser[j].fire(j)
                    else:
                        laser[j].state = False

                    # kill Enemies in laser sight
                    for EnemyObj in Enemies:
                        for k in range(Number_of_Players):
                            if k in Players:
                                if (Players[k].X <= EnemyObj.X + enemyImg.width <= Players[k].X + playerImg[k].width or
                                    Players[k].X <= EnemyObj.X <= Players[k].X + playerImg[k].width) and \
                                        EnemyObj.Y - enemyImg.height <= Players[k].Y:

                                    if EnemyObj in Enemies:
                                        mixer.Sound("Audio\\Death_Enemy.mp3").play()
                                        Enemies.remove(EnemyObj)

                                        # 50/50 chance i will create a new enemy
                                        if random.randint(0, 1):
                                            Enemies.append(Enemy())

            # gaining Laser
            for x in range(Number_of_Players):
                if x in Players:
                    if Players[x].Score >= laser[x].score_to_gain:
                        Players[x].Laser += 1
                        laser[x].score_to_gain += 1000

        # ============================================ Score =======================================================
        # Display player score
        for j in range(Number_of_Players):
            if j in Players:
                display_Data("Score = ", Players[j].Score, 10 + 0.8 * myMainScreen.Width * j, 10)
                display_Data("Lives = ", Players[j].Life, 10 + 0.8 * myMainScreen.Width * j, 40)
                display_Data("Laser = ", Players[j].Laser, 10 + 0.8 * myMainScreen.Width * j, 70)

            else:
                display_Data("Dead", "", 10 + 0.9 * myMainScreen.Width * j, 10)

        # ======================================== Screen Stuff ====================================================
        # Update Screen
        pygame.display.update()

        # Frames per second
        clock.tick(FBS)


game_loop()
pygame.quit()  # un-initializes the pygame library
quit()  # quit the program
