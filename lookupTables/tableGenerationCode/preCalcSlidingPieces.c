#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>



int rookRelevantBits[64] = {
    12, 11, 11, 11, 11, 11, 11, 12,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    12, 11, 11, 11, 11, 11, 11, 12
};

// Bishop relevant occupancy bits per square
int bishopRelevantBits[64] = {
     6,  5,  5,  5,  5,  5,  5,  6,
     5,  5,  5,  5,  5,  5,  5,  5,
     5,  5,  7,  7,  7,  7,  5,  5,
     5,  5,  7,  9,  9,  7,  5,  5,
     5,  5,  7,  9,  9,  7,  5,  5,
     5,  5,  7,  7,  7,  7,  5,  5,
     5,  5,  5,  5,  5,  5,  5,  5,
     6,  5,  5,  5,  5,  5,  5,  6
};

// Generate a random 64-bit unsigned integer
uint64_t random_uint64() {
    return  ((uint64_t)rand() & 0xFFFF) |
           (((uint64_t)rand() & 0xFFFF) << 16) |
           (((uint64_t)rand() & 0xFFFF) << 32) |
           (((uint64_t)rand() & 0xFFFF) << 48);
}

// Generate a sparse random magic candidate
uint64_t random_magic_candidate() {
    return random_uint64() & random_uint64() & random_uint64();
}

uint64_t rook_mask(const int sq) {
    uint64_t mask = 0ULL;
    const int rank = sq / 8;
    const int file = sq % 8;

    for (int f = file + 1; f < 7; f++) mask |= 1ULL << (rank * 8 + f);
    for (int f = file - 1; f > 0; f--) mask |= 1ULL << (rank * 8 + f);
    for (int r = rank + 1; r < 7; r++) mask |= 1ULL << (r * 8 + file);
    for (int r = rank - 1; r > 0; r--) mask |= 1ULL << (r * 8 + file);
    return mask;
}

uint64_t bishop_mask(const int sq) {
    uint64_t mask = 0ULL;
    const int rank = sq / 8;
    const int file = sq % 8;

    for (int r = rank + 1, f = file + 1; r < 7 && f < 7; r++, f++) mask |= 1ULL << (r * 8 + f); // NE
    for (int r = rank + 1, f = file - 1; r < 7 && f > 0; r++, f--) mask |= 1ULL << (r * 8 + f); // NW
    for (int r = rank - 1, f = file + 1; r > 0 && f < 7; r--, f++) mask |= 1ULL << (r * 8 + f); // SE
    for (int r = rank - 1, f = file - 1; r > 0 && f > 0; r--, f--) mask |= 1ULL << (r * 8 + f); // SW

    return mask;
}

int count_bits(uint64_t bb) {
    int count = 0;
    while (bb) { count++; bb &= bb - 1; }
    return count;
}


uint64_t set_occupancy(const int index, const int bits_in_mask, uint64_t mask) {
    assert (mask != 0);
    uint64_t occupancy = 0ULL;
    for (int i = 0; i < bits_in_mask; i++) {
        const int square = __builtin_ctzll(mask);
        mask &= mask - 1;

        if (index & (1 << i))
            occupancy |= 1ULL << square;
    }
    return occupancy;
}

uint64_t rook_attacks_on_the_fly(const int sq, const uint64_t blockers) {
    uint64_t attacks = 0ULL;
    const int rank = sq / 8;
    const int file = sq % 8;

    // Right
    for (int f = file + 1; f <= 7; f++) {
        attacks |= 1ULL << (rank * 8 + f);
        if (blockers & (1ULL << (rank * 8 + f))) break;
    }
    // Left
    for (int f = file - 1; f >= 0; f--) {
        attacks |= 1ULL << (rank * 8 + f);
        if (blockers & (1ULL << (rank * 8 + f))) break;
    }
    // Up
    for (int r = rank + 1; r <= 7; r++) {
        attacks |= 1ULL << (r * 8 + file);
        if (blockers & (1ULL << (r * 8 + file))) break;
    }
    // Down
    for (int r = rank - 1; r >= 0; r--) {
        attacks |= 1ULL << (r * 8 + file);
        if (blockers & (1ULL << (r * 8 + file))) break;
    }

    return attacks;
}

