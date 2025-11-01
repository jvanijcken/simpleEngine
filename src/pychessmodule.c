//
// Created by jvani on 20/10/2025.
//

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <math.h>
#include "../include/transpositionTable.h"
#include "../include/algorithms.h"
#include "../include/zobristHashing.h"
#include "../include/boardEvaluation.h"

// HELPER FUNCTIONS
uint64_t zobristHash(const Board* board, const int color) {
    uint64_t key = 0ULL;

    for (int c = 0; c < 2; c++) {
        for (int piece = 0; piece < 6; piece++) {
            uint64_t pieces = board->pieces[c][piece];

            while (pieces) {
                const int index = __builtin_ctzll(pieces);
                key ^= tableHash[c][piece][index];
                pieces &= pieces - 1;
            }
        }
    }

    if (color) {
        key ^= colorHash;
    }
    return key;
}


int evaluateBoard(const Board *pBoard) {
    int score = 0;

    for (int c = 0; c < 2; c++) {
        for (int p = 0; p < 6; p++) {
            uint64_t pieces = pBoard->pieces[c][p];
            while (pieces) {
                const int index = __builtin_ctzll(pieces);
                pieces &= pieces - 1;  // had a bug before (accidentally used pieces &= -pieces) -> caused infinite loop
                score += pieceEvaluators[c][p][index];
            }
        }
    }
    return score;
}

// IMPORTABLE FUNCTION
static PyObject *
time_limited_iterative_deepening_search(PyObject *self, PyObject *args)
{
    PyObject *pieces_list = NULL;
    PyObject *castle_rights_list = NULL;
    int en_passant = 0;
    int color = 0;
    int maxDepth = 0;
    double durationSeconds = 0.0;

    // Parse Python arguments: (pieces, en_passant, castle_rights, color, maxDepth, duration_seconds)
    if (!PyArg_ParseTuple(
            args, "OOiiid",
            &pieces_list,
            &castle_rights_list,
            &en_passant,
            &color,
            &maxDepth,
            &durationSeconds))
    {
        return NULL;
    }

    // --- Validate input types ---
    if (!PyList_Check(pieces_list)) {
        PyErr_SetString(PyExc_TypeError, "pieces must be a list of ints");
        return NULL;
    }
    if (!PyList_Check(castle_rights_list)) {
        PyErr_SetString(PyExc_TypeError, "castle_rights must be a list of ints");
        return NULL;
    }

    // --- Build C board struct ---
    Board board = {0};

    // Convert pieces list → C array
    // add pieces
    for (int i = 0; i < 64; i++) {
        PyObject *item = PyList_GetItem(pieces_list, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "pieces list must contain ints");
            return NULL;
        }
        const int coloredPiece = (int)PyLong_AsLong(item);

        if (coloredPiece == NO_PIECE) continue;  // another bug fix
        const int c = coloredPiece / 6;
        const int p = coloredPiece % 6;
        board.pieces[c][p] |= (1ULL << i);
    }

    // add colors
    board.colors[WHITE] = board.pieces[WHITE][P] | board.pieces[WHITE][R] | board.pieces[WHITE][N] |
                          board.pieces[WHITE][B] | board.pieces[WHITE][Q] | board.pieces[WHITE][K];
    board.colors[BLACK] = board.pieces[BLACK][P] | board.pieces[BLACK][R] | board.pieces[BLACK][N] |
                          board.pieces[BLACK][B] | board.pieces[BLACK][Q] | board.pieces[BLACK][K];

    // Convert castle_rights list → C array
    const Py_ssize_t num_rights = PyList_Size(castle_rights_list);
    for (Py_ssize_t i = 0; i < num_rights && i < 4; i++) {
        PyObject *item = PyList_GetItem(castle_rights_list, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "castle_rights list must contain ints");
            return NULL;
        }
        const int hasRight = (int)PyLong_AsLong(item);
        board.castle |= (hasRight)? 1ULL << i : 0ULL;
    }

    board.enPassant = (en_passant == NO_MOVE)? 0ULL : 1ULL << en_passant;

    board.hash = zobristHash(&board, color);
    board.eval = evaluateBoard(&board);

    // --- Run the core search ---
    const Result result = timeLimitedIterativeDeepeningSearch(&board, maxDepth, color, durationSeconds);

    // --- Return just the score ---
    return Py_BuildValue("(ii)", result.score, result.depth);
}



