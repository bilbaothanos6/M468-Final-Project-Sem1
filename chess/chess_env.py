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
            self.isCheck, self.pins, self.checks = self.searchPinsandChecks()

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














