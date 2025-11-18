def is_valid(x: int, y: int) -> int:
    if x > 0 and y > 0:
        return 1
    if x < 0 or y < 0:
        return -1
    if not (x == y):
        return 0
    return 2
