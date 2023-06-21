from ..utils.types import Position, List, Tuple
import numpy as np
import random
import time
import hashlib
import copy
from ..game.game import Game
from ..utils.T import T, G
import math
from .Algorithm import Rule

from .MCTS01 import MCTS

wy_ = lambda x: 1/x
def ev_(board: np.ndarray, player: Position, enemy: Position, xturns: int, length: int):
    bd = xturns - abs(board) >= length
    vis = np.zeros(bd.shape, dtype=np.int8)
    # ratemap = np.ones(bd.shape, dtype=np.float16)
    # r, c = bd.shape
    # for i in range(1, r - 2):
    #     for j in range(1, c - 2):
    #         for k in range(4):
    #             x, y = Game.step[k]
    #             if bd[i + x][j + y] == False:
    #                 ratemap[i][j] *= 0.75
                
    score0, score1 = 0, 0
    x, y = enemy
    vis[x][y] = 1
    queue = [(x, y, 1)]
    while queue:
        x, y, z = queue.pop(0)
        for i in range(4):
            xx, yy = Game.step[i]
            xxx, yyy = x + xx, y + yy
            if bd[xxx][yyy] == True and vis[xxx][yyy] != 1:
                vis[xxx][yyy] = 1
                score1 += wy_(z)
                # score1 += wy_(z) * ratemap[xxx][yyy]
                queue.append((xxx, yyy, z + 1))
    x, y = player
    vis[x][y] = 2
    queue = [(x, y, 1)]
    while queue:
        x, y, z = queue.pop(0)
        for i in range(4):
            xx, yy = Game.step[i]
            xxx, yyy = x + xx, y + yy
            if bd[xxx][yyy] == True and vis[xxx][yyy] != 2:
                vis[xxx][yyy] = 2
                score0 += wy_(z)
                # score0 += wy_(z) * ratemap[xxx][yyy]
                queue.append((xxx, yyy, z + 1))

    if score0 == 0: return -1
    
    score0 *= score0
    score1 *= score1

    return (score0 - score1) / (score0 + score1)     
                    

class State_:
    def __init__(
        self, 
        board: np.ndarray, 
        player: Position, 
        enemy: Position,
        xtruns: int,
        length: int,
        game_sta: int = Game.GAME_CARRY_ON,
        hisqueue: str = ''

    ) -> None:
        self.board = board
        self.player = player
        self.enemy = enemy
        self.xturns = xtruns
        self.length = length

        self.game_sta = game_sta
        self.hisqueue = hisqueue
        
        
        self._x, self._l = Game.grow(self.xturns, self.length)
        self.road0, self.road1 = self.__getdir()
        
        self.scorehis = []
        
    def isEnd(self):
        return self.game_sta != Game.GAME_CARRY_ON
    
    
    def __getdir(self) -> Tuple[List[int]]:
        def seek(pos, d):
            x, y = pos
            xx, yy = Game.step[d]
            return not Game.isCrash(self.board[xx + x][yy + y], self._x, self._l)
        ls0, ls1 = [], []
        for i in range(4):
            if seek(self.player, i): ls0.append(i)
            if seek(self.enemy, i): ls1.append(i)
        return ls0, ls1
    
    def __resume(self, dir0: int, dir1: int):
        def move(pos, dir, tboard):
            alive = True
            x, y = pos
            xx, yy = Game.step[dir]
            xxx, yyy = x + xx, y + yy
            
            t = 1 if tboard[x][y] > 0 else -1
            
            if Game.isCrash(tboard[xxx][yyy], self._x, self._l):
                alive = False
                tboard[xxx][yyy] = Game.CRASHRUIN
            else:
                tboard[xxx][yyy] = t * self._x

            return (xxx, yyy), alive
        
        def judge_losser(f0: bool, f1: bool) -> int:
            if f0 == False: return Game.BOTH_DEFEAT if f1 == False else Game.PLAYER0_DEFEAT
            else: return Game.PLAYER1_DEFEAT if f1 == False else Game.GAME_CARRY_ON

        newboard = self.board.copy()
        player, f0 = move(self.player, dir0, newboard)
        enemy, f1 = move(self.enemy, dir1, newboard)
        if player == enemy: 
            f0, f1 = False, False
        
        return State_(newboard, player, enemy,self._x, self._l, 
                     judge_losser(f0, f1), self.hisqueue + str(dir0))
        
    def next(self):
        d0, d1 = 0, 0
        
        if self.road0: d0 = random.choice(self.road0)
        if self.road1: 
            # d1 = random.choice(self.road1) 
            # if T.prob(0.5):
            #     d1 = Rule.persue_room(self.board.copy(), self.enemy, self.player, self.xturns, self.length)
            #     if d1 not in self.road1:
            #         raise Exception('方向错误dfklajasdfasdf')
            # else:
            #     d1 = random.choice(self.road1)
            tpst = State_(self.board, self.player, self.enemy, self.xturns, self.length, self.game_sta, self.hisqueue)
            G.record()
            m___ = MCTS(5, 0.2, 100, tpst, R = 0.8, max_depth=5)
            d1 = m___.run()
        return self.__resume(d0, d1)
    
    def reward(self):
        if self.game_sta == Game.GAME_CARRY_ON:
            return ev_(self.board,self.player, self.enemy,self._x, self._l)
        
        if self.game_sta == Game.PLAYER0_DEFEAT:
            return -1.5
        elif self.game_sta == Game.PLAYER1_DEFEAT:
            return 1
        else:
            return -0.5
    
    def __hash__(self):
        return int(hashlib.md5(self.hisqueue.encode('utf-8')).hexdigest(), 16)
    
    def __eq__(self, other):
        # return hash(self) == hash(other) 
        return self.hisqueue == other.hisqueue
        
    
