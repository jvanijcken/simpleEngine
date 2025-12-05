//
// Created by jvani on 21/09/2025.
//

#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>
#include <wchar.h>
#include <Python.h>

#include "../../include/transpositionTable.h"
#include "../../include/moveGeneration.h"
#include "../../include/algorithms.h"




bool UNWIND = true;
bool CALCULATION_FINISHED = true;
pthread_mutex_t time_mutex = PTHREAD_MUTEX_INITIALIZER;

bool getIsTimeUp() {
    pthread_mutex_lock(&time_mutex);
    const bool unwind = UNWIND;
    pthread_mutex_unlock(&time_mutex);
    return unwind;
}
void setIsTimeUp(const bool value) {
    pthread_mutex_lock(&time_mutex);
    UNWIND = value;
    pthread_mutex_unlock(&time_mutex);
}
bool getIsCalculationFinished() {
    pthread_mutex_lock(&time_mutex);
    const bool calculation_finished = CALCULATION_FINISHED;
    pthread_mutex_unlock(&time_mutex);
    return calculation_finished;
}
void setIsCalculationFinished(const bool value) {
    pthread_mutex_lock(&time_mutex);
    CALCULATION_FINISHED = value;
    pthread_mutex_unlock(&time_mutex);
}

int TTWrites    = 0;
int TTHits      = 0;
int TTMisses    = 0;
int TTConflicts = 0;


TTEntry* probeTT(const uint64_t hash) {
    TTEntry* e = &transTable[TT_INDEX(hash)];
    if (e->hash == hash) {
        TTHits++;
        return e;
    }
    if (e->hash == 0) {
        TTMisses++;
        return NULL;
    }
    TTConflicts++;
    return NULL;
}

TTEntry* sneakyProbeTT(const uint64_t hash)
{
    TTEntry* e = &transTable[TT_INDEX(hash)];
    if (e->hash == hash) {
        return e;
    }
    return NULL;
}

void storeTT(const uint64_t hash, const int depth, const int score, const int flag ) {
    TTEntry* e = &transTable[TT_INDEX(hash)];
    if (e->depth < depth) {
        e->hash  = hash;
        e->depth = depth;
        e->score = score;
        e->flag  = flag;
        TTWrites++;
    }
}


#define CHECKMATE    1000000
#define INF          100000000


int getEval(const Board* board, const int color) {
    const TTEntry* entry = sneakyProbeTT(board->hash);
    if (entry && entry->flag == 0) return entry->score;
    return board->eval * SIGN(color);;
}


#define PLACE_A_BEFORE_B (-1)
#define PLACE_B_BEFORE_A (+1)


int sortDescWhite(const void* a, const void* b) {
    const Board* A = (const Board*)(a);
    const Board* B = (const Board*)(b);

    const int evalA = getEval(A, WHITE);
    const int evalB = getEval(B, WHITE);

    if (evalA > evalB) return PLACE_A_BEFORE_B;
    if (evalA < evalB) return PLACE_B_BEFORE_A;

    return 0;
}
int sortDescBlack(const void* a, const void* b) {
    const Board* A = (const Board*)(a);
    const Board* B = (const Board*)(b);

    const int evalA = getEval(A, BLACK);
    const int evalB = getEval(B, BLACK);

    if (evalA > evalB) return PLACE_A_BEFORE_B;
    if (evalA < evalB) return PLACE_B_BEFORE_A;

    return 0;
}


int (*sortBestMovesFirst(const int color))(const void*, const void*) {
    return color? &sortDescBlack : &sortDescWhite;
}

int principalVariationSearch(const Board* board, const int depth, int alpha, const int beta, const int color) {
    // check if cached
    const TTEntry* entry = probeTT(board->hash);
    if (entry && entry->depth >= depth) {
        if (entry->flag == 0)  return entry->score;
        if (entry->flag == -1 && entry->score <= alpha) return alpha;
        if (entry->flag ==  1 && entry->score >= beta)  return beta;
    }

    if (getIsTimeUp())  return alpha;

    const bool isPastHorizon = depth <= 0;
    const bool isNoisyMove = board->isLastMoveAttack;
    const bool isTooFarPastHorizon = depth < -10;

    if (isPastHorizon && !isNoisyMove) {return board->eval * SIGN(color);}  // continues if noisy position
    if (isTooFarPastHorizon)           {return board->eval * SIGN(color);}  // too expensive

    Board moves[512];
    const int nrOfMoves = generateMoves(board, moves, color);

    if (nrOfMoves == 0 && isInCheck(board, color)) return (-CHECKMATE - depth);
    if (nrOfMoves == 0)                            return 0;

    qsort(moves, nrOfMoves, sizeof(Board), sortBestMovesFirst(color));

    const int oldAlpha = alpha;  // save for caching

    for (int i = 0; i < nrOfMoves; i++) {
        if (getIsTimeUp())  return alpha;
        int score;
        if (i == 0) {
            score = - principalVariationSearch(&moves[i], depth -1, -beta, -alpha, !color);
        }
        else {
            score = - principalVariationSearch(&moves[i], depth -1, -alpha -1, -alpha, !color);
            if (alpha < score && score < beta) {
                score = - principalVariationSearch(&moves[i], depth -1, -beta, -alpha, !color);
            }
        }
        if (score > alpha) {
            alpha = score;
        }
        if (alpha >= beta) {
            break;
        }
        if (getIsTimeUp())  return alpha;
    }
    // store result
    int flag = 0;
    if (alpha <= oldAlpha) flag = -1;
    else if (alpha >= beta) flag = 1;
    storeTT(board->hash, depth, alpha, flag);

    return alpha;
}

