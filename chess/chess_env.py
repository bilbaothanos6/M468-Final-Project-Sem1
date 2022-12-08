class CastlingRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]

        ]
        self.pieceMoveFunctions = {"p": self.pawnMoves, "R": self.rookMoves, "N": self.knightMoves, "B": self.bishopMoves, "Q": self.queenMoves, "K": self.kingMoves}
        self.isCheckmate = False
        self.isStalemate = False
        self.isCheck = False
        self.isWhiteMove = True
        self.pins = []
        self.checks = []
        self.moveLog = []
        self.enpassantCaptureCoordinates = ()
        self.enpassantCaptureCoordinatesLog = [self.enpassantCaptureCoordinates]
        self.castlingRights = CastlingRights(True, True, True, True)
        self.castlingRightsLog = [CastlingRights(self.castlingRights.wks, self.castlingRights, self.castlingRights.wqs, self.castlingRights.bqs)]
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

    def executeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.isWhiteMove = not self.isWhiteMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantCaptureCoordinates = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantCaptureCoordinates = ()

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"
        self.enpassantCaptureCoordinatesLog.append(self.enpassantCaptureCoordinates)

        self.updateCastlingRights(move)
        self.castlingRightsLog.append(CastlingRights(self.castlingRights.wks, self.castlingRights.bks, self.castlingRights.wqs,
                                                     self.castlingRights.bqs))

    def updateCastlingRights(self, move):
        if move.pieceCaptured == "wR":
            if move.endCol == 0:
                self.castlingRights.wqs = False
            elif move.endCol == 7:
                self.castlingRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endCol == 0:
                self.castlingRights.bqs = False
            elif move.endCol == 7:
                self.castlingRights.bks = False

        if move.pieceMoved == "bK":
            self.castlingRights.bqs = False
            self.castlingRights.bks = False
        elif move.pieceMoved == "wK":
            self.castlingRights.wqs = False
            self.castlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.castlingRights.bqs = False
                elif move.startCol == 7:
                    self.castlingRights.bks = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.castlingRights.wqs = False
                elif move.startCol == 7:
                    self.castlingRights.wks = False

    def validMoves(self):
        tempCastlingRights = CastlingRights(self.castlingRights.wks, self.castlingRights.bks,
                                            self.castlingRights.wqs, self.castlingRights.bqs)

        moves = []
        self.isCheck, self.pins, self.checks = self.searchPinsAndChecks()

        if self.isWhiteMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.isCheck:
            if len(self.checks) == 1:
                moves = self.getPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves) -1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.kingMoves(kingRow, kingCol, moves)

        else:
            moves = self.getPossibleMoves()
            if self.isWhiteMove:
                self.getCastlingMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastlingMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheckPosition():
                self.isCheckmate = True
            else:
                self.isStalemate = True
        else:
            self.isCheckmate = False
            self.isStalemate = False

        self.castlingRights = tempCastlingRights
        return moves

    def undoLastMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.isWhiteMove = not self.isWhiteMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantCaptureCoordinatesLog.pop()
            self.enpassantCaptureCoordinates = self.enpassantCaptureCoordinatesLog[-1]

            self.castlingRightsLog.pop()
            self.castlingRights = self.castlingRightsLog[-1]
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
            self.isCheckmate = False
            self.isStalemate = False

    def inCheckPosition(self):
        if self.isWhiteMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def getPossibleMoves(self):
        moves = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                turn = self.board[i][j][0]
                if (turn == "w" and self.isWhiteMove) or (turn == "b" and not self.isWhiteMove):
                    piece = self.board[i][j][1]
                    self.pieceMoveFunctions[piece](i, j, moves)
        return moves

    def searchPinsAndChecks(self):
        pins = []
        checks = []
        isCheck = False
        if self.isWhiteMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for i in range(len(directions)):
            direction = directions[i]
            possiblePin = ()
            for j in range(1, 8):
                endRow = startRow + direction[0] * i
                endCol = startCol + direction[1] * i
                if 0<= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, direction[0], direction[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        enemyType = endPiece[1]
                        if(0 <= i <= 3 and enemyType == "R") or (4 <= i <= 7 and enemyType == "B") or (j == 1 and enemyType == "p" and ((enemyColor == "w" and 6 <= i <= 7) or (enemyColor == "b" and 4 <= i <= 5))) or (enemyType == "Q") or (j == 1 and enemyType == "K"):
                            if possiblePin == ():
                                isCheck = True
                                checks.append((endRow, endCol, direction[0], direction[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
        knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    isCheck = True
                    checks.append((endRow, endCol, move[0], move[1]))

        return isCheck, pins, checks

    def pawnMoves(self, row, col, moves):
        isPinnedPiece = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                isPinnedPiece = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.isWhiteMove:
            moveAmount = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation

        if self.board[row + moveAmount][col] == "--":
            if not isPinnedPiece or pinDirection == (moveAmount, 0):
                moves.append(Move((row, col), (row + moveAmount, col), self.board))
                if row == startRow and self.board[row + 2 * moveAmount][col] == "--":
                    moves.append(Move((row, col), (row + 2 * moveAmount, col), self.board))

        if col - 1 >= 0:
            if not isPinnedPiece or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][col - 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + moveAmount, col - 1), self.board))
                if (row + moveAmount, col - 1) == self.enpassantCaptureCoordinates:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:
                            insideRange = range(kingCol + 1, col - 1)
                            outsideRange = range(col + 1, 8)
                        else:
                            insideRange = range(kingCol - 1, col, -1)
                            outsideRange = range(col - 2, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True

                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, isEnpassantMove = True))

        if col + 1 <= 7:
            if not isPinnedPiece or pinDirection == (moveAmount, +1):
                if self.board[row + moveAmount][col + 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + moveAmount, col + 1), self.board))
                if (row + moveAmount, col + 1) == self.enpassantCaptureCoordinates:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:
                            insideRange = range(kingCol + 1, col)
                            outsideRange = range(col + 2, 8)
                        else:
                            insideRange = range(kingCol - 1, col + 1, -1)
                            outsideRange = range(col - 1, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True

                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, isEnpassantMove = True))

    def rookMoves(self, row, col, moves):
        isPiecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                isPiecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        rookMoves = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.isWhiteMove else "w"
        for move in rookMoves:
            for i in range(1, 8):
                endRow = row + rookMoves[0] * i
                endCol = col + rookMoves[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    if not isPiecePinned or pinDirection == rookMoves or pinDirection == (-move[0], -move[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def knightMoves(self, row, col, moves):
        isPiecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                isPiecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        allyColor = "w" if self.isWhiteMove else "b"
        for move in knightMoves:
            endRow = row + move[0]
            endCol = col + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                if not isPiecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    def queenMoves(self, row, col, moves):
        self.bishopMoves(row, col, moves)
        self.rookMoves(row, col, moves)

    def squareUnderAttack(self, row, col):
        self.isWhiteMove = not self.isWhiteMove
        opponentsMoves = self.getPossibleMoves()
        self.isWhiteMove = not self.isWhiteMove
        for move in opponentsMoves:
            if move.endRow == row and move.endCol == col:
                return True

        return False

    def bishopMoves(self, row, col, moves):
        isPiecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                isPiecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        bishopMoves = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        enemyColor = "b" if self.isWhiteMove else "w"
        for move in bishopMoves:
            for i in range(1, 8):
                endRow = row + move[0] * i
                endCol = col + move[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    if not isPiecePinned or pinDirection == move or pinDirection == (-move[0], -move[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break

                else:
                    break

    def kingMoves(self, row, col, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.isWhiteMove else "b"
        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    isCheck, pins, checks = self.searchPinsAndChecks()
                    if not isCheck:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    if allyColor == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

    def kingSideCastlingMoves(self, row, col, moves):
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove = True))

    def queenSideCastlingMoves(self, row, col, moves):
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove = True))
    def getCastlingMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return
        if (self.isWhiteMove and self.castlingRights.wks) or (not self.isWhiteMove and self.castlingRights.bks):
            self.kingSideCastlingMoves(row, col, moves)
        if (self.isWhiteMove and self.castlingRights.wqs) or (not self.isWhiteMove and self.castlingRights.bqs):
            self.queenSideCastlingMoves(row, col, moves)


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSquare, endSquare, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured == "wp" if self.pieceMoved == "bp" else "bp"
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != "--"
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def __str__(self):
        if self.isCastleMove:
            return "0-0" if self.endCol == 6 else "0-0-0"

        endSquare = self.rankFile(self.endRow, self.endCol)
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare + "Q" if self.isPawnPromotion else endSquare

        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare

    def rankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]

    def chessNotation(self):
        if self.isPawnPromotion:
            return self.rankFile(self.endRow, self.endCol) + "Q"
        if self.isCastleMove:
            if self.endCol == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.isEnpassantMove:
            return self.rankFile(self.startRow, self.startCol)[0] + "x" + self.rankFile(self.endRow, self.endCol) + "e.p."

        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == "p":
                return self.rankFile(self.startRow, self.startCol)[0] + "x" + self.rankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + "x" + self.rankFile(self.endRow, self.endCol)

        else:
            if self.pieceMoved[1] == "p":
                return self.rankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + self.rankFile(self.endRow, self.endCol)



























