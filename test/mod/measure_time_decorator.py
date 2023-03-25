import csv
import time


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} の処理時間は {elapsed_time:.5f} 秒です")

        with open("function_times.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([func.__name__, elapsed_time])

        return result

    return wrapper
