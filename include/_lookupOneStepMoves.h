#ifndef LOOKUP_H
#define LOOKUP_H

#define LOOKUP_H
#include <stdint.h>

extern const uint64_t whitePawnWalkLookup  [64];
extern const uint64_t whitePawnAttackLookup[64];
extern const uint64_t blackPawnWalkLookup  [64];
extern const uint64_t blackPawnAttackLookup[64];
extern const uint64_t knightMovesLookup    [64];
extern const uint64_t kingMovesLookup      [64];
#endif