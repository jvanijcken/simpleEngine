//
// Created by jvani on 23/09/2025.
//


#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>


void precalcMoves(const int deltas[][2], uint64_t array[64], const int directions) {
    for (int i = 0; i < 64; i++) {
        array[i] = 0;
        for (int dir = 0; dir < directions; dir++) {
            const int dr = deltas[dir][0];
            const int dc = deltas[dir][1];
            const int r = (i / 8 + dr);
            const int c = (i % 8 + dc);

            const int isOutOfBounds    = r < 0 || r > 7 || c < 0 || c > 7;
            if (isOutOfBounds) {continue;}
            const uint64_t newPos = 1ULL << (r * 8 + c);
            array[i] |= newPos;
        }
    }
}

void fprintUint64_tArray(FILE* file, const char* variableName, const int length, uint64_t array[64]) {
    fprintf(file, "const uint64_t %s[%d] = {\n", variableName, length);
    for (int i = 0; i < length; i++) {fprintf(file, "    0x%016llxULL,\n", array[i]);}
    fprintf(file, "};\n\n");
}

void generateCFile(const char* filename) {
    FILE* f = fopen(filename, "w");
    if (!f) {
        perror("Failed to open file for writing");
        exit(1);
    }

    const int whitePawnWalkDeltas  [1][2] = {{-1,  0}};
    const int blackPawnWalkDeltas  [1][2] = {{ 1,  0}};
    const int whitePawnAttackDeltas[2][2] = {{-1,  1}, {-1, -1}};
    const int blackPawnAttackDeltas[2][2] = {{ 1,  1}, { 1, -1}};
    const int knightMoveDeltas     [8][2] = {{ 1,  2}, {-1,  2}, {-1, -2}, { 1, -2},
                                             { 2,  1}, {-2,  1}, {-2, -1}, { 2, -1}};
    const int kingMoveDeltas       [8][2] = {{ 1,  1}, { 1, -1}, {-1,  1}, {-1, -1},
                                             { 0,  1}, { 0, -1}, { 1,  0}, {-1,  0}};

    uint64_t whitePawnWalkLookup  [64];
    uint64_t whitePawnAttackLookup[64];
    uint64_t blackPawnWalkLookup  [64];
    uint64_t blackPawnAttackLookup[64];
    uint64_t knightMovesLookup    [64];
    uint64_t kingMovesLookup      [64];

    precalcMoves(whitePawnWalkDeltas  , whitePawnWalkLookup  , 1);
    precalcMoves(whitePawnAttackDeltas, whitePawnAttackLookup, 2);
    precalcMoves(blackPawnWalkDeltas  , blackPawnWalkLookup  , 1);
    precalcMoves(blackPawnAttackDeltas, blackPawnAttackLookup, 2);
    precalcMoves(knightMoveDeltas     , knightMovesLookup    , 8);
    precalcMoves(kingMoveDeltas       , kingMovesLookup      , 8);

    fprintf(f, "#include <stdint.h>\n\n");

    fprintUint64_tArray(f, "whitePawnWalkLookup"  , 64, whitePawnWalkLookup  );
    fprintUint64_tArray(f, "whitePawnAttackLookup", 64, whitePawnAttackLookup);
    fprintUint64_tArray(f, "blackPawnWalkLookup"  , 64, blackPawnWalkLookup  );
    fprintUint64_tArray(f, "blackPawnAttackLookup", 64, blackPawnAttackLookup);
    fprintUint64_tArray(f, "knightMovesLookup"    , 64, knightMovesLookup    );
    fprintUint64_tArray(f, "kingMovesLookup"      , 64, kingMovesLookup      );
}


void generateHeaderFile(const char* filename) {
    FILE* f = fopen(filename, "w");
    if (!f) {
        perror("Failed to open file for writing");
        exit(1);
    }

    fprintf(f, "#ifndef LOOKUP_H\n#define LOOKUP_H\n\n");
    fprintf(f, "#define LOOKUP_H\n");
    fprintf(f, "#include <stdint.h>\n\n");

    fprintf(f, "extern const uint64_t whitePawnWalkLookup  [64];\n");
    fprintf(f, "extern const uint64_t whitePawnAttackLookup[64];\n");
    fprintf(f, "extern const uint64_t blackPawnWalkLookup  [64];\n");
    fprintf(f, "extern const uint64_t blackPawnAttackLookup[64];\n");
    fprintf(f, "extern const uint64_t knightMovesLookup    [64];\n");
    fprintf(f, "extern const uint64_t kingMovesLookup      [64];\n");

    fprintf(f, "#endif");   
}

int main() {
    generateCFile     ("lookupOneStepMoves.c");
    generateHeaderFile("lookupOneStepMoves.h");
    return 0;
}