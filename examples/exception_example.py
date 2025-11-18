def test_exceptions():
    # Basic try/except
    try:
        x = 10 / 0
    except ZeroDivisionError:
        print("Division by zero")

    # Try/except with variable
    try:
        items = [1, 2, 3]
        value = items[10]
    except IndexError as e:
        print("Index out of range")

    # Try/except/finally
    try:
        data = 42
        result = data / 2
    except Exception as e:
        print("Error occurred")
    finally:
        print("Cleanup")

    # Raising exceptions
    try:
        raise ValueError("Invalid value")
    except ValueError:
        print("Caught ValueError")

    return 0
