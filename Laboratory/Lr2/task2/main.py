import subprocess

async_file = "async.py"
thread_file = "thread.py"
process_file = "process.py"

def run_scripts():
    subprocess.run(["python", async_file], shell=True, check=True)
    subprocess.run(["python", thread_file], shell=True, check=True)
    subprocess.run(["python", process_file], shell=True, check=True)

if __name__ == "__main__":
    run_scripts()
