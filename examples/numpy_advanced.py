import numpy as np

def advanced_operations():
    # Matrix operations
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])

    # Matrix multiplication
    C = np.matmul(A, B)

    # Linear algebra
    det_A = np.linalg.det(A)
    inv_A = np.linalg.inv(A)

    # Array operations
    arr1 = np.array([1, 5, 3, 2, 4])
    max_idx = np.argmax(arr1)
    min_idx = np.argmin(arr1)

    # Stacking
    stacked = np.vstack((A, B))

    return det_A
