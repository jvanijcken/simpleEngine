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

#include "../include/transpositionTable.h"
#include "../include/moveGeneration.h"
#include "../include/algorithms.h"

#include "../testing/debugTools.h"

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


TTEntry* probeTT(const uint64_t hash) {
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
    }
}


#define CHECKMATE    1000000
#define INF          100000000


int getEval(const Board* board, const int color) {
    const TTEntry* entry = probeTT(board->hash);
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

    const bool isPastHorizon = depth <= 0;
    const bool isNoisyMove = board->isLastMoveAttack;
    const bool isTooFarPastHorizon = depth < -10;

    if (getIsTimeUp())                 {return board->eval * SIGN(color);}
    if (isPastHorizon && !isNoisyMove) {return board->eval * SIGN(color);}  // continues if noisy position
    if (isTooFarPastHorizon)           {return board->eval * SIGN(color);}  // too expensive


    Board results[512];
    const int nrOfMoves = generateMoves(board, results, false, color);

    // checkmate and stalemate
    if (nrOfMoves == 0 && isInCheck(board, color)) return (-CHECKMATE - depth);
    if (nrOfMoves == 0)                            return 0;

    // order with estimated best moves first
    qsort(results, nrOfMoves, sizeof(Board), sortBestMovesFirst(color));

    const int oldAlpha = alpha;  // save for caching

    for (int i = 0; i < nrOfMoves; i++) {
        int score;
        if (i == 0) {
            // principal search (presumed best move)
            score = - principalVariationSearch(&results[i], depth - 1, - beta     , -alpha, !color);
        }
        else {
            // scout search (cheap)
            score = - principalVariationSearch(&results[i], depth - 1, - alpha - 1, -alpha, !color);

            if (alpha < score && score < beta) {  // use full search if scout failed (presumed best move wasn't the best move)
                score = - principalVariationSearch(&results[i], depth - 1, -beta, -alpha, !color);
            }
        }

        // fixme cached results dont give the best board
        if (score > alpha) {
            alpha = score;
        } // save if best score & save best move
        if (alpha >= beta) {
            break;
        }  // prune if possible
        if (getIsTimeUp()) {
            return alpha;
        }
    }

    // store result
    int flag = 0;
    if (alpha <= oldAlpha) flag = -1;
    else if (alpha >= beta) flag = 1;
    storeTT(board->hash, depth, alpha, flag);

    return alpha;
}

int movePrincipalVariationSearch(const Board* board, const int depth, int alpha, const int beta, const int color, Board* pBestMove) {
    // we cant check if cached, because that wiuldnt give us a move

    Board results[512];
    const int nrOfMoves = generateMoves(board, results, false, color);

    // checkmate and stalemate
    *pBestMove = *board;
    if (nrOfMoves == 0 && isInCheck(board, color)) return (-CHECKMATE - depth);
    if (nrOfMoves == 0)                            return 0;

    // order with estimated best moves first
    qsort(results, nrOfMoves, sizeof(Board), sortBestMovesFirst(color));

    for (int i = 0; i < nrOfMoves; i++) {
        const int score = - principalVariationSearch(&results[i], depth - 1, - beta, -alpha, !color);

        if (score > alpha) {
            alpha = score;
            *pBestMove = results[i];
        } // save if best score & save best move
        if (getIsTimeUp()) {
            return alpha;
        }
    }
    return alpha;
}

typedef struct {
    Board* pBoard;
    int depth;
    int color;
} DSArgs;

void* threadedIDS(void* arg) {
    const DSArgs* args = (DSArgs*)(arg);

    setIsTimeUp(false);

    int score = 0;
    int depth = 0;
    Board bestMove = {0};

    while (depth < args->depth) {
        if (getIsTimeUp()) {  // check if time is up
            break;
        }
        score = movePrincipalVariationSearch(args->pBoard, depth, -INF, INF, args->color, &bestMove);

        if (score >= CHECKMATE || score <= -CHECKMATE) {  // if checkmate is found you can stop
            break;
        }
        depth++;
    }
    setIsCalculationFinished(true);

    Result* pResult = malloc(sizeof(Result));
    pResult->score = 0;
    pResult->depth = 0;
    pResult->bestMove = bestMove;

    return (void*)pResult;
}

Result iterativeDeepeningSearch(Board* board, const int depth, const int color, PyObject* stop) {
    pthread_t monitor_thread;

    DSArgs* args = malloc(sizeof(DSArgs));
    if (!args) {
        fprintf(stderr, "Failed to allocate IDSArgs\n");
        return (Result){0, 0};
    }
    args->pBoard = board;
    args->depth  = depth;
    args->color  = color;

    setIsTimeUp(false);
    setIsCalculationFinished(false);

    pthread_create(&monitor_thread, NULL, threadedIDS, args);

    bool isCalculationInterrupted = false;
    while (true) {

        PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject* result = PyObject_CallMethod(stop, "is_set", NULL);
        const int should_stop = PyObject_IsTrue(result);
        Py_XDECREF(result);
        PyGILState_Release(gstate);

        if (getIsCalculationFinished()) {
            break;
        }
        // check for max time
        if (should_stop) {
            isCalculationInterrupted = true;
            break;
        }

        usleep(100000); // sleep 100ms to avoid busy spinning
    }

    // Signal the worker thread to stop if needed
    setIsTimeUp(true);

    // Join the monitor thread and retrieve result
    void* finalScore;
    pthread_join(monitor_thread, &finalScore);
    Result result = *(Result*)(finalScore);
    result.calculationsInterrupted = isCalculationInterrupted;
    free(finalScore);
    free(args);

    return result;
}

void* threadedDS(void* arg) {
    const DSArgs* args = (DSArgs*)(arg);

    Board bestMove = {0};
    Result* pResult  = malloc(sizeof(Result));

    const int sign = args->color? -1 : 1;
    pResult->score = sign * movePrincipalVariationSearch(args->pBoard, args->depth, -INF, INF, args->color, &bestMove);
    pResult->depth = args->depth;
    pResult->bestMove = bestMove;

    setIsCalculationFinished(true);

    return (void*)(pResult);
}

Result directSearch(Board* board, const int depth, const int color, PyObject* stop) {
    pthread_t monitor_thread;

    DSArgs* args = malloc(sizeof(DSArgs));
    if (!args) {
        fprintf(stderr, "Failed to allocate IDSArgs\n");
        return (Result){0, 0};
    }
    args->pBoard = board;
    args->depth = depth;
    args->color = color;

    setIsTimeUp(false);
    setIsCalculationFinished(false);

    pthread_create(&monitor_thread, NULL, threadedDS, args);

    bool isCalculationInterrupted = false;
    while (true) {

        PyGILState_STATE gstate = PyGILState_Ensure();
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
    void* finalScore;
    pthread_join(monitor_thread, &finalScore);
    Result result = *(Result*)(finalScore);
    result.calculationsInterrupted = isCalculationInterrupted;
    free(finalScore);
    free(args);

    return result;
}
