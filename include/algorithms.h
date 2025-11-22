//
// Created by jvani on 21/09/2025.
//

#ifndef SIMPLEENGINE_CORE_H
#define SIMPLEENGINE_CORE_H


#include "transpositionTable.h"

typedef struct {
    Board moves[512]            ;
    int scores[512]             ;
    int nrOfMoves               ;
    int alpha                   ;
    int TTWrites                ;
    int TTHits                  ;
    int TTMisses                ;
    int TTConflicts             ;
    bool calculationsInterrupted;
} Result;

Result iterativeDeepeningSearch(Board* board, int depth, int color, PyObject* stop);
Result directSearch(Board* board, int depth, int color, PyObject* stop);

#endif //SIMPLEENGINE_CORE_H