// IMPORTABLE FUNCTION
static PyObject *
iterative_deepening_search(PyObject *self, PyObject *args)
{
    PyObject *pieces_list = NULL;
    PyObject *castle_rights_list = NULL;
    int en_passant = 0;
    int color = 0;
    int maxDepth = 0;

    // Parse Python arguments: (pieces, en_passant, castle_rights, color, maxDepth, duration_seconds)
    if (!PyArg_ParseTuple(
            args, "OOiii",
            &pieces_list,
            &castle_rights_list,
            &en_passant,
            &color,
            &maxDepth))
    {
        return NULL;
    }

    // --- Validate input types ---
    if (!PyList_Check(pieces_list)) {
        PyErr_SetString(PyExc_TypeError, "pieces must be a list of ints");
        return NULL;
    }
    if (!PyList_Check(castle_rights_list)) {
        PyErr_SetString(PyExc_TypeError, "castle_rights must be a list of ints");
        return NULL;
    }

    // --- Build C board struct ---
    Board board = {0};

    // Convert pieces list → C array
    // add pieces
    for (int i = 0; i < 64; i++) {
        PyObject *item = PyList_GetItem(pieces_list, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "pieces list must contain ints");
            return NULL;
        }
        const int coloredPiece = (int)PyLong_AsLong(item);

        if (coloredPiece == NO_PIECE) continue;  // another bug fix
        const int c = coloredPiece / 6;
        const int p = coloredPiece % 6;
        board.pieces[c][p] |= (1ULL << i);
    }

    // add colors
    board.colors[WHITE] = board.pieces[WHITE][P] | board.pieces[WHITE][R] | board.pieces[WHITE][N] |
                          board.pieces[WHITE][B] | board.pieces[WHITE][Q] | board.pieces[WHITE][K];
    board.colors[BLACK] = board.pieces[BLACK][P] | board.pieces[BLACK][R] | board.pieces[BLACK][N] |
                          board.pieces[BLACK][B] | board.pieces[BLACK][Q] | board.pieces[BLACK][K];

    // Convert castle_rights list → C array
    const Py_ssize_t num_rights = PyList_Size(castle_rights_list);
    for (Py_ssize_t i = 0; i < num_rights && i < 4; i++) {
        PyObject *item = PyList_GetItem(castle_rights_list, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "castle_rights list must contain ints");
            return NULL;
        }
        const int hasRight = (int)PyLong_AsLong(item);
        board.castle |= (hasRight)? 1ULL << i : 0ULL;
    }

    board.enPassant = (en_passant == NO_MOVE)? 0ULL : 1ULL << en_passant;

    board.hash = zobristHash(&board, color);
    board.eval = evaluateBoard(&board);

    // --- Run the core search ---
    const Result result =  iterativeDeepeningSearch(&board, maxDepth, color);

    // --- Return just the score ---
    return Py_BuildValue("(ii)", result.score, result.depth);
}

// MODULE


// IMPORTABLE FUNCTION
static PyObject *
force_stop_calculations(PyObject *self, PyObject *args)
{
    forceStopCalculations();
    Py_RETURN_NONE;
}

static PyMethodDef PyChessMethods[] = {
    {
        "time_limited_iterative_deepening_search",
        time_limited_iterative_deepening_search,
        METH_VARARGS,
        "Call time_limited_iterative_deepening_search function"
    },
    {
        "iterative_deepening_search",
        iterative_deepening_search,
        METH_VARARGS,
        "Call iterative_deepening_search function"
    },
    {
        "force_stop_calculations",
        force_stop_calculations,
        METH_VARARGS,
        "Call force_stop_calculations function"
    },
    {
        NULL, NULL, 0, NULL
    }
};

// Module definition
static PyModuleDef pychessmodule = {
    PyModuleDef_HEAD_INIT,
    "PyChess",
    "Python Chess module with Board object",
    -1,
    PyChessMethods,  // <- attach methods here!
    NULL, NULL, NULL, NULL
};


// Module initialization
PyMODINIT_FUNC
PyInit_PyChess(void) {

    PyObject *m = PyModule_Create(&pychessmodule);
    if (m == NULL)
        return NULL;

    return m;
}
