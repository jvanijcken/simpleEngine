#ifndef MAGIC_H
#define MAGIC_H

#define MAGIC_H
#include <stdint.h>

extern const int      rookRelevantBits[64];
extern const uint64_t rookMasks       [64       ];
extern const uint64_t rookAttacksTable[64 * 4096];
extern const uint64_t rookMagicNumbers[64       ];
extern const int      bishopRelevantBits[64];
extern const uint64_t bishopMasks       [64      ];
extern const uint64_t bishopAttacksTable[64 * 512];
extern const uint64_t bishopMagicNumbers[64      ];

#endif