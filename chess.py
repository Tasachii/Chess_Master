import pygame
from constants import *

pygame.init()

def draw_status_bar():
    status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                   'Black: Select a Piece to Move!', 'Black: Select a Destination!']
    pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
    pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
    screen.blit(big_font.render(status_text[turn_step], True, 'black'), (20, 820))


def draw_borders():
    pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)


def draw_grid_lines():
    for i in range(9):
        pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
        pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)


def draw_forfeit_button():
    screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))


def draw_promotion_message():
    if white_promote or black_promote:
        pygame.draw.rect(screen, 'gray', [0, 800, WIDTH - 200, 100])
        pygame.draw.rect(screen, 'gold', [0, 800, WIDTH - 200, 100], 5)
        screen.blit(big_font.render('Select Piece to Promote Pawn', True, 'black'), (20, 820))


def draw_board():
    for i in range(32):
        column = i % 4
        row = i // 4
        if row % 2 == 0:
            pygame.draw.rect(screen, 'light gray', [600 - (column * 200), row * 100, 100, 100])
        else:
            pygame.draw.rect(screen, 'light gray', [700 - (column * 200), row * 100, 100, 100])
    draw_status_bar()
    draw_borders()
    draw_grid_lines()
    draw_forfeit_button()
    draw_promotion_message()


def draw_pieces():
    # White Piece
    for i in range(len(white_pieces)):
        index = piece_list.index(white_pieces[i])
        if white_pieces[i] == 'pawn':
            screen.blit(white_pawn, (white_locations[i][0] * 100 + 22, white_locations[i][1] * 100 + 30))
        else:
            screen.blit(white_images[index], (white_locations[i][0] * 100 + 10, white_locations[i][1] * 100 + 10))
        if turn_step < 2 and selection == i:
            pygame.draw.rect(screen, 'red', [white_locations[i][0] * 100 + 1,
                                               white_locations[i][1] * 100 + 1, 100, 100], 2)
    # ฺBlack Piece
    for i in range(len(black_pieces)):
        index = piece_list.index(black_pieces[i])
        if black_pieces[i] == 'pawn':
            screen.blit(black_pawn, (black_locations[i][0] * 100 + 22, black_locations[i][1] * 100 + 30))
        else:
            screen.blit(black_images[index], (black_locations[i][0] * 100 + 10, black_locations[i][1] * 100 + 10))
        if turn_step >= 2 and selection == i:
            pygame.draw.rect(screen, 'blue', [black_locations[i][0] * 100 + 1,
                                                black_locations[i][1] * 100 + 1, 100, 100], 2)


def draw_valid(moves):
    color = 'red' if turn_step < 2 else 'blue'
    for move in moves:
        pygame.draw.circle(screen, color, (move[0] * 100 + 50, move[1] * 100 + 50), 5)


def draw_captured():
    for i in range(len(captured_pieces_white)):
        captured_piece = captured_pieces_white[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_black_images[index], (825, 5 + 50 * i))
    for i in range(len(captured_pieces_black)):
        captured_piece = captured_pieces_black[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_white_images[index], (925, 5 + 50 * i))


def draw_check():
    global check
    check = False
    if turn_step < 2 and 'king' in white_pieces:
        king_index = white_pieces.index('king')
        king_location = white_locations[king_index]
        for options in black_options:
            if king_location in options:
                check = True
                if counter < 15:
                    pygame.draw.rect(screen, 'dark red', [white_locations[king_index][0] * 100 + 1,
                                                             white_locations[king_index][1] * 100 + 1, 100, 100], 5)
    elif turn_step >= 2 and 'king' in black_pieces:
        king_index = black_pieces.index('king')
        king_location = black_locations[king_index]
        for options in white_options:
            if king_location in options:
                check = True
                if counter < 15:
                    pygame.draw.rect(screen, 'dark blue', [black_locations[king_index][0] * 100 + 1,
                                                             black_locations[king_index][1] * 100 + 1, 100, 100], 5)


def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
    screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render('Press ENTER to Restart!', True, 'white'), (210, 240))


# pawn promotion

def check_promotion():
    white_promotion = False
    black_promotion = False
    promote_index = 100
    for i in range(len(white_pieces)):
        if white_pieces[i] == 'pawn' and white_locations[i][1] == 7:
            white_promotion = True
            promote_index = i
    for i in range(len(black_pieces)):
        if black_pieces[i] == 'pawn' and black_locations[i][1] == 0:
            black_promotion = True
            promote_index = i
    return white_promotion, black_promotion, promote_index


