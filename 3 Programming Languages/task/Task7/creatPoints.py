import ctypes
import random

class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)] 

def create_point_file(filename, num_pairs=1000):
    with open(filename, 'w') as f:
        for i in range(num_pairs):
            x1, y1 = random.randint(-100, 100), random.randint(-100, 100)
            x2, y2 = random.randint(-100, 100), random.randint(-100, 100)
            f.write(f"{x1},{y1} {x2},{y2}\n")

if __name__ == "__main__":
    create_point_file("points.txt")

