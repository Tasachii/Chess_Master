# chess_board.py
import pygame
from constants import *
from chess_piece import ChessPiece


class ChessBoard:
    def __init__(self, screen):
        self.screen = screen
        self.white_pieces = []
        self.black_pieces = []
        self.captured_white = []
        self.captured_black = []
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.medium_font = pygame.font.Font('freesansbold.ttf', 40)
        self.big_font = pygame.font.Font('freesansbold.ttf', 50)
        self.selected_piece = None
        self.white_ep = (100, 100)  # En passant square
        self.black_ep = (100, 100)  # En passant square
        self.playing_as_white = True  # Stores which side the player chose to play as

    def setup_board(self):
        # Clear all piece data
        self.white_pieces = []
        self.black_pieces = []
        self.captured_white = []
        self.captured_black = []

        # Set the piece order based on which side we're playing
        if self.playing_as_white:
            # If playing as white, pieces will be ordered: R N B Q K B N R
            white_piece_types = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
            black_piece_types = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        else:
            # If playing as black, pieces will be ordered: R N B K Q B N R
            white_piece_types = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook']
            black_piece_types = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook']

        # Create white pieces
        for i, piece_type in enumerate(white_piece_types):
            self.white_pieces.append(ChessPiece(piece_type, WHITE, (i, 0), self))

        # Create white pawns
        for i in range(8):
            self.white_pieces.append(ChessPiece('pawn', WHITE, (i, 1), self))

        # Create black pieces
        for i, piece_type in enumerate(black_piece_types):
            self.black_pieces.append(ChessPiece(piece_type, BLACK, (i, 7), self))

        # Create black pawns
        for i in range(8):
            self.black_pieces.append(ChessPiece('pawn', BLACK, (i, 6), self))

    def set_playing_side(self, as_white):
        self.playing_as_white = as_white
        self.setup_board()

    def draw_board(self, flipped=False):
        # Draw chess board squares (light blue and white)
        for row in range(8):
            for col in range(8):
                screen_y = 7 - row if flipped else row

                if (row + col) % 2 == 0:
                    pygame.draw.rect(self.screen, LIGHT_BLUE, [col * 100, screen_y * 100, 100, 100])
                else:
                    pygame.draw.rect(self.screen, WHITE, [col * 100, screen_y * 100, 100, 100])

        # Draw board outline
        for i in range(9):
            pygame.draw.line(self.screen, 'black', (0, 100 * i), (800, 100 * i), 2)
            pygame.draw.line(self.screen, 'black', (100 * i, 0), (100 * i, 800), 2)

        # Display board information
        flip_status = "Flipped (Black side)" if flipped else "Normal (White side)"
        self.screen.blit(self.font.render(f"Board: {flip_status}", True, 'black'), (810, 50))

        side_text = "Playing as: White" if self.playing_as_white else "Playing as: Black"
        self.screen.blit(self.font.render(side_text, True, 'black'), (810, 80))

        # Draw board outline
        for i in range(9):
            pygame.draw.line(self.screen, 'black', (0, 100 * i), (800, 100 * i), 2)
            pygame.draw.line(self.screen, 'black', (100 * i, 0), (100 * i, 800), 2)

        # Display board information
        flip_status = "Flipped (Black side)" if flipped else "Normal (White side)"
        self.screen.blit(self.font.render(f"Board: {flip_status}", True, 'black'), (810, 50))

        side_text = "Playing as: White" if self.playing_as_white else "Playing as: Black"
        self.screen.blit(self.font.render(side_text, True, 'black'), (810, 80))

    def draw_menu(self):
        # Draw the background
        self.screen.fill(DARK_GRAY)

        # Draw the game title
        title_text = "Chess Game"
        title_render = self.big_font.render(title_text, True, 'white')
        title_rect = title_render.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(title_render, title_rect)

        # Draw the "Play as White" button
        white_button = pygame.Rect(WIDTH // 2 - 150, 300, 300, 80)
        pygame.draw.rect(self.screen, WHITE, white_button)
        pygame.draw.rect(self.screen, 'black', white_button, 2)  # Border
        white_text = self.medium_font.render("Play as White", True, 'black')
        white_text_rect = white_text.get_rect(center=white_button.center)
        self.screen.blit(white_text, white_text_rect)

        # Draw the "Play as Black" button
        black_button = pygame.Rect(WIDTH // 2 - 150, 420, 300, 80)
        pygame.draw.rect(self.screen, BLACK, black_button)
        pygame.draw.rect(self.screen, 'white', black_button, 2)  # Border
        black_text = self.medium_font.render("Play as Black", True, 'white')
        black_text_rect = black_text.get_rect(center=black_button.center)
        self.screen.blit(black_text, black_text_rect)

        return white_button, black_button

    def draw_status_area(self, turn_step):
        # Draw status area at bottom of screen
        pygame.draw.rect(self.screen, GRAY, [0, 800, WIDTH, 100])
        pygame.draw.rect(self.screen, GOLD, [0, 800, WIDTH, 100], 5)
        pygame.draw.rect(self.screen, GOLD, [800, 0, 200, HEIGHT], 5)

        status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                       'Black: Select a Piece to Move!', 'Black: Select a Destination!']
        self.screen.blit(self.big_font.render(status_text[turn_step], True, 'black'), (20, 820))
        self.screen.blit(self.medium_font.render('FORFEIT', True, 'black'), (810, 830))
        # Controls
        self.screen.blit(self.font.render('Press F to flip board', True, 'black'), (810, 780))
        self.screen.blit(self.font.render('Press R to restart', True, 'black'), (810, 750))

    def draw_pieces(self, turn_step, selection, flipped=False):
        # Draw all pieces on the board
        for i, piece in enumerate(self.white_pieces):
            x, y = piece.position
            # Transform coordinates for drawing if board is flipped
            screen_y = 7 - y if flipped else y

            if piece.piece_type == 'pawn':
                self.screen.blit(piece.image, (x * 100 + 22, screen_y * 100 + 30))
            else:
                self.screen.blit(piece.image, (x * 100 + 10, screen_y * 100 + 10))

            if turn_step < 2 and selection == i:
                pygame.draw.rect(self.screen, RED,
                                 [x * 100 + 1, screen_y * 100 + 1, 100, 100], 2)

        for i, piece in enumerate(self.black_pieces):
            x, y = piece.position
            # Transform coordinates for drawing if board is flipped
            screen_y = 7 - y if flipped else y

            if piece.piece_type == 'pawn':
                self.screen.blit(piece.image, (x * 100 + 22, screen_y * 100 + 30))
            else:
                self.screen.blit(piece.image, (x * 100 + 10, screen_y * 100 + 10))

            if turn_step >= 2 and selection == i:
                pygame.draw.rect(self.screen, BLUE,
                                 [x * 100 + 1, screen_y * 100 + 1, 100, 100], 2)

    def draw_captured(self):
        # Show captured white pieces on the side panel
        for i, piece in enumerate(self.captured_white):
            self.screen.blit(piece.small_image, (825, 5 + 50 * i))

        # Show captured black pieces on the side panel
        for i, piece in enumerate(self.captured_black):
            self.screen.blit(piece.small_image, (925, 5 + 50 * i))

    def draw_valid_moves(self, valid_moves, turn_step, flipped=False):
        # Draw circles on valid move positions
        color = RED if turn_step < 2 else BLUE
        for move in valid_moves:
            x, y = move
            # Transform y coordinate if board is flipped
            screen_y = 7 - y if flipped else y
            pygame.draw.circle(self.screen, color, (x * 100 + 50, screen_y * 100 + 50), 5)

    def draw_check(self, counter, flipped=False):
        check_detected = False

        # Look for white king in check
        white_king = next((p for p in self.white_pieces if p.piece_type == 'king'), None)
        if white_king:
            # See if any black piece can attack white king
            for black_piece in self.black_pieces:
                if white_king.position in black_piece.get_valid_moves():
                    check_detected = True
                    # Flash visual indicator (only during certain animation frames)
                    if counter < 15:
                        x, y = white_king.position
                        screen_y = 7 - y if flipped else y
                        pygame.draw.rect(self.screen, DARK_RED,
                                         [x * 100 + 1, screen_y * 100 + 1, 100, 100], 5)

        # Look for black king in check
        black_king = next((p for p in self.black_pieces if p.piece_type == 'king'), None)
        if black_king:
            # See if any white piece can attack black king
            for white_piece in self.white_pieces:
                if black_king.position in white_piece.get_valid_moves():
                    check_detected = True
                    # Flash visual indicator (only during certain animation frames)
                    if counter < 15:
                        x, y = black_king.position
                        screen_y = 7 - y if flipped else y
                        pygame.draw.rect(self.screen, DARK_BLUE,
                                         [x * 100 + 1, screen_y * 100 + 1, 100, 100], 5)

        return check_detected

    def draw_castling(self, castling_moves, turn_step, flipped=False):
        # Pick color based on whose turn it is
        highlight_color = RED if turn_step < 2 else BLUE

        # Draw visual indicators for each castling option
        for king_pos, rook_pos in castling_moves:
            k_x, k_y = king_pos
            r_x, r_y = rook_pos

            # Handle flipped board coordinates
            k_screen_y = 7 - k_y if flipped else k_y
            r_screen_y = 7 - r_y if flipped else r_y

            # Draw connecting line between king and rook positions
            pygame.draw.line(self.screen, highlight_color,
                             (k_x * 100 + 50, k_screen_y * 100 + 70),
                             (r_x * 100 + 50, r_screen_y * 100 + 70), 2)

            # Draw indicators for king's destination
            pygame.draw.circle(self.screen, highlight_color, (k_x * 100 + 50, k_screen_y * 100 + 70), 8)
            self.screen.blit(self.font.render('king', True, 'black'), (k_x * 100 + 30, k_screen_y * 100 + 70))

            # Draw indicators for rook's destination
            pygame.draw.circle(self.screen, highlight_color, (r_x * 100 + 50, r_screen_y * 100 + 70), 8)
            self.screen.blit(self.font.render('rook', True, 'black'), (r_x * 100 + 30, r_screen_y * 100 + 70))

    def draw_promotion(self, color, turn_step):
        # Show promotion piece selection UI
        pygame.draw.rect(self.screen, 'dark gray', [800, 0, 200, 420])

        # Display all promotion options
        promotions = PROMOTION_PIECES
        for i, piece_type in enumerate(promotions):
            piece = ChessPiece(piece_type, color, (0, 0), self)
            self.screen.blit(piece.image, (860, 5 + 100 * i))

        # Add border around the promotion area
        pygame.draw.rect(self.screen, color, [800, 0, 200, 420], 8)

        # Show promotion instruction message
        pygame.draw.rect(self.screen, GRAY, [0, 800, WIDTH - 200, 100])
        pygame.draw.rect(self.screen, GOLD, [0, 800, WIDTH - 200, 100], 5)
        self.screen.blit(self.big_font.render('Select Piece to Promote Pawn', True, 'black'), (20, 820))

    def is_king_in_check(self, color):
        # Find the king
        if color == WHITE:
            king = next((p for p in self.white_pieces if p.piece_type == 'king'), None)
            opponent_pieces = self.black_pieces
        else:
            king = next((p for p in self.black_pieces if p.piece_type == 'king'), None)
            opponent_pieces = self.white_pieces

        # If king not found, return False
        if not king:
            return False

        # Check if any opponent piece can capture the king
        for piece in opponent_pieces:
            if king.position in piece.get_valid_moves():
                return True

        return False

    def is_square_under_attack(self, position, attacking_color):
        # Get all pieces of the attacking color
        if attacking_color == WHITE:
            opponent_pieces = self.white_pieces
        else:
            opponent_pieces = self.black_pieces

        # Check if any piece can move to the target position
        for piece in opponent_pieces:
            if position in piece.get_valid_moves():
                return True

        return False

    def is_checkmate(self, color):
        # If not in check, can't be checkmate
        if not self.is_king_in_check(color):
            return False

        # Try every possible move to see if any can get out of check
        pieces_to_check = self.white_pieces if color == WHITE else self.black_pieces

        for piece in pieces_to_check:
            valid_moves = piece.get_valid_moves()
            original_position = piece.position

            # Try each possible move
            for move in valid_moves:
                # Keep track of any captured piece
                captured_piece = self.get_piece_at_position(move)
                captured_black = None
                captured_white = None

                # Handle piece capture simulation
                if captured_piece is not None:
                    if captured_piece.color == WHITE:
                        self.white_pieces.remove(captured_piece)
                        captured_white = captured_piece
                    else:
                        self.black_pieces.remove(captured_piece)
                        captured_black = captured_piece

                # Simulate the move
                piece.position = move

                # Check if king is still in check after move
                still_in_check = self.is_king_in_check(color)

                # Undo the move
                piece.position = original_position

                # Put back any captured piece
                if captured_white is not None:
                    self.white_pieces.append(captured_white)
                if captured_black is not None:
                    self.black_pieces.append(captured_black)

                # If this move gets us out of check, not checkmate
                if not still_in_check:
                    return False

        # If no move can get us out of check, it's checkmate
        return True

    def check_castling(self, color):
        castling_moves = []

        # Can't castle while in check
        if self.is_king_in_check(color):
            return castling_moves

        # Find king and rooks
        if color == WHITE:
            king = next((p for p in self.white_pieces if p.piece_type == 'king'), None)
            rooks = [p for p in self.white_pieces if p.piece_type == 'rook']
            opponent_color = BLACK
        else:
            king = next((p for p in self.black_pieces if p.piece_type == 'king'), None)
            rooks = [p for p in self.black_pieces if p.piece_type == 'rook']
            opponent_color = WHITE

        # If king has moved or doesn't exist, can't castle
        if not king or king.has_moved:
            return castling_moves

        # Check each rook for castling possibility
        for rook in rooks:
            # Skip if rook has already moved
            if rook.has_moved:
                continue

            # Get positions
            king_x, king_y = king.position
            rook_x, rook_y = rook.position

            # Handle kingside vs queenside castling
            if rook_x > king_x:  # Kingside castling
                # Check squares between king and rook
                path_squares = [(king_x + 1, king_y), (king_x + 2, king_y)]
                # Final positions after castling
                king_dest = (king_x + 2, king_y)
                rook_dest = (king_x + 1, king_y)
            else:  # Queenside castling
                # Check squares between king and rook
                path_squares = [(king_x - 1, king_y), (king_x - 2, king_y)]
                # Extra square to check for queenside
                extra_square = (king_x - 3, king_y)
                # Final positions after castling
                king_dest = (king_x - 2, king_y)
                rook_dest = (king_x - 1, king_y)

                # For queenside, need to check one more square
                # (that square can be under attack, but must be empty)
                if extra_square in self.get_all_piece_positions():
                    continue

            # Path must be clear and safe
            path_safe = True

            # Check if path is clear of pieces
            for square in path_squares:
                if square in self.get_all_piece_positions():
                    path_safe = False
                    break

            # Check if squares are safe from attack
            for square in path_squares:
                if self.is_square_under_attack(square, opponent_color):
                    path_safe = False
                    break

            # Add castling move if all conditions met
            if path_safe:
                castling_moves.append((king_dest, rook_dest))

        return castling_moves

    def get_piece_at_position(self, position):
        # Search all pieces to find one at the given position
        for piece in self.white_pieces + self.black_pieces:
            if piece.position == position:
                return piece
        return None

    def get_all_piece_positions(self):
        # Get positions of all pieces on the board
        return [piece.position for piece in self.white_pieces + self.black_pieces]

    def get_piece_positions(self, color):
        # Get positions of pieces of a specific color
        if color == WHITE:
            return [piece.position for piece in self.white_pieces]
        else:
            return [piece.position for piece in self.black_pieces]

    def get_opponent_positions(self, color):
        # Get positions of opponent pieces
        if color == WHITE:
            return [piece.position for piece in self.black_pieces]
        else:
            return [piece.position for piece in self.white_pieces]

    def get_en_passant_square(self, color):
        # Return the current en passant target square
        return self.white_ep if color == WHITE else self.black_ep