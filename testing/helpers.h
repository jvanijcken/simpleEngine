//
// Created by jvani on 22/09/2025.
//

#ifndef SIMPLEENGINE_HELPERS_H
#define SIMPLEENGINE_HELPERS_H

#include "../include/globals.h"

void printBoard(const Board* board, int indent);
void printIndexAsCoords(int index);
void printMove(uint64_t start, uint64_t end);
void printUint(uint64_t value);

#endif //SIMPLEENGINE_HELPERS_H