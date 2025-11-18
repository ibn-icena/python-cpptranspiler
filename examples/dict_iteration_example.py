def test_dict_iteration():
    data = {"a": 1, "b": 2, "c": 3}

    # Iterate over items (key-value pairs)
    for key, value in data.items():
        print(key, value)

    # Iterate over keys
    for key in data.keys():
        print(key)

    # Iterate over values
    for value in data.values():
        print(value)
