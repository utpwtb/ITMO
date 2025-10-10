#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int x;
    int y;
} Point;

typedef enum {
    Triangle,
    Square,
    Circle
} ShapeType;

typedef struct {
    Point p;
    ShapeType type;
    char* name;
} Shape;

typedef struct {
    Shape* shapes;
    int size;
} Container;


Container* init_container();
void add_new_shape(Container* ct, Point p, char* name, ShapeType type);
void print(Container* ct);
void remove_shape_by_index(Container* ct, int i);

int main() {
   Container* ct = init_container();

    // TODO:
    // add_new_shape
    // print
    // remove_shape_by_index
    add_new_shape(ct, (Point) { 1, 2 }, "triangle1", Triangle);
    add_new_shape(ct, (Point) { 3, 4 }, "square1", Square);
    add_new_shape(ct, (Point) { 5, 6 }, "circle", Circle);
    print(ct);
    remove_shape_by_index(ct, 0);
    print(ct);
    free(ct->shapes);
    free(ct);
    return 0;
}

Container* init_container() {
    Container* ct = malloc(sizeof(Container));
    ct->shapes = NULL;
    ct->size = 0;
    return ct;
}

void add_new_shape(Container* ct, Point p, char* name, ShapeType type) {
    init_container();

    Shape* temp= realloc(ct->shapes, (ct->size + 1) * sizeof(Shape));
    if (temp== NULL) {
        return;
    }
    ct->shapes = temp;

    ct->shapes[ct->size].p = p;
    ct->shapes[ct->size].type = type;

    ct->shapes[ct->size].name = malloc(strlen(name) + 1);
    strcpy(ct->shapes[ct->size].name, name);

    ct->size++;
}

void print(Container* ct) {
    printf("Size of Container: %d\n", ct->size);
    for (int i = 0; i < ct->size; i++)
    {
        Shape s = ct->shapes[i];

        char* type;
        if (s.type == Triangle)
        {
            type = "Triangle";
        }
        else if(s.type == Square)
        {
            type = "Square";
        }
        else if(s.type == Circle)
        {
            type = "Circle";
        }
        else
        {
            type = "NULL";
        }

        printf("Shape%d : name=%s type=%s pos=(%d,%d)\n",
            i, s.name, type, s.p.x, s.p.y);
    }
}

void remove_shape_by_index(Container* ct, int i) {
    free(ct->shapes[i].name);

    for (int j = i; j < ct->size - 1; j++) {
        ct->shapes[j] = ct->shapes[j + 1];
    }

    

    Shape* temp = realloc(ct->shapes, ct->size * sizeof(Shape));
    // TODO if
    if (temp == NULL)
    {
        return;
    }
    ct->shapes = temp;

    ct->size--;
}