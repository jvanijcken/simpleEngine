//
// Created by jvani on 21/09/2025.
//
#include "../include/transpositionTable.h"
#include "../include/attackTables.h"
#include "../include/magicBitboards.h"

#define MAX_ROOK_INDEX_BITS 12
#define MAX_ROOK_ENTRIES (1 << MAX_ROOK_INDEX_BITS) // 4096
#define MAX_BISHOP_INDEX_BITS 9
#define MAX_BISHOP_ENTRIES (1 << MAX_BISHOP_INDEX_BITS) // 512

uint64_t pawnMoves(const int square, const Board* board, const int color) {

    if (color) {  // black!
        const uint64_t attacks = blackPawnAttackLookup[square] &  (board->colors[!color] | board->enPassant);
        const uint64_t pushes  = blackPawnWalkLookup  [square] & ~(board->colors[ color] | board->colors[!color]);

        if ((RANK7 & (1ULL << square)) && (pushes != 0) ) {  // second push
            const uint64_t secondPush = pushes << 8 & ~(board->colors[color] | board->colors[!color]);
            return attacks | pushes | secondPush;
        }
        return attacks | pushes;
    } else {  // white!
        const uint64_t attacks = whitePawnAttackLookup[square] &  (board->colors[!color] | board->enPassant);
        const uint64_t pushes  = whitePawnWalkLookup  [square] & ~(board->colors[ color] | board->colors[!color]);

        if ((RANK2 & (1ULL << square)) && (pushes != 0)) {  // second push
            const uint64_t secondPush = pushes >> 8 & ~(board->colors[color] | board->colors[!color]);
            return attacks | pushes | secondPush;}
        return attacks | pushes;
    }
}
uint64_t knightMoves(const int square, const Board* board, const int color) {
    const uint64_t moves = knightMovesLookup[square] & ~board->colors[color];
    return moves;
}
uint64_t kingMoves(const int square, const Board* board, const int color) {
    const uint64_t moves = kingMovesLookup[square] & ~board->colors[color];
    return moves;  // castling logic is handled in the general move generator
}
uint64_t rookAttacks(const int square, const Board* board, const int color) {
    uint64_t occupancy = board->colors[color] | board->colors[!color];

    occupancy &= rookMasks[square];
    occupancy *= rookMagicNumbers[square];
    occupancy >>= (64 - rookRelevantBits[square]);

    const uint64_t magic = (square * MAX_ROOK_ENTRIES) + occupancy;
    const uint64_t result = rookAttacksTable[magic] & ~board->colors[color];

    return result;
}
uint64_t bishopAttacks(const int square, const Board* board, const int color) {
    uint64_t occupancy = board->colors[color] | board->colors[!color];

    occupancy &= bishopMasks[square];
    occupancy *= bishopMagicNumbers[square];
    occupancy >>= (64 - bishopRelevantBits[square]);

    const uint64_t magic = (square * MAX_BISHOP_ENTRIES) + occupancy;
    const uint64_t result = bishopAttacksTable[magic] & ~board->colors[color];

    return result;
}
uint64_t queenMoves(const int square, const Board* board, const int color) {
    const uint64_t orthogonal = rookAttacks(square, board, color);
    const uint64_t diagonal = bishopAttacks(square, board, color);
    const uint64_t result = orthogonal | diagonal;
    return result;
}
MoveFunction moveFunctions[PIECE_COUNT] = {
    pawnMoves,
    rookAttacks,
    knightMoves,
    bishopAttacks,
    queenMoves,
    kingMoves,
};
