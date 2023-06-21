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



wy = lambda x: (1/x) ** 1.4
def ev(board: np.ndarray, player: Position, enemy: Position, xturns: int, length: int):
    bd = xturns - abs(board) >= length
    vis = np.zeros(bd.shape, dtype=np.int8)
    score = np.zeros(bd.shape, dtype = np.float16)
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
                ttt = wy(z)
                score1 += ttt
                score[xxx][yyy] = ttt
                # score1 += wy(z) * ratemap[xxx][yyy]
                queue.append((xxx, yyy, z + 1))
    x, y = player
    vis[x][y] = 2
    queue = [(x, y, 1)]
    c1, c2 = 0, 0
    while queue:
        x, y, z = queue.pop(0)
        for i in range(4):
            xx, yy = Game.step[i]
            xxx, yyy = x + xx, y + yy
            if bd[xxx][yyy] == True and vis[xxx][yyy] != 2:
                vis[xxx][yyy] = 2
                score0 += wy(z)
                c1 += 1
                if score[xxx][yyy] > 0:
                    c2 += 2
                    score0 += score[xxx][yyy]
                    
                # score0 += wy(z) * ratemap[xxx][yyy]
                queue.append((xxx, yyy, z + 1))

    if score0 == 0: return -1
    
    score0 = score0 * c1 / (c1 + c2)
    score0 *= score0
    score1 *= score1

    return (score0 - score1) / (score0 + score1)     
                    

class State:
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
        self.max_roads_couple = len(self.road1) * len(self.road0)
        
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
        
        return State(newboard, player, enemy,self._x, self._l, 
                     judge_losser(f0, f1), self.hisqueue + str(dir1) + str(dir0))
        
    def next(self):
        d0, d1 = 0, 0
        
        if self.road0: d0 = random.choice(self.road0)
        if self.road1: d1 = random.choice(self.road1)
        # if self.road1: 
        #     # d1 = random.choice(self.road1) 
        #     if T.prob(0.5):
        #         d1 = Rule.persue_room(self.board.copy(), self.enemy, self.player, self.xturns, self.length)
        #         if d1 not in self.road1:
        #             raise Exception('方向错误dfklajasdfasdf')
        #     else:
        #         d1 = random.choice(self.road1)
        return self.__resume(d0, d1)
    
    def reward(self):
        if self.game_sta == Game.GAME_CARRY_ON:
            return ev(self.board,self.player, self.enemy,self._x, self._l)
        
        if self.game_sta == Game.PLAYER0_DEFEAT:
            return -1
        elif self.game_sta == Game.PLAYER1_DEFEAT:
            return 1
        else:
            return -0.1
    
    def __hash__(self):
        return int(hashlib.md5(self.hisqueue.encode('utf-8')).hexdigest(), 16)
    
    def __eq__(self, other):
        # return hash(self) == hash(other) 
        return hash(self.hisqueue) == hash(other.hisqueue)
        
    
class Node:
    def __init__(self, state: State, parent = None, depth = 0) -> None:
        self.vis: int = 1
        self.reward: int = 0
        self.rewardE: int = 0
        self.state = state
        self.children: List[Node] = []
        self.parent = parent
        self.depth = depth

        self.temp: float = 0.0
        

    def add_child(self, state) -> None:
        self.children.append(Node(state, self, self.depth + 1))
    
    # def isLeaf(self) -> None:
    #     return self.state.isEnd()
    
    def update(self, reward: int) -> None:
        self.vis += 1
        self.reward += reward
        self.rewardE -= reward

    def isFull(self):
        return len(self.children) >= self.state.max_roads_couple
    
    def __gt__(self, other):
        # return self.reward / self.vis > other.reward / other.vis
        return self.vis > other.vis
    
    def __eq__(self, other) -> bool:
        if other == None: return False
        self.state == other.state
        
    def __str__(self) -> str:
        return 'dir:' + self.state.hisqueue + " reward:" + str(self.reward) + ' vis:' + str(self.vis) + ' avg:' + str(self.reward / self.vis)
    
    def __repr__(self) -> str:
        return 'dir:' + self.state.hisqueue + " reward:" + str(self.reward) + ' vis:' + str(self.vis) + ' avg:' + str(self.reward / self.vis)
                

