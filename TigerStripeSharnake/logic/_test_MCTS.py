# from __future__ import annotations
import numpy as np
import math
import random
import time
import hashlib
import copy
from ..game.game import Game
from ..utils.T import T, G
from .Algorithm import Rule
from ..utils.types import Position, List, Tuple

# from log import logger

class State:
    def __init__(
        self, 
        board: np.ndarray, 
        player: Position, 
        enemy: Position,
        xtruns: int,
        length: int,
        depth: int,
        re = None,
        finished = False,
        dir = None
    ) -> None:
        self.board = board
        self.player = player
        self.enemy = enemy
        self.xturns = xtruns
        self.length = length
        self.depth = depth

        self.game_finished = finished
        self.re = re
        self.dir = dir


        _x, _l = Game.grow(self.xturns, self.length)
        def seek(pos, d):
            x, y = pos
            xx, yy = Game.step[d]
            xxx, yyy = x + xx, y + yy
            return not Game.isCrash(self.board[xxx][yyy], _x, _l)
        self.ls0, self.ls1 = [], []
        for i in range(4):
            if seek(self.player, i): self.ls0.append(i)
            if seek(self.enemy, i): self.ls1.append(i)

    def isEnd(self):
        return self.game_finished

    def __move(
        self, 
        pos: Position, 
        dir: int, 
        tempboard: np.ndarray, 
        xturns: int, 
        length: int,
    ) -> Tuple[Position, bool, np.ndarray]:
        
        alive = True
        x, y = pos
        xx, yy = Game.step[dir]
        xxx, yyy = x + xx, y + yy

        t = 1 if tempboard[x][y] > 0 else -1

        if Game.isCrash(tempboard[xxx][yyy], xturns, length):
            alive = False
            tempboard[xxx][yyy] = Game.CRASHRUIN
        else:
            tempboard[xxx][yyy] = t * xturns

        return (xxx, yyy), alive, tempboard
    
    def __judge_losser(self, f0: bool, f1: bool) -> int:
        if f0 == False:
            if f1 == False:
                return Game.BOTH_DEFEAT
            else:
                return Game.PLAYER0_DEFEAT
        elif f1 == False:
            return Game.PLAYER1_DEFEAT
        else:
            return Game.GAME_CARRY_ON

    def __resume(self, dir0: int, dir1: int):
        assert self.game_finished == False, '终止状态'

        xturns, snake_length = Game.grow(self.xturns, self.length)

        tempboard = self.board.copy()
        player, f0, tempboard = self.__move(self.player, dir0, tempboard, xturns, snake_length)
        enemy, f1, tempboard = self.__move(self.enemy, dir1, tempboard, xturns, snake_length)
        if player == enemy:
            f0, f1 = False, False

        losser = self.__judge_losser(f0, f1)
        if losser != Game.GAME_CARRY_ON:
            game_finished = True
            re = losser
        else:
            game_finished = False
            re = None
        
        sta = State(tempboard, player, enemy, xturns, snake_length, self.depth + 1, re=re, finished = game_finished, dir = dir0)
        return sta
    
    def next(self):
        d0, d1 = 0, 0
        
        if len(self.ls0) > 0: d0 = random.choice(self.ls0)
        if len(self.ls1) > 0: 
            # d1 = Rule.persue_room(self.board,self.enemy,self.player,self.xturns,self.length)
            # if d1 not in self.ls1:
            #     d1 = 0
            d1 = random.choice(self.ls1)
        # d0, d1 = random.randint(0, 3), random.randint(0, 3)

        return self.__resume(d0, d1)
            
    def reward(self):
        if self.re == Game.PLAYER0_DEFEAT:
            return -0.2
        elif self.re == Game.PLAYER1_DEFEAT:
            return 1
        else:
            return 0

    # def __call__(self, *args):
    #     return self.next(*args)
    
    def __hash__(self):
        return int(hashlib.md5(str(self.board).encode('utf-8')).hexdigest(), 16)
    
    def __eq__(self, other):
        return hash(self) == hash(other) 


