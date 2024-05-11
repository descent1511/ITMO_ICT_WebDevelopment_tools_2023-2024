import multiprocessing
from value import N,num_tasks
def calculate_sum(start, end, result):
    partial_sum = sum(range(start, end))
    result.put(partial_sum)

def main():
    result = multiprocessing.Queue()
    processes = []
    step = N // num_tasks

    for i in range(num_tasks):
        start = i * step + 1
        end = (i + 1) * step + 1 if i < num_tasks - 1 else N+1
        process = multiprocessing.Process(target=calculate_sum, args=(start, end, result))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    total_sum = 0
    while not result.empty():
        total_sum += result.get()


if __name__ == "__main__":
    import time
    start_time = time.time()
    main()
    print("Execution time (process):", time.time() - start_time)
