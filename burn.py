import multiprocessing
import time

def infinite_loop():
    # Simple, non-stop computational arithmetic to peg the processor core
    x = 0
    while True:
        x += 1

if __name__ == "__main__":
    # Get total count of available logic threads
    cores = multiprocessing.cpu_count()
    print(f"🔥 Spawning computational workers across all {cores} CPU cores...")
    print("📢 Check Task Manager now! Press Ctrl + C in this window to stop.")
    
    processes = []
    for _ in range(cores):
        p = multiprocessing.Process(target=infinite_loop)
        p.start()
        processes.append(p)
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping workers...")
        for p in processes:
            p.terminate()