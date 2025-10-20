//
// Created by jvani on 21/09/2025.
//

#ifndef SIMPLEENGINE_GLOBALS_H
#define SIMPLEENGINE_GLOBALS_H

#include <stdbool.h>
#include <stdint.h>

#define NO_PIECE (-1)
#define NO_MOVE (-1)
#define ROW_LENGTH 8
#define BOARD_SIZE 64

#define A8 (1ULL << 0)
#define B8 (1ULL << 1)
#define C8 (1ULL << 2)
#define D8 (1ULL << 3)
#define E8 (1ULL << 4)
#define F8 (1ULL << 5)
#define G8 (1ULL << 6)
#define H8 (1ULL << 7)

#define A7 (1ULL << 8)
#define B7 (1ULL << 9)
#define C7 (1ULL << 10)
#define D7 (1ULL << 11)
#define E7 (1ULL << 12)
#define F7 (1ULL << 13)
#define G7 (1ULL << 14)
#define H7 (1ULL << 15)

#define A6 (1ULL << 16)
#define B6 (1ULL << 17)
#define C6 (1ULL << 18)
#define D6 (1ULL << 19)
#define E6 (1ULL << 20)
#define F6 (1ULL << 21)
#define G6 (1ULL << 22)
#define H6 (1ULL << 23)

#define A5 (1ULL << 24)
#define B5 (1ULL << 25)
#define C5 (1ULL << 26)
#define D5 (1ULL << 27)
#define E5 (1ULL << 28)
#define F5 (1ULL << 29)
#define G5 (1ULL << 30)
#define H5 (1ULL << 31)

#define A4 (1ULL << 32)
#define B4 (1ULL << 33)
#define C4 (1ULL << 34)
#define D4 (1ULL << 35)
#define E4 (1ULL << 36)
#define F4 (1ULL << 37)
#define G4 (1ULL << 38)
#define H4 (1ULL << 39)

#define A3 (1ULL << 40)
#define B3 (1ULL << 41)
#define C3 (1ULL << 42)
#define D3 (1ULL << 43)
#define E3 (1ULL << 44)
#define F3 (1ULL << 45)
#define G3 (1ULL << 46)
#define H3 (1ULL << 47)

#define A2 (1ULL << 48)
#define B2 (1ULL << 49)
#define C2 (1ULL << 50)
#define D2 (1ULL << 51)
#define E2 (1ULL << 52)
#define F2 (1ULL << 53)
#define G2 (1ULL << 54)
#define H2 (1ULL << 55)

#define A1 (1ULL << 56)
#define B1 (1ULL << 57)
#define C1 (1ULL << 58)
#define D1 (1ULL << 59)
#define E1 (1ULL << 60)
#define F1 (1ULL << 61)
#define G1 (1ULL << 62)
#define H1 (1ULL << 63)

#define RANK1 (A1 | B1 | C1 | D1 | E1 | F1 | G1 | H1)
#define RANK2 (A2 | B2 | C2 | D2 | E2 | F2 | G2 | H2)
#define RANK3 (A3 | B3 | C3 | D3 | E3 | F3 | G3 | H3)
#define RANK4 (A4 | B4 | C4 | D4 | E4 | F4 | G4 | H4)
#define RANK5 (A5 | B5 | C5 | D5 | E5 | F5 | G5 | H5)
#define RANK6 (A6 | B6 | C6 | D6 | E6 | F6 | G6 | H6)
#define RANK7 (A7 | B7 | C7 | D7 | E7 | F7 | G7 | H7)
#define RANK8 (A8 | B8 | C8 | D8 | E8 | F8 | G8 | H8)

#define WHITE 0
#define BLACK 1

#define TT_SIZE (1 << 20)  // ~1M entries
#define TT_INDEX(hash) ((hash) & (TT_SIZE - 1))

#define SIGN(color) ((color) == 0 ? 1 : -1)

typedef enum {
    P,
    R,
    N,
    B,
    Q,
    K,
    PIECE_COUNT
} Pieces;

typedef struct {
    uint64_t pieces[2][6];
    uint64_t colors[2];
    uint64_t enPassant;
    uint64_t hash;
    uint8_t  castle;
    int moveIndex;
    int eval;
} Board;


typedef uint64_t (*MoveFunction)(int, const Board*, int);

typedef struct {
    uint64_t hash;
    int depth;
    int score;
    int flag;  // 0 = exact, -1 = alpha, +1 = beta
} TTEntry;

extern TTEntry transTable[TT_SIZE];



#define BLACK_QUEENSIDE (1ULL << 0)
#define BLACK_KINGSIDE  (1ULL << 1)
#define WHITE_QUEENSIDE (1ULL << 2)
#define WHITE_KINGSIDE  (1ULL << 3)

#define BLACK_CASTLES (1ULL << 0 | 1ULL << 1)
#define WHITE_CASTLES (1ULL << 2 | 1ULL << 3)

//extern const uint64_t kingStartPositions[CASTLE_MOVE_COUNT];
//extern const uint64_t kingEndPositions  [CASTLE_MOVE_COUNT];
//extern const uint64_t freeCastleSquares [CASTLE_MOVE_COUNT];
//extern const uint64_t safeCastleSquares [CASTLE_MOVE_COUNT];
//extern const uint64_t rookStartPositions[CASTLE_MOVE_COUNT];
//extern const uint64_t rookEndPositions  [CASTLE_MOVE_COUNT];
//extern const uint8_t  castleRights      [CASTLE_MOVE_COUNT];


#endif //SIMPLEENGINE_GLOBALS_H