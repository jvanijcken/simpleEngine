//
// Created by jvani on 22/09/2025.
//
#include <assert.h>

#include "../include/transpositionTable.h"
#include "../include/moveFunctions.h"
#include "../include/boardEvaluation.h"
#include "../include/zobristHashing.h"


bool canBeAttacked(uint64_t position, const Board* board, const int color) {
    assert (color == 1 || color == 0);
    while (position) {
        for (int piece = P; piece <= K; piece++) {
            const uint64_t attackerPieces    = board->pieces[!color][piece];
            assert (position != 0);
            const uint64_t attackerPositions = moveFunctions[piece](__builtin_ctzll(position), board, color);
            if ((attackerPieces & attackerPositions) != 0) {
                return true;
            }
        }
        position &= position - 1;
    }
    return false;
}
bool isInCheck(const Board* board, const int color) {
    return canBeAttacked(board->pieces[color][K], board, color);
}
int getPiece(const Board* board, const uint64_t position, const int color) {
    for (int piece = 0; piece < PIECE_COUNT; piece++) {
        if ((board->pieces[color][piece] & position) != 0) {
            return piece;
        }
    }
    return NO_PIECE;
}

void addMove(Board* result, const uint64_t start, const uint64_t end,
        const int startPiece, const int endPiece, const int capturedPiece, const int color,
        const int startIndex, const int endIndex) {
    // Clear start from piece and side
    result->pieces[color][startPiece] &= ~start;
    result->colors[color]             &= ~start;
    result->eval -= pieceEvaluators[color][startPiece][startIndex];
    result->hash ^= tableHash      [color][startPiece][startIndex];

    // Handle capture if any
    if (capturedPiece != NO_PIECE) {
        result->pieces[!color][capturedPiece] &= ~end;
        result->colors[!color]                &= ~end;
        result->eval -= pieceEvaluators[!color][capturedPiece][endIndex];
        result->hash ^= tableHash      [!color][capturedPiece][endIndex];
    }
    // Place the moving piece (or promotion)
    result->pieces[color][endPiece] |= end;
    result->colors[color]           |= end;
    result->eval += pieceEvaluators[color][endPiece][endIndex];
    result->hash ^= tableHash      [color][endPiece][endIndex];

    result->hash ^= colorHash;

    //revoke castling rights
    if (color) {  // black
        if (startPiece == K) {  // obviously king cannot be captured
            result->castle &= ~BLACK_KINGSIDE; result->castle &= ~BLACK_QUEENSIDE;
        }
        if ((startPiece == R && start == A8) || (capturedPiece == R && end == A8)) {
            result->castle &= ~BLACK_QUEENSIDE;
        }
        if ((startPiece == R && start == H8) || (capturedPiece == R && end == H8)) {
            result->castle &= ~BLACK_KINGSIDE;
        }
    }
    else {  // white
        if (startPiece == K) {
            result->castle &= ~WHITE_KINGSIDE; result->castle &= ~WHITE_QUEENSIDE;
        }
        if ((startPiece == R && start == A1) || (capturedPiece == R && end == A1)) {
            result->castle &= ~WHITE_QUEENSIDE;
        }
        if ((startPiece == R && start == H1) || (capturedPiece == R && end == H1)) {
            result->castle &= ~WHITE_KINGSIDE;
        }
    }

    // update en passant
    if      (startPiece == P && color == WHITE && start >> 16 == end) {
        result->enPassant = start >> 8;
    }
    else if (startPiece == P && color == BLACK && start << 16 == end) {
        result->enPassant = start << 8;
    } else {
        result->enPassant = 0ULL;
    }

    // update isLastMoveAttack
    result->isLastMoveAttack = (capturedPiece != NO_PIECE);
}

