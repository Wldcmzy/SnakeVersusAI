from typing import Optional
from ..game.game import Game
import random

class SnakeBase:
    def __init__(self, *args) -> None:
        self.load(*args)
        

    def load(self, *args) -> None:
        '''
        加载游戏
        参数:
            args: 游戏的初始化信息, 类型同Game.get_history的返回值
        返回:
            None
        '''
        width, height, x, y, obs, history_mine, history_enemy = args

        if x == 1 and y == 1:
            player0 = (x, y)
            player1 = (width, height)
            self.player_id = 0
            history0 = history_mine
            history1 = history_enemy
        else:
            player0 = (1, 1)
            player1 = (x, y)
            self.player_id = 1
            history1 = history_mine
            history0 = history_enemy

        self.game = Game(width, height, player0, player1, obs)
        
        for i in range(len(history0)):
            self.game(history0[i], history1[i])

        
        self.my_dir = 0
        
    
    # def set_player_id(self, x: int) -> None:
    #     '''
    #     设置玩家编号
    #     参数:
    #         x: 玩家编号(0 or 1)
    #     返回:
    #         None
    #     '''
    #     self.player_id = x

    def get_rule(self):
        '''
        获得蛇的行为逻辑, 应当在继承中背重写
        参数:
            无
        返回:
            一个指导蛇行为逻辑的函数，必须传入固定的参数，返回值为蛇的爬行方向，形如：
            def func(
    
                # 一张大小为(n + 2, m + 2)对局地图(元素类型为numpy.int16的numpy数组)
                # 地图实质是从Game对象导出的，这里做简单介绍
                
                # 地图例子:
                #array([[16128, 16128, 16128, 16128, 16128, 16128],
                #   	[16128,     1, 16128,     0,     0, 16128],
                #   	[16128,     2,     3,     4,     0, 16128],
                #  		[16128,     0,     0, 16128,     0, 16128],
                #   	[16128,    -4,    -3,    -2,    -1, 16128],
                #   	[16128, 16128, 16128, 16128, 16128, 16128]], dtype=int16)
                
                # 墙表示为0x3f00(16128)，地图的边界是一圈墙，中间大小为(n, m)的区域是竞技场
                # 其他数字表示此格子最后一次被蛇进入的回合数，正数代表玩家0，负数代表玩家1
                board: np.ndarray, 
                
                
                # 蛇自己头部的坐标 (int, int)
                player: Position, 
                
                # 对手蛇头部的坐标 (int, int)
                enemy: Position, 
                
                # 当前回合数
                xturns: int,
                
                # 当前蛇的长度，注意，预测方向时应使用下一回合蛇的长度进行计算，详见RandomSanke例子
                length: int
            ):
                return random.randint(0, 3)
        '''
        pass

    def resume(self, enemy_dir: int, debug: bool = False) -> int:
        '''
        游戏推进一回合
        参数:
            enemy_dir: (
                in [0, 1, 2, 3] 对手上一回合的爬行方向，
                若 < 0 代表不推进回合, 常用于游戏的首个回合
            )
        返回:
            [int]游戏状态 (
                Game.NO_ACTION: 不推进回合
                Game.BOTH_DEFEAT: 两玩家都死亡
                Game.PLAYER0_DEFEAT: 玩家0死亡
                Game.PLAYER1_DEFEAT: 玩家1死亡
                Game.GAME_CARRY_ON: 无事发生，游戏继续
            )
        '''
        player0, player1 = self.my_dir, enemy_dir
        if self.player_id == 1:
            player0, player1 = player1, player0

        res = Game.NO_ACTION
        if enemy_dir >= 0:
            res = self.game(player0, player1)
            
        if debug:
            self.game.debug()
        
        return res  

    def act(self) -> int:
        '''
        预测蛇下一步的行动
        参数:
            无
        返回:
            蛇下一步的爬行方向
        '''
        me, enemy = self.game.player0, self.game.player1
        if self.player_id == 1:
            me, enemy = enemy, me

        self.my_dir = self.get_rule()(self.game.board, me, enemy, self.game.xturns, self.game.snake_length)
        return self.my_dir


    def __call__(self, enemy_dir: int, debug: bool = False) -> Optional[int]:
        '''
        集 推进回合(resume) 和 行为预测(act) 为一体
        enemy_dir: (
                in [0, 1, 2, 3] 对手上一回合的爬行方向，
                若 < 0 代表不推进回合, 只预测方向, 常用于游戏的首个回合
            )
        返回:
            蛇下一步的爬行方向
        '''
        res = self.resume(enemy_dir, debug)
        d = None
        if res in [Game.GAME_CARRY_ON, Game.NO_ACTION]:
            d = self.act()
            if debug:
                print('next dir = ', d)
        else:
            if debug:
                print('game end:', res)
        return d


        