typedef struct {
    Board* pBoard;
    int depth;
    int color;
} Args;

void* Ds(void* _args) {

    // deconvert args
    const Args* p_args = (Args*)_args;
    const Board* board = p_args->pBoard;
    const int depth    = p_args->depth;
    const int color    = p_args->color;

    if (getIsTimeUp()) return NULL;

    // set TT params
    TTWrites    = 0;
    TTHits      = 0;
    TTMisses    = 0;
    TTConflicts = 0;

    // initialize params
    int alpha            = -INF;
    Result* result       = calloc(1, sizeof(Result));
    Board moves[512]    = {0};
    int scores[512]     = {0};
    int starts[512]     = {0};
    int ends[512]       = {0};
    const int nrOfMoves = generateDetailedMoves(board, moves, color, starts, ends);

    if (nrOfMoves == 0 && isInCheck(board, color)) {
        result->alpha = - CHECKMATE;
        return result;
    }
    if (nrOfMoves == 0) {
        result->alpha = -1;
        return result;
    }
    for (int i = 0; i < nrOfMoves; i++) {  // iterate over moves
        const int beta    = INF;
        scores[i] = -principalVariationSearch(&moves[i], depth -1, -beta, -alpha, !color);

        if (scores[i] > alpha) {
            alpha = scores[i];
        }
        if (getIsTimeUp()) return NULL;
    }

    for (int i = 0; i < 512; i++) result->moves[i]   = moves[i];
    for (int i = 0; i < 512; i++) result->scores[i]  = scores[i];
    result->nrOfMoves = nrOfMoves;
    result->alpha = (color)? -alpha : alpha;
    for (int i = 0; i < 512; i++) result->starts[i]  = starts[i];
    for (int i = 0; i < 512; i++) result->ends[i]    = ends[i];

    // write TT params
    result->TTWrites    = TTWrites   ;
    result->TTHits      = TTHits     ;
    result->TTMisses    = TTMisses   ;
    result->TTConflicts = TTConflicts;


    setIsCalculationFinished(true);  // signal im ready
    return result;
}

bool isBoardEmpty(const Board* pBoard) {
    for (int p = 0; p < PIECE_COUNT; p++) {
        for (int c = 0; c < 2; c++) {
            if (pBoard->pieces[c][p] != 0) return false;
        }
    }
    return true;
}


Result directSearch(Board* board, const int depth, const int color, PyObject* stop) {
    setIsTimeUp(false);
    setIsCalculationFinished(false);

    pthread_t thread;
    Args args = {board, depth, color};

    pthread_create(&thread, NULL, Ds, &args);

    bool isCalculationInterrupted = false;
    while (true) {

        const PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject* result = PyObject_CallMethod(stop, "is_set", NULL);
        const int should_stop = PyObject_IsTrue(result);
        Py_XDECREF(result);
        PyGILState_Release(gstate);

        if (getIsCalculationFinished()) {
            break;
        }
        if (should_stop) {
            isCalculationInterrupted = true;
            break;
        }
        usleep(100000); // sleep 100ms to avoid busy spinning
    }

    // Signal the worker thread to stop if needed
    setIsTimeUp(true);

    // Join the monitor thread and retrieve result
    void* threadResult;
    pthread_join(thread, &threadResult);
    Result result = {0};
    if (threadResult == NULL) {
        result.calculationsInterrupted = isCalculationInterrupted;
    }
    else {
        result = *(Result*)(threadResult);
        free(threadResult);
    }
    result.calculationsInterrupted = isCalculationInterrupted;

    return result;
}
