#define DLLEXPORT __declspec(dllexport)

typedef struct 
{
    int x;
    int y;
} Point;

typedef _Bool (*FilterFunc)(Point p);

DLLEXPORT int filter(const Point* src, int count, Point* dst, FilterFunc func)
{
    int outCount = 0;

    for (int i = 0; i < count; ++i)
    {
        if (func(src[i]))
        {
            dst[outCount++] = src[i];
        }
    }

    return outCount;
}
