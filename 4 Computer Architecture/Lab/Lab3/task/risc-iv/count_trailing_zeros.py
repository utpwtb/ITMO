def count_trailing_zeros(n):
    """计算整数二进制表示中尾随零的数量。

    参数:
        n (int): 要计算尾随零的整数。

    返回:
        int: 尾随零的数量。
    """
    if n == 0:
        return 32
    count = 0
    while (n & 1) == 0:
        count += 1
        n >>= 1
    return count


assert count_trailing_zeros(1) == 0    # 1 的二进制是 0001，没有尾随零
assert count_trailing_zeros(2) == 1    # 2 的二进制是 0010，有 1 个尾随零
assert count_trailing_zeros(16) == 4   # 16 的二进制是 10000，有 4 个尾随零