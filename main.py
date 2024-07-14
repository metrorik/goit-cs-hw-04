import threading
import multiprocessing
import time
from queue import Queue



# пошук ключових слів у файлі
def search_keywords_in_file(filepath, keywords):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()
        found_keywords = {keyword: [] for keyword in keywords}
        for keyword in keywords:
            if keyword in text:
                found_keywords[keyword].append(filepath)
        return found_keywords
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        return None

# об'єднання результатів пошуку
def merge_results(result_list):
    merged = {}
    for result in result_list:
        for keyword, files in result.items():
            if keyword not in merged:
                merged[keyword] = []
            merged[keyword].extend(files)
    return merged



# Багатопотоковий підхід використовуючи threading
def worker_thread(file_queue, keywords, result_queue):
    while not file_queue.empty():
        filepath = file_queue.get()
        result = search_keywords_in_file(filepath, keywords)
        if result:
            result_queue.put(result)
        file_queue.task_done()

def threaded_search(files, keywords):
    file_queue = Queue()
    result_queue = Queue()
    results = []

    for filepath in files:
        file_queue.put(filepath)

    threads = []
    for _ in range(min(4, len(files))):
        thread = threading.Thread(target=worker_thread, args=(file_queue, keywords, result_queue))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    while not result_queue.empty():
        results.append(result_queue.get())

    return merge_results(results)



# Багатопроцесорний підхід використовуючи multiprocessing
def worker_process(file_queue, keywords, result_queue):
    while not file_queue.empty():
        filepath = file_queue.get()
        result = search_keywords_in_file(filepath, keywords)
        if result:
            result_queue.put(result)
        file_queue.task_done()

def multiprocess_search(files, keywords):
    file_queue = multiprocessing.JoinableQueue()
    result_queue = multiprocessing.Queue()
    results = []

    for filepath in files:
        file_queue.put(filepath)

    processes = []
    for _ in range(min(4, len(files))):
        process = multiprocessing.Process(target=worker_process, args=(file_queue, keywords, result_queue))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    while not result_queue.empty():
        results.append(result_queue.get())

    return merge_results(results)





# Головна функція main
def main():
    files = ["file1.txt", "file2.txt", "file3.txt"]  # список файлів
    keywords = ["keyword1", "keyword2", "keyword3"]  # ключові слова

    # threading
    start_time = time.time()
    thread_results = threaded_search(files, keywords)
    thread_duration = time.time() - start_time
    print(f"Threading results: {thread_results}")
    print(f"Threading duration: {thread_duration} seconds")

    # multiprocessing
    start_time = time.time()
    process_results = multiprocess_search(files, keywords)
    process_duration = time.time() - start_time
    print(f"Multiprocessing results: {process_results}")
    print(f"Multiprocessing duration: {process_duration} seconds")
    
if __name__ == "__main__":
    main()
