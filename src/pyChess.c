//
// Created by jvani on 20/10/2025.
//

#include <Python.h>
#include "../include/transpositionTable.h"
#include "../include/algorithms.h"
#include "../include/zobristHashing.h"
#include "../include/boardEvaluation.h"



uint64_t zobristHash(const Board* board, const int color) {
    uint64_t key = 0ULL;
    if (color) {
        key ^= colorHash;
    }
    for (int c = 0; c < 2; c++) {
        for (int piece = 0; piece < 6; piece++) {
            uint64_t pieces = board->pieces[c][piece];

            while (pieces) {
                const int index = __builtin_ctzll(pieces);
                key ^= tableHash[c][piece][index];
                pieces &= pieces - 1;
            }
        }
    }
    return key;
}


int evaluateBoard(const Board *pBoard) {
    int score = 0;

    for (int c = 0; c < 2; c++) {
        for (int p = 0; p < 6; p++) {
            uint64_t pieces = pBoard->pieces[c][p];
            while (pieces) {
                const int index = __builtin_ctzll(pieces);
                pieces &= -pieces;
                score += pieceEvaluators[c][p][index];
            }
        }
    }
    return score;
}


void buildBoard(const int pieces[64], const int passant, const int castles[4], Board* board, const int color) {
    // clear board
    for (int c = 0; c < 2; c++) {
        for (int p = 0; p < 6; p++) {
            board->pieces[c][p] = 0ULL;
        }
    }
    board->enPassant = (passant == -1)? 0ULL : 1ULL << passant;

    // add pieces
    for (int i = 0; i < 64; i++) {
        const int coloredPiece = pieces[i];
        if (coloredPiece == NO_PIECE) break;
        const int c = coloredPiece / 6;
        const int p = coloredPiece % 6;
        board->pieces[c][p] |= (1ULL << i);
    }

    // add colors
    board->colors[WHITE] = board->pieces[WHITE][P] | board->pieces[WHITE][R] | board->pieces[WHITE][N] |
                           board->pieces[WHITE][B] | board->pieces[WHITE][Q] | board->pieces[WHITE][K];
    board->colors[BLACK] = board->pieces[BLACK][P] | board->pieces[BLACK][R] | board->pieces[BLACK][N] |
                           board->pieces[BLACK][B] | board->pieces[BLACK][Q] | board->pieces[BLACK][K];

    // add castles
    board->castle = 0ULL;
    for (int i = 0; i < 4; i++) {
        if (castles[i] == 0) break;
        board->castle |= 1ULL << i;
    }
    board->hash = zobristHash(board, color);
    board->eval = evaluateBoard(board);
}


void readBoard(int result[], int *pPassant, int castles[4], const Board *pBoard) {
    for (int i = 0; i < 64; i++) {
        result[i] = NO_PIECE;
    }

    for (int i = 0; i < 64; i++) {
        for (int p = 0; p < 12; p++) {
            const int color = p / 6;
            const int piece = p & 6;
            if (pBoard->pieces[color][piece] & (1ULL << i)) {
                result[i] = p;
                break;
            }
        }
    }
    *pPassant = __builtin_ctzll(pBoard->enPassant);

    for (int i = 0; i < 4; i++) {
        if (pBoard->castle & 1ULL << i) {
            castles[i] = 1;
        }
        else {
            castles[i] = 0;
        }
    }
}


int pyIDS(int pieces[][64], int passant[], int castles[][4],
        const int color, const int maxDepth, const int durationSeconds) {

    // convert the args into a Board
    Board board;
    Board bestSeq[maxDepth];
    buildBoard(pieces[0], passant[0], castles[0], &board, color);

    // calculation
    const int score = timeLimitedIterativeDeepeningSearch(&board, maxDepth, color, bestSeq, durationSeconds);

    // put bestSeq into args
    for (int i = 1; i < maxDepth; i++) {
        readBoard(pieces[i], &passant[i], castles[i], &bestSeq[i]);
    }
    return score;
}