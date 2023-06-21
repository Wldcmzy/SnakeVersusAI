
        var cvs = document.getElementById('mycanv');
        var ctx = cvs.getContext('2d');
        var bs = 39;
        const cw = "black", cn = "lightgray", c0 = "green", c1 = "red", cr = 'blue';
        var tail = '▾', head = '◉'
        var GROW_QUICK_TURN = 10, GROW_NORMAL_TURN = 3


        function packline(y, x, mod, len){
            x *= bs, y *= bs, len *= bs;
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(x, y);
            if(mod === 'row'){
                ctx.lineTo(x + len, y);
            }else if(mod === 'col'){
                ctx.lineTo(x, y + len);
            }
            ctx.stroke();
        }

        function packlines(board){
            let r = board.length, c = board[0].length;
            for(var i = 0; i<=r; i ++){
                packline(i, 0, 'row', c);
            }
            for(var i = 0; i<=c; i ++){
                packline(0, i, 'col', r);
            }
        }

        function packcell(y, x, c) {
            x = x * bs, y = y * bs;
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.arcTo(x, y + bs, x + bs, y + bs, 0);
            ctx.arcTo(x + bs, y + bs, x + bs, y, 0);
            ctx.arcTo(x + bs, y, x, y, 0);
            ctx.arcTo(x, y, x, y + bs, 0);
            ctx.fillStyle = c;
            ctx.fill();
            ctx.restore();
        }

        function packcells(board, lim, xturns){
            let t0 = 0x3fff, t1 = 0x3fff, t0x = null, t0y = null, t1x = null, t1y = null;
            let r = board.length, c = board[0].length;
            for(var i = 0; i<r; i++){
                for(var j = 0; j<c; j++){
                    var color;
                    if(board[i][j] == 0x3f00){
                        color = cw;
                    }else if(board[i][j] == 0x3f01){
                       color = cr;
                    }else if(lim >= Math.abs(board[i][j])){
                        color = cn;
                    }else if(board[i][j] > 0){
                        if(t0 > board[i][j]){
                            t0x = i, t0y = j;
                            t0 = board[i][j];
                        }
                        color = c0;
                    }else if(board[i][j] < 0){
                        if(t1 > Math.abs(board[i][j])){
                            t1x = i, t1y = j;
                            t1 = Math.abs(board[i][j]);
                        }
                        color = c1;
                    }else{
                        color = cn;
                    }
                    packcell(i, j, color);
                }
            }

            nextxturns = xturns + 1;
            if(nextxturns <= GROW_QUICK_TURN + 1){

            }else if((nextxturns - GROW_QUICK_TURN - 1) % GROW_NORMAL_TURN == 0){

            }else{
                // 标记下回合消亡格
                packtext(t0x, t0y, tail)
                packtext(t1x, t1y, tail)
            }
        }

        function packtext(y, x, t){
            x *= bs, y *= bs;
            y += 1;
            ctx.save();
            ctx.font = '25px Arial';
            ctx.fillStyle = 'yellow';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(t, x + bs / 2, y + bs / 2);
            ctx.restore();
        }

        function clearcvs(){
            cvs.width = cvs.width
        }
        
        function pack(board, xturns, len, head0x, head0y, head1x, head1y){
            console.log(board)
            clearcvs()
            let lim = xturns - len;
            packcells(board, lim, xturns);
            packlines(board);
            packtext(head0x, head0y, head)
            packtext(head1x, head1y, head)
        }

        // function test(){
        //     var testlen = 13, testurn = 19
        //     var test0x = 5, test0y = 7
        //     var test1x = 7, test1y = 3
        //     var testboard = 
        //         [
        //         [16128,16128,16128,16128,16128,16128,16128,16128,16128,16128,16128],
        //         [16128,1,2,3,4,5,0,0,0,0,16128],
        //         [16128,0,0,0,0,6,0,0,16128,0,16128],
        //         [16128,0,0,0,0,7,0,0,0,16128,16128],
        //         [16128,-14,-13,-12,-11,8,0,16128,0,0,16128],
        //         [16128,-15,-16,-17,-10,9,18,19,0,0,16128],
        //         [16128,0,0,-18,-9,10,17,16,15,0,16128],
        //         [16128,0,0,-19,-8,11,12,13,14,0,16128],
        //         [16128,16128,0,16128,-7,0,0,0,0,0,16128],
        //         [16128,0,0,0,-6,-5,-4,-3,-2,-1,16128],
        //         [16128,16128,16128,16128,16128,16128,16128,16128,16128,16128,16128],
        //         ]
        //     pack(testboard, testurn, testlen, test0x, test0y, test1x, test1y)
        // }
        
        // test()

        
