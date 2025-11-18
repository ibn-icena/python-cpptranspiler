def test_lambdas():
    # Simple lambda
    double = lambda x: x * 2
    result1 = double(5)
    print(result1)

    # Lambda with multiple parameters
    add = lambda x, y: x + y
    result2 = add(3, 4)
    print(result2)

    # Lambda with more complex expression
    multiply = lambda a, b: a * b + 10
    result3 = multiply(2, 3)
    print(result3)

    return result1
