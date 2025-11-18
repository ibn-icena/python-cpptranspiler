def find_first_positive(n: int) -> int:
    i = 0
    while i < n:
        i += 1
        if i < 0:
            continue
        if i > 10:
            break
        return i
    return -1
