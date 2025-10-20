//
// Created by jvani on 22/09/2025.
//
#include <stdio.h>
#include "../include/globals.h"

int myGetPiece(const Board* board, const uint64_t position) {
    for (int color = 0; color < 2; color++) {
        for (int piece = 0; piece <PIECE_COUNT; piece++) {
            if ((board->pieces[color][piece] & position) != 0) {
                return piece;
            }
        }
    }
    return NO_PIECE;
}

void printBoard(const Board* board, const int indent) {
    for (int i = 0; i < 64; i++) {
        if (i % 8 == 0) {
            for (int x = 0; x < indent; x++) {printf("\t");};
        }
        const uint64_t pos = 1ULL << i;

        if (pos & board->colors[WHITE]) {
            printf("w");
        }
        if (pos & board->colors[BLACK]) {
            printf("b");
        }
        if (pos & ~(board->colors[WHITE] | board->colors[BLACK])) {
            printf("_");
        }

        const int piece = myGetPiece(board, pos);
        if (piece == NO_PIECE) {
            printf("_ ");
        } else {
            const char pieces[12] = {'p', 'r', 'n', 'b', 'q', 'k', 'p', 'r', 'n', 'b', 'q', 'k'};
            printf("%c ", pieces[piece]);
        }
        if (i % 8 == 7) {
            printf("\n");
        }
    }
}

void printIndexAsCoords(const int index) {
    const int r = index / 8;
    const int c = index % 8;
    const char cols[8] = {'a', 'b', 'c' ,'d', 'e', 'f', 'g', 'h'};
    printf("%c", cols[c]);
    printf("%d", 8 -r);
}

void printMove(const uint64_t start, const uint64_t end) {
    const int s = __builtin_ctzll(start);
    const int e = __builtin_ctzll(end);
    printIndexAsCoords(s);
    printf(" -> ");
    printIndexAsCoords(e);
    printf("\n");
}

void printUint(const uint64_t value) {
    for (int i = 0; i < 64; i++) {
        if (i % 8 == 0) {printf("\n");}
        if (value & (1ULL << i)) {printf("x  ");} else {printf("_  ");}
    }
}