//
// Created by jvani on 21/09/2025.
//

#ifndef SIMPLEENGINE_CORE_H
#define SIMPLEENGINE_CORE_H


#include "transpositionTable.h"

typedef struct {
    int score;
    int depth;
    Board bestMove;
} Result;

void forceStopCalculations();
Result iterativeDeepeningSearch(Board* board, int depth, int color, PyObject* stop);
Result directSearch(Board* board, int depth, int color, PyObject* stop);

#endif //SIMPLEENGINE_CORE_H