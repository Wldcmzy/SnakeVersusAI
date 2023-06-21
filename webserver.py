
if __name__ == '__main__':
    def LoadModules():
        import webmodules.snake

    from webmodules._main import HOST, PORT, app, ws

    LoadModules()

    ws.init_app(app)
    ws.run(app, host=HOST, port=PORT)
    