def draw_promotion():
    pygame.draw.rect(screen, 'dark gray', [800, 0, 200, 420])
    if white_promote:
        color = 'white'
        for i in range(len(white_promotions)):
            piece = white_promotions[i]
            index = piece_list.index(piece)
            screen.blit(white_images[index], (860, 5 + 100 * i))
    elif black_promote:
        color = 'black'
        for i in range(len(black_promotions)):
            piece = black_promotions[i]
            index = piece_list.index(piece)
            screen.blit(black_images[index], (860, 5 + 100 * i))
    pygame.draw.rect(screen, color, [800, 0, 200, 420], 8)


def check_promo_select():
    mouse_pos = pygame.mouse.get_pos()
    left_click = pygame.mouse.get_pressed()[0]
    x_pos = mouse_pos[0] // 100
    y_pos = mouse_pos[1] // 100
    if (white_promote or black_promote) and left_click and x_pos > 7 and y_pos < 4:
        if white_promote:
            white_pieces[promo_index] = white_promotions[y_pos]
        elif black_promote:
            black_pieces[promo_index] = black_promotions[y_pos]

# ============ MOVE OPTION CHECK FUNCTIONS ============
# (สมมุติว่าโค้ดพื้นฐานเหล่านี้ได้ถูกจัดเตรียมไว้แล้ว)


def check_options(pieces, locations, turn):
    global castling_moves
    moves_list = []
    all_moves_list = []
    castling_moves = []
    for i in range(len(pieces)):
        location = locations[i]
        piece = pieces[i]
        if piece == 'pawn':
            moves_list = check_pawn(location, turn)
        elif piece == 'rook':
            moves_list = check_rook(location, turn)
        elif piece == 'knight':
            moves_list = check_knight(location, turn)
        elif piece == 'bishop':
            moves_list = check_bishop(location, turn)
        elif piece == 'queen':
            moves_list = check_queen(location, turn)
        elif piece == 'king':
            moves_list, castling_moves = check_king(location, turn)
        all_moves_list.append(moves_list)
    return all_moves_list


