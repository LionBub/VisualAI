import Constants as Const


class BoundBox:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.n = min(y0, y1)
        self.s = max(y0, y1)
        self.e = max(x0, x1)
        self.w = min(x0, x1)


class Placeable:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.name = 'Empty'
        self.bound = None
        self.color = None
        self.drawing = None

    def setDrawing(self, d):
        self.drawing = d

    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y


class Circle(Placeable):
    index = 0

    def __init__(self, x, y, r):
        super().__init__(x, y)
        self.name = f'Circle({Circle.index})'
        self.bound = BoundBox(x + r, y + r, x - r, y - r)
        self.color = 'green'
        self.radius = r
        Circle.index += 1

    def setX(self, x):
        super().setX(x)
        self.bound = BoundBox(self.x + self.radius, self.y + self.radius, self.x - self.radius, self.y - self.radius)

    def setY(self, y):
        super().setY(y)
        self.bound = BoundBox(self.x + self.radius, self.y + self.radius, self.x - self.radius, self.y - self.radius)


class Comment(Placeable):
    def __init__(self, x, y, text):
        super().__init__(x, y)
        self.name = 'Comment'
        self.bound = BoundBox(x + 100, y + 100, x - 100, y - 100)
        self.color = 'yellow'
        self.text = text


class LayerBlock(Placeable):
    index = 0

    def __init__(self, x, y, size, spacing):  # assuming neuron radius is 50
        super().__init__(x, y)
        self.name = f'LayerBlock({LayerBlock.index})'
        self.bound = BoundBox(x + spacing, y + spacing * size, x - spacing, y - spacing * size)
        self.color = Const.COL_B
        self.ncolor = 'yellow'
        self.size = size
        self.spacing = spacing
        LayerBlock.index += 1

    def setX(self, x):
        super().setX(x)
        self.bound = BoundBox(self.x + self.spacing, self.y + self.spacing * self.size, self.x - self.spacing,
                              self.y - self.spacing * self.size)

    def setY(self, y):
        super().setY(y)
        self.bound = BoundBox(self.x + self.spacing, self.y + self.spacing * self.size, self.x - self.spacing,
                              self.y - self.spacing * self.size)
