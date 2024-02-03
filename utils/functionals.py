import os
import pickle
import time
from urllib import request
import nltk
from nltk.corpus import wordnet as wn
import Levenshtein as lv
from tqdm import tqdm
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from param import settings as params

num_cpu_cores = params['num_cpu_cores']
num_processes = num_cpu_cores
path_to_cache = params['path_to_cache']
bb_groups_filename = params['bb_groups_filename']
toy = params['toy']
batched = params['batched']

# print(num_cpu_cores, num_processes, path_to_cache, bb_groups_filename, toy, batched)
# global variables required for the entire class
med_matrix = [] # matrix for storing lv distances
wordnet = None
bb_groups = None
wn_length = None
num_groups_bb = None
num_matrix_rows = 0

# convert the birkbeck data to dictionary of correct to misspelled words
def get_bb_groups(url):
    global bb_groups, num_groups_bb

    # birkbeck has
    # total words : 42269
    # correct words : 6136
    # misspelled words : 36133
    bb_cache_filepath = f'{path_to_cache}/{bb_groups_filename}'

    # if data already exists, then lazy load
    if(os.path.exists(bb_cache_filepath)):
        with open(bb_cache_filepath, 'rb') as f:
            bb_groups = pickle.load(f)
    else:
        bb_corpus = request.urlopen(url).read().decode('utf-8')
        bb_groups = split_data(bb_corpus, '$')

        with open(bb_cache_filepath,'wb') as f:
            pickle.dump(bb_groups, f)
    num_groups_bb = len(bb_groups)
    return bb_groups

# convert the wordnet corpus to an indexed list
# if already present, return from cache
def get_wordnet_index(output = None):
    global wordnet, wn_length

    if not output : output = 'cache/wordnet_index.pkl'
    if(not os.path.exists(output)):
        # download the wordnet corpus
        nltk.download('wordnet')
        wordnet = list(wn.words(lang='eng'))
        save_file(wordnet, output)
    else:
        wordnet = read_file(output)
    wn_length = len(wordnet)
    return wordnet


# split the data into groups of words separated by words starting with the character char
def split_data(data, char):
    groups = []
    current_group = []

    lines = data.split('\n')

    for line in lines:
        word = line.strip()
        if word.startswith(char):
            # start a new group when a word with '$' is encountered
            if current_group:
                groups.append(current_group)
            current_group = [word[1:].lower()]  # remove the starting dollar sign
        else:
            current_group.append(word.lower())
    # add the last group if it's not empty
    if current_group:
        groups.append(current_group)

    return groups

# create levenshtein distance matrix if not already saved
# for each misspelled word in bb w_i, this will calculate the
# levelshtein distance of each word in wordnet
def get_med_matrix(output = None):
    global med_matrix, bb_groups, wordnet, wn_length, num_groups_bb, num_matrix_rows

    if not output: output = f'{path_to_cache}/med_matrix_sorted{".toy" if toy else ""}.pkl'
    if os.path.exists(output) :
        med_matrix = read_file(output)
        return med_matrix

    if toy:
        bb_groups = bb_groups[0:200]
        wordnet = wordnet[0:100000]
        wn_length = len(wordnet)
        num_groups_bb = len(bb_groups)

    row = 0 # count to store the number of misspelled tokens visited from bb_groups, also the current row count of the matrix

    # create matrix iteratively
    # there is a scope of parallelization here
    for i in tqdm(range(num_groups_bb)):
        # for each group we calculate the tuples and produce a row for them storing only the indices
        # e.g : for bb_group[i] = [car, care, cart], there will be one row for each tuple ...
        # ... (i, 1), (i, 2) and the correct spell 'car' will be addressed via (i, 0)
        # ... (i, j) = group i mw j
        for j in range(1, len(bb_groups[i])):
            med_matrix.append([(i, j)])
            med_matrix[row] += [(-1, k) for k in range(wn_length)]
            row += 1

    assert len(med_matrix[0]) == wn_length + 1

    num_matrix_rows = row
    # get the list of row numbers to divide into chunks later
    rows = list(np.arange(row))

    # start the timer
    start = time.time()

    if batched:
        # Split data into chunks
        row_chunks = chunk_data(rows, num_processes)
        # Call the parallel processing function for each chunk
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            # results = executor.map(do_sth, durations)
            futures = []
            # row_chunk contains row indices for this instance
            for row_chunk in row_chunks:
                start_row = row_chunk[0]
                last_row = row_chunk[-1]
                futures.append(executor.submit(process_rows_mp, row_chunk, med_matrix[start_row: last_row + 1], bb_groups, wordnet, wn_length))
                # print_matrix(process_rows_mp(row_chunk, med_matrix[start_row: last_row + 1], bb_groups, wordnet, wn_length))
            for i, row_chunk in enumerate(row_chunks):
                result = futures[i].result()
                start_row = row_chunk[0]
                last_row = row_chunk[-1]
                med_matrix[start_row:last_row + 1] = result
    else:
        process_rows(rows)

    end = time.time()
    total_time = end - start

    print(f'\ntime taken to form the sorted matrix : {total_time:.2f} seconds || {(total_time / 60):.2f} minutes || {(total_time / 3600):.2f} hours\n')
    print(f'-----------------------------------')

    # print(f'\nmed matrix after sorting : \n')
    # print_matrix()

    # save to cache
    save_file(med_matrix, output)
    return med_matrix

 # update the med_matrix with the sorted rows
