import PyChess
print(dir(PyChess))

b = PyChess.Board([-1] * 64, [0] * 4, -1, 0)
print(b.color)

if __name__ == "__main__":
    pass