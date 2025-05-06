# chess_piece.py
import pygame
from constants import *


class ChessPiece:
    def __init__(self, piece_type, color, position, board):
        self.piece_type = piece_type
        self.color = color
        self.position = position
        self.board = board
        self.has_moved = False
        self.load_image()

    def load_image(self):
        img_name = f"images/{self.color} {self.piece_type}.png"
        self.image = pygame.image.load(img_name)
        if self.piece_type == 'pawn':
            self.image = pygame.transform.scale(self.image, (65, 65))
        else:
            self.image = pygame.transform.scale(self.image, (80, 80))

        # Create small version for captured pieces
        self.small_image = pygame.transform.scale(self.image, (45, 45))

    def draw(self, screen):
        x, y = self.position
        if self.piece_type == 'pawn':
            screen.blit(self.image, (x * 100 + 22, y * 100 + 30))
        else:
            screen.blit(self.image, (x * 100 + 10, y * 100 + 10))

    def get_valid_moves(self):
        if self.piece_type == 'pawn':
            return self._check_pawn_moves()
        elif self.piece_type == 'rook':
            return self._check_rook_moves()
        elif self.piece_type == 'knight':
            return self._check_knight_moves()
        elif self.piece_type == 'bishop':
            return self._check_bishop_moves()
        elif self.piece_type == 'queen':
            return self._check_queen_moves()
        elif self.piece_type == 'king':
            moves, castling = self._check_king_moves()
            return moves

    def _check_pawn_moves(self):
        # Logic for pawn moves
        moves = []
        x, y = self.position

        if self.color == WHITE:
            # Forward moves
            if (x, y + 1) not in self.board.get_all_piece_positions() and y < 7:
                moves.append((x, y + 1))
                # First move can be two squares
                if not self.has_moved and (x, y + 2) not in self.board.get_all_piece_positions():
                    moves.append((x, y + 2))

            # Capture moves
            for dx in [-1, 1]:
                capture_pos = (x + dx, y + 1)
                if capture_pos in self.board.get_opponent_positions(self.color):
                    moves.append(capture_pos)

            # En passant
            if (x + 1, y + 1) == self.board.get_en_passant_square(BLACK):
                moves.append((x + 1, y + 1))
            if (x - 1, y + 1) == self.board.get_en_passant_square(BLACK):
                moves.append((x - 1, y + 1))
        else:
            # Similar logic for black pawns (reversed direction)
            # Forward moves
            if (x, y - 1) not in self.board.get_all_piece_positions() and y > 0:
                moves.append((x, y - 1))
                # First move can be two squares
                if not self.has_moved and (x, y - 2) not in self.board.get_all_piece_positions():
                    moves.append((x, y - 2))

            # Capture moves
            for dx in [-1, 1]:
                capture_pos = (x + dx, y - 1)
                if capture_pos in self.board.get_opponent_positions(self.color):
                    moves.append(capture_pos)

            # En passant
            if (x + 1, y - 1) == self.board.get_en_passant_square(WHITE):
                moves.append((x + 1, y - 1))
            if (x - 1, y - 1) == self.board.get_en_passant_square(WHITE):
                moves.append((x - 1, y - 1))

        return moves

    def _check_rook_moves(self):
        # Logic for rook moves
        moves = []
        x, y = self.position

        # Check in 4 directions (up, down, left, right)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dx, dy in directions:
            for i in range(1, 8):
                new_pos = (x + i * dx, y + i * dy)
                # Check if position is on the board
                if not (0 <= new_pos[0] <= 7 and 0 <= new_pos[1] <= 7):
                    break

                # Check if position has a friendly piece
                if new_pos in self.board.get_piece_positions(self.color):
                    break

                moves.append(new_pos)

                # If we hit an enemy piece, stop after adding this move
                if new_pos in self.board.get_opponent_positions(self.color):
                    break

        return moves

    def _check_knight_moves(self):
        # Logic for knight moves
        moves = []
        x, y = self.position

        # Knights move in L-shape: 2 in one direction, 1 in perpendicular direction
        possible_moves = [
            (x + 1, y + 2), (x + 2, y + 1), (x + 2, y - 1), (x + 1, y - 2),
            (x - 1, y - 2), (x - 2, y - 1), (x - 2, y + 1), (x - 1, y + 2)
        ]

        for new_pos in possible_moves:
            # Check if position is on the board
            if not (0 <= new_pos[0] <= 7 and 0 <= new_pos[1] <= 7):
                continue

            # Check if position has a friendly piece
            if new_pos in self.board.get_piece_positions(self.color):
                continue

            moves.append(new_pos)

        return moves

    def _check_bishop_moves(self):
        # Logic for bishop moves
        moves = []
        x, y = self.position

        # Check in 4 diagonal directions
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dx, dy in directions:
            for i in range(1, 8):
                new_pos = (x + i * dx, y + i * dy)
                # Check if position is on the board
                if not (0 <= new_pos[0] <= 7 and 0 <= new_pos[1] <= 7):
                    break

                # Check if position has a friendly piece
                if new_pos in self.board.get_piece_positions(self.color):
                    break

                moves.append(new_pos)

                # If we hit an enemy piece, stop after adding this move
                if new_pos in self.board.get_opponent_positions(self.color):
                    break

        return moves

    def _check_queen_moves(self):
        # Queen combines rook and bishop moves
        return self._check_rook_moves() + self._check_bishop_moves()

    def _check_king_moves(self):
        # Logic for king moves
        moves = []
        castling_moves = []
        x, y = self.position

        # Regular moves in all 8 directions
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip the current position

                new_pos = (x + dx, y + dy)
                # Check if position is on the board
                if not (0 <= new_pos[0] <= 7 and 0 <= new_pos[1] <= 7):
                    continue

                # Check if position has a friendly piece
                if new_pos in self.board.get_piece_positions(self.color):
                    continue

                moves.append(new_pos)

        # Castling logic will be handled by the board class
        return moves, castling_moves

    def move(self, new_position):
        self.position = new_position
        self.has_moved = True