def is_prime(n):
    """检查一个自然数是否为素数"""
    if n < 1:
        return -1
    if n == 1:
        return 0
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return 0
    return 1


assert is_prime(5) == 1
assert is_prime(4) == 0
assert is_prime(7) == 1
assert is_prime(8) == 0
assert is_prime(283) == 1
assert is_prime(284) == 0
assert is_prime(293) == 1