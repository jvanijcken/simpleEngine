//
// Created by jvani on 24/09/2025.
//

//
// Created by jvani on 21/09/2025.
//
#include <stdio.h>
#include <stdlib.h>

typedef enum {WP, WR, WN, WB, WQ, WK, BP, BR, BN, BB, BQ, BK, PIECE_COUNT} Pieces;

int whitePawnPositionEvaluation[64] = {
    0,   0,  0,  0,   0,   0,   0,   0,
   50,  50, 50, 50,  50,  50,  50,  50,
   10,  10, 20, 30,  30,  20,  10,  10,
    5,   5, 10, 25,  25,  10,   5,   5,
    0,   0,  0, 20,  20,   0,   0,   0,
    5, - 5,-10,  0,   0, -10,  -5,   5,
    5,  10, 10, 20, -20,  10,  10,   5,
    0,   0,  0,  0,   0,   0,   0,   0
};
int blackPawnPositionEvaluation[64] = {
    0,   0,   0,   0,   0,   0,   0,   0,
    5,  10,  10, -20, -20,  10,  10,   5,
    5,  -5, -10,   0,   0, -10,  -5,   5,
    0,   0,   0,  20,  20,   0,   0,   0,
    5,   5,  10,  25,  25,  10,   5,   5,
    10,  10,  20,  30, 30,  20,  10,  10,
    50,  50,  50,  50, 50,  50,  50,  50,
    0,   0,   0,   0,   0,   0,   0,   0
};
int rookPositionEvaluation[64] = {
    0,   0,   0,   0,   0,   0,   0,   0,
    5,  10,  10,  10,  10,  10,  10,   5,
   -5,   0,   0,   0,   0,   0,   0,  -5,
   -5,   0,   0,   0,   0,   0,   0,  -5,
   -5,   0,   0,   0,   0,   0,   0,  -5,
   -5,   0,   0,   0,   0,   0,   0,  -5,
   -5,   0,   0,   0,   0,   0,   0,  -5,
    0,   0,   0,   5,   5,   0,   0,   0
};
int knightPositionEvaluation[64] = {
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
};
int bishopPositionEvaluation[64] = {
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
 };
int queenPositionEvaluation[64] = {
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,   5,   5,   5,   0, -10,
     -5,   0,   5,   5,   5,   5,   0,  -5,
      0,   0,   5,   5,   5,   5,   0,  -5,
    -10,   5,   5,   5,   5,   5,   0, -10,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20
 };
int whiteKingPositionEvaluation[64] = {
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
     20,  20,   0,   0,   0,   0,  20,  20,
     20,  30,   0,   0,   0,   0,  30,  20
 };
int blackKingPositionEvaluation[64] = {
    20,  30,   0,   0,   0,   0,  30,  20,
    20,  20,   0,   0,   0,   0,  20,  20,
   -10, -20, -20, -20, -20, -20, -20, -10,
   -20, -30, -30, -40, -40, -30, -30, -20,
   -30, -40, -40, -50, -50, -40, -40, -30,
   -30, -40, -40, -50, -50, -40, -40, -30,
   -30, -40, -40, -50, -50, -40, -40, -30,
   -30, -40, -40, -50, -50, -40, -40, -30
};


void generateHeaderFile(const char* filename) {
    FILE* f = fopen(filename, "w");
    if (!f) {
        perror("Failed to open file for writing");
        exit(1);
    }

    fprintf(f, "#ifndef LOOKUP_H\n#define LOOKUP_H\n\n");
    fprintf(f, "#define LOOKUP_H\n");
    fprintf(f, "#include <stdint.h>\n\n");
    fprintf(f, "extern const int pieceEvaluators[12][64];\n\n");
    fprintf(f, "#endif");
}


void fprintIntArray(FILE* file, const char* variableName, const int length, int array[64]) {
    fprintf(file, "const int %s[%d] = {\n", variableName, length);
    for (int i = 0; i < length; i++) {fprintf(file, "    %d,\n", array[i]);}
    fprintf(file, "};\n\n");
}

void generateCFile(const char* filename) {
    FILE* f = fopen(filename, "w");
    if (!f) {
        perror("Failed to open file for writing");
        exit(1);
    }

    int pieceEvaluators[PIECE_COUNT][64];
    for (int i = 0; i < 64; i++) {
        pieceEvaluators[WP][i] = +100   +whitePawnPositionEvaluation[i];
        pieceEvaluators[BP][i] = -100   -blackPawnPositionEvaluation[i];
        pieceEvaluators[WR][i] = +500   +rookPositionEvaluation     [i];
        pieceEvaluators[BR][i] = -500   -rookPositionEvaluation     [i];
        pieceEvaluators[WN][i] = +320   +knightPositionEvaluation   [i];
        pieceEvaluators[BN][i] = -320   -knightPositionEvaluation   [i];
        pieceEvaluators[WB][i] = +330   +bishopPositionEvaluation   [i];
        pieceEvaluators[BB][i] = -330   -bishopPositionEvaluation   [i];
        pieceEvaluators[WQ][i] = +900   +queenPositionEvaluation    [i];
        pieceEvaluators[BQ][i] = -900   -queenPositionEvaluation    [i];
        pieceEvaluators[WK][i] = +20000 +whiteKingPositionEvaluation[i];
        pieceEvaluators[BK][i] = -20000 -blackKingPositionEvaluation[i];
    }

    fprintf(f, "const int pieceEvaluators[12][64] = {\n");
    for (int p = 0; p < PIECE_COUNT; p++) {
        fprintf(f, "{");
        for (int i = 0; i < 64; i++) {
            if (i % 8 == 0) fprintf(f, "\n");
            fprintf(f, "%d, ", pieceEvaluators[p][i]);
        }
        fprintf(f, "\n}, \n");
    }
    fprintf(f, "};");
}

int main(void) {
    generateCFile("evaluators.c");
    generateHeaderFile("evaluators.h");
    return 0;
}


