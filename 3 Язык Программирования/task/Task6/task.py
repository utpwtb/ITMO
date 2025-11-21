import ctypes
import random
import os

class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)] 

def create_point_file(filename, num_pairs=1000):
    with open(filename, 'w') as f:
        for i in range(num_pairs):
            x1, y1 = random.randint(0, 100), random.randint(0, 100)
            x2, y2 = random.randint(0, 100), random.randint(0, 100)
            f.write(f"{x1},{y1} {x2},{y2}\n")

def load_points(filename="points.txt"):
    pointsA = []
    pointsB = []
    with open(filename, "r") as f:
        for line in f:
            A, B = line.strip().split(" ")
            x1, y1 = map(int, A.split(","))
            x2, y2 = map(int, B.split(","))

            pointsA.append(Point(x1, y1))
            pointsB.append(Point(x2, y2))
    return pointsA, pointsB

if __name__ == "__main__":
    print("Start program")

    create_point_file("points.txt")

    pointsA, pointsB = load_points()
    count = len(pointsA)

    lib_name = "point_lib.dll" if os.name == "nt" else "point_lib.so"
    lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), lib_name)
    

    try:
        c_lib = ctypes.CDLL(lib_path)
        print(f"Библиотека успешно загружена: {lib_path}")
    except Exception as e:
        print(f"ОШИБКА: Не удалось загрузить библиотеку '{lib_path}'")
        print(f"Детали ошибки: {e}")
        exit()

    c_lib.process_points.argtypes = [
        ctypes.POINTER(Point),
        ctypes.POINTER(Point),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double)
    ]
    c_lib.process_points.restype = None

    ArrayPoint = Point * count
    ArrayDouble = ctypes.c_double * count

    arrA = ArrayPoint(*pointsA)
    arrB = ArrayPoint(*pointsB)
    results = ArrayDouble()

    c_lib.process_points(arrA, arrB, count, results)

    print("Результаты:")
    for i in range(count):
        print(f"{i+1}) distance = {results[i]}")