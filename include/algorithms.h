//
// Created by jvani on 21/09/2025.
//

#ifndef SIMPLEENGINE_CORE_H
#define SIMPLEENGINE_CORE_H


#include "transpositionTable.h"

int iterativeDeepeningSearch(const Board* board, int maxDepth, int color, Board bestSeq[]);
int timeLimitedIterativeDeepeningSearch(Board* board, int maxDepth, int color,
        Board bestSeq[], int durationSeconds);

#endif //SIMPLEENGINE_CORE_H