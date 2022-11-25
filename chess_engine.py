from winreg import KEY_NOTIFY


class Game_Status():

    def __init__(self):
        # self.board = [
        #     ["bR","bN","bB","bQ","bK","bB","bN","bR"],
        #     ["bP","bP","bP","bP","bP","bP","bP","bP"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["wP","wP","wP","wP","wP","wP","wP","wP"],
        #     ["wR","wN","wB","wQ","wK","wB","wN","wR"],
        # ]

        self.board = [
            ["bR","bR","bR","bR","bK","bR","bR","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],
        ]
        
        

        #手番： True -> white, False -> Black
        self.white_to_move = True

        self.moveLog = []

        self.wK_location = '74'
        self.bK_location = '04'

        self.checkMate = False
        self.staleMate = False

        #キングやルークが動く　or　キャスリングをしたらFalseにする
        self.castle_possible_white = True
        self.castle_possible_black = True
        self.castle_possible_wK = True
        self.castle_possible_wQ = True
        self.castle_possible_bK = True
        self.castle_possible_bQ = True
    
    def make_move(self, move_start, move_end):
        start_row = int(move_start[0])
        start_col = int(move_start[1])
        end_row = int(move_end[0])
        end_col = int(move_end[1])

        #動かしたコマと、とったコマ
        piece_moved = self.board[start_row][start_col]
        piece_captured = self.board[end_row][end_col]

        #もともとのセルを空欄にし、動かしたコマを移動先のセルに置く
        self.board[start_row][start_col] = '--'
        self.board[end_row][end_col] = piece_moved

        #キングの位置を更新
        if piece_moved == 'wK':
            self.wK_location = str(end_row) + str(end_col)
        elif piece_moved == 'bK':
            self.bK_location = str(end_row) + str(end_col)

        #-------------------
        #特殊処理への対応
        #-------------------

        #ポーンプロモーション
        if (piece_moved == 'wP' and end_row == 0) or (piece_moved == 'bP' and end_row == 7):
            self.board[end_row][end_col] = self.board[end_row][end_col][0] + 'Q'

        #キャスリング用の設定
        self.make_move_castling(start_row, start_col, end_row, end_col, piece_moved, piece_captured)

        #アンパッサン処理
        if piece_moved[1] == 'P' and piece_captured == '--':
            if start_col != end_col:
                #remove existing opponent Pawn
                if self.white_to_move:
                    self.board[end_row + 1][end_col] = '--'
                else:
                    self.board[end_row - 1][end_col] = '--'

        #手番を変える
        self.white_to_move = not self.white_to_move


        move = [start_row, start_col, end_row, end_col, piece_moved, piece_captured]
        self.moveLog.append(move)
        print(self.moveLog)

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            # '''
            # move 0: start row
            #      1: start col
            #      2: end row
            #      3: end col
            #      4: piece moved
            #      5: piece captured
            
            # '''

            self.board[move[0]][move[1]] = move[4]
            self.board[move[2]][move[3]] = move[5]
            self.white_to_move = not self.white_to_move

            #キングの位置を更新（moved_pieceがキングのとき、start_rowとstart_colをセットする）
            if move[4] == 'wK':
                self.wK_location = str(move[0]) + str(move[1])
            elif move[4] == 'bK':
                self.bK_location = str(move[0]) + str(move[1])

            #----------------------
            #特殊処理への対応
            #----------------------

            #キャスリングの取り消し
            if move[4] == 'wK':
                self.castle_possible_white = True
                if move[3] - move[1] == 2:
                    self.board[move[2]][move[3] + 1] = self.board[move[2]][move[3] - 1]
                    self.board[move[2]][move[3] - 1] = '--'
                    self.castle_possible_wK = True
                elif move[3] - move[1] == -2:
                    self.board[move[2]][move[3] - 2] = self.board[move[2]][move[3] + 1]
                    self.board[move[2]][move[3] + 1] = '--'
                    self.castle_possible_wQ = True
            elif move[4] == 'bK':
                self.castle_possible_black = True
                if move[3] - move[1] == 2:
                    self.board[move[2]][move[3] + 1] = self.board[move[2]][move[3] - 1]
                    self.board[move[2]][move[3] - 1] = '--'
                    self.castle_possible_bK = True
                elif move[3] - move[1] == -2:
                    self.board[move[2]][move[3] - 2] = self.board[move[2]][move[3] + 1]
                    self.board[move[2]][move[3] + 1] = '--'
                    self.castle_possible_bQ = True
                
            #アンパッサンの取り消し
            if move[4][1] == 'P' and move[5] == '--' and move[1] != move[3]:
                if move[4][0] == 'w':
                    self.board[move[0]][move[3]] = 'bP'
                else:
                    self.board[move[0]][move[3]] = 'wP'



        self.checkMate = False
        self.staleMate = False
        self.drawGame  = False

        print('undo_move: ', self.moveLog)

    def get_valid_moves(self):

        work_castle_possible_white = self.castle_possible_white 
        work_castle_possible_black = self.castle_possible_black
        work_castle_possible_wK = self.castle_possible_wK
        work_castle_possible_wQ = self.castle_possible_wQ 
        work_castle_possible_bK = self.castle_possible_bK 
        work_castle_possible_bQ = self.castle_possible_bQ

        moves = self.get_all_possible_moves()

        #キャスリングの動きを追加
        self.get_castling_moves(moves)

        #アンパッサンの動きを追加
        self.get_enpassant_moves(moves)

        self.remove_invalid_moves(moves)
        #movesがブランクの場合には、ゲーム終了処理を行う
        if len(moves) == 0:
            if self.confirm_check():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
            self.drawGame  = False
        #ドローか否かを調べる
        if self.confirm_draw():
            self.drawGame = True
        else:
            self.drawGame = False
 
        #キャスリングフラグを戻す
        self.castle_possible_white = work_castle_possible_white
        self.castle_possible_black = work_castle_possible_black 
        self.castle_possible_wK = work_castle_possible_wK 
        self.castle_possible_wQ = work_castle_possible_wQ  
        self.castle_possible_bK = work_castle_possible_bK  
        self.castle_possible_bQ = work_castle_possible_bQ  
 
 
 
        return moves

    def check_valid_move(self, move_start, move_end, valid_moves):
        if not valid_moves:
            return False
        
        for move in valid_moves:
            if move[0] == move_start and move[1] == move_end:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        #len(self.board) = 8
        #range(8) -> 0 ~ 7
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece_color = self.board[row][col][0]
                piece_type = self.board[row][col][1]
                if (piece_color == 'w' and self.white_to_move) or (piece_color == 'b' and not self.white_to_move):
                    if piece_type == 'P':
                        self.get_Pawn_moves(row, col, moves)
                    elif piece_type == 'N':
                        self.get_Night_moves(row, col, moves)
                    elif piece_type == 'B':
                        self.get_Bishop_moves(row, col, moves)
                    elif piece_type == 'R':
                        self.get_Rook_moves(row, col, moves)
                    elif piece_type == 'Q':
                        self.get_Queen_moves(row, col, moves)
                    elif piece_type == 'K':
                        self.get_King_moves(row, col, moves)
        return moves

    def remove_invalid_moves(self, moves):
        for i in range(len(moves) - 1, -1, -1):
            move = moves[i]
            #まず自分を動かしてみる。
            self.make_move(move[0], move[1])

            #make_moveの中で、手番が変更されているので、自分に戻す
            self.white_to_move = not self.white_to_move

            #チェックされていたら、その動きは配列から削除する
            if self.confirm_check():
                moves.remove(moves[i])

            #手番を元に戻す　→　つまり相手になる
            self.white_to_move = not self.white_to_move

            #動かした手を戻す　→　このundo_moveの中で、手番を変更しているので、結果自分に戻る
            self.undo_move()
    
    def confirm_check(self):
        #手番のキングの位置を指定して、confirm_attackを呼び出す
        if self.white_to_move:
            king_location = self.wK_location
        else:
            king_location = self.bK_location
        return self.confirm_attack(king_location)

    def confirm_attack(self, square):
        self.white_to_move = not self.white_to_move
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opp_moves:
            #移動先=squareならばTrue
            if move[1] == square:
                return True
        return False

    def confirm_draw(self):
        count_wB = 0
        count_bB = 0
        count_wN = 0
        count_bN = 0
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                square = self.board[row][col]
                #ポーン、クイーン、ルークが黒白関係なくボード上に１つでもあれば、ドローではない
                if square[1] == 'P' or square[1] == 'Q' or square[1] == 'R':
                    return False
                else:
                    if square == 'wB':
                        count_wB += 1
                        #同色のビショップが２枚　or　同色のビショップ１枚＋ナイト１枚あれば、ドローではない
                        if count_wB == 2 or count_wN >= 1:
                            return False
                    elif square == 'bB':
                        count_bB += 1
                        #同色のビショップが２枚　or　同色のビショップ１枚＋ナイト１枚あれば、ドローではない
                        if count_bB == 2 or count_bN >= 1:
                            return False        

                    elif square == 'wN':
                        count_wN += 1
                        #同色のビショップ１枚＋ナイト１枚あれば、ドローではない
                        if count_wB >= 1:
                            return False
                    
                    elif square == 'bN':
                        count_bN += 1
                        #同色のビショップ１枚＋ナイト１枚あれば、ドローではない
                        if count_bB >= 1:
                            return False
        #上記以外はすべてドロー
        return True
    
    def get_Pawn_moves(self, row, col, moves):
        if self.white_to_move:
            row_adj = -1
            row_start = 6
            row_start_adj = -2
            opp_piece = 'b'
        else:
            row_adj = 1
            row_start = 1
            row_start_adj = 2
            opp_piece = 'w'

        if row > 0 and row < 7:
            end_row = row + row_adj
            end_col = col
            #前に進む場合
            if self.board[end_row][end_col] == '--':
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

                end_row = row + row_start_adj
                end_col = col
                if row == row_start and self.board[end_row][end_col] == '--':
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)

            #相手のコマをとる場合
            #白:左、黒：右
            if col - 1 >= 0:
                end_row = row + row_adj
                end_col = col - 1
                if self.board[end_row][end_col][0] == opp_piece:
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)  

            #白:右、黒：左
            if col + 1 <= 7:
                end_row = row + row_adj
                end_col = col + 1
                if self.board[end_row][end_col][0] == opp_piece:
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)      

    def get_Night_moves(self, row, col, moves):

        # 1) vertical up
        if row > 1 and col > 0:
            end_row = row - 2
            end_col = col - 1
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

        if row > 1 and col < 7:
            end_row = row - 2
            end_col = col + 1
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

        # 2) left move
        if row > 0 and col > 1:
            end_row = row - 1
            end_col = col - 2
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)
        
        if row < 7 and col > 1:
            end_row = row + 1
            end_col = col - 2
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

        # 3) vertical down
        if row < 6 and col > 0:
            end_row = row + 2
            end_col = col - 1
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)
        
        if row < 6 and col < 7:
            end_row = row + 2
            end_col = col + 1
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)
        
        # 4) right move
        if row > 0 and col < 6:
            end_row = row - 1
            end_col = col + 2
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)
        if row < 7 and col < 6:
            end_row = row + 1
            end_col = col + 2
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

    def get_Bishop_moves(self, row, col, moves):
        #Row:減少、Col:増加
        for row_num in range(row-1, -1, -1):
            if col + (row - row_num) < 8:
                end_row = row_num
                end_col = col + row - row_num
                if self.board[end_row][end_col] == '--':
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)
                #同じ色のピースがあった場合　→　そこを含まない、かつ、それ以上先には進めないのでbreak
                elif self.board[end_row][end_col][0] == self.board[row][col][0]:
                    break 
                #違う色のピースがあった場合　→　そこを含む（とる）、かつ、そこで終わるのでbreak
                else:
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)
                    break
        
        #Row:増加、Col:減少
        for row_num in range(row+1, 8):
            if col + (row - row_num) >= 0:
                end_row = row_num
                end_col = col + row - row_num
                if self.board[end_row][end_col] == '--':
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)
                #同じ色のピースがあった場合　→　そこを含まない、かつ、それ以上先には進めないのでbreak
                elif self.board[end_row][end_col][0] == self.board[row][col][0]:
                    break 
                #違う色のピースがあった場合　→　そこを含む（とる）、かつ、そこで終わるのでbreak
                else:
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)
                    break
        
        #Row:減少、Col:減少
        for row_num in range(row-1, -1, -1):
            if col - (row - row_num) >= 0:
                end_row = row_num
                end_col = col - (row - row_num)
                if self.board[end_row][end_col] == '--':
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)
                #同じ色のピースがあった場合　→　そこを含まない、かつ、それ以上先には進めないのでbreak
                elif self.board[end_row][end_col][0] == self.board[row][col][0]:
                    break 
                #違う色のピースがあった場合　→　そこを含む（とる）、かつ、そこで終わるのでbreak
                else:
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)
                    break
            
        #Row:増加、Col:増加
        for row_num in range(row+1, 8):
            if col - (row - row_num) < 8:
                end_row = row_num
                end_col = col - (row - row_num)
                if self.board[end_row][end_col] == '--':
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)
                #同じ色のピースがあった場合　→　そこを含まない、かつ、それ以上先には進めないのでbreak
                elif self.board[end_row][end_col][0] == self.board[row][col][0]:
                    break 
                #違う色のピースがあった場合　→　そこを含む（とる）、かつ、そこで終わるのでbreak
                else:
                    move = (str(row) + str(col), str(end_row) + str(end_col))
                    moves.append(move)
                    break

    def get_Rook_moves(self, row, col, moves):
        #白：アップ、黒；ダウン
        for row_num in range(row - 1, -1, -1):
            end_row = row_num
            end_col = col
            #空欄だった場合→そこを含む
            if self.board[end_row][end_col] == '--':
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

            #同じ色のピースがあった場合→そこを含まない、かつ、それ以上先には進めないのでbreak
            elif self.board[end_row][end_col][0] == self.board[row][col][0]:
                break 
            #違う色のピースがあった場合→そこを含む（取る）、かつ、それ以上先には進めないのでbreak
            else:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)
                break

        #白：ダウン、黒；アップ
        for row_num in range(row + 1, 8):
            end_row = row_num
            end_col = col
            #空欄だった場合→そこを含む
            if self.board[end_row][end_col] == '--':
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

            #同じ色のピースがあった場合→そこを含まない、かつ、それ以上先には進めないのでbreak
            elif self.board[end_row][end_col][0] == self.board[row][col][0]:
                break 
            #違う色のピースがあった場合→そこを含む（取る）、かつ、それ以上先には進めないのでbreak
            else:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)
                break

        #白：右、黒；左
        for col_num in range(col + 1, 8):
            end_row = row
            end_col = col_num
            #空欄だった場合→そこを含む
            if self.board[end_row][end_col] == '--':
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

            #同じ色のピースがあった場合→そこを含まない、かつ、それ以上先には進めないのでbreak
            elif self.board[end_row][end_col][0] == self.board[row][col][0]:
                break 
            #違う色のピースがあった場合→そこを含む（取る）、かつ、それ以上先には進めないのでbreak
            else:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)
                break

        #白：左、黒；右
        for col_num in range(col - 1, -1, -1):
            end_row = row
            end_col = col_num
            #空欄だった場合→そこを含む
            if self.board[end_row][end_col] == '--':
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

            #同じ色のピースがあった場合→そこを含まない、かつ、それ以上先には進めないのでbreak
            elif self.board[end_row][end_col][0] == self.board[row][col][0]:
                break 
            #違う色のピースがあった場合→そこを含む（取る）、かつ、それ以上先には進めないのでbreak
            else:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)
                break

    def get_Queen_moves(self, row, col, moves):
        self.get_Bishop_moves(row, col, moves)
        self.get_Rook_moves(row, col, moves)

    def get_King_moves(self, row, col, moves):
        
        #白：前方、黒：後方
        if row > 0 and col > 0:
            end_row = row - 1
            end_col = col - 1
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

        if row > 0:
            end_row = row - 1
            end_col = col
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)    

        if row > 0 and col < 7:
            end_row = row - 1
            end_col = col + 1
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

        #白；後方、黒：前方
        if row < 7 and col > 0:
            end_row = row + 1
            end_col = col - 1
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

        if row < 7:
            end_row = row + 1
            end_col = col
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)    

        if row < 7 and col < 7:
            end_row = row + 1
            end_col = col + 1
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

        #左右
        if col > 0:
            end_row = row
            end_col = col - 1
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)

        if col < 7:
            end_row = row
            end_col = col + 1
            if self.board[end_row][end_col] == '--' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                move = (str(row) + str(col), str(end_row) + str(end_col))
                moves.append(move)    

    def get_castling_moves(self, moves):
        if not self.confirm_check():

            #白番（キングサイド）
            if self.white_to_move and self.castle_possible_wK and self.castle_possible_white:
                king_row = 7
                king_col_current = 4
                king_col_next = king_col_current + 1
                king_col_goal = king_col_current + 2
                #間にコマがない
                if self.board[king_row][king_col_next] == '--' and self.board[king_row][king_col_goal] == '--':
                    #キングが移動する場所が攻撃されていない
                    if not self.confirm_attack(str(king_row) + str(king_col_next)) and \
                        not self.confirm_attack(str(king_row) + str(king_col_goal)):

                        move = (str(king_row) + str(king_col_current), str(king_row) + str(king_col_goal))
                        moves.append(move)

            #白番（クイーンサイド）
            if self.white_to_move and self.castle_possible_wQ and self.castle_possible_white:
                king_row = 7
                king_col_current = 4
                king_col_next = king_col_current - 1
                king_col_goal = king_col_current - 2
                king_col_next_of_goal = king_col_current - 3
                #間にコマがない
                if self.board[king_row][king_col_next] == '--' and self.board[king_row][king_col_goal] == '--' \
                    and self.board[king_row][king_col_next_of_goal] == '--':
                    #キングが移動する場所が攻撃されていない
                    if not self.confirm_attack(str(king_row) + str(king_col_next)) and \
                        not self.confirm_attack(str(king_row) + str(king_col_goal)):

                        move = (str(king_row) + str(king_col_current), str(king_row) + str(king_col_goal))
                        moves.append(move)    

            #黒番（キングサイド）
            if not self.white_to_move and self.castle_possible_bK and self.castle_possible_black:
                king_row = 0
                king_col_current = 4
                king_col_next = king_col_current + 1
                king_col_goal = king_col_current + 2
                #間にコマがない
                if self.board[king_row][king_col_next] == '--' and self.board[king_row][king_col_goal] == '--':
                    #キングが移動する場所が攻撃されていない
                    if not self.confirm_attack(str(king_row) + str(king_col_next)) and \
                        not self.confirm_attack(str(king_row) + str(king_col_goal)):

                        move = (str(king_row) + str(king_col_current), str(king_row) + str(king_col_goal))
                        moves.append(move)


            #黒番（クイーンサイド）
            if not self.white_to_move and self.castle_possible_bQ and self.castle_possible_black:
                king_row = 0
                king_col_current = 4
                king_col_next = king_col_current - 1
                king_col_goal = king_col_current - 2
                king_col_next_of_goal = king_col_current - 3
                #間にコマがない
                if self.board[king_row][king_col_next] == '--' and self.board[king_row][king_col_goal] == '--' \
                    and self.board[king_row][king_col_next_of_goal] == '--':
                    #キングが移動する場所が攻撃されていない
                    if not self.confirm_attack(str(king_row) + str(king_col_next)) and \
                        not self.confirm_attack(str(king_row) + str(king_col_goal)):

                        move = (str(king_row) + str(king_col_current), str(king_row) + str(king_col_goal))
                        moves.append(move)

    def make_move_castling(self, start_row, start_col, end_row, end_col, piece_moved, piece_captured):
        #---------------------
        #キャスリング処理
        #---------------------
        if piece_moved == 'wK':
            if end_col - start_col == 2:
                self.board[end_row][end_col - 1] = self.board[end_row][end_col + 1] #rook
                self.board[end_row][end_col + 1] = '--' #もともとルークがいた場所
                self.castle_possible_wK = False
            elif end_col - start_col == -2:
                self.board[end_row][end_col + 1] = self.board[end_row][end_col - 2] #rook
                self.board[end_row][end_col - 2] = '--' #もともとルークがいた場所
                self.castle_possible_wQ = False
            
            self.castle_possible_white = False

        elif piece_moved == 'bK':
            if end_col - start_col == 2:
                self.board[end_row][end_col - 1] = self.board[end_row][end_col + 1] #rook
                self.board[end_row][end_col + 1] = '--' #もともとルークがいた場所
                self.castle_possible_bK = False
            elif end_col - start_col == -2:
                self.board[end_row][end_col + 1] = self.board[end_row][end_col - 2] #rook
                self.board[end_row][end_col - 2] = '--'
                self.castle_possible_bQ = False
            
            self.castle_possible_black = False

        #-----------------------------
        #キャスリングフラグに関する処理
        #-----------------------------

        #ルークが動いたらFalseにする
        if piece_moved == 'wR' and start_col == '7':
            self.castle_possible_wK = False
        elif piece_moved == 'wR' and start_col == '0':
            self.castle_possible_wQ = False
        elif piece_moved == 'bR' and start_col == '7':
            self.castle_possible_bK = False
        elif piece_moved == 'bR' and start_col == '0':
            self.castle_possible_bQ = False
        
        #ルークがCaptureされたらFalseにする
        if piece_captured == 'wR' and end_col == '7':
            self.castle_possible_wK = False
        elif piece_captured == 'wR' and end_col == '0':
            self.castle_possible_wQ = False
        elif piece_captured == 'bR' and end_col == '7':
            self.castle_possible_bK = False
        elif piece_captured == 'bR' and end_col == '0':
            self.castle_possible_bQ = False

    def get_enpassant_moves(self, moves):
        
        if len(self.moveLog) > 0:
            #----------------
            #最後の動きを抽出
            #----------------
            move = self.moveLog[-1]
            current_row = move[2]
            current_col = move[3]
            opp_row = current_row
            moved_piece = move[4]
            moved_square = abs(move[0] - move[2])
            if moved_piece[0] == 'w':
                new_piece = 'bP'
            else:
                new_piece = 'wP'


            #-----------------
            #アンパッサン処理
            #-----------------
            if moved_piece[1] == 'P':
                if moved_square == 2:
                    #最後に動いたコマが白ポーンの場合
                    if moved_piece == 'wP':
                        if current_col < 7:
                            #白から見て右側が黒ポーンの場合
                            if self.board[current_row][current_col + 1] == new_piece:
                                end_row = current_row + 1
                                end_col = current_col
                                opp_col = current_col + 1
                                move1 = (str(opp_row) + str(opp_col), str(end_row) + str(end_col))
                                moves.append(move1)

                        if current_col > 0:
                            #白から見て左側が黒ポーンの場合
                            if self.board[current_row][current_col - 1] == new_piece:
                                end_row = current_row + 1
                                end_col = current_col
                                opp_col = current_col - 1
                                move1 = (str(opp_row) + str(opp_col), str(end_row) + str(end_col))
                                moves.append(move1)

                    #最後に動いたコマが黒ポーンの場合
                    else:
                        if current_col < 7:
                            #黒から見て右側が黒ポーンの場合
                            if self.board[current_row][current_col + 1] == new_piece:
                                end_row = current_row - 1
                                end_col = current_col
                                opp_col = current_col + 1
                                move1 = (str(opp_row) + str(opp_col), str(end_row) + str(end_col))
                                moves.append(move1)

                        if current_col > 0:
                            #黒から見て左側が白ポーンの場合
                            if self.board[current_row][current_col - 1] == new_piece:
                                end_row = current_row - 1
                                end_col = current_col
                                opp_col = current_col - 1
                                move1 = (str(opp_row) + str(opp_col), str(end_row) + str(end_col))
                                moves.append(move1)
