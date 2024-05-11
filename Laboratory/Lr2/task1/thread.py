import threading
from value import N,num_tasks
def calculate_sum(start, end, result):
    partial_sum = sum(range(start, end))
    result.append(partial_sum)

def main():
    result = []
    threads = []
    step = N // num_tasks

    for i in range(num_tasks):
        start = i * step + 1
        end = (i + 1) * step + 1 if i < num_tasks - 1 else N+1
        thread = threading.Thread(target=calculate_sum, args=(start, end, result))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(result)

if __name__ == "__main__":
    import time
    
    start_time = time.time()
    main()
    print("Execution time (thread):", time.time() - start_time)
