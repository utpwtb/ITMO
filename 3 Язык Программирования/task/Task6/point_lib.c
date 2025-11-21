#include "stdio.h"
#include <math.h>

typedef struct Point {
    int x;
    int y;
} Point;

// __declspec(dllexport)
void process_points(Point* pointsA, Point* pointsB, size_t count, double* results) {
    for (size_t i = 0; i < count; i++) {
        int dx = pointsA[i].x - pointsB[i].x;
        int dy = pointsA[i].y - pointsB[i].y;
        results[i] = sqrt(dx*dx + dy*dy);
    }
}