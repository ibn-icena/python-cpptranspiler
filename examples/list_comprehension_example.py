def test_list_comprehensions():
    # Simple comprehension
    squares = [x**2 for x in range(10)]

    # Comprehension with filter
    evens = [x for x in range(20) if x % 2 == 0]

    # Comprehension with expression
    doubled = [x * 2 for x in range(5)]

    # Nested comprehension
    matrix = [[i * j for j in range(3)] for i in range(3)]

    return squares