class Node:
    def __init__(self, state: State, parent = None) -> None:
        self.vis: int = 1
        self.reward: int = 0
        self.state = state
        self.children: List[Node] = []
        self.parent = parent

    def add_child(self, state) -> None:
        self.children.append(Node(state, self))
    
    # def isLeaf(self) -> None:
    #     return self.state.isEnd()
    
    def update(self, reward: int) -> None:
        self.vis += 1
        self.reward += reward

    def isFull(self):
        if len(self.state.ls1) == 0:
            return len(self.children) >= len(self.state.ls0)
        return len(self.children) >= len(self.state.ls0) * len(self.state.ls1)
    
    def __gt__(self, other):
        return self.reward / self.vis > other.reward / other.vis



class MCTS:
    def __init__(self, C: int,  time_limit: int, loop_limit: int, state: State) -> None:
        self.time_limit = time_limit
        self.loop_limit = loop_limit
        self.C = C
        self.root = Node(state)

    def expand(self, node: Node):
        children_state = [x.state for x in node.children]
        new_state = node.state.next()
        # print(node.state.board, hash(node.state))
        # print(new_state.board, hash(new_state))
        
        while new_state in children_state:
            new_state = node.state.next()
            # print(node.state.board, hash(node.state))
            # print(new_state.board, hash(new_state))
            # print(hash(node.state))
            # print(hash(new_state))
            # if len(children_state) > 0:
            #     print(children_state[0].board)
            #     print(new_state.board)
        node.add_child(new_state)

        return node.children[-1]

    def best(self, node: Node):
        best_value = -0x3fffffff
        best_node = []
        for child in node.children:
            a = child.reward / child.vis
            b = self.C * math.sqrt(math.log(node.vis) / child.vis)
            value = a + b
            if value == best_value:
                best_node.append(child)
            if value > best_value:
                best_value = value
                best_node = [child]
            
        if not best_node:
            # logger.error('无最佳节点')
            print('无最佳节点')
            
        return random.choice(best_node)
    
    def chioce(self, node: Node, p: float = 0.5):
        while not node.state.isEnd():
            if not node.children:
                return self.expand(node)
            
            if T.prob(p) and not node.isFull():
                return self.expand(node)

            node = self.best(node)

        return node
    
    def reward(self, state: State):
        while not state.isEnd():
            state = state.next()
        return state.reward()
    
    def backup(self, node: Node, reward):
        while node != None:
            node.update(reward)
            node = node.parent

    def run(self):
        
        for i in range(self.loop_limit):
            if time.time() - G.TIME > self.time_limit:
                break
            # if i % 1000 == 0:
            #     print(i)
            # print(i)
            node = self.chioce(self.root)
            reward = self.reward(node.state)
            self.backup(node, reward)

        w = sorted(self.root.children)
        # for each in w:
        #     print('%d %-.5f  %-.5f  %-.5f' % (each.state.dir, each.reward / each.vis, each.reward, each.vis))
        s = [None, None, None, None]
        for x in w:
            if s[x.state.dir] == None:
                s[x.state.dir] = 0
            if x.reward < 0:
                s[x.state.dir] += x.reward / x.vis - 1.85
            else:
                s[x.state.dir] += x.reward / x.vis

        b = [(-9999, 0)]
        for i in range(len(s)):
            if s[i] == None: continue
            if s[i] > b[0][0]:
                b = [(s[i], i)]
            elif s[i] == b[0][0]:
                b.append((s[i], i))
        
        return random.choice(b)[1]

        # return self.best(self.root)
        


    
def MCTSmethod(board: np.ndarray, player: Position, enemy: Position, xturns: int, length: int):
    s = State(board, player, enemy, xturns, length, depth=0)
    # print(s.ls0, s.ls1)
    # print(s.board)
    b = MCTS(2,5.5, 999999, s)
    x = b.run()
    # print('len=',len(x.children))
    # for each in b.root.children:
    #     print('%d %-.5f  %-.5f  %-.5f' % (each.state.dir, each.reward / each.vis, each.reward, each.vis) )
    
    return x
    # return x.state.dir