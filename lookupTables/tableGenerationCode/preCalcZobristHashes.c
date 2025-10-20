//
// Created by jvani on 08/10/2025.
//


#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>


uint64_t random_uint64() {
    return  ((uint64_t)rand() & 0xFFFF) |
           (((uint64_t)rand() & 0xFFFF) << 16) |
           (((uint64_t)rand() & 0xFFFF) << 32) |
           (((uint64_t)rand() & 0xFFFF) << 48);
}

void generateCFile(const char* filename) {
    FILE* f = fopen(filename, "w");
    if (!f) {
        perror("Failed to open file for writing");
        exit(1);
    }
    fprintf(f, "#include <stdint.h>\n\n");

    fprintf(f, "const uint64_t colorHash = %" PRIu64 ";\n\n", random_uint64());

    fprintf(f, "uint64_t tableHash[2][6][64] = {\n");
    for (int color = 0; color < 2; color++) {
        fprintf(f, "\t{\n");
        for (int piece = 0; piece < 6; piece++) {
            fprintf(f, "\t{\n");
            for (int i = 0; i < 64; i++) {
                fprintf(f, "%" PRIu64 ", \n", random_uint64());
            }
            fprintf(f, "\t}, \n");
        }
        fprintf(f, "\t}, \n");
    }
    fprintf(f, "};\n");
}


void generateHeaderFile(const char* filename) {
    FILE* f = fopen(filename, "w");
    if (!f) {
        perror("Failed to open file for writing");
        exit(1);
    }

    fprintf(f, "#ifndef ZOBRIST_H\n#define ZOBRIST_H\n\n");

    fprintf(f, "#define ZOBRIST_H\n");
    fprintf(f, "#include <stdint.h>\n\n");

    fprintf(f, "extern const uint64_t colorHash;\n\n");

    fprintf(f, "extern const uint64_t tableHash[2][6][64];\n");

    fprintf(f, "\n#endif");
}

int main() {
    srand(1804289383); // Seed for reproducibility
    generateCFile     ("zobristHashing.c");
    generateHeaderFile("zobristHashing.h");
    return 0;
}