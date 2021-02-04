import tkinter
from tkinter import ttk
import math
import os, sys

try:
    from PIL import Image, ImageTk
except ImportError:
    error = """The PyBreak needs PIL to run but failed to import it.
    Please consider to install the libarary Pillow by:

    $ pip install Pillow
    """
    sys.exit(error)

class Vector2D:
    """Represents a 2d vector."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x, self.y + other.y)
        else:
            raise TypeError("Vector2D is required.")
    
    __iadd__ = __add__

    def __sub__(self, other):
        return self.__add__(-other)
    
    __isub__ = __sub__

    def __mul__(self, other):
        if isinstance(other, Vector2D):
            return self.dot_product(other)
        elif type(other) in (int, float, complex):
            return Vector2D(self.x * other, self.y * other)
        else:
            raise TypeError("Vector2D or number is required.")
   
    __rmul__ = __mul__

    def __neg__(self):
        return self.__mul__(-1)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def magnitude(self):
        """Returns the magnitude of the vector."""
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalize(self):
        """Returns the corresponding unit vector as a new vector.
        If the original vector is a zero vector, return None."""
        length = self.magnitude()
        if length == 0:
            return None
        return Vector2D(self.x / length, self.y / length)
    
    def dot_product(self, other):
        """Returns the dot product of SELF and OTHER."""
        return self.x * other.x + self.y * other.y

    def project(self, other):
        """Returns the projection of SELF onto OTHER."""
        axis = other.normalize()
        dp = self.dot_product(axis)
        return dp * axis

    def normal(self):
        """Returns the perpendicular vector."""
        return Vector2D(-self.y, self.x)

    def clamp(self, x_bound, y_bound):
        """Clamps the vector to a vector of
        x and y within x_bound and y_bound respectively,
        then returns it."""

        def clamp_helper(value, upper, lower):
            """Clamps the VALUE to a value within UPPER and LOWER, then returns it."""
            result = min(value, upper)
            result = max(result, lower)
            return result

        x = clamp_helper(self.x, x_bound, -x_bound)
        y = clamp_helper(self.y, y_bound, -y_bound)
        return Vector2D(x, y)

    def same_direction(self, other):
        """Returns True if in same direction as OTHER,
        False otherwise."""
        return self.normalize() == other.normalize()

class Line2D:
    """Represents a line in a plane."""

    def __init__(self, a: Vector2D, n: Vector2D):
        """Creates the line of vector form x = A + tN,
        where A is a point on the line,
        and N is a unit vector in the direction of the line.
        Then as scalar t varies, x gives the locus of the line."""
        self.a = a
        self.n = n
    
    def dist_to(self, point: Vector2D):
        """Returns the distance to POINT."""
        return self.perpendicular(point).magnitude()
    
    def perpendicular(self, point: Vector2D):
        p_to_a = self.a - point
        return p_to_a.project(self.n) - p_to_a

class GameObject:
    
    def __new__(cls, game, *args, **kwargs):
        obj = super().__new__(cls)
        game.add_object(cls, obj)
        return obj

    def __init__(self, game, *args, **kwargs):
        self.game = game
        self.id = self.draw(game.cv, *args, **kwargs)

    def destory(self):
        self.game.cv.delete(self.id)
        self.game.remove_object(self)

    def update(self):
        pass

    def on_collision(self, other):
        pass

    @staticmethod
    def draw(cv, *args, **kwargs):
        return -1

class Wall(GameObject):
    """Represents a wall in the game."""

    def __init__(self, game, a, n):
        self.game = game
        self.line = Line2D(a, n)

    def on_collision(self, ball):
        direction = self.line.perpendicular(ball.center)
        ball.bounce(direction)

    def destory(self):
        self.game.remove_object(self)

class Buttom(Wall):
    """Represents the buttom of the canvas."""

    def __init__(self, game):
        """Creates the buttom y = game.height."""
        a = Vector2D(0, game.height)
        n = Vector2D(1, 0)
        super().__init__(game, a, n)

    def on_collision(self, ball):
        ball.destory()

class Ball(GameObject):
    """Represents a ball."""

    def __init__(self, game, x, y, radius, color='#636e72'):
        self.game = game
        self.center = Vector2D(x, y)
        self.radius = radius
        self.id = self.draw(game.cv, x, y, radius, color)
        v1 = self.game.height // 300
        self.velocity = Vector2D(v1, -v1)
        self.released = False

    @staticmethod
    def draw(cv, x, y, radius, color):
        return cv.create_oval(x - radius, y - radius, x + radius, y + radius, fill = color)

    def release(self, _):
        self.released = True
        self.move(self.velocity)

    def update(self):
        if not self.released:
            paddle = self.game.objects['Paddle'][0]
            diff = Vector2D(paddle.center.x - self.center.x, 0)
            self.move(diff)
            return
        self.check_collision()
        self.move(self.velocity)

    def move(self, diff):
        self.game.cv.move(self.id, diff.x, diff.y)
        self.center += diff

    def check_collision(self):
        self.check_walls()
        self.check_rectangles()

    def check_walls(self):
        for wall in self.game.objects['Wall']:
            if wall.line.dist_to(self.center) <= self.radius:
                wall.on_collision(self)
                break

    def check_rectangles(self):
        for rect in Rectangle.nearby(self):
            if self.collides_rect(rect):
                if not rect.collision:
                    rect.collision = True
                    rect.on_collision(self)
                return
            else:
                rect.collision = False

    def collides_rect(self, rect):
        """Returns Ture if collides with RECT,
        False otherwise."""
        self_rect = self.center - rect.center
        clamped = self_rect.clamp(rect.wx, rect.wy)
        closest = rect.center + clamped
        diff = self.center - closest
        if diff.magnitude() == 0:
            rect.diff = -self.velocity
        else:
            rect.diff = diff
        return diff.magnitude() <= self.radius

    def bounce(self, direction):
        """Simulates perfect elastic collision on the DIRECTION."""
        if direction.magnitude == 0:
            return
        v1 = self.velocity.project(direction)
        if v1.same_direction(direction):
            self.velocity += v1
        else:
            self.velocity -= v1 * 2

class Rectangle(GameObject):
    color = 'blue'

    def __init__(self, game, x, y, wx, wy):
        self.game = game
        self.center = Vector2D(x, y)
        self.wx = wx
        self.wy = wy
        self.id = self.draw(game.cv, x, y, wx, wy, self.color)
        self.diff = None
        self.collision = False

    @staticmethod
    def draw(cv, x, y, wx, wy, color):
        x1, y1 = x - wx, y - wy
        x2, y2 = x + wx, y + wy
        return cv.create_rectangle(x1, y1, x2, y2, fill=color, tag="paddle")

    @staticmethod
    def nearby(obj):
        """Returns rectangles nearby OBJ,
        which means they may have collision with OBJ."""
        result = obj.game.objects['Rectangle'][:]
        return result

    def right_edge_x(self):
        return self.center.x + self.wx

    def left_edge_x(self):
        return self.center.x - self.wx
    
    def on_collision(self, ball):
        ball.bounce(self.diff)

    def change_wx(self, value):
        self.wx = value
        self.game.cv.delete(self.id)
        self.id = self.draw(self.game.cv, self.center.x, self.center.y, self.wx, self.wy, self.color)

class Paddle(Rectangle):
    color = '#0984e3'

    def __init__(self, *args):
        super().__init__(*args)
        self.velocity = Vector2D(self.game.width // 50, 0)
        self.direction = 0

    def update(self):
        self.move(self.direction * self.velocity)
        self.direction = 0

    def right_key(self, _):
        if not self.game.is_running:
            return
        self.direction = 1
    
    def left_key(self, _):
        if not self.game.is_running:
            return
        self.direction = -1
    
    def move(self, diff):
        right_most = self.right_edge_x() >= self.game.width and diff.x >= 0
        left_most = self.left_edge_x() <= 0 and diff.x <= 0
        if right_most or left_most:
            return
        self.game.cv.move(self.id, diff.x, diff.y)
        self.center += diff

class Block(Rectangle):
    """Represents a Block."""

    def __init__(self, game, x, y, wx, wy):
        self.img_tk = None
        self.durable = 1
        super().__init__(game, x, y, wx, wy)

    @classmethod
    def get_img_path(cls, appendix=[]):
        names = [cls.__name__] + appendix
        return 'image/{}.png'.format('_'.join(names))

    def draw(self, *args, **kwargs):
        """Displays the [class_name].png image stored in directory image."""
        if not self.img_tk:
            self.img_tk = self.read_imagetk(self.get_img_path(), self.wx * 2, self.wy * 2)
        return self.game.cv.create_image(self.center.x, self.center.y, image=self.img_tk)

    @staticmethod
    def read_imagetk(file, width, height):
        if os.path.exists(file):
            img = Image.open(file)
        else:
            img = Image.open(Block.get_img_path())
        img = img.resize(size=(int(width), int(height)))
        return ImageTk.PhotoImage(img)

    def destory(self):
        self.game.score.set(self.game.score.get() + 1)
        super().destory()
    
    def on_collision(self, ball):
        super().on_collision(ball)
        self.durable -= 1
        self.apply_effect(ball)
        if self.durable <= 0:
            self.destory()

    def apply_effect(self, ball):
        """Will be called when collides with a ball."""
        pass
    
class HardBlock(Block):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.durable = 2

    def apply_effect(self, _):
        self.redraw(self.get_img_path(['crack']))

    def redraw(self, file):
        self.game.cv.delete(self.id)
        self.img_tk = self.read_imagetk(file, self.wx * 2, self.wy * 2)
        self.id = self.draw()

class SplitBlock(Block):

    def apply_effect(self, ball):
        new_ball = Ball(self.game, ball.center.x, ball.center.y, ball.radius)
        new_ball.velocity = -ball.velocity
        new_ball.released = True


class ExtendBlock(Block):

    def apply_effect(self, _):
        paddle = self.game.objects['Paddle'][0]
        paddle.change_wx(paddle.wx * 1.5)

class ShortenBlock(Block):

    def apply_effect(self, _):
        paddle = self.game.objects['Paddle'][0]
        paddle.change_wx(paddle.wx / 1.5)

class SpeedUpBlock(Block):

    def apply_effect(self, ball):
        ball.velocity *= 1.5

class SlowDownBlock(Block):

    def apply_effect(self, ball):
        ball.velocity *= 1 / 1.5

class Game:
    """A class for holding every information needed for the PyBreak game.
    
    Any other object for the game should be passed a Game object during initiation."""
    instruction_str = 'MOVE:  <  >\nRELEASE:  SPACE'
    over_str = 'Game Over!'
    clear_str = 'Game Clear!\nCongratulations!'

    def __init__(self, stage, width=600, height=480, dt=10):
        self.stage = stage
        self.width = width
        self.height = height * 0.9
        self.dt = dt
        self.win = tkinter.Tk()
        self.win.title('PyBreak - ' + stage.name)
        self.objects = {}
        self.create_ui()
        self.create_canvas()
        self.is_running = False

    def add_object(self, cls, obj):
        """Adds OBJ into objects which is a dictionary with 
        class names as keys and
        a list of all instance of the corresponding class as values."""
        for name in self.class_names(cls):
            if not name in self.objects:
                self.objects[name] = []
            self.objects[name].append(obj)

    def remove_object(self, obj):
        """Removes OBJ from objects which is a dictionary with
        class names as keys and
        lists of all instance of the corresponding class as values."""
        for name in self.class_names(obj.__class__):
            self.objects[name].remove(obj)

    @staticmethod
    def class_names(cls):
        """Yields every class name from CLS's name,
        then its super class's name,
        until one of the base_names"""
        for c in cls.__mro__:
            yield c.__name__
            if c == GameObject:
                break

    def start(self):
        self.clear()
        self.create_paddle()
        self.create_ball()
        self.create_blocks()
        self.create_walls()
        if not self.is_running:
            self.is_running = True
            self.update()
        self.win.mainloop()
        
    def update(self):
        if not self.objects['Block']:
            self.game_clear()
        elif not self.objects['Ball']:
            self.game_over()
        else:
            for obj in self.objects['GameObject']:
                obj.update()
            if self.is_running:
                self.win.after(self.dt, self.update)

    def game_over(self):
        self.is_running = False
        self.restart_button['fg']='green'
        self.message.set(self.over_str)

    def game_clear(self):
        self.is_running = False
        self.message.set(self.clear_str)

    def create_ui(self):
        frameh = widgeth = self.height / 9
        widgetw = self.width / 6
        self.frame = ttk.Frame(self.win, width=self.width, height=frameh).pack()
        self.score = tkinter.IntVar(value=0)
        ttk.Label(self.frame, text='Score').place(
            x=widgetw / 2, y=0, width=widgetw, height=widgeth)
        ttk.Label(self.frame, textvariable=self.score).place(
            x=widgetw, y=0, width=widgetw, height=widgeth)
        self.message = tkinter.StringVar(value=self.instruction_str)
        tkinter.Label(self.frame, textvariable=self.message, fg='red', bg='#ececec').place(
            x=self.width / 2 - widgetw / 2, y=0, width=widgetw, height=widgeth)
        self.restart_button = tkinter.Button(self.frame, text='Restart', command=self.start)
        self.restart_button.place(x=self.width - widgetw, y=0, width=widgetw, height=widgeth)

    def create_canvas(self):
        self.cv = tkinter.Canvas(self.win, width=self.width, height=self.height, bg='white')
        self.cv.pack()

    def clear(self):
        self.objects = {}
        self.cv.delete('all')
        self.score.set(0)
        self.restart_button['fg']='black'
        self.message.set(self.instruction_str)

    def create_paddle(self):
        x = self.width / 2
        y = self.height * 15 // 16
        wx = self.width // 13
        wy = self.height // 60
        paddle = Paddle(self, x, y, wx, wy)
        self.win.bind('<Right>', paddle.right_key)
        self.win.bind('<Left>', paddle.left_key)

    def create_ball(self):
        r = self.height // 48
        paddle = self.objects['Paddle'][0]
        x = paddle.center.x
        y = paddle.center.y - paddle.wy - r
        ball = Ball(self, x, y, r)
        self.win.bind('<space>', ball.release)

    def create_blocks(self):
        if (self.stage.n == 0 or self.stage.m == 0):
            return
        w = (self.width - 2) // self.stage.n
        h = self.height / 2 // self.stage.m
        for i in range(self.stage.m):
            for j in range(self.stage.n):
                x = 2 + w / 2 + w * j
                y = 2 + h / 2 + h * i
                block = self.stage.blocks[i][j]
                if block:
                    block(self, x, y, w / 2, h / 2)
    
    def create_walls(self):
        Buttom(self)
        Wall(self, Vector2D(0, 0), Vector2D(0, 1))          # Left
        Wall(self, Vector2D(self.width, 0), Vector2D(0, 1)) # Right
        Wall(self, Vector2D(0, 0), Vector2D(1, 0))          # Top

class Stage:

    def __init__(self, name, m, n, blocks):
        self.name = name
        self.m = m
        self.n = n
        self.blocks = blocks

def parse_dict(file):
    result = {}
    with open(file, 'r') as f:
        for line in f:
            items = line.split(':')
            result[items[0].strip()] = eval(items[1].strip())
    return result

def parse_stage(file, block_type):
    blocks = []
    with open(file, 'r') as f:
        sizes = f.readline().split()
        m, n = (int(i) for i in sizes)
        for line in f:
            items = line.split()
            blocks.append([block_type[i] for i in items])
    name = file.split('/')[-1]
    return Stage(name, m, n, blocks)

if __name__ == '__main__':
    block_type = parse_dict('config/block_type')
    stage_dir = 'stage/'
    stage_file = 'demo' if len(sys.argv) == 1 else sys.argv[1]
    stage = parse_stage(stage_dir + stage_file, block_type)
    game = Game(stage, 1280, 720)
    game.start()