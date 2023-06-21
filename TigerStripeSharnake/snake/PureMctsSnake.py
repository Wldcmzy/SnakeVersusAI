from ._SnakeBase import SnakeBase
from ..logic.MCTS06 import MCTSmethod

class PureMctsSnake(SnakeBase):
    def __init__(self, *args) -> None:
        super().__init__(*args)
    
    def get_rule(self):
        return MCTSmethod
        
