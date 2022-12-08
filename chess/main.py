import pygame as p
import chess_env, model_chess
import sys
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_WIDTH = 250
MOVE_LOG_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadChessVectors():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

def generateGameState(screen, gameState, validMoves, squareSelected):
    generateBoard(screen)
    highlightMoves(screen, gameState, validMoves, squareSelected)
    generateChessPieces(screen, gameState.board)


def generateBoard(screen):

    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlightMoves(screen, gameState, validMoves, squareSelected):
    if (len(gameState.moveLog)) > 0:
        lastMove = gameState.moveLog[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (lastMove.endCol * SQUARE_SIZE, lastMove.endRow * SQUARE_SIZE))
    if squareSelected != ():
        row, col = squareSelected
        if gameState.board[row][col][0] == (
                'w' if gameState.isWhiteMove else 'b'):
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE))


def generateChessPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def generateMoveLog(screen, gameState, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_WIDTH, MOVE_LOG_HEIGHT)
    p.draw.rect(screen, p.Color('black'), moveLogRect)
    moveLog = gameState.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + '. ' + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1]) + "  "
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 5
    lineSpacing = 2
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


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, False, p.Color("gray"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color('black'))
    screen.blit(textObject, textLocation.move(2, 2))


def animateMove(move, screen, board, clock):
    global colors
    dRow = move.endRow - move.startRow
    dCol = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dRow) + abs(dCol)) * framesPerSquare
    for frame in range(frameCount + 1):
        row, col = (move.startRow + dRow * frame / frameCount, move.startCol + dCol * frame / frameCount)
        generateBoard(screen)
        generateChessPieces(screen, board)
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


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gameState = chess_env.GameState()
    validMoves = gameState.validMoves()
    moveMade = False
    animate = False
    loadChessVectors()
    running = True
    squareSelected = ()
    playerClicks = []
    gameOver = False
    aiThinking = False
    moveUndone = False
    moveFinderProcess = None
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    playerOne = True
    playerTwo = False

    while running:
        humanTurn = (gameState.isWhiteMove and playerOne) or (not gameState.isWhiteMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
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


            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gameState.undoLastMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if aiThinking:
                        moveFinderProcess.terminate()
                        aiThinking = False
                    moveUndone = True
                if e.key == p.K_r:
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
            animate = False
            moveUndone = False

        generateGameState(screen, gameState, validMoves, squareSelected)

        if not gameOver:
            generateMoveLog(screen, gameState, moveLogFont)

        if gameState.isCheckmate:
            gameOver = True
            if gameState.isWhiteMove:
                drawEndGameText(screen, "Black wins by checkmate!")
            else:
                drawEndGameText(screen, "White wins by checkmate!")

        elif gameState.isStalemate:
            gameOver = True
            drawEndGameText(screen, "It's a stalemate.")

        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()