uint64_t bishop_attacks_on_the_fly(const int sq, const uint64_t blockers) {
    uint64_t attacks = 0ULL;
    const int rank = sq / 8;
    const int file = sq % 8;

    for (int r = rank + 1, f = file + 1; r <= 7 && f <= 7; r++, f++) {
        attacks |= 1ULL << (r * 8 + f);
        if (blockers & (1ULL << (r * 8 + f))) break;
    }
    for (int r = rank + 1, f = file - 1; r <= 7 && f >= 0; r++, f--) {
        attacks |= 1ULL << (r * 8 + f);
        if (blockers & (1ULL << (r * 8 + f))) break;
    }
    for (int r = rank - 1, f = file + 1; r >= 0 && f <= 7; r--, f++) {
        attacks |= 1ULL << (r * 8 + f);
        if (blockers & (1ULL << (r * 8 + f))) break;
    }
    for (int r = rank - 1, f = file - 1; r >= 0 && f >= 0; r--, f--) {
        attacks |= 1ULL << (r * 8 + f);
        if (blockers & (1ULL << (r * 8 + f))) break;
    }

    return attacks;
}

bool find_magic_number(
        const int sq,
        const int relevant_bits,
        uint64_t* magic,
        uint64_t* attacks_table,
        uint64_t (*move_on_the_fly_function)(int, uint64_t),
        uint64_t (*mask_function)(int),
        int maxEntries) {

    const uint64_t mask = mask_function(sq);
    const int num_entries = 1 << relevant_bits;

    uint64_t occupancies[maxEntries];
    uint64_t attacks[maxEntries];
    uint64_t used_attacks[maxEntries];

    // 1. Generate all occupancies and attacks
    for (int i = 0; i < num_entries; i++) {
        occupancies[i] = set_occupancy(i, relevant_bits, mask);
        attacks[i] = move_on_the_fly_function(sq, occupancies[i]);
    }

    // 2. Try random magic candidates
    for (int k = 0; k < 100000000; k++) {
        const uint64_t candidate = random_magic_candidate();

        memset(used_attacks, 0xFF, sizeof(used_attacks));  // use 0xFF to clearly mark unused entries
        bool fail = false;

        for (int i = 0; i < num_entries; i++) {
            uint64_t index = (occupancies[i] * candidate) >> (64 - relevant_bits);
            index &= (num_entries - 1);  // ensure index is in range

            if (used_attacks[index] == ~0ULL)
                used_attacks[index] = attacks[i];
            else if (used_attacks[index] != attacks[i]) {
                fail = true;
                break;
            }
        }

        if (!fail) {
            *magic = candidate;
            memcpy(attacks_table, used_attacks, sizeof(uint64_t) * num_entries);
            return true;
        }
    }
    return false;  // failed to find a magic number
}


void init_magic(
        uint64_t magicNumbers[],
        uint64_t attacksTable[],
        const int relevantBits[64],
        uint64_t (*move_on_the_fly_function)(int, uint64_t),
        uint64_t (*mask_function)(int),
        const int maxIndexBits) {

    for (int sq = 0; sq < 64; sq++) {
        uint64_t* table_ptr = &attacksTable[sq << maxIndexBits]; // 2^12 = 4096 max
        const int bits = relevantBits[sq];


        if (find_magic_number(sq, bits, &magicNumbers[sq], table_ptr,
                              move_on_the_fly_function, mask_function, 1 << maxIndexBits)) {
            printf("square %d\n", sq);
        } else {
            printf("Failed to find magic number for square %d\n", sq);
            exit(1);
        }
    }
}

void fprintUint64_tArray(FILE* file, const char* variableName, const int length, uint64_t array[64]) {
    fprintf(file, "const uint64_t %s[%d] = {\n", variableName, length);
    for (int i = 0; i < length; i++) {fprintf(file, "    0x%016llxULL,\n", array[i]);}
    fprintf(file, "};\n\n");
}

void fprintIntArray(FILE* file, const char* variableName, const int length, int array[64]) {
    fprintf(file, "const int %s[%d] = {\n", variableName, length);
    for (int i = 0; i < length; i++) {fprintf(file, "    %d,\n", array[i]);}
    fprintf(file, "};\n\n");
}


#define MAX_ROOK_INDEX_BITS 12
#define MAX_ROOK_ENTRIES (1 << MAX_ROOK_INDEX_BITS) // 4096

