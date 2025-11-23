//
// Created by jvani on 22/09/2025.
//

#ifndef SIMPLEENGINE_MOVEGENERATION_H
#define SIMPLEENGINE_MOVEGENERATION_H

#include "transpositionTable.h"

bool isInCheck(const Board* board,  int color);
int generateMoves(const Board* board, Board results[], int color);
int generateDetailedMoves(const Board* board, Board results[], int color, int starts[], int ends[]);

#endif //SIMPLEENGINE_MOVEGENERATION_H