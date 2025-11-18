def test_file_io():
    # Write to file
    with open("output.txt", "w") as f:
        f.write("Hello World")
        f.write("Second line")

    # Read entire file
    with open("output.txt", "r") as f:
        content = f.read()
        print(content)

    # Read lines
    with open("output.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            print(line)

    # Append to file
    with open("output.txt", "a") as f:
        f.write("Appended line")

    return 0