#define MAX_BISHOP_INDEX_BITS 9
#define MAX_BISHOP_ENTRIES (1 << MAX_BISHOP_INDEX_BITS) // 512

void generateCFile(const char* filename) {
    FILE* f = fopen(filename, "w");
    if (!f) {
        perror("Failed to open file for writing");
        exit(1);
    }

    // NB using this on the stack causes stackoverflow
    uint64_t *rookAttacksTable   = malloc(sizeof(uint64_t) * 64 * 4096);
    uint64_t *rookMagicNumbers   = malloc(sizeof(uint64_t) * 64);
    uint64_t *bishopAttacksTable = malloc(sizeof(uint64_t) * 64 * 512);
    uint64_t *bishopMagicNumbers = malloc(sizeof(uint64_t) * 64);

    for (int i = 0;  i < (64 * 4096); i++) {rookAttacksTable  [i] = UINT64_MAX;}
    for (int i = 0;  i < (64 * 512 ); i++) {bishopAttacksTable[i] = UINT64_MAX;}

    if (!rookAttacksTable || !rookMagicNumbers || !bishopAttacksTable || !bishopMagicNumbers) {
        fprintf(stderr, "Memory allocation failed in export_data\n");
        exit(1);
    }
    fprintf(f, "#include <stdint.h>\n\n");

    uint64_t rookMasks[64];
    for (int i = 0; i < 64; i++) {rookMasks[i] = rook_mask(i);}

    init_magic(
        rookMagicNumbers,
        rookAttacksTable,
        rookRelevantBits,
        rook_attacks_on_the_fly,
        rook_mask,
        MAX_ROOK_INDEX_BITS
        );
    fprintIntArray     (f, "rookRelevantBits", 64       , rookRelevantBits);
    fprintUint64_tArray(f, "rookMasks"       , 64       , rookMasks       );
    fprintUint64_tArray(f, "rookAttacksTable", 64 * 4096, rookAttacksTable);
    fprintUint64_tArray(f, "rookMagicNumbers", 64       , rookMagicNumbers);

    uint64_t bishopMasks[64];
    for (int i = 0; i < 64; i++) {bishopMasks[i] = bishop_mask(i);}

    init_magic(
        bishopMagicNumbers,
        bishopAttacksTable,
        bishopRelevantBits,
        bishop_attacks_on_the_fly,
        bishop_mask,
        MAX_BISHOP_INDEX_BITS
        );

    fprintIntArray     (f, "bishopRelevantBits", 64      , bishopRelevantBits);
    fprintUint64_tArray(f, "bishopMasks"       , 64      , bishopMasks       );
    fprintUint64_tArray(f, "bishopAttacksTable", 64 * 512, bishopAttacksTable);
    fprintUint64_tArray(f, "bishopMagicNumbers", 64      , bishopMagicNumbers);

    free(rookAttacksTable);
    free(rookMagicNumbers);
    free(bishopAttacksTable);
    free(bishopMagicNumbers);
}


void generateHeaderFile(const char* filename) {
    FILE* f = fopen(filename, "w");
    if (!f) {
        perror("Failed to open file for writing");
        exit(1);
    }

    fprintf(f, "#ifndef MAGIC_H\n#define MAGIC_H\n\n");
    fprintf(f, "#define MAGIC_H\n");
    fprintf(f, "#include <stdint.h>\n\n");

    fprintf(f, "extern const int      rookRelevantBits[64];\n");
    fprintf(f, "extern const uint64_t rookMasks       [64       ];\n");
    fprintf(f, "extern const uint64_t rookAttacksTable[64 * 4096];\n");
    fprintf(f, "extern const uint64_t rookMagicNumbers[64       ];\n");

    fprintf(f, "extern const int      bishopRelevantBits[64];\n");
    fprintf(f, "extern const uint64_t bishopMasks       [64      ];\n");
    fprintf(f, "extern const uint64_t bishopAttacksTable[64 * 512];\n");
    fprintf(f, "extern const uint64_t bishopMagicNumbers[64      ];\n");

    fprintf(f, "\n#endif");
}


int main() {
    srand(1804289383); // Seed for reproducibility
    generateCFile     ("lookupSlidingMoves.c");
    generateHeaderFile("lookupSlidingMoves.h");
    return 0;
}


