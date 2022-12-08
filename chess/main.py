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
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def drawGameState(screen, gameState, validMoves, squareSelected):
    generateBoard(screen)
    highlightMoves(screen, gameState, validMoves, squareSelected)
    generateGamePieces(screen, gameState.board)

def generateBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = colors[((i + j) % 2)]
            p.draw.rect(screen, color, p.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def highlightMoves(screen, gameState, validMoves, squareSelected):
    if (len(gameState.moveLog)) > 0:
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
            selected.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == i and move.startCol == j:
                    screen.blit(selected, (move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE))

def generateGamePieces(screen, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            gamePiece = board[i][j]
            if gamePiece != "--":
                screen.blit(IMAGES[gamePiece], p.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def generateMoveLog(screen, gameState, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_WIDTH, MOVE_LOG_HEIGHT)
    p.draw.rect(screen, p.Color('black'), moveLogRect)
    moveLog = gameState.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + '. ' + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1]) + " "
        moveTexts.append(moveString)
    movesPerRow = 3
    lineSpacing = 2
    padding = 5
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]

        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

def animateMove(move, screen, board, clock):
    global colors
    dRow = move.endRow - move.startRow
    dCol = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dRow) + abs(dCol)) * framesPerSquare
    for frame in range(frameCount + 1):
        row, col = (move.startRow + dRow * frame / frameCount, move.startCol + dCol * frame / frameCount)
        generateBoard(screen)
        generateGamePieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enpassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQUARE_SIZE, enpassantRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)

def generateEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 30, True, False)
    textObject = font.render(text, False, p.Color("gray"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color('black'))
    screen.blit(textObject, textLocation.move(2, 2))

def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gameState = chess_env.GameState()
    validMoves = gameState.validMoves()
    animate = False
    moveMade = False
    loadChessVectors()
    running = True
    squareSelected = ()
    playerClicks = []
    gameOver = False
    moveUndone = False
    aiThinking = False
    moveFinderProcess = None
    moveLogFont = p.font.SysFont("Helvetica", 14, False, False)
    playerOne = True
    playerTwo = False

    while running:
        humanTurn = (gameState.isWhiteMove and playerOne) or (not gameState.isWhiteMove and playerTwo)
        for i in p.event.get():
            if i.type == p.QUIT:
                p.quit()
                sys.exit()
            elif i.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    row = location[1] // SQUARE_SIZE
                    col = location[0] // SQUARE_SIZE
                    if squareSelected == (row, col) or col >= 8:
                        squareSelected = ()
                        playerClicks = []
                    else:
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = chess_env.Move(playerClicks[0], playerClicks[1], gameState.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gameState.executeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                squareSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [squareSelected]
            elif i.type == p.KEYDOWN:
                if i.key == p.K_z:
                    gameState.undoLastMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if aiThinking:
                        moveFinderProcess.terminate()
                        aiThinking = False
                    moveUndone = True
                if i.key == p.K_r:
                    gameState = chess_env.GameState()
                    validMoves = gameState.validMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if aiThinking:
                        moveFinderProcess.terminate()
                        aiThinking = False
                    moveUndone = True

        if not gameOver and not humanTurn and not moveUndone:
            if not aiThinking:
                aiThinking = True
                returnSequence = Queue()
                moveFinderProcess = Process(target=model_chess.findTheBestMove, args=(gameState, validMoves, returnSequence))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                aiMove = returnSequence.get()
                if aiMove is None:
                    aiMove = model_chess.findRandomMove(validMoves)
                gameState.executeMove(aiMove)
                moveMade = True
                animate = True
                aiThinking = False

        if moveMade:
            if animate:
                animateMove(gameState.moveLog[-1], screen, gameState.board, clock)
            validMoves = gameState.validMoves()
            moveMade = False
            moveUndone = False
            animate = False

        drawGameState(screen, gameState, validMoves, squareSelected)

        if not gameOver:
            generateMoveLog(screen, gameState, moveLogFont)

        if gameState.isCheckmate:
            gameOver = True
            if gameState.isWhiteMove:
                generateEndGameText(screen, "Black wins by checkmate!")
            else:
                generateEndGameText(screen, "White wins by checkmate!")

        elif gameState.isStalemate:
            gameOver = True
            generateEndGameText(screen, "Well fought. It's a stalemate.")

        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()






