import asyncio
from value import N,num_tasks
async def calculate_sum(start, end):
    return sum(range(start, end))

async def main():
    tasks = []
    step = N // num_tasks

    for i in range(num_tasks):
        start = i * step + 1
        end = (i + 1) * step + 1 if i < num_tasks - 1 else N+1
        tasks.append(asyncio.create_task(calculate_sum(start, end)))

    partial_sums = await asyncio.gather(*tasks)
    total_sum = sum(partial_sums)

if __name__ == "__main__":
    import time
   
    start_time = time.time()
    asyncio.run(main())
    print("Execution time (async):", time.time() - start_time)