from multiprocessing import Process

def worker(name: str, count: int):
    print("Worker", name, count)

def main():
    # Create processes
    p1 = Process(target=worker, args=("A", 5))
    p2 = Process(target=worker, args=("B", 10))

    # Processes start automatically in C++
    # p1.start()
    # p2.start()

    # Wait for completion
    p1.join()
    p2.join()
