import time


def measure_time(func):
    """
    A decorator to measure the execution time of a function.

    Args:
        func (callable): The function whose execution time will be measured.

    Returns:
        callable: A wrapper function that measures the execution time.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}:{execution_time:.4f} seconds")
        return result
    
    return wrapper