class MCTS:
    tls = [1]
    def __init__(self, 
        C: int, 
        time_limit: int, 
        loop_limit: int, 
        state: State,
        R: float = 0.95,
        max_depth: int = 10,
    ) -> None:
        self.time_limit = time_limit
        self.loop_limit = loop_limit
        self.C = C
        self.root = Node(state)
        
        self.R = R
        self.max_depth = max_depth
    
    def expand(self, node: Node):
        children_s_state = [x.state for x in node.children]
        new_state = node.state.next()
        
        while new_state in children_s_state:
            new_state = node.state.next()
        node.add_child(new_state)

        return node.children[-1]

    def best(self, node: Node):
        log_fa_vis = math.log(node.vis)
        best_node = []
        array: List[Node] = node.children.copy()

        if time.time() - G.TIME > 2 and T.prob(0.6):
            mx_E_dir = len(node.state.road1)
            dic = {'0': 0, '1': 0, '2': 0, '3': 0, }
            vnum = []
            for each in array:
                d, s = each.state.hisqueue[-1], each.reward / each.vis
                if s > 0:
                    dic[d] += s
                else:
                    dic[d] += s * 10
            for k, v in dic.items():
                if v > 0:
                    vnum.append(k)
            if len(vnum) > 0:
               # if T.prob(0.0001):
               #     print(vnum)
                for i in range(len(array)):
                    d, s = each.state.hisqueue[-1], each.reward / each.vis
                    if d in vnum:
                        if s > 0:
                            best_node.extend([array[i]] * int(s * 10))
                        else:
                            best_node.append(array[i])
            
            if len(best_node) > 0:
                return random.choice(best_node)

        array.sort(key = lambda x: x.reward / x.vis + self.C * math.sqrt(log_fa_vis / x.vis), reverse=True)
        arrayE: List[Node] = node.children.copy()
        arrayE.sort(key = lambda x: x.rewardE / x.vis + self.C * math.sqrt(log_fa_vis / x.vis), reverse=True)
        

        sset = set()
        for i in range(len(array)):
            if array[i].state.hisqueue in sset: best_node.append(array[i])
            sset.add(array[i].state.hisqueue)

            if arrayE[i].state.hisqueue in sset: best_node.append(arrayE[i])
            sset.add(arrayE[i].state.hisqueue)

            if best_node != []:
                return random.choice(best_node)
    
    def chioce(self, node: Node, p: float = 0.5):
        while not node.state.isEnd():
            if not node.children:
                return self.expand(node)
            
            if T.prob(p) and not node.isFull():
                return self.expand(node)

            node = self.best(node)

        return node
    
    def go(self, node: Node):
        t_node = node
        cnt = 0
        while not t_node.state.isEnd():
            if cnt >= self.max_depth: break
            s = t_node.state.next()
            cs = [x.state for x in t_node.children]
            if s not in cs:
                t_node.add_child(s)
                t_node = t_node.children[-1]
            else:
                idx = cs.index(s)
                t_node = t_node.children[idx]
            cnt += 1
        return t_node
    
    def backup(self, node: Node, reward):
        while len(MCTS.tls) < node.depth + 1:
            MCTS.tls.append(MCTS.tls[-1] * self.R)
        idx = 0
        while node != None:
            node.update(reward * MCTS.tls[idx])
            node.state.scorehis.append(reward * MCTS.tls[idx])
            node = node.parent
            idx += 1

    def run(self, debug = False):
        for i in range(self.loop_limit):
            # if i % 1000 == 0:
            #     print(i)
            if time.time() - G.TIME > self.time_limit:
                break
            
            node = self.chioce(self.root, p = 0.5)
            # node = self.go(node)
            reward = node.state.reward()
            
            self.backup(node, reward)

        w = sorted(self.root.children, reverse=True)
        
        for each in w:
            print(each.state.hisqueue[-2:], each.vis, each.reward, each.reward / each.vis, each.rewardE, each.rewardE / each.vis)
        ans = 0
        # for i in w:
        #     print(i.state.hisqueue)
        for i in range(1, min(4, len(w))):
            if w[i].state.hisqueue[-2] == w[0].state.hisqueue[-2]:
                if w[i].reward / w[i].vis > w[0].reward / w[0].vis:
                    ans = i
        return int(w[ans].state.hisqueue[-1])


from .cfg import MCTS_TIME, MCTS_LOOP
def MCTSmethod(board: np.ndarray, player: Position, enemy: Position, xturns: int, length: int):
    sta = State(board.copy(), player, enemy, xturns, length)
    return MCTS(0.8, MCTS_TIME, MCTS_LOOP, sta, R = 0.9, max_depth=4).run()
    
    
