import concurrent.futures
import time
import os
import threading

def scan(start_directory, threads): #sdirectory, monitor, verbose, threads, charttype, reportdir
    start_time = time.time()
    processed_or_queued = set() #to avoid repetition
    active_futures = {}
    count = 0
    totalsize = 0
    lock = threading.RLock()

    def worker(dir):
        nonlocal count, totalsize
        subdirectories_found = []

        for item in os.scandir(dir) :
            try:
                current_item_path = os.path.join(dir, item.name)
                if item.is_dir(follow_symlinks=False):
                    #print(f"Directory: {item.path}")
                    subdirectories_found.append(item.path)
                elif item.is_file(follow_symlinks=False):
                    try:
                        with lock:
                            count += 1
                    except FileNotFoundError:
                        pass
                    #print(f"File: {item.path}")
                    #do calculation!!!!!!!!!!!!!!
            except PermissionError:
                print("Permission denied!")
            except FileNotFoundError:
                print("Directory not found!")
        
        return subdirectories_found

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        if os.path.isdir(start_directory):
            dir_to_scan = start_directory
            processed_or_queued.add(os.path.realpath(start_directory))
        else:
            print("Error: Directory '{start_directory' is not valid.}")
        
        future = executor.submit(worker, dir_to_scan)
        active_futures[future] = dir_to_scan #to match futures with its directory

        while active_futures:
            done_futures, _ = concurrent.futures.wait(active_futures.keys(),
                                            return_when=concurrent.futures.FIRST_COMPLETED) # _ represents not done futures
            
            for future in done_futures:
                original_dir_scanned = active_futures.pop(future) #get directory back from matching

                try:
                    new_subdirs = future.result()

                    for subdir in new_subdirs:
                        real_subdir_path = os.path.realpath(subdir)
                        if real_subdir_path not in processed_or_queued:
                            processed_or_queued.add(subdir)
                            new_future = executor.submit(worker, real_subdir_path)

                            active_futures[new_future] = real_subdir_path
                except Exception as e:
                    pass
                    #print(f"Task for directory '{original_dir_scanned}' raised an exception: {e}")
        
        print("Scanning complete.")
        print(f"Time taken for the scan: {time.time()-start_time:.2f} seconds")
        print(f"Total number of files scanned: {count}")