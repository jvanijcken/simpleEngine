//
// Created by jvani on 21/09/2025.
//

#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#include "../include/_globals.h"
#include "../include/moveGeneration.h"

bool UNWIND = true;
bool CALCULATION_FINISHED = true;
pthread_mutex_t time_mutex = PTHREAD_MUTEX_INITIALIZER;


TTEntry* probeTT(const uint64_t hash) {
    TTEntry* e = &transTable[TT_INDEX(hash)];
    return (e->hash == hash) ? e : NULL;
}

void storeTT(const uint64_t hash, const int depth, const int score, const int flag) {
    TTEntry* e = &transTable[TT_INDEX(hash)];
    e->hash = hash;
    e->depth = depth;
    e->score = score;
    e->flag = flag;
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


int (*colorSort(const int color))(const void*, const void*) {
    return color? &sortDescBlack : &sortDescWhite;
}


int principalVariationSearch(const Board* board, const int depth, int alpha, const int beta, const int color, Board bestSeq[]) {

    bestSeq[0] = *board;

    // check if cached
    const TTEntry* entry = probeTT(board->hash);
    if (entry && entry->depth >= depth) {
        if (entry->flag == 0)  return entry->score;
        if (entry->flag == -1 && entry->score <= alpha) return alpha;
        if (entry->flag ==  1 && entry->score >= beta)  return beta;
    }

    // check if time is up
    pthread_mutex_lock(&time_mutex);
    bool unwind = UNWIND;
    pthread_mutex_unlock(&time_mutex);

    if (depth == 0 || unwind) {
        return board->eval * SIGN(color);  // eval from MY perspective
    }
    Board results[512];

    const int nrOfMoves = generateMoves(board, results, false, color);

    if (nrOfMoves == 0 && isInCheck(board, color)) return (-CHECKMATE - depth);
    if (nrOfMoves == 0) return 0;

    // order with estimated best moves first
    qsort(results, nrOfMoves, sizeof(Board), colorSort(color));

    const int oldAlpha = alpha;  // save for caching
    for (int i = 0; i < nrOfMoves; i++) {


        Board localBestSeq[depth];
        memset(localBestSeq, 0, sizeof(localBestSeq));

        int score;

        if (i == 0) {
            // principal search (presumed best move)
            score = - principalVariationSearch(&results[i], depth - 1, - beta     , -alpha, !color, localBestSeq);
        } else {
            // scout search (cheap)
            score = - principalVariationSearch(&results[i], depth - 1, - alpha - 1, -alpha, !color, localBestSeq);

            // use full search if scout failed (presumed best move wasn't the best move)
            if (alpha < score && score < beta) {
                score = - principalVariationSearch(&results[i], depth - 1, -beta, -alpha, !color, localBestSeq);
            }
        }

        // save if best score
        if (score > alpha) {
            alpha = score;
            for (int x = 0; x < depth; x++) {bestSeq[x + 1] = localBestSeq[x];}  // copy
        }
        // prune if possible
        if (alpha >= beta) {
            break;
        }

        // check if time is up
        pthread_mutex_lock(&time_mutex);
        unwind = UNWIND;
        pthread_mutex_unlock(&time_mutex);
        if (unwind) {
            printf("SCR %d\n", alpha);
            return alpha;
        }

    }
    // store hash
    int flag = 0;
    if (alpha <= oldAlpha) flag = -1;
    else if (alpha >= beta) flag = 1;
    storeTT(board->hash, depth, alpha, flag);

    return alpha;
}

void* updateUnwind(void* arg) {
    const int seconds = *(int*)arg;
    const time_t start_time = time(NULL);
    const time_t end_time = start_time + seconds;

    // Set unwind to false (allows computation)
    pthread_mutex_lock(&time_mutex);
    UNWIND = false;
    pthread_mutex_unlock(&time_mutex);

    printf("[Timer] Looping for %d seconds...\n", seconds);

    while (time(NULL) < end_time) {
        usleep(100000);  // sleep 100ms to avoid busy spinning
    }

    // Set the flag to false
    pthread_mutex_lock(&time_mutex);
    UNWIND = true;  // Set unwind to true (stops computation)
    pthread_mutex_unlock(&time_mutex);

    printf("[Timer] Done!\n");
    return NULL;
}

int iterativeDeepeningSearch(const Board* board, const int maxDepth, const int color,
        Board bestSeq[]) {

    pthread_mutex_lock(&time_mutex);
    UNWIND = false;
    pthread_mutex_unlock(&time_mutex);

    int score = -INF;
    for (int depth = 0; depth < maxDepth; depth++) {
        // check if time is up
        pthread_mutex_lock(&time_mutex);
        const bool unwind = UNWIND;
        pthread_mutex_unlock(&time_mutex);
        if (unwind) break;

        score = principalVariationSearch(board, depth, -INF, INF, color, bestSeq);
        printf("Q %d\n", score);
    }
    pthread_mutex_lock(&time_mutex);
    UNWIND = true;
    pthread_mutex_unlock(&time_mutex);
    printf("PR %d\n", score);
    return score;
}

typedef struct {
    Board* pBoard;
    int maxDepth;
    int color;
    Board* bestSeq;
} IDSArgs;

void* wrappedIDS(void* arg) {
    const IDSArgs* args = (IDSArgs*)(arg);
    int* result = malloc(sizeof(int));
    *result = iterativeDeepeningSearch(args->pBoard, args->maxDepth, args->color, args->bestSeq);

    pthread_mutex_lock(&time_mutex);
    CALCULATION_FINISHED = true;
    pthread_mutex_unlock(&time_mutex);

    return (void*)(result);
}

int timeLimitedIterativeDeepeningSearch(Board* board, const int maxDepth, const int color,
        Board bestSeq[], const int durationSeconds) {
    pthread_t monitor_thread;

    IDSArgs args = {board, maxDepth, color, bestSeq};

    UNWIND = false;  // no threads yet, so we can safely set this variable
    CALCULATION_FINISHED = false;

    pthread_create(&monitor_thread, NULL, wrappedIDS, &args);

    const time_t start_time = time(NULL);
    const time_t end_time = start_time + durationSeconds;

    while (true) {

        // check if calculation finished
        pthread_mutex_lock(&time_mutex);
        const bool finished = CALCULATION_FINISHED;
        pthread_mutex_unlock(&time_mutex);
        if (finished) {
            break;
        }

        // check for max time
        if (time(NULL) >= end_time) {
            break;
        }
        usleep(100000);  // sleep 100ms to avoid busy spinning
    }

    // Set unwind to true (stops computation if computation is still running)
    pthread_mutex_lock(&time_mutex);
    UNWIND = true;
    pthread_mutex_unlock(&time_mutex);

    // get the result of our thread
    void* finalScore;
    pthread_join(monitor_thread, &finalScore);
    const int result = *(int*)(finalScore);
    free(finalScore);

    return result;

}
