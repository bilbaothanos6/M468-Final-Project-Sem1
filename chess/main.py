import chess_env
import model_chess
import pygame as p
import sys
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_HEIGHT = BOARD_HEIGHT
MOVE_LOG_WIDTH = 250
MAX_FPS = 15
IMAGES = {}
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION

def loadChessVectors():
    pieces = ["wp", "wR", "wN", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def drawGameState(screen, gameState, validMoves, squareSelected):
    drawBoard(screen)
    highlightMoves(screen, gameState, validMoves, squareSelected)
    drawGamePieces(screen, gameState.board)

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = colors[((i + j) % 2)]
            p.draw.rect(screen, color, p.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE))

def highlightMoves(screen, gameState, validMoves, squareSelected):
    if (len(gameState.move_log)) > 0:
        lastMove = gameState.moveLog[-1]
        selected = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        selected.set_alpha(100)
        selected.fill(p.Color("green"))
        screen.blit(selected, (lastMove.endCol * SQUARE_SIZE, lastMove.endRow * SQUARE_SIZE))
    if squareSelected != ():
        i, j = squareSelected
        if gameState.board[i][j][0] == ("w" if gameState.isWhiteMove else "b"):
            selected = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            selected.set_alpha(100)
            selected.fill(p.Color("blue"))
            screen.blit(selected, (j * SQUARE_SIZE, i * SQUARE_SIZE))
            screen.fill(p.COLOR("yellow"))
            for move in validMoves:
                if move.startRow == i and move.startCol == j:
                    screen.blit(selected, (move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE))


def drawGamePieces(screen, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            gamePiece = board[i][j]
            if gamePiece != "--":
                screen.blit(IMAGES[gamePiece], p.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE))

