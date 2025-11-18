def test_string_methods(text: str):
    # Test split
    words = text.split(" ")
    csv_values = text.split(",")
    whitespace_split = text.split()

    # Test strip
    trimmed = text.strip()
    left_trim = text.lstrip()
    right_trim = text.rstrip()

    # Test join
    joined = ",".join(words)

    # Test replace
    replaced = text.replace("old", "new")

    # Test startswith/endswith
    starts = text.startswith("Hello")
    ends = text.endswith("world")

    return joined
