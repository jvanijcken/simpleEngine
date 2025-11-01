//
// Created by jvani on 21/09/2025.
//

#ifndef SIMPLEENGINE_CORE_H
#define SIMPLEENGINE_CORE_H


#include "transpositionTable.h"

typedef struct {
    int score;
    int depth;
} Result;

void forceStopCalculations();
Result directSearch(const Board* board, int depth, int color);
Result iterativeDeepeningSearch(const Board* board, int maxDepth, int color);
Result timeLimitedIterativeDeepeningSearch(Board* board, int maxDepth, int color, double durationSeconds);

#endif //SIMPLEENGINE_CORE_H