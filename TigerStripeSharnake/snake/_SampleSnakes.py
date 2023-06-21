from ..logic.Algorithm import Rule
from ._SnakeBase import SnakeBase

class RandomSnake(SnakeBase):
    def __init__(self, *args) -> None:
        super().__init__(*args)
    
    def get_rule(self):
        return Rule.random
        

class PersueRoomSnake(SnakeBase):
    def __init__(self, *args) -> None:
        super().__init__(*args)
    
    def get_rule(self):
        return Rule.persue_room