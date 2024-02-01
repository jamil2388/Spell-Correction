import os
import pickle
from urllib import request
import nltk
from nltk.corpus import wordnet as wn
import Levenshtein as lv
from tqdm import tqdm
import numpy as np
import multiprocessing as mp
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
    global bb_groups, wordnet, wn_length, num_groups_bb

    if not output: output = f'cache/med_matrix_sorted{".toy" if toy else ""}.pkl'
    if os.path.exists(output) : return read_file(output)

    if toy:
        bb_groups = bb_groups[:5]
        wordnet = wordnet[300:305]
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

    # distribute the med task to cores
    rows = np.arange(row)

    if batched:
        # Split the rows into chunks to distribute to processes
        row_chunks = [rows[i:i + num_processes] for i in range(0, len(rows), num_processes)]

        # process_rows(row_chunks[1])
        # print_matrix()

        # Use multiprocessing.Pool to parallelize the processing of rows
        with mp.Pool(processes=num_processes) as pool:
            pool.map(process_rows, row_chunks)

        # # Flatten the results from row chunks to a flat list
        # flattened_results = [result for chunk_results in result_rows for result in chunk_results]
        #
        # # Update the med_matrix with the results
        # for row, results in flattened_results:
        #     for result in results:
        #         med_matrix[row][1:] = result
    else:
        # for i in rows:
        #     for j in tqdm(range(wn_length)):
        #         group = med_matrix[i][0][0]
        #         mw = med_matrix[i][0][1]
        #         item = bb_groups[group][mw]
        #
        #         med_matrix[i][j + 1] = (lv.distance(item, wordnet[j]), j)
        #     # sort the row based on the lv distances
        #     med_matrix[i][1:] = sorted(med_matrix[i][1:], key = lambda x : x[0])
        process_rows(rows)

    print(f'\nmed matrix after sorting : \n')
    print_matrix()

    # save to cache
    save_file(med_matrix, output)

 # update the med_matrix with the sorted rows
def process_rows(row_chunk, med_matrix, bb_groups, wordnet, num_groups_bb, wn_length):

    for i in tqdm(row_chunk, position=0, leave=False):
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
    return med_matrix

### utils

# save as pickle
def save_file(data, output):
    # save the file given the output
    with open(output, 'wb') as f:
        pickle.dump(data)
    print(f'\n saved file at : {output}\n')

def read_file(input):
    with open(input, 'rb') as f:
        return pickle.load(f)

# pretty print the med_matrix
def print_matrix():
    for i in range(len(med_matrix)):
        print(f'{med_matrix[i]}')
    print()