def check_king(position, color):
    moves_list = []
    castle_moves = check_castling()
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    targets = [(1, 0), (1, 1), (1, -1), (-1, 0),
               (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for target in targets:
        new_pos = (position[0] + target[0], position[1] + target[1])
        if new_pos not in friends_list and 0 <= new_pos[0] <= 7 and 0 <= new_pos[1] <= 7:
            moves_list.append(new_pos)
    return moves_list, castle_moves


def check_queen(position, color):
    moves_list = check_bishop(position, color)
    moves_list += check_rook(position, color)
    return moves_list


def check_bishop(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    directions = [(1, -1), (-1, -1), (1, 1), (-1, 1)]
    for d in directions:
        chain = 1
        while True:
            new_pos = (position[0] + d[0]*chain, position[1] + d[1]*chain)
            if new_pos not in friends_list and 0 <= new_pos[0] <= 7 and 0 <= new_pos[1] <= 7:
                moves_list.append(new_pos)
                if new_pos in enemies_list:
                    break
                chain += 1
            else:
                break
    return moves_list


def check_rook(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for d in directions:
        chain = 1
        while True:
            new_pos = (position[0] + d[0]*chain, position[1] + d[1]*chain)
            if new_pos not in friends_list and 0 <= new_pos[0] <= 7 and 0 <= new_pos[1] <= 7:
                moves_list.append(new_pos)
                if new_pos in enemies_list:
                    break
                chain += 1
            else:
                break
    return moves_list


def check_pawn(position, color):
    moves_list = []
    if color == 'white':
        if (position[0], position[1]+1) not in white_locations and (position[0], position[1]+1) not in black_locations and position[1] < 7:
            moves_list.append((position[0], position[1]+1))
            if (position[0], position[1]+2) not in white_locations and (position[0], position[1]+2) not in black_locations and position[1] == 1:
                moves_list.append((position[0], position[1]+2))
        if (position[0]+1, position[1]+1) in black_locations:
            moves_list.append((position[0]+1, position[1]+1))
        if (position[0]-1, position[1]+1) in black_locations:
            moves_list.append((position[0]-1, position[1]+1))
        if (position[0]+1, position[1]+1) == black_ep:
            moves_list.append((position[0]+1, position[1]+1))
        if (position[0]-1, position[1]+1) == black_ep:
            moves_list.append((position[0]-1, position[1]+1))
    else:
        if (position[0], position[1]-1) not in white_locations and (position[0], position[1]-1) not in black_locations and position[1] > 0:
            moves_list.append((position[0], position[1]-1))
            if (position[0], position[1]-2) not in white_locations and (position[0], position[1]-2) not in black_locations and position[1] == 6:
                moves_list.append((position[0], position[1]-2))
        if (position[0]+1, position[1]-1) in white_locations:
            moves_list.append((position[0]+1, position[1]-1))
        if (position[0]-1, position[1]-1) in white_locations:
            moves_list.append((position[0]-1, position[1]-1))
        if (position[0]+1, position[1]-1) == white_ep:
            moves_list.append((position[0]+1, position[1]-1))
        if (position[0]-1, position[1]-1) == white_ep:
            moves_list.append((position[0]-1, position[1]-1))
    return moves_list


def check_knight(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    targets = [(1, 2), (1, -2), (2, 1), (2, -1),
               (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for t in targets:
        new_pos = (position[0] + t[0], position[1] + t[1])
        if new_pos not in friends_list and 0 <= new_pos[0] <= 7 and 0 <= new_pos[1] <= 7:
            moves_list.append(new_pos)
    return moves_list


def check_castling():
    castle_moves = []
    rook_indexes = []
    rook_locations = []
    king_index = 0
    king_pos = (0, 0)
    if turn_step > 1:  # White turn
        for i in range(len(white_pieces)):
            if white_pieces[i] == 'rook':
                rook_indexes.append(white_moved[i])
                rook_locations.append(white_locations[i])
            if white_pieces[i] == 'king':
                king_index = i
                king_pos = white_locations[i]
        if not white_moved[king_index] and False in rook_indexes and not check:
            for i in range(len(rook_indexes)):
                castle = True
                if rook_locations[i][0] > king_pos[0]:
                    empty_squares = [(king_pos[0]+1, king_pos[1]),
                                     (king_pos[0]+2, king_pos[1]),
                                     (king_pos[0]+3, king_pos[1])]
                else:
                    empty_squares = [(king_pos[0]-1, king_pos[1]),
                                     (king_pos[0]-2, king_pos[1])]
                for square in empty_squares:
                    if square in white_locations or square in black_locations or square in black_options or rook_indexes[i]:
                        castle = False
                if castle:
                    castle_moves.append((empty_squares[1], empty_squares[0]))
    else:  # Black turn
        for i in range(len(black_pieces)):
            if black_pieces[i] == 'rook':
                rook_indexes.append(black_moved[i])
                rook_locations.append(black_locations[i])
            if black_pieces[i] == 'king':
                king_index = i
                king_pos = black_locations[i]
        if not black_moved[king_index] and False in rook_indexes and not check:
            for i in range(len(rook_indexes)):
                castle = True
                if rook_locations[i][0] > king_pos[0]:
                    empty_squares = [(king_pos[0]+1, king_pos[1]),
                                     (king_pos[0]+2, king_pos[1]),
                                     (king_pos[0]+3, king_pos[1])]
                else:
                    empty_squares = [(king_pos[0]-1, king_pos[1]),
                                     (king_pos[0]-2, king_pos[1])]
                for square in empty_squares:
                    if square in white_locations or square in black_locations or square in white_options or rook_indexes[i]:
                        castle = False
                if castle:
                    castle_moves.append((empty_squares[1], empty_squares[0]))
    return castle_moves


def draw_castling(moves):
    color = 'red' if turn_step < 2 else 'blue'
    for move in moves:
        pygame.draw.circle(screen, color, (move[0][0]*100+50, move[0][1]*100+70), 8)
        screen.blit(font.render('king', True, 'black'), (move[0][0]*100+30, move[0][1]*100+70))
        pygame.draw.circle(screen, color, (move[1][0]*100+50, move[1][1]*100+70), 8)
        screen.blit(font.render('rook', True, 'black'), (move[1][0]*100+30, move[1][1]*100+70))
        pygame.draw.line(screen, color, (move[0][0]*100+50, move[0][1]*100+70),
                         (move[1][0]*100+50, move[1][1]*100+70), 2)


# MAIN GAME
winner = ''
game_over = False
counter = 0
selection = 100
turn_step = 0
valid_moves = []
selected_piece = ''
white_ep = (100, 100)
black_ep = (100, 100)
white_promote = False
black_promote = False
promo_index = 100

# เรียกฟังก์ชันตรวจสอบตัวเลือกเริ่มต้น
black_options = check_options(black_pieces, black_locations, 'black')
white_options = check_options(white_pieces, white_locations, 'white')

run = True
while run:
    timer.tick(fps)
    if counter < 30:
        counter += 1
    else:
        counter = 0

    screen.fill('dark gray')
    draw_board()
    draw_pieces()
    draw_captured()
    draw_check()


    white_promote, black_promote, promo_index = check_promotion()
    if white_promote or black_promote:
        draw_promotion()
        check_promo_select()

    if selection != 100:
        valid_moves = check_valid_moves()  # สมมุติว่ามีฟังก์ชัน check_valid_moves() ให้เลือกเมื่อนิ้วถูกเลือก
        draw_valid(valid_moves)
        if selected_piece == 'king':
            draw_castling(castling_moves)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            x_coord = event.pos[0] // 100
            y_coord = event.pos[1] // 100
            click_coords = (x_coord, y_coord)
            if turn_step <= 1:  # จัดการสำหรับฝั่งขาว
                if click_coords in [(8, 8), (9, 8)]:
                    winner = 'black'
                if click_coords in white_locations:
                    selection = white_locations.index(click_coords)
                    selected_piece = white_pieces[selection]
                    if turn_step == 0:
                        turn_step = 1
                if click_coords in valid_moves and selection != 100:
                    white_ep = check_ep(white_locations[selection], click_coords)
                    white_locations[selection] = click_coords
                    white_moved[selection] = True
                    if click_coords in black_locations:
                        black_piece = black_locations.index(click_coords)
                        captured_pieces_white.append(black_pieces[black_piece])
                        if black_pieces[black_piece] == 'king':
                            winner = 'white'
                        black_pieces.pop(black_piece)
                        black_locations.pop(black_piece)
                        black_moved.pop(black_piece)
                    if click_coords == black_ep:
                        black_piece = black_locations.index((black_ep[0], black_ep[1]-1))
                        captured_pieces_white.append(black_pieces[black_piece])
                        black_pieces.pop(black_piece)
                        black_locations.pop(black_piece)
                        black_moved.pop(black_piece)
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 2
                    selection = 100
                    valid_moves = []
                elif selection != 100 and selected_piece == 'king':
                    for move in castling_moves:
                        if click_coords == move[0]:
                            white_locations[selection] = click_coords
                            white_moved[selection] = True
                            rook_coords = (0, 0) if click_coords == (1, 0) else (7, 0)
                            rook_index = white_locations.index(rook_coords)
                            white_locations[rook_index] = move[1]
                            black_options = check_options(black_pieces, black_locations, 'black')
                            white_options = check_options(white_pieces, white_locations, 'white')
                            turn_step = 2
                            selection = 100
                            valid_moves = []
            elif turn_step > 1:  # จัดการสำหรับฝั่งดำ
                if click_coords in [(8, 8), (9, 8)]:
                    winner = 'white'
                if click_coords in black_locations:
                    selection = black_locations.index(click_coords)
                    selected_piece = black_pieces[selection]
                    if turn_step == 2:
                        turn_step = 3
                if click_coords in valid_moves and selection != 100:
                    black_ep = check_ep(black_locations[selection], click_coords)
                    black_locations[selection] = click_coords
                    black_moved[selection] = True
                    if click_coords in white_locations:
                        white_piece = white_locations.index(click_coords)
                        captured_pieces_black.append(white_pieces[white_piece])
                        if white_pieces[white_piece] == 'king':
                            winner = 'black'
                        white_pieces.pop(white_piece)
                        white_locations.pop(white_piece)
                        white_moved.pop(white_piece)
                    if click_coords == white_ep:
                        white_piece = white_locations.index((white_ep[0], white_ep[1]+1))
                        captured_pieces_black.append(white_pieces[white_piece])
                        white_pieces.pop(white_piece)
                        white_locations.pop(white_piece)
                        white_moved.pop(white_piece)
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 0
                    selection = 100
                    valid_moves = []
                elif selection != 100 and selected_piece == 'king':
                    for move in castling_moves:
                        if click_coords == move[0]:
                            black_locations[selection] = click_coords
                            black_moved[selection] = True
                            rook_coords = (0, 7) if click_coords == (1, 7) else (7, 7)
                            rook_index = black_locations.index(rook_coords)
                            black_locations[rook_index] = move[1]
                            black_options = check_options(black_pieces, black_locations, 'black')
                            white_options = check_options(white_pieces, white_locations, 'white')
                            turn_step = 0
                            selection = 100
                            valid_moves = []

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                game_over = False
                winner = ''
                white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
                white_moved = [False] * 16
                black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
                black_moved = [False] * 16
                captured_pieces_white = []
                captured_pieces_black = []
                turn_step = 0
                selection = 100
                valid_moves = []
                black_options = check_options(black_pieces, black_locations, 'black')
                white_options = check_options(white_pieces, white_locations, 'white')

    if winner != '':
        game_over = True
        draw_game_over()

    pygame.display.flip()
pygame.quit()