class NodeDD_:
    def __init__(self, State_: State_, parent = None, depth = 0) -> None:
        self.vis: int = 1
        self.reward: int = 0
        self.State_ = State_
        self.children: List[NodeDD_] = []
        self.parent = parent
        self.depth = depth
        

    def add_child(self, State_) -> None:
        self.children.append(NodeDD_(State_, self, self.depth + 1))
    
    # def isLeaf(self) -> None:
    #     return self.State_.isEnd()
    
    def update(self, reward: int) -> None:
        self.vis += 1
        self.reward += reward

    def isFull(self):
        return len(self.children) >= len(self.State_.road0)
    
    def __gt__(self, other):
        return self.reward / self.vis > other.reward / other.vis
    
    def __eq__(self, other) -> bool:
        if other == None: return False
        self.State_ == other.State_
        
    def __str__(self) -> str:
        return 'dir:' + self.State_.hisqueue + " reward:" + str(self.reward) + ' vis:' + str(self.vis) + ' avg:' + str(self.reward / self.vis)
    
    def __repr__(self) -> str:
        return 'dir:' + self.State_.hisqueue + " reward:" + str(self.reward) + ' vis:' + str(self.vis) + ' avg:' + str(self.reward / self.vis)
                

class MCTS_:
    tls = [1]
    def __init__(self, 
        C: int, 
        time_limit: int, 
        loop_limit: int, 
        State_: State_,
        R: float = 0.85,
        max_depth: int = 10,
    ) -> None:
        self.time_limit = time_limit
        self.loop_limit = loop_limit
        self.C = C
        self.root = NodeDD_(State_)
        
        self.R = R
        self.max_depth = max_depth
    
    def expand(self, Node_: NodeDD_):
        children_s_State_ = [x.State_ for x in Node_.children]
        new_State_ = Node_.State_.next()
        
        while new_State_ in children_s_State_:
            new_State_ = Node_.State_.next()
        Node_.add_child(new_State_)

        return Node_.children[-1]

    def best(self, Node_: NodeDD_):
        best_value = -0x3fffffff
        best_Node_ = []
        for child in Node_.children:
            a = child.reward / child.vis
            # b = self.C * math.sqrt(math.log(Node_.vis) / child.vis)
            b = self.C * math.sqrt(math.log(Node_.vis) / child.vis)
            value = a + b
            # print(a, b)
            if value == best_value:
                best_Node_.append(child)
            if value > best_value:
                best_value = value
                best_Node_ = [child]
            
        if not best_Node_:
            raise Exception('无最佳节点')
            
        return random.choice(best_Node_)
    
    def chioce(self, Node_: NodeDD_, p: float = 0.5):
        while not Node_.State_.isEnd():
            if not Node_.children:
                return self.expand(Node_)
            
            if T.prob(p) and not Node_.isFull():
                return self.expand(Node_)

            Node_ = self.best(Node_)

        return Node_
    
    def go(self, Node_: NodeDD_):
        t_Node_ = Node_
        cnt = 0
        while not t_Node_.State_.isEnd():
            if cnt >= self.max_depth: break
            s = t_Node_.State_.next()
            cs = [x.State_ for x in t_Node_.children]
            if s not in cs:
                t_Node_.add_child(s)
                t_Node_ = t_Node_.children[-1]
            else:
                idx = cs.index(s)
                t_Node_ = t_Node_.children[idx]
            cnt += 1
        return t_Node_
    
    def backup(self, Node_: NodeDD_, reward):
        while len(MCTS_.tls) < Node_.depth + 1:
            MCTS_.tls.append(MCTS_.tls[-1] * self.R)
        idx = 0
        while Node_ != None:
            Node_.update(reward * MCTS_.tls[idx])
            Node_.State_.scorehis.append(reward * MCTS_.tls[idx])
            Node_ = Node_.parent
            idx += 1

    def run(self, debug = False):
        for i in range(self.loop_limit):
            if i % 1000 == 0:
                print(i)
            if time.time() - G.TIME___ > self.time_limit:
                break
            
            Node_ = self.chioce(self.root)
            Node_ = self.go(Node_)
            reward = Node_.State_.reward()
            
            self.backup(Node_, reward)

        w = sorted(self.root.children, reverse=True)
        
        for each in w:
            print(each)
            # print(each.State_.scorehis[:10])
        
        return int(w[0].State_.hisqueue[-1])


from .cfg import MCTS_TIME, MCTS_LOOP
def MCTS_method(board: np.ndarray, player: Position, enemy: Position, xturns: int, length: int):
    sta = State_(board.copy(), player, enemy, xturns, length)
    return MCTS_(5, MCTS_TIME, MCTS_LOOP, sta).run()
    
    
