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

DEBUG = True
INFO = True

DEBUG = False
INFO = False


BAD_MULTI = 4
# EV = 0.85
weilist = [0]
weilist.extend([1/math.sqrt(x) for x in range(1, 100)])
# print(weilist)
def ev(board: np.ndarray, player: Position, enemy: Position, xturns: int, length: int):
    bd = (xturns - abs(board) >= length)
    vis = np.zeros(bd.shape, dtype=np.int8)
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
                score1 += weilist[z]
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
                score0 += weilist[z]
                queue.append((xxx, yyy, z + 1))

    if score1 == 0:
        if score0 == 0:
            return -0.1
        else:
            return 1
    elif score0 == 0:
        return -1
    
    r, c = bd.shape
    r = r * 0.5 - 1
    c = c * 0.5 - 1

    res = ((score0 - score1) / (score0 + score1))

    x1, y1 = enemy
    x0, y0 = player
    eabs = lambda x: 1.33 ** abs(x)
    res += -0.11 * (eabs(x0 - r) + eabs(y0 - c) - eabs(x1 - r) - eabs(y1 - c)) / (r + c)

    if DEBUG:
        with open('_test_dt.txt', 'a', encoding='utf-8') as f:
            f.write(str(2 * (score0 - score1) / (score0 + score1)) + '\n')
        
        print('score0, 1 = ', score0, score1)
        print('res = ', res)
        for each in  board.tolist():
            print('[', end = '')
            for v in each:
                print('%-6d' % v, end = '')
            print(']')


    return res
                    

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
        return self.__resume(d0, d1)
    
    def reward(self):
        if self.game_sta == Game.GAME_CARRY_ON:
            return ev(self.board,self.player, self.enemy,self._x, self._l)
        
        if self.game_sta == Game.PLAYER0_DEFEAT:
            if DEBUG:
                pass
                # print('FF  You die')
                for each in  self.board.tolist():
                    print('[', end = '')
                    for v in each:
                        print('%-6d' % v, end = '')
                    print(']')
                # print('>>>>>>> -1, ', eev)
            return -1
        elif self.game_sta == Game.PLAYER1_DEFEAT:
            if DEBUG:
                pass
                # print('FF You win')
                for each in  self.board.tolist():
                    print('[', end = '')
                    for v in each:
                        print('%-6d' % v, end = '')
                    print(']')
            #     print('>>>>>>> 1, ', eev)
            return 1
        else:
            # print('FF draw')
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
        self.tempE: float = 0.0
        

    def add_child(self, state) -> None:
        self.children.append(Node(state, self, self.depth + 1))
    
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

    def __init__(self, 
        C: int, 
        time_limit: int, 
        loop_limit: int, 
        state: State,
        R: float = 0.95,
        max_depth: int = 10,
        expand_rate: float = 0.65,
        random_node_rate: float = 0.5
    ) -> None:
        self.time_limit = time_limit
        self.loop_limit = loop_limit
        self.C = C
        self.root = Node(state)
        
        self.R = R
        self.max_depth = max_depth
        self.expand_rate = expand_rate
        self.random_node_rate = random_node_rate

    
    def expand(self, node: Node):
        children_s_state = [x.state for x in node.children]
        new_state = node.state.next()
        
        while new_state in children_s_state:
            new_state = node.state.next()
        node.add_child(new_state)

        return node.children[-1]

    def best(self, node: Node):
        log_fa_vis = math.log(node.vis)
        x = node.children
        ch0, ch1 = [0.0] * 4, [0.0] * 4
        ms0, ms1 = [False] * 4, [False] * 4
 
        for i in range(len(x)):

            ext = self.C * math.sqrt(log_fa_vis / x[i].vis)
            x[i].temp = x[i].reward / x[i].vis + ext
            # x[i].temp = x[i].reward / x[i].vis
            idx = int(x[i].state.hisqueue[-1])
            ms0[idx] = True
            if x[i].temp <= 0:
                ch0[idx] += x[i].temp * BAD_MULTI
            else:
                ch0[idx] += x[i].temp

            x[i].tempE = x[i].rewardE / x[i].vis + ext
            # x[i].tempE = x[i].rewardE / x[i].vis
            idx = int(x[i].state.hisqueue[-2])
            ms1[idx] = True
            if x[i].tempE <= 0:
                ch1[idx] += x[i].tempE * BAD_MULTI
            else:
                ch1[idx] += x[i].tempE

        for i in range(4):
            if ms0[i] == False:
                ch0[i] -= 999
            if ms1[i] == False:
                ch1[i] -= 999

        # ch0, ch1 = list(zip(ch0, range(4))), list(zip(ch1, range(4)))
        # ch0.sort(key=lambda x: x[0], reverse=True)
        # ch1.sort(key=lambda x: x[0], reverse=True)
        if DEBUG:
            print(ch0)
            print(ch1)
        # ch0 = [x[1] for x in ch0]
        # ch1 = [x[1] for x in ch1]
        # if DEBUG:
        #     print(ch1)

        best_node = []

        maxvalue = -99999
        for i in range(len(x)):
            t = x[i].state.hisqueue[-2:]
            t0, t1 = ch0[int(t[1])] , ch1[int(t[0])]
            if t0 < 0: t0 *= BAD_MULTI
            if t1 < 0: t1 *= BAD_MULTI
            v = t0 + t1
            if DEBUG:
                print(t, v)
            if abs(v - maxvalue) < 1e-5:
                best_node.append(x[i])
            elif v > maxvalue:
                maxvalue = v
                best_node = [x[i]]

        return random.choice(best_node)
    
    def chioce(self, node: Node, p: float = 0.5, pr = 0.5):
        ifrandom = T.prob(pr)
        while not node.state.isEnd():
            if node.depth >= self.max_depth: break
            if not node.children:
                return self.expand(node)
            
            if T.prob(p) and not node.isFull():
                return self.expand(node)
            
            if ifrandom:
                node = random.choice(node.children)
            else:
                node = self.best(node)
        return node
    
    def go(self, node: Node):
        t_node = node
        it = 0
        while not t_node.state.isEnd():
            it += 1
            if it > 2: break
            if t_node.depth >= self.max_depth: break
            s = t_node.state.next()
            cs = [x.state for x in t_node.children]
            if s not in cs:
                t_node.add_child(s)
                t_node = t_node.children[-1]
            else:
                idx = cs.index(s)
                t_node = t_node.children[idx]
        return t_node
    
    def backup(self, node: Node, reward):
        while node != None:
            node.update(reward)
            node.state.scorehis.append(reward)
            node = node.parent

    def run(self, debug = False):
        for i in range(self.loop_limit):
            if INFO and i % 1000 == 0:
                print(i)
            if time.time() - G.TIME > self.time_limit:
                break
            
            node = self.chioce(self.root, p = self.expand_rate, pr = self.random_node_rate)
            # node = self.go(node)
            if DEBUG:
                print('node_depth = ', node.depth)

            reward = node.state.reward()
            
            self.backup(node, reward)


        # # 根据好坏
        # if INFO:
        #     for each in self.root.children:
        #         print('op=',each.state.hisqueue[-2:],'vis=', each.vis)
        #         print('rew=', each.reward, 'avg=', each.reward / each.vis)
        #         print('rewE=', each.rewardE, 'avgE=', each.rewardE / each.vis)
        #     cntz = 0
        #     ceng = 0
        #     lst = [(self.root, cntz)]
        #     while lst != []:
        #         ls = lst.copy()
        #         lst = []
        #         ceng += 1
        #         print('--------[[[ceng = ', ceng, ']]]----------')
        #         for each,fa in ls:
        #             cntz += 1
        #             print(cntz, 'fa=', fa)
        #             print('>>> op=',each.state.hisqueue[-2:],'vis=', each.vis)
        #             print('>>> rew=', each.reward, 'avg=', each.reward / each.vis)
        #             print('>>> rewE=', each.rewardE, 'avgE=', each.rewardE / each.vis)
        #             for xx in each.children:
        #                 lst.append((xx, cntz))

       
        # ch = [0.0] * 4
        # ms = [False] * 4
        # for each in self.root.children:
        #     t = each.reward / each.vis
        #     d = int(each.state.hisqueue[-1])
        #     ms[d] = True
        #     if t <=0 :
        #         ch[d] += BAD_MULTI * t
        #     else:
        #         ch[d] += t
        # for i in range(4):
        #     if ms[i] == False:
        #         ch[i] -= 999
        # # print(ch)
        # return ch.index(max(ch))

        # 根据次数(vis)
        self.root.children.sort(key=lambda x: x.vis, reverse=True)
        if INFO:
            # from graphviz import Digraph
            # from graphviz import Source
            # dot = Digraph(
            #     name='try1',
            #     comment='',
            #     filename=None,
            #     directory=None,
            #     format="png",
            #     engine=None,
            #     encoding='utf8',
            #     graph_attr={'rankdir':'TB'},
            #     node_attr={'color':'black','fontcolor':'black','fontname':'FangSong','fontsize':'12','style':'rounded','shape':'box'},
            #     edge_attr={'color':'red','fontcolor':'#888888','fontsize':'10','fontname':'FangSong'},
            #     body=None,
            #     strict=False
            # )

            # dot.node('B','B=====',shape = 'circle')
            # dot.node('C', 'C-----',shape = 'triangle', color = 'blue', fontcolor = 'green')
            # dot.edge('C','D')
            # dot.view()

            cntz = 0
            ceng = 0
            lst = [(self.root, cntz)]
            while lst != []:
                ls = lst.copy()
                lst = []
                ceng += 1
                print('--------[[[ceng = ', ceng, ']]]----------')
                for each,fa in ls:
                    cntz += 1
                    print(cntz, 'fa=', fa)
                    print('>>> op=',each.state.hisqueue[-2:],'vis=', each.vis)
                    print('>>> rew=', each.reward, 'avg=', each.reward / each.vis)
                    print('>>> rewE=', each.rewardE, 'avgE=', each.rewardE / each.vis)
                    for xx in each.children:
                        lst.append((xx, cntz))

            for each in self.root.children:
                print('DIRE = ',each.state.hisqueue[-1] , 'op=',each.state.hisqueue[-2:],'vis=', each.vis)
                print('rew=', each.reward, 'avg=', each.reward / each.vis)
                print('rewE=', each.rewardE, 'avgE=', each.rewardE / each.vis)

        return int(self.root.children[0].state.hisqueue[-1])
        



from .cfg import MCTS_TIME, MCTS_LOOP
def MCTSmethod(board: np.ndarray, player: Position, enemy: Position, xturns: int, length: int):
    sta = State(board.copy(), player, enemy, xturns, length)
    return MCTS(1, MCTS_TIME, MCTS_LOOP, sta, expand_rate=0.5, random_node_rate=0.1, max_depth=10).run()
    
    
