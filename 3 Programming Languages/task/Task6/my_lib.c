long long fib_rec(int n) {
    if (n <= 1) {
        return n;
    }
    return fib_rec(n - 2) + fib_rec(n - 1);
}