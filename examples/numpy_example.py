import numpy as np

def matrix_operations(n: int) -> float:
    # Create arrays
    arr = np.array([1, 2, 3, 4, 5])
    zeros = np.zeros(10)
    ones = np.ones(5)

    # Mathematical operations
    total = np.sum(arr)
    avg = np.mean(arr)

    # Matrix operations
    mat1 = np.ones((3, 3))
    mat2 = np.eye(3)
    result = np.dot(mat1, mat2)

    # Access elements
    val = result[0, 1]

    return avg
