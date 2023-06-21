from flask import request
from flask_socketio import emit
from .._main import ws
# from ...TigerStripeSharnake import SlitherOnWebServer, PersueRoomSnake
from TigerStripeSharnake import SlitherOnWebServer, PersueRoomSnake, PureMctsSnake, G

@ws.on('connect', namespace='/snake')
def onconnect() -> None:
    print(f'websocket connected, ip = {request.remote_addr}, namespace = /snake')

@ws.on('disconnect', namespace='/snake')
def ondisconnect() -> None:
    print(f'websocket disconnected, ip = {request.remote_addr}, namespace = /snake')

@ws.on('request', namespace='/snake')
def snake_request(req: str) -> None:
    try:
        G.record()
        res = SlitherOnWebServer(PersueRoomSnake).run(req)
        emit('response', res, namespace = '/snake')
    except Exception as e:
        print(type(e), str(e))
        emit('response', '游戏结束', namespace = '/snake')
