from .utils.jsoner import Jsoner
from .snake._SnakeBase import SnakeBase

class Slither:
    def __init__(self, snake_class) -> None:
        self.snake_class = snake_class
        self.dir = 0

    def load(self) -> None:
        '''
        读入并加载游戏信息
        '''
        self.snake: SnakeBase = self.snake_class(*Jsoner.unpack_board(input()))
    
    def act(self, data = None, debug = False) -> int:
        '''
        行为预测
        '''
        if data == None:
            enemy_dir = -1
        else:
            enemy_dir = Jsoner.unpack_dir(data)
        return self.snake(enemy_dir, debug)

    def run(self, debug = False) -> None:
        '''
        运行
        '''
        self.load()
        d = self.act(debug = debug)
        # while True:
        #     if d == None:
        #         break
        #     print(Jsoner.pack_dir(d))
        #     d = self.act(data = input(), debug = debug)
        if d != None:
            print(Jsoner.pack_dir(d))

    
class SlitherOnWebServer(Slither):
    def __init__(self, snake_class) -> None:
        super().__init__(snake_class)
    
    def load(self, msg: str) -> None:
        self.snake: SnakeBase = self.snake_class(*Jsoner.unpack_board(msg))

    def act(self, data=None, debug=False) -> int:
        return super().act(data, debug)

    def run(self, msg: str, debug=False) -> str:
        self.load(msg)
        d = self.act(debug = debug)
        
        return Jsoner.pack_server_msg(
            self.snake.game.board,
            d,
            self.snake.game.xturns,
            self.snake.game.snake_length,
            self.snake.game.player0,
            self.snake.game.player1,
        )

    
