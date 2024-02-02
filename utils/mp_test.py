'''
this file is for testing multiprocessing scenarios
'''
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import functionals as F
import time


def do_sth(duration = 2):
    print(f'Sleeping for {duration} seconds')
    time.sleep(duration)
    return f'Done Sleeping {duration} seconds'

def update_matrix(rows, mm_chunk):

    print(f'processing for rows :\n{rows}\n')

    for row in range(len(rows)):
        # ignore the first element of the list, because it stores the group and item info of bb_groups
        mm_chunk[row][1:] = sorted(mm_chunk[row][1:], key = lambda x: x[0])
    return mm_chunk

def chunk_data(data_indices, num_chunks):

    chunk_size = len(data_indices) // num_chunks
    chunks = [data_indices[i:i + chunk_size] for i in range(0, len(data_indices), chunk_size)]
    return chunks

if __name__ == '__main__':
    print(f'...............running mp_test as main................')

    # for sleep example
    durations = [4.1, 3.0, 5.2, 1.2, 2.3, 3.2]

    # ---------------------------------------------- #
    # num_rows = 5, wn_length = 6
    num_rows = 5
    wn_length = 6
    mm = [[(15, 1),(14, 0),(4, 1),(11, 1),(7, 3),(4, 4)], \
          [(30, 1),(4, 0),(5, 1),(5, 2),(7, 3),(6, 4)], \
          [(91, 2),(9, 0),(4, 1),(6, 2),(7, 3),(1, 4)], \
          [(21, 1),(5, 0),(13, 1),(7, 2),(8, 3),(3, 4)], \
          [(23, 1),(12, 0),(3, 1),(6, 2),(8, 3),(1, 4)]]

    row_indices = list(range(num_rows))
    chunks = chunk_data(row_indices, 2)

    # for chunk in chunks:
    #     start_row = chunk[0]
    #     last_row = chunk[-1]
    #     mm[start_row:last_row + 1] = update_matrix(chunk, mm[start_row: last_row + 1])
    # ---------------------------------------------- #

    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        # results = executor.map(do_sth, durations)
        futures = []
        for chunk in chunks:
            start_row = chunk[0]
            last_row = chunk[-1]
            futures.append(executor.submit(update_matrix, chunk, mm[start_row: last_row + 1]))
        for i, chunk in enumerate(chunks):
            future = futures[i].result()
            start_row = chunk[0]
            last_row = chunk[-1]
            mm[start_row:last_row + 1] = future
    end = time.time()
    runtime = end - start
    print(f'\nprogram runtime : {runtime}')
    F.print_matrix(mm)

