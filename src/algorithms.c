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

#include "../include/transpositionTable.h"
#include "../include/moveGeneration.h"
#include "../include/algorithms.h"

bool UNWIND = true;
bool CALCULATION_FINISHED = true;
pthread_mutex_t time_mutex = PTHREAD_MUTEX_INITIALIZER;

uint64_t tt_collisions = 0;
uint64_t tt_probes = 0;
uint64_t tt_hits = 0;

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
    tt_probes++;
    TTEntry* e = &transTable[TT_INDEX(hash)];
    if (e->hash == hash) {
        tt_hits++;
        return e;
    }
    if (e->hash) {
        tt_collisions++;
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

    if (getIsTimeUp())                 return board->eval * SIGN(color);
    if (isPastHorizon && !isNoisyMove) return board->eval * SIGN(color);  // continues if noisy position
    if (isTooFarPastHorizon)           return board->eval * SIGN(color);  // too expensive


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

        if (score > alpha) alpha = score;  // save if best score
        if (alpha >= beta) break;  // prune if possible
        if (getIsTimeUp()) return alpha;
        
    }

    // store result
    int flag = 0;
    if (alpha <= oldAlpha) flag = -1;
    else if (alpha >= beta) flag = 1;
    storeTT(board->hash, depth, alpha, flag);

    return alpha;
}

Result iterativeDeepeningSearch(const Board* board, const int maxDepth, const int color) {

    pthread_mutex_lock(&time_mutex);
    UNWIND = false;
    pthread_mutex_unlock(&time_mutex);

    int score = -INF;

    int depth = 0;
    while (depth < maxDepth) {
        if (getIsTimeUp()) break;  // check if time is up

        score = principalVariationSearch(board, depth, -INF, INF, color);
        if (score >= CHECKMATE || score <= -CHECKMATE) break;  // if checkmate is found you can stop
        depth++;
    }

    setIsTimeUp(true);
    return (Result){score, depth};
}

void forceStopCalculations() {
    setIsTimeUp(true);
}

typedef struct {
    Board* pBoard;
    int maxDepth;
    int color;
} IDSArgs;

void* threadedIDS(void* arg) {
    const IDSArgs* args = (IDSArgs*)(arg);
    Result* pResult = malloc(sizeof(Result));
    *pResult = iterativeDeepeningSearch(args->pBoard, args->maxDepth, args->color);

    setIsCalculationFinished(true);

    return (void*)(pResult);
}

Result timeLimitedIterativeDeepeningSearch(Board* board, const int maxDepth, const int color, const double durationSeconds) {
    pthread_t monitor_thread;

    tt_collisions = 0;
    tt_probes     = 0;
    tt_hits       = 0;

    IDSArgs* args = malloc(sizeof(IDSArgs));
    if (!args) {
        fprintf(stderr, "Failed to allocate IDSArgs\n");
        return (Result){0, 0};
    }
    args->pBoard = board;
    args->maxDepth = maxDepth;
    args->color = color;

    setIsTimeUp(false);
    setIsCalculationFinished(false);

    pthread_create(&monitor_thread, NULL, threadedIDS, args);

    // --- Use high-resolution timer ---
    struct timespec start_time, current_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    while (true) {
    
        clock_gettime(CLOCK_MONOTONIC, &current_time);  // Get current time

        const double elapsed = (double)(current_time.tv_sec - start_time.tv_sec)
                             + (double)(current_time.tv_nsec - start_time.tv_nsec) / 1e9f;

        if (getIsCalculationFinished()) {
            printf("calculation finished \n");
            break;
        }
        // check for max time
        if (elapsed >= durationSeconds) {
            printf("calculation time up \n");
            break;
        }

        usleep(100000); // sleep 100ms to avoid busy spinning
    }

    // Signal the worker thread to stop if needed
    setIsTimeUp(true);

    // Join the monitor thread and retrieve result
    void* finalScore;
    pthread_join(monitor_thread, &finalScore);
    const Result result = *(Result*)(finalScore);
    free(finalScore);
    free(args);

    printf("tt_collisions = %llu \n", tt_collisions);
    printf("tt_probes     = %llu \n", tt_probes);
    printf("tt_hits       = %llu \n", tt_hits);

    return result;
}