def process_rows(row_chunk, progress_desc = None):
    global med_matrix, bb_groups, wordnet, num_groups_bb, wn_length

    for i in tqdm(row_chunk, position=0, leave=False, desc=progress_desc):
        row_result = []
        for j in range(wn_length):
            group = med_matrix[i][0][0]
            mw = med_matrix[i][0][1]
            item = bb_groups[group][mw]

            distance = lv.distance(item, wordnet[j])
            row_result.append((distance, j))
        # Sort the row based on the Levenshtein distances
        row_result.sort(key=lambda x: x[0])

        # directly update the desired portion of the med_matrix
        med_matrix[i][1:] = row_result

# Function to chunk the data, num_chunks = num_processes
def chunk_data(data_indices, num_chunks):

    chunk_size = len(data_indices) // num_chunks
    chunks = [data_indices[i:i + chunk_size] for i in range(0, len(data_indices), chunk_size)]
    return chunks

# calculate s@k for all the elements in the matrix
def calc_s_at_k(med_matrix = None, output = None):
    global num_matrix_rows

    if not output: output = f'{path_to_cache}/s_at_k{".toy" if toy else ""}.pkl'
    if os.path.exists(output): return read_file(output)

    # num_columns = 3 for s@k with 1, 5 and 10
    s_at_k = np.full((num_matrix_rows, 3), 0)
    for i in tqdm(range(num_matrix_rows)):
        group = med_matrix[i][0][0]
        for j in range(1, 11):
            correct_word = bb_groups[group][0]
            dict_word_index = med_matrix[i][j][1]
            dict_word = wordnet[dict_word_index]

            if((j >= 1 and j < 5) and correct_word == dict_word):
                s_at_k[i][0] = 1
                s_at_k[i][1] = 1
                s_at_k[i][2] = 1
                print(f'found match for : {correct_word}')
                break
            if((j >= 5 and j < 10) and correct_word == dict_word):
                s_at_k[i][1] = 1
                s_at_k[i][2] = 1
                print(f'found match for : {correct_word}')
                break
            if(j == 10 and correct_word == dict_word):
                s_at_k[i][2] = 1
                print(f'found match for : {correct_word}')
    # save to cache
    save_file(s_at_k, output)
    return s_at_k

def get_s_at_k_parallel(med_matrix = None, output = None):

    if not output: output = f'{path_to_cache}/s_at_k{".toy" if toy else ""}.pkl'
    if os.path.exists(output): return read_file(output)

    num_matrix_rows = len(med_matrix)
    # num_columns = 3 for s@k with 1, 5 and 10
    s_at_k = np.full((num_matrix_rows, 3), 0)
    row_chunks = chunk_data(list(range(num_matrix_rows)), num_processes)

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        # results = executor.map(do_sth, durations)
        futures = []
        # row_chunk contains row indices for this instance
        for row_chunk in row_chunks:
            start_row = row_chunk[0]
            last_row = row_chunk[-1]
            futures.append(
                executor.submit(calc_s_at_k_chunk, row_chunk, s_at_k[start_row: last_row + 1], med_matrix[start_row: last_row + 1], bb_groups, wordnet))
            # calc_s_at_k_chunk(row_chunk, s_at_k[start_row: last_row + 1], med_matrix[start_row: last_row + 1], bb_groups, wordnet)
        for i, row_chunk in enumerate(row_chunks):
            result = futures[i].result()
            start_row = row_chunk[0]
            last_row = row_chunk[-1]
            s_at_k[start_row:last_row + 1] = result


    # save to cache
    save_file(s_at_k, output)
    return s_at_k

def calc_s_at_k_chunk(row_chunk, sk_chunk, mm_chunk, bb_groups, wordnet):

    for i, row in enumerate(tqdm(row_chunk)):
        group = mm_chunk[i][0][0]
        for j in range(1, 11):
            correct_word = bb_groups[group][0]
            dict_word_index = mm_chunk[i][j][1]
            dict_word = wordnet[dict_word_index]

            if((j >= 1 and j < 5) and correct_word == dict_word):
                sk_chunk[i][0] = 1
                sk_chunk[i][1] = 1
                sk_chunk[i][2] = 1
                # print(f'found match for : {correct_word}')
                break
            if((j >= 5 and j < 10) and correct_word == dict_word):
                sk_chunk[i][1] = 1
                sk_chunk[i][2] = 1
                # print(f'found match for : {correct_word}')
                break
            if(j == 10 and correct_word == dict_word):
                sk_chunk[i][2] = 1
                # print(f'found match for : {correct_word}')
    return sk_chunk

### utils

# save as pickle
def save_file(data, output):
    # save the file given the output
    with open(output, 'wb') as f:
        pickle.dump(data, f)
    print(f'\n saved file at : {output}\n')

def read_file(input):
    with open(input, 'rb') as f:
        return pickle.load(f)

# pretty print the med_matrix
def print_matrix(med_matrix = None):
    for i in range(len(med_matrix)):
        print(f'{med_matrix[i]}')
    print()

## multiprocessing section
# mm = med_matrix
# here the row indices of the mm_chunk will always be from 0 -> size(row_chunk) - 1
def process_rows_mp(row_chunk, mm_chunk, bb_groups, wordnet, wn_length, progress_desc = None):

    for i, row in enumerate(tqdm(row_chunk, leave=False, desc=progress_desc)):
        row_result = []
        for j in range(wn_length):
            group = mm_chunk[i][0][0]
            mw = mm_chunk[i][0][1]
            item = bb_groups[group][mw]

            distance = lv.distance(item, wordnet[j])
            row_result.append((distance, j))
        # Sort the row based on the Levenshtein distances
        row_result.sort(key=lambda x: x[0])

        # directly update the desired portion of the med_matrix
        mm_chunk[i][1:] = row_result
    return mm_chunk