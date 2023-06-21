import numpy as np
from random import randint
from typing import Tuple
from .config import MAP_SIZE_N, MAP_SIZE_M, OBSTACLE_WEIGHT, STEP
from ..utils.types import Position

class Game:

    EMPTY = 0
    PLAYERSTART0 = 1
    PLAYERSTART1 = -1
    OBSTACLE = 0x3f00
    CRASHRUIN = 0x3f01

    NO_ACTION = -1
    PLAYER0_DEFEAT = 0
    PLAYER1_DEFEAT = 1
    BOTH_DEFEAT = 2
    GAME_CARRY_ON = 3  

    GROW_QUICK_TURN = 10
    GROW_NORMAL_TURN = 3
    
    step = STEP

    @staticmethod
    def grow(xturns: int, length: int) -> int:
        xturns += 1
        if xturns <= Game.GROW_QUICK_TURN + 1:
            length += 1
        elif (xturns - Game.GROW_QUICK_TURN - 1) % Game.GROW_NORMAL_TURN == 0:
            length += 1
        return xturns, length

    @staticmethod
    def isCrash(cell_value: int, xturns: int, length: int) -> bool:
        # print(f'{xturns} - abs({cell_value}) < {length} is {xturns - abs(cell_value) < length}')
        return xturns - abs(cell_value) < length

    def __init__(self, *args, **kwargs):
        self.initial(*args, **kwargs)

    def initial(self, *args, **kwargs):
        ''' 
        初始化地图
        参数:
            args: 见 __loadboard 方法
            kwargs: 见 __create_board 方法
        返回:
            None
        '''
        try:
            self.__load_board(*args)
        except Exception as e:
            self.__create_board(**kwargs)
        self.history0 = []
        self.history1 = []
        self.xturns = 1
        self.snake_length = 1
        self.game_finished = False

    def __plain_board(self, n: int, m: int) -> np.ndarray:
        '''
        得到一张只有边界墙的口型空地图
        参数:
            n: 地图行  
            m: 地图列
        返回:
            一张只有边界墙的口型空地图
        '''
        board = np.zeros((n + 2, m + 2), dtype=np.int16)
        for i in range(n + 2):
            board[i][0] = Game.OBSTACLE
            board[i][m + 1] = Game.OBSTACLE
        for j in range(m + 2):
            board[0][j] = Game.OBSTACLE
            board[n + 1][j] = Game.OBSTACLE
        return board


    def __create_board(self, **kwargs) -> None:
        '''
        创建一张新的随机地图到self.board, 若指定参数有误, 使用随机
        参数:
            kwargs: { n = 地图行, m = 地图列, num = 墙数量}
        返回:
            None
        '''

        try:
            n, m = kwargs['n'], kwargs['m']
        except KeyError:
            n, m =  randint(*MAP_SIZE_N), randint(*MAP_SIZE_M)
        self.width, self.height = n, m

        self.board = self.__plain_board(n, m)

        # while True:
        #     x, y = randint(1, n), randint(1, m)
        #     if self.board[x][y] == Game.EMPTY:
        #         self.board[x][y] = Game.PLAYERTEMP
        #         self.player0 = (x, y)
        #         break
        
        # while True:
        #     x, y = randint(1, n), randint(1, m)
        #     if self.board[x][y] == Game.EMPTY:
        #         self.player1 = (x, y)
        #         x, y = self.player0
        #         self.board[x][y] = Game.EMPTY
        #         break
        self.player0 = (1, 1)
        self.player1 = (n, m)
        self.board[1][1] = Game.PLAYERSTART0
        self.board[n][m] = Game.PLAYERSTART1

        try:
            obstacle_num = kwargs['num']
        except KeyError:
            obstacle_num = int((n * m) ** OBSTACLE_WEIGHT)
        obstacle_num = min(obstacle_num, (n * m) // 4)

        self.obstacle_list = []
        while obstacle_num > 0:
            x, y = randint(1, n), randint(1, m)
            if self.board[x][y] == Game.EMPTY:
                self.board[x][y] = Game.OBSTACLE
                self.obstacle_list.append((x, y))
                obstacle_num -= 1

        self.obstacle_list = tuple(self.obstacle_list)

        self.isload = False
        
        
    def __load_board(
        self,
        width: int,
        height: int,
        player0: Position,
        player1: Position,
        obstacle: Tuple[Position],
    ) -> None:
        '''
        加载一张游戏地图到self.board
        参数:
            width, height: 地图行, 地图列
            player0, player1: 玩家0位置, 玩家1位置
            obstacle: 障碍列表
        返回:
            None
        '''

        self.width, self.height = width, height
        self.board = self.__plain_board(width, height)

        self.player0, self.player1 = player0, player1
        x, y = self.player0
        self.board[x][y] = Game.PLAYERSTART0
        x, y = self.player1
        self.board[x][y] = Game.PLAYERSTART1

        self.obstacle_list = tuple(obstacle)

        for x, y in self.obstacle_list:
            self.board[x][y] = Game.OBSTACLE

        self.isload = True

    def get_history(self) -> Tuple[int, Tuple[Position]]:
        '''
        获取对局历史
        参数:
            无
        返回:
            地图初始化信息和双方玩家的行为历史
        '''
        return (
            self.width, 
            self.height, 
            self.player0, 
            self.player1, 
            self.obstacle_list,
            tuple(self.history0),
            tuple(self.history1),
        )

    # def __judge_edge(self, x: int, y: int) -> bool:
    #     return x >= 1 and x <= self.width and y >= 1 and y <= self.height
   
    def __judge_losser(self, f0: bool, f1: bool) -> int:
        '''
        判断失败者
        参数:
            f0: 玩家0是否还活着 True = 活着, False = 死亡
            f1: 同理
        返回:
            [int]游戏状态 (
                Game.BOTH_DEFEAT: 两玩家都死亡
                Game.PLAYER0_DEFEAT: 玩家0死亡
                Game.PLAYER1_DEFEAT: 玩家1死亡
                Game.GAME_CARRY_ON: 无事发生，游戏继续
            )
        '''
        if f0 == False:
            if f1 == False:
                return Game.BOTH_DEFEAT
            else:
                return Game.PLAYER0_DEFEAT
        elif f1 == False:
            return Game.PLAYER1_DEFEAT
        else:
            return Game.GAME_CARRY_ON

    def __move(self, pos: Position, dir: int, player: int) -> Tuple[Position, bool]:
        '''
        让一个玩家爬行一步, 并得到下一个回合的坐标和存活状态
        若蛇不存活, 坐标可能是一个非法值, 应当失去意义
        参数:
            pos = 玩家坐标
            dir = 爬行方向
            player = 玩家标识(0 or 1)
        返回:
            [Position]玩家坐标, [bool]存活标志 (alive = True 代表存活)
        注意:
            返回的alive变量没有考虑两条蛇同时走一个点的情况
        '''
        alive = True
        x, y = pos
        xx, yy = Game.step[dir]
        xxx, yyy = x + xx, y + yy

        t = 1 if player == 0 else -1

        if self.isCrash(self.board[xxx][yyy], self.xturns, self.snake_length):
            alive = False
            self.board[xxx][yyy] = Game.CRASHRUIN
        else:
            self.board[xxx][yyy] = t * self.xturns

        return (xxx, yyy), alive

    def resume(self, dir0: int, dir1: int) -> int:
        '''
        模拟游戏推进一回合
        参数:
            dir0: 玩家0的爬行方向
            dir1: 同理
        返回:
            [int]游戏状态 (
                Game.BOTH_DEFEAT: 两玩家都死亡
                Game.PLAYER0_DEFEAT: 玩家0死亡
                Game.PLAYER1_DEFEAT: 玩家1死亡
                Game.GAME_CARRY_ON: 无事发生，游戏继续
            )
        '''

        assert self.game_finished == False, '游戏结束'

        self.history0.append(dir0)
        self.history1.append(dir1)

        self.xturns, self.snake_length = self.grow(self.xturns, self.snake_length)

        self.player0, f0 = self.__move(self.player0, dir0, 0)
        self.player1, f1 = self.__move(self.player1, dir1, 1)
        if self.player0 == self.player1:
            f0, f1 = False, False

        losser = self.__judge_losser(f0, f1)
        if losser != Game.GAME_CARRY_ON:
            self.game_finished = True

        return losser


    def debug(self):
        print(self.__str__())


    def __str__(self):
        return \
        f'玩家0: {self.player0}, 玩家1: {self.player1}\n' + \
        f'长度{self.snake_length}, 回合数:{self.xturns}\n' + \
        f'结束情况: {self.game_finished}\n' + \
        f'{self.board}'

    def __repr__(self):
        return \
        f'玩家0: {self.player0}, 玩家1: {self.player1}\n' + \
        f'长度{self.snake_length}, 回合数:{self.xturns}\n' + \
        f'结束情况: {self.game_finished}\n' + \
        f'{self.board}'

    def __call__(self, dir0: int, dir1: int) -> int:
        return self.resume(dir0, dir1)
        
        

        
        


        
