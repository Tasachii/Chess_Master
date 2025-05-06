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
        self.winner_by_time = False  # Flag for win by timeout
        self.game_over = False
        self.white_promote = False
        self.black_promote = False
        self.promo_index = 100
        self.board_flipped = False  # False = white at bottom, True = black at bottom
        self.last_flip_time = 0  # Prevents rapid consecutive button presses

        # Add variables for time control
        self.time_control = BLITZ  # Default value
        self.white_time = 0  # Will be set when time mode is selected
        self.black_time = 0  # Will be set when time mode is selected
        self.last_move_time = 0  # Time of the last move

        # Game state
        self.game_state = MENU  # Start with menu screen

        # FIXME: Need to implement proper AI opponent later

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
            elif self.game_state == TIME_SELECT:
                game_running = self.handle_time_selection()
            elif self.game_state == PLAYING:
                game_running = self.handle_gameplay()

                # Update timers during gameplay
                if not self.game_over and not self.white_promote and not self.black_promote:
                    self.update_timers()

            pygame.display.flip()

        pygame.quit()

    def handle_menu(self):
        # Draw side selection menu
        white_button, black_button, quit_button = self.board.draw_menu()

        # Check for mouse clicks on buttons
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if white_button.collidepoint(mouse_pos):
                    # Set to play as white
                    self.board.playing_as_white = True  # Direct assignment instead of method call
                    # White pieces at bottom (not flipped)
                    self.board_flipped = False
                    # Go to time selection screen
                    self.game_state = TIME_SELECT

                elif black_button.collidepoint(mouse_pos):
                    # Set to play as black
                    self.board.playing_as_white = False  # Direct assignment instead of method call
                    # Black pieces at bottom (flipped)
                    self.board_flipped = True
                    # Go to time selection screen
                    self.game_state = TIME_SELECT

                elif quit_button.collidepoint(mouse_pos):
                    # Exit the game
                    return False

        return True

    def handle_time_selection(self):
        # Draw time selection screen
        self.screen.fill(DARK_GRAY)

        # Draw title
        title_font = pygame.font.Font('freesansbold.ttf', 60)
        title = title_font.render("Select Time Control", True, GOLD)
        title_rect = title.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Create buttons for each time mode
        button_width, button_height = 400, 80
        buttons = []

        for i in range(4):
            y_pos = 250 + i * 100
            button = pygame.Rect(WIDTH // 2 - button_width // 2, y_pos, button_width, button_height)
            buttons.append(button)

            # Check if mouse is over button
            mouse_pos = pygame.mouse.get_pos()
            hover = button.collidepoint(mouse_pos)

            # Draw button with hover effect
            if hover:
                pygame.draw.rect(self.screen, LIGHT_BLUE, button.inflate(10, 10), border_radius=15)
            pygame.draw.rect(self.screen, WOOD_BROWN, button, border_radius=15)
            pygame.draw.rect(self.screen, GOLD if hover else WOOD_DARK, button, 4, border_radius=15)

            # Draw text on button
            button_font = pygame.font.Font('freesansbold.ttf', 36)
            minutes = TIME_CONTROLS[i] // 60
            text = f"{TIME_NAMES[i]}: {minutes} minute{'s' if minutes > 1 else ''}"
            button_text = button_font.render(text, True, CREAM_WHITE)
            text_rect = button_text.get_rect(center=button.center)
            self.screen.blit(button_text, text_rect)

        # Create a Back button in the bottom left corner
        back_button = pygame.Rect(30, HEIGHT - 80, 120, 50)
        back_hover = back_button.collidepoint(mouse_pos)

        # Draw back button with hover effect
        if back_hover:
            pygame.draw.rect(self.screen, LIGHT_BLUE, back_button.inflate(10, 10), border_radius=10)
        pygame.draw.rect(self.screen, WOOD_DARK, back_button, border_radius=10)
        pygame.draw.rect(self.screen, GOLD if back_hover else WOOD_BROWN, back_button, 3, border_radius=10)

        # Back button text
        back_font = pygame.font.Font('freesansbold.ttf', 24)
        back_text = back_font.render("Back", True, CREAM_WHITE)
        back_text_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_text_rect)

        # Check for input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                # Check if Back button was clicked
                if back_button.collidepoint(mouse_pos):
                    self.game_state = MENU
                    return True

                # Check time selection buttons
                for i, button in enumerate(buttons):
                    if button.collidepoint(mouse_pos):
                        # Select time mode
                        self.time_control = i
                        self.white_time = TIME_CONTROLS[i]
                        self.black_time = TIME_CONTROLS[i]
                        # Start game
                        self.start_game()
                        break

            # Allow ESC to go back to side selection
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = MENU

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
        self.winner_by_time = False
        self.game_over = False
        self.white_promote = False
        self.black_promote = False
        self.promo_index = 100

        # Make sure board setup is consistent with selected side
        self.board.setup_board()

        # Record start time
        self.last_move_time = pygame.time.get_ticks()

    def update_timers(self):
        # Reduce time only for the side that's currently playing
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.last_move_time) / 1000  # Convert to seconds

        if self.turn_step < 2:  # White's turn
            self.white_time -= elapsed
            if self.white_time <= 0:
                self.white_time = 0
                self.winner = BLACK
                self.winner_by_time = True
                self.game_over = True
        else:  # Black's turn
            self.black_time -= elapsed
            if self.black_time <= 0:
                self.black_time = 0
                self.winner = WHITE
                self.winner_by_time = True
                self.game_over = True

        self.last_move_time = current_time

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
            # Pass time values to status area
            self.board.draw_status_area(self.turn_step, self.white_time, self.black_time)
            self.board.draw_pieces(self.turn_step, self.selection, self.board_flipped)
            self.board.draw_captured()

            # Check for check condition and draw indicator
            previous_check = self.check
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

                                    # Update last move time for timer
                                    self.last_move_time = pygame.time.get_ticks()

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

                                    # Update last move time for timer
                                    self.last_move_time = pygame.time.get_ticks()

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

        # Update last move time for timer
        self.last_move_time = pygame.time.get_ticks()

        # Check for checkmate after move
        opponent_color = BLACK if piece.color == WHITE else WHITE
        if self.board.is_checkmate(opponent_color):
            self.winner = WHITE if piece.color == WHITE else BLACK
            self.game_over = True

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
        win_text = "White Win" if self.winner == WHITE else "Black Win"

        # Add text indicating win by timeout
        if self.winner_by_time:
            win_text += " by Timeout"

        title = title_font.render(win_text, True, CREAM_WHITE)

        # Message prompting to press Enter to play again
        message = message_font.render("Press Enter to play again", True, CREAM_WHITE)

        # Center messages
        self.screen.blit(title, (panel_rect.centerx - title.get_width() // 2, panel_rect.y + 60))
        self.screen.blit(message, (panel_rect.centerx - message.get_width() // 2, panel_rect.y + 120))

        self.game_over = True

    def reset_game(self):
        # Reset the game state but keep the same side and time control
        playing_as_white = self.board.playing_as_white
        current_time_control = self.time_control

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
        self.winner_by_time = False
        self.game_over = False
        self.white_promote = False
        self.black_promote = False
        self.promo_index = 100

        # Set board orientation based on which side is playing
        self.board_flipped = not playing_as_white

        # Reset timers
        self.time_control = current_time_control
        self.white_time = TIME_CONTROLS[self.time_control]
        self.black_time = TIME_CONTROLS[self.time_control]
        self.last_move_time = pygame.time.get_ticks()