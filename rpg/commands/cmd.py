from ..utils import clear

class Command:
    def __init__(self, owner):
        self.owner = owner

class Any_Clear(Command):
    def __init__(self, owner):
        super(Any_Clear, self).__init__(owner)
        self.min_args = 0
        self.max_args = 0

    def __call__(self):
        clear()
