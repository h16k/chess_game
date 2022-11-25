import pygame as p
import chess_engine

#Pygameに関する設定
BOARD_WIDTH = BOARD_HEIGHT = 640
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 30
#コマ
IMAGES = {}
#ボードの色
COLORS = ["#FFF5E1", "#855E42"]

def main():
    #Pygameに関する設定
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    #コマの読み込み
    load_images()
    #chess_engineのクラスの読み込み
    gs = chess_engine.Game_Status()
    valid_moves = gs.get_valid_moves()

    flg_running = True
    flg_resigne = False
    flg_gameover = False



    player_click = []
    square_clicked = ''


    while flg_running:
        for e in p.event.get():   
            if e.type == p.QUIT:
                flg_running = False
            
            elif e.type == p.KEYDOWN:
                #Z : やり直し
                if e.key == p.K_z:
                    gs.undo_move()
                    valid_moves = gs.get_valid_moves()
                    flg_resigne = False
                    flg_gameover = False
                # Q : end
                elif e.key == p.K_q:
                    flg_running = False
                
                # R : reset
                elif e.key == p.K_r:
                    gs = chess_engine.Game_Status()
                    valid_moves = gs.get_valid_moves()
                    player_click = []
                    square_clicked = ''
                    flg_running = True
                    flg_resigne = False
                    flg_gameover = False

                # X : 投了
                elif e.key == p.K_x:
                    flg_resigne = True
                    flg_gameover = True


            elif e.type == p.MOUSEBUTTONDOWN:
                if not flg_gameover:
                    #クリックした場所の把握
                    location = p.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    # print(location[0], location[1], col, row)

                #同じ場所を２回クリックしたらキャンセル扱い
                if square_clicked == str(row) + str(col):
                    square_clicked = ''
                    player_click = []
                    valid_moves = gs.get_valid_moves()

                #空欄を最初にクリックした場合も無効
                elif len(player_click) == 0 and gs.board[row][col] == '--':
                    square_clicked = ''
                    player_click = []
                elif len(player_click) == 0 and gs.board[row][col][0] == 'b' and gs.white_to_move:
                    square_clicked = ''
                    player_click = []
                elif len(player_click) == 0 and gs.board[row][col][0] == 'w' and not gs.white_to_move:
                    square_clicked = ''
                    player_click = []

                else:    
                    square_clicked = str(row) + str(col)
                    player_click.append(square_clicked)
                    print('player_click = ', player_click)

                if len(player_click) == 2:
                    if gs.check_valid_move(player_click[0], player_click[1], valid_moves):
                        gs.make_move(player_click[0], player_click[1])
                        square_clicked = ''
                        player_click = []
                        valid_moves = gs.get_valid_moves()
                    else:
                        player_click = [square_clicked]




        #ボードとコマの描画
        draw_game_status(screen, gs, valid_moves, square_clicked) 

        #終了メッセージをボード上に表示
        if gs.checkMate or gs.staleMate or gs.drawGame or flg_resigne:
            flg_gameover = True
            if gs.staleMate:
                text = 'Stalemate'
            elif gs.checkMate:
                if gs.white_to_move:
                    text = 'Player2 Win'
                else:
                    text = 'Player1 Win'
            elif flg_resigne:
                text = 'surrender'
            else:
                text = 'Draw'
            draw_message(screen, text)
        
        #Pygameに関する設定
        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_status(screen, gs, valid_moves, square_clicked):
    draw_board(screen)
    draw_pieces(screen, gs.board)
    draw_squares_color(screen, gs, valid_moves, square_clicked)


def draw_board(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = COLORS[((r+c) % 2)]
            p.draw.rect(screen,color,p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_squares_color(screen, gs, valid_moves, square_clicked):
    if square_clicked != '':
        row = int(square_clicked[0])
        col = int(square_clicked[1])

        if (gs.board[row][col][0] == 'w' and gs.white_to_move) or (gs.board[row][col][0] == 'b' and not gs.white_to_move):
            #クリックしたマス   
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(150) #0:透明　255:不透明
            s.fill(p.Color('red'))
            screen.blit(s,(col * SQUARE_SIZE, row * SQUARE_SIZE))
            #移動可能なマス
            s.fill(p.Color('orange'))
            for move in valid_moves:
                if move[0] == square_clicked:
                    col_highlight = int(move[1][1])
                    row_highlight = int(move[1][0])
                    screen.blit(s,(col_highlight * SQUARE_SIZE, row_highlight * SQUARE_SIZE))

def draw_message(screen, text):
    font_path = f'C:/Windows/Fonts/meiryo.ttc'
    font = p.font.Font(font_path, 50)
    textObject = font.render(text, 0, p.Color('Red'))
    x_length = BOARD_WIDTH/2 - textObject.get_width()/2
    y_height = BOARD_HEIGHT/2 - textObject.get_height()/2
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(x_length, y_height)
    screen.blit(textObject, textLocation)

def load_images():
    pieces = ['wP','wR','wN','wB','wK','wQ','bP','bR','bN','bB','bK','bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/'+ piece + '.png'),(SQUARE_SIZE, SQUARE_SIZE))





if __name__ == '__main__':
    main()

