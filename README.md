

# PyBreak
A block breaking game based on Python!

## Requirements
-  Python3

- Python Libarary ```Pillow```
 If you haven't installed yet, try this in a Terminal:
 ```pip install Pillow```

## Usage
### Run ```pybreak.py``` in a Terminal
 Run a demo for all of block types:

```python3 pybreak.py```

 Or select a stage by a command line argument such as:

```python3 pybreak.py stage1```

# Description
## Game Control System
### `class Game`

    game = Game(stage, width=600, height=480, dt=10)
creates a Game object ```game``` based on the given stage.

- ```game.objects```
A dictionary maps string of class name to list of corresponding objects, for all subclasses of GameObject.

| keys |values  |
|--|--|
| ```'GameObject'``` |```[<Ball instance>, <Paddle instance>, <Block instance>, ...]```|
| ```'Ball'``` |```[<Ball instance>, ...]```|
| ```'Paddle'``` |```[<Paddle instance>]```|
| ```'Block'``` |```[<Block instance>, <HardBlock instance>, ...]```|
| ... |...|

- ```game.start()```
Will start to run the game, which calls `obj.update()` every `dt` milliseconds for any `obj` where `obj` is a `GameObject` object and ==belongs to== `game`.
 
### `class GameObject`
All objects used for the game should be a instance of `GameObject`.
However, the `GameObject` class is not supposed to be instanciated directly. Instead, use a subclass of `GameObject` with a constructor of:

    __init__(self, game, *args, **kwargs)
This will make sure that the given `game` object knows this new object ==belongs to== itself.

### `class Stage`
**NOTE: Instead of instanciating `Stage` objects, it's better to use files, which will be described  next.**

	__init__(self, name, m, n, blocks)

- `name`
The name of the stage. Will be displayed in the title of the window.
- `m`
The number of rows of blocks.
- `n`
The number of cols of blocks.
- `blocks`
A list of lists of block classes in a row.

### Files for Stage
 - In the directory `config`, there is a file named `block_type`, which maps symbols to subclasses of `Block` in a format of
 
    {symbol}: {class_name}

 - In the directory `stage`, every file defines a stage with
   * its file name as `stage.name`, which is also the **command line argument for stage selection**
   * first line consists of 2 integers as `stage.m` and `stage.n`, respectively
   * remaining lines as `stage.blocks` using symbols defined in `block_type` mentioned above.
   
 - Take a look at existing files for an example.

## Physics Engine
### Collision Detection
AABB - Circle collision detection from [here](https://learnopengl.com/In-Practice/2D-Game/Collisions/Collision-Detection) by [Joey de Vries](https://joeydevries.com/#home) .
![enter image description here](https://learnopengl.com/img/in-practice/breakout/collisions_aabb_circle.png)![enter image description here](https://learnopengl.com/img/in-practice/breakout/collisions_aabb_circle_radius_compare.png)
### Perfect Elastic Collision
[Elastic collision](https://en.wikipedia.org/wiki/Elastic_collision)

## Blocks
### `class Block`
![Block](https://user-images.githubusercontent.com/48979946/106998455-e4d13200-67c7-11eb-8292-765b8a2ac57c.png)

A basic Block. Nothing special.

 - Will be rendered using a png image stored in the directory `image` with a file name of `{class_name}.png`. If not exists for a subclass, using `Block.png` instead.

 - `__init__(self, game, x, y, wx, wy)`
Creates a `Block` object with `center` at `(x, y)`, half x-span of `wx`, and half y-span of `wy`.
**Should be called explicitly if a subclass overrides it.**

 - `self.duration = 1`
indicates the necessary number of hits by a ball to destory it.

 - `apply_effect(self, ball)`
will be called whenever a collision with a `ball` happens.
Override this in subclasses to customize its behavior.

### `class HardBlock`
![HardBlock](https://user-images.githubusercontent.com/48979946/106998467-e7cc2280-67c7-11eb-8bdb-ef106bf6ce70.png)

A HardBlock. Needs 2 hits to destory.
- Has a total `duration` of `2`.
- Cracks when first hit.

![HardBlock_crack](https://user-images.githubusercontent.com/48979946/106998473-e8fd4f80-67c7-11eb-89c4-0b9b3f9f427f.png)

### `class SplitBlock`
![SplitBlock](https://user-images.githubusercontent.com/48979946/106998484-ec90d680-67c7-11eb-9a67-71c1adc3d32d.png)

A SplitBlock. Splits the ball.
- If hit by a `ball`, makes it to split into 2.

### `class ExtendBlock`
![ExtendBlock](https://user-images.githubusercontent.com/48979946/106998463-e69af580-67c7-11eb-8ae4-54361778cc11.png)

An ExtendBlock. Extends the paddle.
- If hit by a `ball`, extends the `paddle` by 50%.

### `class ShortenBlock`
![ShortenBlock](https://user-images.githubusercontent.com/48979946/106998476-ea2e7c80-67c7-11eb-94d2-d9989b6c964e.png)

A ShortenBlock. Shortens the paddle.
- If hit by a `ball`, shortens the `paddle` by 1/3.

### `class SpeedUpBlock`
![SpeedUpBlock](https://user-images.githubusercontent.com/48979946/106998482-ec90d680-67c7-11eb-9ec2-250bf464c252.png)

A SpeedUpBlock. Speeds up the ball.
- If hit by a `ball`, speeds it up by 50%.

### `class SlowDownBlock`
![SlowDownBlock](https://user-images.githubusercontent.com/48979946/106998481-ebf84000-67c7-11eb-92bb-e1a61419e4df.png)

A SlowDownBlock. Slows down the ball.
- If hit by a `ball`, slows it down by 1/3.
