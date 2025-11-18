def get_coords():
    x = 10
    y = 20
    return x, y

def get_triple():
    return 1, 2, 3

def test_tuple_unpacking():
    # Multiple returns from function
    result_x, result_y = get_coords()
    print(result_x, result_y)

    # Direct tuple unpacking
    a, b = (1, 2)
    print(a, b)

    # Triple unpacking
    x, y, z = get_triple()
    print(x, y, z)

    return result_x
