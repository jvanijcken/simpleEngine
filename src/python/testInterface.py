import PyChess
print(dir(PyChess))

b = PyChess.Board([-1] * 64, [0] * 4, -1, 0)
print(b.color)
print("b =", b)
print("b.color =", getattr(b, "color", None))

result = PyChess.pyIDS(b, b.color, 3, 2)
print(f"{result = }")


if __name__ == "__main__":
    pass