int blackKingsideCastle(Board* result) {
    if ((result->castle & BLACK_KINGSIDE) == 0) return 0;// can castle anymore
    if (result->colors[WHITE] | result->colors[BLACK] & (F8 | G8)) return 0;  // space not free
    if (canBeAttacked(E8 |F8 | G8, result, BLACK)) return 0;  // check if space is free

    addMove(result, E8, G8, K, K, NO_PIECE, BLACK, __builtin_ctzll(E8), __builtin_ctzll(G8));
    addMove(result, H8, F8, R, R, NO_PIECE, BLACK, __builtin_ctzll(H8), __builtin_ctzll(F8));
    result->hash ^= colorHash;  //corrections
    return 1;
}
int blackQueensideCastle(Board* result) {
    if ((result->castle & BLACK_QUEENSIDE) == 0) return 0;// can castle anymore
    if (result->colors[WHITE] | result->colors[BLACK] & (D8 | C8 | B8)) return 0;  // space not free
    if (canBeAttacked(E8 | D8 | C8, result, BLACK)) return 0;  // check if space is free

    addMove(result, E8, C8, K, K, NO_PIECE, BLACK, __builtin_ctzll(E8), __builtin_ctzll(C8));
    addMove(result, A8, D8, R, R, NO_PIECE, BLACK, __builtin_ctzll(A8), __builtin_ctzll(D8));
    result->hash ^= colorHash;  //corrections
    return 1;
}
int whiteKingsideCastle(Board* result) {
    if ((result->castle & WHITE_KINGSIDE) == 0) return 0;// can castle anymore
    if (result->colors[WHITE] | result->colors[BLACK] & (F1 | G1)) return 0;  // space not free
    if (canBeAttacked(E1 | F1 | G1, result, WHITE)) return 0;  // check if space is free

    addMove(result, E1, G1, K, K, NO_PIECE, BLACK, __builtin_ctzll(E1), __builtin_ctzll(G1));
    addMove(result, H1, F1, R, R, NO_PIECE, BLACK, __builtin_ctzll(H1), __builtin_ctzll(F1));
    result->hash ^= colorHash;  //corrections
    return 1;
}
int whiteQueensideCastle(Board* result) {
    if ((result->castle & WHITE_QUEENSIDE) == 0) return 0;// can castle anymore
    if (result->colors[WHITE] | result->colors[BLACK] & (D1 | C1 | B1)) return 0;  // space not free
    if (canBeAttacked(E1 | D1 | C1, result, WHITE)) return 0;  // check if space is free

    addMove(result, E1, C1, K, K, NO_PIECE, BLACK, __builtin_ctzll(E1), __builtin_ctzll(C1));
    addMove(result, A1, D1, R, R, NO_PIECE, BLACK, __builtin_ctzll(A1), __builtin_ctzll(D1));
    result->hash ^= colorHash;  //corrections
    return 1;
}

int generateMoves(const Board* board, Board results[], const bool attacksOnly, const int color) {
    int moveCount = 0;

    for (int startPiece = P; startPiece <= K; startPiece++) {
        const MoveFunction function = moveFunctions[startPiece];
        uint64_t pieces = board->pieces[color][startPiece];

        while (pieces) {
            const uint64_t start = pieces & -pieces;
            const int startIndex = __builtin_ctzll(start);
            uint64_t moves = function(startIndex, board, color);
            pieces &= pieces - 1;

            if (attacksOnly) {moves &= board->colors[!color];}

            while (moves) {
                const uint64_t end = moves & -moves;
                const int endIndex = __builtin_ctzll(end);
                moves &= moves - 1;

                const int capturedPiece = getPiece(board, end, !color);

                const int promotionPieces[4] = {R, N, B, Q};
                const int nrOfMoves  = (startPiece == P && end & (RANK8 | RANK1))? 4 : 1;
                const int* endPieces = (startPiece == P && end & (RANK8 | RANK1))? promotionPieces : &startPiece;

                for (int i  = 0; i < nrOfMoves; i++) {
                    const int endPiece = endPieces[i];

                    Board* result = &results[moveCount];
                    *result = *board;

                    addMove(result, start, end, startPiece, endPiece, capturedPiece, color, startIndex, endIndex);

                    moveCount += !isInCheck(result, color);
                }
            }
        }
    }
    // add castle moves
    results[moveCount + 0] = *board;
    results[moveCount + 1] = *board;
    if (color) {
        moveCount += blackKingsideCastle (&results[moveCount]);
        moveCount += blackQueensideCastle(&results[moveCount]);
    } else {
        moveCount += whiteKingsideCastle (&results[moveCount]);
        moveCount += whiteQueensideCastle(&results[moveCount]);
    }
    return moveCount;
}
