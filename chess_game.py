# chess_game.py
import pygame
import math
import os
from constants import *
from chess_board import ChessBoard
from chess_piece import ChessPiece


class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption('Chess Master')
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

        # Initialize sounds if available
        self.init_sounds()

        # FIXME: Need to implement proper AI opponent later

    def init_sounds(self):
        # Initialize pygame mixer
        pygame.mixer.init()

        # Set default empty sounds
        self.move_sound = None
        self.capture_sound = None
        self.check_sound = None
        self.promote_sound = None
        self.game_start_sound = None
        self.game_end_sound = None

        # Create sounds directory if it doesn't exist
        os.makedirs("sounds", exist_ok=True)

        # Try to load sounds if they exist
        try:
            if os.path.exists("sounds/move.wav"):
                self.move_sound = pygame.mixer.Sound('sounds/move.wav')
                self.move_sound.set_volume(0.5)

            if os.path.exists("sounds/capture.wav"):
                self.capture_sound = pygame.mixer.Sound('sounds/capture.wav')
                self.capture_sound.set_volume(0.6)

            if os.path.exists("sounds/check.wav"):
                self.check_sound = pygame.mixer.Sound('sounds/check.wav')
                self.check_sound.set_volume(0.7)

            if os.path.exists("sounds/promote.wav"):
                self.promote_sound = pygame.mixer.Sound('sounds/promote.wav')
                self.promote_sound.set_volume(0.6)

            if os.path.exists("sounds/game_start.wav"):
                self.game_start_sound = pygame.mixer.Sound('sounds/game_start.wav')
                self.game_start_sound.set_volume(0.5)

            if os.path.exists("sounds/game_end.wav"):
                self.game_end_sound = pygame.mixer.Sound('sounds/game_end.wav')
                self.game_end_sound.set_volume(0.7)
        except FileNotFoundError as e:
            print(f"Warning: Sound file not found: {e.filename}. Game will continue without sounds.")
        except Exception:
            print("Warning: Some sound files couldn't be loaded. Game will continue without sounds.")

    def play_sound(self, sound_obj):
        if sound_obj:
            try:
                sound_obj.play()
            except:
                pass  # Continue without sound if there's an error

    def run(self):
        game_running = True  # More descriptive than just 'run'
        while game_running:
            self.clock.tick(FPS)

            # Update counter for animations
            if self.counter < 30:
                self.counter += 1
            else:
                self.counter = 0

            # Handle game based on current state
            if self.game_state == MENU:
                game_running = self.handle_menu()
            elif self.game_state == PLAYING:
                game_running = self.handle_gameplay()

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
                    # Set to play as white
                    self.board.set_playing_side(True)
                    # White pieces at bottom (not flipped)
                    self.board_flipped = False
                    self.start_game()

                elif black_button.collidepoint(mouse_pos):
                    # Set to play as black
                    self.board.set_playing_side(False)
                    # Black pieces at bottom (flipped)
                    self.board_flipped = True
                    self.start_game()

        return True

    def start_game(self):
        self.game_state = PLAYING
        # Chess rule: White always moves first
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

        # Play game start sound
        self.play_sound(self.game_start_sound)

    def handle_gameplay(self):
        try:
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

            # Check for check condition and draw indicator
            previous_check = self.check
            self.check = self.board.draw_check(self.counter, self.board_flipped)

            # Play check sound if just entered check
            if not previous_check and self.check:
                self.play_sound(self.check_sound)

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
                    self.play_sound(self.game_end_sound)
                elif self.turn_step >= 2 and self.board.is_checkmate(BLACK):
                    self.winner = WHITE
                    self.game_over = True
                    self.play_sound(self.game_end_sound)

            # Show game over screen if needed
            if self.winner:
                self.draw_game_over()
        except Exception as e:
            print(f"Error in gameplay: {e.__class__.__name__}: {e}")

        return True

    def handle_mouse_click(self, pos):
        # Calculate board position from screen coordinates
        square_size = self.board.square_size
        start_pos = self.board.start_pos

        # Check if click is on the board
        if pos[0] >= start_pos and pos[0] < start_pos + square_size * 8 and \
                pos[1] >= start_pos and pos[1] < start_pos + square_size * 8:
            # Convert screen position to board coordinates
            x_coord = (pos[0] - start_pos) // square_size
            y_coord = (pos[1] - start_pos) // square_size

            # Convert coordinates based on board orientation
            if self.board_flipped:
                y_coord = 7 - y_coord
        else:
            # Click is outside the board
            # Check forfeit button
            forfeit_rect = pygame.Rect(850, 830, 220, 50)
            if forfeit_rect.collidepoint(pos):
                self.winner = BLACK if self.turn_step <= 1 else WHITE
                self.game_over = True
                self.play_sound(self.game_end_sound)
            return

        click_coords = (x_coord, y_coord)

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
                        # Verify king won't be in check after move
                        if self.is_move_safe_for_king(piece, click_coords, WHITE):
                            self.move_piece(piece, click_coords)
                            self.turn_step = 2
                            self.selection = 100
                            self.valid_moves = []
                        else:
                            # Warning: move would put king in check
                            print("Cannot move: King would be in check")

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

                                    # Play move sound
                                    self.play_sound(self.move_sound)

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
                        # Verify king won't be in check after move
                        if self.is_move_safe_for_king(piece, click_coords, BLACK):
                            self.move_piece(piece, click_coords)
                            self.turn_step = 0
                            self.selection = 100
                            self.valid_moves = []
                        else:
                            # Warning: move would put king in check
                            print("Cannot move: King would be in check")

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

                                    # Play move sound
                                    self.play_sound(self.move_sound)

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

    def is_move_safe_for_king(self, piece, new_position, color):
        """Check if move keeps king safe from check"""
        # Store original position and potentially captured piece
        original_position = piece.position
        captured_piece = self.board.get_piece_at_position(new_position)
        captured_white = None
        captured_black = None

        # Simulate piece capture
        if captured_piece:
            if captured_piece.color == WHITE:
                self.board.white_pieces.remove(captured_piece)
                captured_white = captured_piece
            else:
                self.board.black_pieces.remove(captured_piece)
                captured_black = captured_piece

        # Move piece to new position
        piece.position = new_position

        # Check if king is still safe
        king_safe = not self.board.is_king_in_check(color)

        # Restore original board state
        piece.position = original_position

        # Return any captured pieces
        if captured_white:
            self.board.white_pieces.append(captured_white)
        if captured_black:
            self.board.black_pieces.append(captured_black)

        return king_safe

    def get_valid_moves(self):
        self.valid_moves = []
        self.castling_moves = []

        # Fixed index out of range bug
        if self.turn_step <= 1:
            # Ensure selection is valid before accessing piece
            if 0 <= self.selection < len(self.board.white_pieces):
                piece = self.board.white_pieces[self.selection]
                all_possible_moves = piece.get_valid_moves()

                # Filter moves that would leave king in check
                for move in all_possible_moves:
                    if self.is_move_safe_for_king(piece, move, WHITE):
                        self.valid_moves.append(move)

                # Get castling moves if king is selected
                if piece.piece_type == 'king':
                    self.castling_moves = self.board.check_castling(piece.color)
        else:
            # Ensure selection is valid before accessing piece
            if 0 <= self.selection < len(self.board.black_pieces):
                piece = self.board.black_pieces[self.selection]
                all_possible_moves = piece.get_valid_moves()

                # Filter moves that would leave king in check
                for move in all_possible_moves:
                    if self.is_move_safe_for_king(piece, move, BLACK):
                        self.valid_moves.append(move)

                # Get castling moves if king is selected
                if piece.piece_type == 'king':
                    self.castling_moves = self.board.check_castling(piece.color)

    def move_piece(self, piece, new_position):
        # Flag to track if a capture occurs
        capture_occurred = False

        # Check for en passant capture
        if piece.piece_type == 'pawn':
            if piece.color == WHITE and new_position == self.board.black_ep:
                # Capture black pawn that moved two squares
                captured_pos = (new_position[0], new_position[1] - 1)
                captured_piece = self.board.get_piece_at_position(captured_pos)
                if captured_piece:
                    self.board.black_pieces.remove(captured_piece)
                    self.board.captured_black.append(captured_piece)
                    capture_occurred = True
            elif piece.color == BLACK and new_position == self.board.white_ep:
                # Capture white pawn that moved two squares
                captured_pos = (new_position[0], new_position[1] + 1)
                captured_piece = self.board.get_piece_at_position(captured_pos)
                if captured_piece:
                    self.board.white_pieces.remove(captured_piece)
                    self.board.captured_white.append(captured_piece)
                    capture_occurred = True

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
            # Verify not capturing a king (rule #1 - kings cannot be captured)
            if captured_piece.piece_type == 'king':
                print("Error: Cannot capture a king")
                return False

            if captured_piece.color == WHITE:
                self.board.white_pieces.remove(captured_piece)
                self.board.captured_white.append(captured_piece)
            else:
                self.board.black_pieces.remove(captured_piece)
                self.board.captured_black.append(captured_piece)
            capture_occurred = True

        # Move the piece
        piece.move(new_position)

        # Play appropriate sound
        if capture_occurred:
            self.play_sound(self.capture_sound)
        else:
            self.play_sound(self.move_sound)

        # Check for checkmate after move
        opponent_color = BLACK if piece.color == WHITE else WHITE
        if self.board.is_checkmate(opponent_color):
            self.winner = WHITE if piece.color == WHITE else BLACK
            self.game_over = True
            self.play_sound(self.game_end_sound)

        return True

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
        # Calculate which promotion option was clicked
        panel_rect = pygame.Rect(850, 200, 300, 450)

        # Check if click is in promotion area
        if not panel_rect.collidepoint(pos):
            return

        # Calculate which option was clicked
        option_height = 90
        option_index = (pos[1] - (panel_rect.y + 80)) // option_height

        # Validate option index
        if option_index < 0 or option_index >= len(PROMOTION_PIECES):
            return

        promotion_piece = PROMOTION_PIECES[option_index]

        if self.white_promote:
            # Get pawn position
            pawn = self.board.white_pieces[self.promo_index]
            pawn_pos = pawn.position

            # Replace pawn with new piece
            self.board.white_pieces.pop(self.promo_index)
            self.board.white_pieces.append(ChessPiece(promotion_piece, WHITE, pawn_pos, self.board))

            self.white_promote = False

            # Play promotion sound
            self.play_sound(self.promote_sound)

            # Check for checkmate after promotion
            if self.board.is_checkmate(BLACK):
                self.winner = WHITE
                self.game_over = True
                self.play_sound(self.game_end_sound)

        elif self.black_promote:
            # Get pawn position
            pawn = self.board.black_pieces[self.promo_index]
            pawn_pos = pawn.position

            # Replace pawn with new piece
            self.board.black_pieces.pop(self.promo_index)
            self.board.black_pieces.append(ChessPiece(promotion_piece, BLACK, pawn_pos, self.board))

            self.black_promote = False

            # Play promotion sound
            self.play_sound(self.promote_sound)

            # Check for checkmate after promotion
            if self.board.is_checkmate(WHITE):
                self.winner = BLACK
                self.game_over = True
                self.play_sound(self.game_end_sound)

    def check_promotion_selection(self):
        # Track mouse hover for promotion options
        mouse_pos = pygame.mouse.get_pos()
        panel_rect = pygame.Rect(850, 200, 300, 450)

        # Check if mouse is in promotion area
        if panel_rect.collidepoint(mouse_pos):
            # Calculate which option is being hovered
            option_height = 90
            option_index = (mouse_pos[1] - (panel_rect.y + 80)) // option_height

            # Validate option index
            if 0 <= option_index < len(PROMOTION_PIECES):
                # Set highlight option
                self.board.highlight_promotion_option = option_index
        else:
            # Clear highlight when mouse is not over options
            self.board.highlight_promotion_option = -1

        # Check for click
        if pygame.mouse.get_pressed()[0]:
            self.handle_promotion_click(mouse_pos)

    def draw_valid_moves(self):
        # Draw valid moves for selected piece
        self.board.draw_valid_moves(self.valid_moves, self.turn_step, self.board_flipped)

        # Draw castling moves if applicable
        if self.castling_moves:
            self.board.draw_castling(self.castling_moves, self.turn_step, self.board_flipped)

    def draw_game_over(self):
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        # Create game over panel
        panel_width, panel_height = 500, 200
        panel_rect = pygame.Rect((WIDTH - panel_width) // 2, (HEIGHT - panel_height) // 2,
                                 panel_width, panel_height)

        # Draw panel with winner color accent
        winner_color = WHITE if self.winner == WHITE else BLACK

        pygame.draw.rect(self.screen, WOOD_BROWN, panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, winner_color, panel_rect, 5, border_radius=15)

        # Draw winner message
        title_font = pygame.font.Font('freesansbold.ttf', 48)
        message_font = pygame.font.Font('freesansbold.ttf', 24)

        # Winner text
        winner_text = "White Win" if self.winner == WHITE else "Black Win"
        title = title_font.render(winner_text, True, CREAM_WHITE)

        # Message prompting to press Enter to play again
        message = message_font.render("Please Enter to play again", True, CREAM_WHITE)

        # Center messages
        self.screen.blit(title, (panel_rect.centerx - title.get_width() // 2, panel_rect.y + 60))
        self.screen.blit(message, (panel_rect.centerx - message.get_width() // 2, panel_rect.y + 120))

        self.game_over = True

    def reset_game(self):
        # Reset the game state but keep the same side
        playing_as_white = self.board.playing_as_white
        self.board = ChessBoard(self.screen)
        self.board.playing_as_white = playing_as_white
        self.board.setup_board()

        self.turn_step = 0  # White always starts first (chess rules)
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

        # Set board orientation based on which side is playing
        # If playing as white, board is not flipped
        # If playing as black, board is flipped
        self.board_flipped = not playing_as_white

        # Reinitialize the sound effects
        self.init_sounds()

        # Play game start sound
        self.play_sound(self.game_start_sound)