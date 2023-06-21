import json
from typing import Tuple
from .types import Position
import numpy as np

class Jsoner:
    @staticmethod
    def pack_board(
        width: int,
        height: int,
        player0: Position,
        player1: Position,
        obstacle: Tuple[Position],
        history0: Tuple[Position],
        history1: Tuple[Position],
    ) -> str:
        dic0 = {}
        dic0['width'] = width
        dic0['height'] = height
        dic0['obstacle'] = [{'x' : x, 'y': y} for x, y in obstacle]
        dic1 = dic0.copy()
        x, y = player0
        dic0['x'] = y
        dic0['y'] = x
        x, y = player1
        dic1['x'] = y
        dic1['y'] = x
        d0 = {}
        lst0 = [dic0]
        lst0.extend([{'direction' : x} for x in history1])
        d0['requests'] = lst0
        d0['responses'] = [{'direction' : x} for x in history0]
        d1 = {}
        lst1 = [dic1]
        lst1.extend([{'direction' : x} for x in history0])
        d1['requests'] = lst1
        d1['responses'] = [{'direction' : x} for x in history1]

        return json.dumps(d0), json.dumps(d1)

    @staticmethod
    def unpack_board(data: str) -> Tuple[int, Tuple[Position]]:
        data = json.loads(data)
        res = data['responses']
        req = data['requests']
        data = req[0]
        width, height = data['width'], data['height']
        # player0, player1 = (data['0']['x'], data['0']['y']), (data['1']['x'], data['1']['y'])
        x, y = data['y'], data['x']
        obstacle = ((z['y'], z['x']) for z in data['obstacle'])

        history_mine = [x['direction'] for x in res]
        history_enemy = [x['direction'] for x in req[1 : ]]

        return width, height, x, y, obstacle, history_mine, history_enemy


    @staticmethod
    def pack_dir(x: int) -> str:
        return json.dumps({"response" : {'direction' : x}})
    
    @staticmethod
    def unpack_dir(s: str) -> int:
        return json.loads(s)['requests'][-1]['direction']

    
    @staticmethod
    def pack_server_msg(
        board: np.ndarray,
        dir: int,
        xturns: int,
        length: int,
        player0: Position,
        player1: Position,
    ) -> str:
        return json.dumps({
            'board': board.tolist(),
            'dir': dir,
            'xturns': xturns,
            'length': length,
            'player0': player0,
            'player1': player1,
        })


    # @staticmethod
    # def gen_next_baord_for_debug(
    #     width: int,
    #     height: int,
    #     player0: Position,
    #     player1: Position,
    #     obstacle: Tuple[Position],
    #     history0: Tuple[Position],
    #     history1: Tuple[Position],
    #     next0: int,
    #     next1: int,
    # ) -> str:
    #     dic0 = {}
    #     dic0['width'] = width
    #     dic0['height'] = height
    #     dic0['obstacle'] = [{'x' : x, 'y': y} for x, y in obstacle]
    #     dic1 = dic0.copy()
    #     x, y = player0
    #     dic0['x'] = y
    #     dic0['y'] = x
    #     x, y = player1
    #     dic1['x'] = y
    #     dic1['y'] = x
    #     d0 = {}
    #     lst0 = [dic0]
    #     lst0.extend([{'direction' : x} for x in history1])
    #     d0['requests'] = lst0
    #     d0['responses'] = [{'direction' : x} for x in history0]
    #     d1 = {}
    #     lst1 = [dic1]
    #     lst1.extend([{'direction' : x} for x in history0])
    #     d1['requests'] = lst1
    #     d1['responses'] = [{'direction' : x} for x in history1]

    #     d0['responses'].append({'direction' : next0})
    #     d0['requests'].append({'direction' : next1})
    #     d1['responses'].append({'direction' : next1})
    #     d1['requests'].append({'direction' : next0})

    #     return json.dumps(d0), json.dumps(d1)