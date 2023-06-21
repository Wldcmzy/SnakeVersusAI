

        var mydict;
        var enemy_dir;
        var ok = false;
        var playerid;

        var up = document.getElementById("up")
        var down = document.getElementById("down")
        var left = document.getElementById("left")
        var right = document.getElementById("right")
        var newg = document.getElementById("new")
        var msgp = document.getElementById("msg")

        ws = io.connect(
            'ws://' + document.domain + ':' + location.port + '/snake', 
            {
                reconnectionDelayMax: 10000,
                query: {
                    
                }
            }
        );

        ws.on("connect", (revconnect) => {
            console.log('已连接服务器')
        })

        ws.on("disconnect", (revconnect) => {
            console.log('已断开连接')
            alert('服务器连接断开...')
        })

        ws.on('response', (res) => {
            if(res == '游戏结束'){
                alert('游戏结束了');
                wait()
                setmsgp(clear = true)
                clearcvs()
            }else{
                res = JSON.parse(res)
                pack(res.board, res.xturns, res.length, res.player0[0], res.player0[1], res.player1[0], res.player1[1])
                enemy_dir = res.dir
                resume()
                setmsgp()
            }

        })

        var dict = {
            'left': 0,
            'down': 1,
            'right': 2,
            'up': 3,
        }

        up.addEventListener('click', () => {
            if(cango()){
                newdir(dict.up)
                send()
            }
        })

        down.addEventListener('click', () => {
            if(cango()){
                newdir(dict.down)
                send()
            }
        })

        left.addEventListener('click', () => {
            if(cango()){
                newdir(dict.left)
                send()
            }
        })

        right.addEventListener('click', () => {
            if(cango()){
                newdir(dict.right)
                send()
            }
        })

        newg.addEventListener('click', () => {
            mydict = gen()
            send()
        })

        function wait(){
            ok = false
        }

        function resume(){
            ok = true
        }

        function cango(){
            return ok
        }

        function send(){
            req = JSON.stringify(mydict)
            console.log(req)
            ws.emit('request', req)
            wait()
        }

        function newdir(x){
            mydict.requests.push({"direction": x})
            mydict.responses.push({"direction": enemy_dir})
        }

        function gen(){
            let tmydict = {
                'requests': [],
                'responses': [],
            }
            let r = Math.floor(Math.random() * 10) + 8
            let c = Math.floor(Math.random() * 10) + 8
            let x, y;
            if(Math.random() < 0.5){
                x = 1, y = 1;
                playerid = 0;
            }else{
                x = r, y = c;
                playerid = 1;
            }
            let inidict = {
                "height":c,
                "width":r,
                "x": y,
                "y": x,
                "obstacle": []
            }
            const mp = new Map()
            let num = Math.floor(Math.random() * ((r - 1) * (c - 1) * 0.1)) + 3
            num = Math.min(num, Math.max(r, c))
            let cnt = 0
            while(cnt < num){
                x = Math.floor(Math.random() * r)
                y = Math.floor(Math.random() * c)
                if(x >=1 && x <= r && y >= 1 && y <= c){
                    if(x == 1 && y == 1) continue;
                    if(x == r && y == c) continue;
                    let xy = x * 100 + y;
                    if(mp.get(xy) == null){
                        mp.set(xy, 1)
                        inidict.obstacle.push({"x":y,"y":x})
                        cnt += 1;
                    }
                }
            }
            tmydict.requests.push(inidict)
            return tmydict;
        }
        
        function setmsgp(clear = false){
            if(clear){
                msgp.innerHTML = ''
                return;
            }
            if(playerid == 1){
                msgp.innerHTML = '你是绿蛇'
                msgp.style.color = 'green'
            }else{
                msgp.innerHTML = '你是红蛇'
                msgp.style.color = 'red'
            }
        }
        

