from ..game.config import STEP
from ..game.game import Game
from ..utils.types import Position
import numpy as np
import random

class Rule:
    
    @staticmethod
    def random(board: np.ndarray, player: Position, enemy: Position, xturns: int, length: int):
        xturns, length = Game.grow(xturns, length)
        d = random.randint(0, 3)
        for i in range(3):
            xx, yy = STEP[d]
            x, y = player
            xxx, yyy = x + xx, y + yy

            if Game.isCrash(board[xxx][yyy], xturns, length):
                d = (d + 1) % 4
            else:
                break
        return d

    @staticmethod
    def persue_room(board: np.ndarray, player: Position, enemy: Position, xturns: int, length: int):
        xturns, length = Game.grow(xturns, length)

        r, c = board.shape
        ans = []
        score = {0: 9.3, 1: 3, 2: 0.9}

        for i in range(4):
            x, y = player
            xx, yy = STEP[i]
            xxx, yyy = xx + x, yy + y

            v = 0
            if Game.isCrash(board[xxx][yyy], xturns, length):
                v = -1000
            else:  
                vis = {}
                lst = [(xxx, yyy, 0)]
                while len(lst) > 0:
                    x, y, t = lst.pop(0)
                    if t > 2 or (x, y) in vis: continue
                    vis[(x, y)] = True
                    for j in range(4):
                        xx, yy = STEP[j]
                        xxx, yyy = xx + x, yy + y
                        if not Game.isCrash(board[xxx][yyy], xturns, length):
                            v += score[t]
                            lst.append((xxx, yyy, t + 1))
            ans.append(v)
        # print(ans)
        d = 0
        for i in range(len(ans)):
            if ans[d] < ans[i]:
                d = i
        return d
    
    
    







