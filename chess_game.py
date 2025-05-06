# chess_game.py
import pygame
from constants import *
from chess_project.Chess_Project.chess_board import ChessBoard
from chess_piece import ChessPiece


class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption('Time to Chess')
        self.clock = pygame.time.Clock()
        self.board = ChessBoard(self.screen)
        self.turn_step = 0  # 0-white select, 1-white move, 2-black select, 3-black move
        self.selection = 100  # Selected piece index
        self.valid_moves = []
        self.castling_moves = []
        self.counter = 0  # For animations
        self.check = False
        self.winner = ''
        self.game_over = False
        self.white_promote = False
        self.black_promote = False
        self.promo_index = 100
        self.board_flipped = False  # False = white at bottom, True = black at bottom
        self.last_flip_time = 0  # Prevents rapid consecutive button presses

        # Game state
        self.game_state = MENU  # Start with menu screen

        # Board will be initialized after choosing a side

    def run(self):
        run = True
        while run:
            self.clock.tick(FPS)

            # Update counter for animations
            if self.counter < 30:
                self.counter += 1
            else:
                self.counter = 0

            # Handle game based on current state
            if self.game_state == MENU:
                self.handle_menu()
            elif self.game_state == PLAYING:
                self.handle_gameplay()

            pygame.display.flip()

        pygame.quit()

    def handle_menu(self):
        # Draw side selection menu
        white_button, black_button = self.board.draw_menu()

        # Check for mouse clicks on buttons
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if white_button.collidepoint(mouse_pos):
                    # Play as white - white pieces at bottom
                    self.board.set_playing_side(True)
                    self.board_flipped = False  # White at bottom
                    self.start_game()

                elif black_button.collidepoint(mouse_pos):
                    # Play as black - black pieces at bottom
                    self.board.set_playing_side(False)
                    self.board_flipped = True  # Black at bottom
                    self.start_game()

                    # White always moves first
                    self.turn_step = 0

        return True

    def start_game(self):
        self.game_state = PLAYING
        self.turn_step = 0
        self.selection = 100
        self.valid_moves = []
        self.castling_moves = []
        self.counter = 0
        self.check = False
        self.winner = ''
        self.game_over = False
        self.white_promote = False
        self.black_promote = False
        self.promo_index = 100
        self.board.setup_board()

    def handle_gameplay(self):
        # Check for F key press (board flip)
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        if keys[pygame.K_f] and current_time - self.last_flip_time > 300:  # Debounce key press
            self.board_flipped = not self.board_flipped  # Toggle board orientation
            print(f"Board flipped: {self.board_flipped}")
            self.last_flip_time = current_time

        # Draw everything
        self.screen.fill(DARK_GRAY)
        self.board.draw_board(self.board_flipped)
        self.board.draw_status_area(self.turn_step)
        self.board.draw_pieces(self.turn_step, self.selection, self.board_flipped)
        self.board.draw_captured()
        self.check = self.board.draw_check(self.counter, self.board_flipped)

        # Handle promotion
        if not self.game_over:
            self.check_promotion()
            if self.white_promote:
                self.board.draw_promotion(WHITE, self.turn_step)
                self.check_promotion_selection()
            elif self.black_promote:
                self.board.draw_promotion(BLACK, self.turn_step)
                self.check_promotion_selection()

        # Draw valid moves for selected piece - only when in selection phase
        if self.selection != 100 and (self.turn_step == 1 or self.turn_step == 3):
            self.draw_valid_moves()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.game_over:
                if not self.white_promote and not self.black_promote:
                    self.handle_mouse_click(event.pos)
                else:
                    self.handle_promotion_click(event.pos)

            if event.type == pygame.KEYDOWN:
                # Handle one-time key presses
                if event.key == pygame.K_r:
                    # Return to side selection menu
                    self.game_state = MENU
                elif event.key == pygame.K_f:
                    # F key already handled above for continuous presses
                    pass
                elif self.game_over and event.key == pygame.K_RETURN:
                    self.reset_game()

        # Check for checkmate
        if not self.game_over and self.check:
            if self.turn_step < 2 and self.board.is_checkmate(WHITE):
                self.winner = BLACK
                self.game_over = True
            elif self.turn_step >= 2 and self.board.is_checkmate(BLACK):
                self.winner = WHITE
                self.game_over = True

        # Show game over screen if needed
        if self.winner:
            self.draw_game_over()

        return True

    def handle_mouse_click(self, pos):
        x_coord = pos[0] // 100
        y_coord = pos[1] // 100

        # Convert coordinates based on board orientation
        if self.board_flipped and y_coord < 8:  # Only convert chess board coordinates, not UI
            y_coord = 7 - y_coord

        click_coords = (x_coord, y_coord)

        # Check forfeit button
        if click_coords == (8, 8) or click_coords == (9, 8):
            self.winner = BLACK if self.turn_step <= 1 else WHITE
            self.game_over = True
            return

        # Handle white's turn
        if self.turn_step <= 1:
            # Select piece
            if self.turn_step == 0:
                for i, piece in enumerate(self.board.white_pieces):
                    if piece.position == click_coords:
                        self.selection = i
                        self.turn_step = 1
                        self.get_valid_moves()
                        break
            else:
                # Get the selected piece first
                if self.selection != 100 and 0 <= self.selection < len(self.board.white_pieces):
                    piece = self.board.white_pieces[self.selection]

                    # Move selected piece
                    if click_coords in self.valid_moves:
                        self.move_piece(piece, click_coords)
                        self.turn_step = 2
                        self.selection = 100
                        self.valid_moves = []

                    # Handle castling
                    elif piece.piece_type == 'king':
                        for king_pos, rook_pos in self.castling_moves:
                            if click_coords == king_pos:
                                # Find rook to castle with
                                if king_pos[0] > piece.position[0]:  # Kingside
                                    rook = next((p for p in self.board.white_pieces if
                                                 p.piece_type == 'rook' and p.position[0] > piece.position[0]), None)
                                else:  # Queenside
                                    rook = next((p for p in self.board.white_pieces if
                                                 p.piece_type == 'rook' and p.position[0] < piece.position[0]), None)

                                if rook:
                                    # Move king to castling position
                                    piece.move(king_pos)
                                    # Move rook to castling position
                                    rook.move(rook_pos)

                                self.turn_step = 2
                                self.selection = 100
                                self.valid_moves = []
                                self.castling_moves = []

                # Cancel selection if clicking on another white piece
                if any(p.position == click_coords for p in self.board.white_pieces):
                    for i, piece in enumerate(self.board.white_pieces):
                        if piece.position == click_coords:
                            self.selection = i
                            self.get_valid_moves()
                            break

        # Handle black's turn (similar logic)
        else:
            # Select piece
            if self.turn_step == 2:
                for i, piece in enumerate(self.board.black_pieces):
                    if piece.position == click_coords:
                        self.selection = i
                        self.turn_step = 3
                        self.get_valid_moves()
                        break
            else:
                # Get the selected piece first
                if self.selection != 100 and 0 <= self.selection < len(self.board.black_pieces):
                    piece = self.board.black_pieces[self.selection]

                    # Move selected piece
                    if click_coords in self.valid_moves:
                        self.move_piece(piece, click_coords)
                        self.turn_step = 0
                        self.selection = 100
                        self.valid_moves = []

                    # Handle castling
                    elif piece.piece_type == 'king':
                        for king_pos, rook_pos in self.castling_moves:
                            if click_coords == king_pos:
                                # Find rook to castle with
                                if king_pos[0] > piece.position[0]:  # Kingside
                                    rook = next((p for p in self.board.black_pieces if
                                                 p.piece_type == 'rook' and p.position[0] > piece.position[0]), None)
                                else:  # Queenside
                                    rook = next((p for p in self.board.black_pieces if
                                                 p.piece_type == 'rook' and p.position[0] < piece.position[0]), None)

                                if rook:
                                    # Move king to castling position
                                    piece.move(king_pos)
                                    # Move rook to castling position
                                    rook.move(rook_pos)

                                self.turn_step = 0
                                self.selection = 100
                                self.valid_moves = []
                                self.castling_moves = []

                # Cancel selection if clicking on another black piece
                if any(p.position == click_coords for p in self.board.black_pieces):
                    for i, piece in enumerate(self.board.black_pieces):
                        if piece.position == click_coords:
                            self.selection = i
                            self.get_valid_moves()
                            break

    def get_valid_moves(self):
        self.valid_moves = []
        self.castling_moves = []

        # Fixed index out of range bug
        if self.turn_step <= 1:
            # Ensure selection is valid before accessing piece
            if 0 <= self.selection < len(self.board.white_pieces):
                piece = self.board.white_pieces[self.selection]
                self.valid_moves = piece.get_valid_moves()

                # Get castling moves if king is selected
                if piece.piece_type == 'king':
                    self.castling_moves = self.board.check_castling(piece.color)
        else:
            # Ensure selection is valid before accessing piece
            if 0 <= self.selection < len(self.board.black_pieces):
                piece = self.board.black_pieces[self.selection]
                self.valid_moves = piece.get_valid_moves()

                # Get castling moves if king is selected
                if piece.piece_type == 'king':
                    self.castling_moves = self.board.check_castling(piece.color)

    def move_piece(self, piece, new_position):
        # Check for en passant capture
        if piece.piece_type == 'pawn':
            if piece.color == WHITE and new_position == self.board.black_ep:
                # Capture black pawn that moved two squares
                captured_pos = (new_position[0], new_position[1] - 1)
                captured_piece = self.board.get_piece_at_position(captured_pos)
                if captured_piece:
                    self.board.black_pieces.remove(captured_piece)
                    self.board.captured_black.append(captured_piece)
            elif piece.color == BLACK and new_position == self.board.white_ep:
                # Capture white pawn that moved two squares
                captured_pos = (new_position[0], new_position[1] + 1)
                captured_piece = self.board.get_piece_at_position(captured_pos)
                if captured_piece:
                    self.board.white_pieces.remove(captured_piece)
                    self.board.captured_white.append(captured_piece)

        # Update en passant square
        if piece.piece_type == 'pawn' and abs(piece.position[1] - new_position[1]) == 2:
            # Set en passant square after pawn moves two squares
            middle_y = (piece.position[1] + new_position[1]) // 2
            if piece.color == WHITE:
                self.board.white_ep = (new_position[0], middle_y)
            else:
                self.board.black_ep = (new_position[0], middle_y)
        else:
            # Reset en passant squares
            if piece.color == WHITE:
                self.board.white_ep = (100, 100)
            else:
                self.board.black_ep = (100, 100)

        # Handle capturing
        captured_piece = self.board.get_piece_at_position(new_position)
        if captured_piece:
            if captured_piece.color == WHITE:
                self.board.white_pieces.remove(captured_piece)
                self.board.captured_white.append(captured_piece)
            else:
                self.board.black_pieces.remove(captured_piece)
                self.board.captured_black.append(captured_piece)

        # Move the piece
        piece.move(new_position)

        # Check for checkmate after move
        opponent_color = BLACK if piece.color == WHITE else WHITE
        if self.board.is_checkmate(opponent_color):
            self.winner = WHITE if piece.color == WHITE else BLACK
            self.game_over = True

    def check_promotion(self):
        # Check for pawn promotion
        self.white_promote = False
        self.black_promote = False

        for i, piece in enumerate(self.board.white_pieces):
            if piece.piece_type == 'pawn' and piece.position[1] == 7:
                self.white_promote = True
                self.promo_index = i
                break

        for i, piece in enumerate(self.board.black_pieces):
            if piece.piece_type == 'pawn' and piece.position[1] == 0:
                self.black_promote = True
                self.promo_index = i
                break

    def handle_promotion_click(self, pos):
        x_coord = pos[0] // 100
        y_coord = pos[1] // 100

        # Check if click is in promotion area
        if x_coord >= 8 and y_coord < 4:
            promotion_piece = PROMOTION_PIECES[y_coord]

            if self.white_promote:
                # Get pawn position
                pawn = self.board.white_pieces[self.promo_index]
                pawn_pos = pawn.position

                # Replace pawn with new piece
                self.board.white_pieces.pop(self.promo_index)
                self.board.white_pieces.append(ChessPiece(promotion_piece, WHITE, pawn_pos, self.board))

                self.white_promote = False

                # Check for checkmate after promotion
                if self.board.is_checkmate(BLACK):
                    self.winner = WHITE
                    self.game_over = True

            elif self.black_promote:
                # Get pawn position
                pawn = self.board.black_pieces[self.promo_index]
                pawn_pos = pawn.position

                # Replace pawn with new piece
                self.board.black_pieces.pop(self.promo_index)
                self.board.black_pieces.append(ChessPiece(promotion_piece, BLACK, pawn_pos, self.board))

                self.black_promote = False

                # Check for checkmate after promotion
                if self.board.is_checkmate(WHITE):
                    self.winner = BLACK
                    self.game_over = True

    def check_promotion_selection(self):
        # Check if user has selected a promotion piece
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]

        if left_click:
            x_pos = mouse_pos[0] // 100
            y_pos = mouse_pos[1] // 100

            if x_pos > 7 and y_pos < 4:
                self.handle_promotion_click(mouse_pos)

    def draw_valid_moves(self):
        # Draw valid moves for selected piece
        self.board.draw_valid_moves(self.valid_moves, self.turn_step, self.board_flipped)

        # Draw castling moves if applicable
        if self.castling_moves:
            self.board.draw_castling(self.castling_moves, self.turn_step, self.board_flipped)

    def draw_game_over(self):
        pygame.draw.rect(self.screen, 'black', [200, 200, 400, 70])
        if self.winner == WHITE:
            self.screen.blit(self.board.font.render('White won by checkmate!', True, 'white'), (210, 210))
        else:
            self.screen.blit(self.board.font.render('Black won by checkmate!', True, 'white'), (210, 210))
        self.screen.blit(self.board.font.render('Press ENTER to Restart!', True, 'white'), (210, 240))
        self.game_over = True

    def reset_game(self):
        # Reset the game state but keep the same side
        playing_as_white = self.board.playing_as_white
        self.board = ChessBoard(self.screen)
        self.board.playing_as_white = playing_as_white
        self.board.setup_board()

        self.turn_step = 0
        self.selection = 100
        self.valid_moves = []
        self.castling_moves = []
        self.counter = 0
        self.check = False
        self.winner = ''
        self.game_over = False
        self.white_promote = False
        self.black_promote = False
        self.promo_index = 100

        # Maintain board orientation based on playing side
        # If playing as white, keep white at bottom (board_flipped=False)
        # If playing as black, keep black at bottom (board_flipped=True)
        self.board_flipped = not playing_as_white