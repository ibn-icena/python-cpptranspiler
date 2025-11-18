def test_list_methods():
    numbers = [1, 2, 3, 4, 5]

    # Test extend
    more_numbers = [6, 7, 8]
    numbers.extend(more_numbers)

    # Test insert
    numbers.insert(0, 0)

    # Test remove
    numbers.remove(3)

    # Test index
    idx = numbers.index(5)

    # Test count
    count = numbers.count(2)

    return idx
