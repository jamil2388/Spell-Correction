import multiprocessing
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

num_cpu_cores = params["num_cpu_cores"]
num_processes = num_cpu_cores
path_to_cache = params["path_to_cache"]
cw_filename = params["cw_filename"]
iw_filename = params["iw_filename"]
iw_matrix_filename = params["iw_matrix_filename"]
toy = params["toy"]
batched = params["batched"]

# print(num_cpu_cores, num_processes, path_to_cache, bb_groups_filename, toy, batched)
# global variables required for the entire class
med_matrix = []  # matrix for storing lv distances
wordnet = None
wn_length = None
bb_length = 0 # length of iw
num_matrix_rows = 0

toy_wn_start = params['toy_wn_start']
toy_wn_end = params['toy_wn_end']
toy_bb_start = params['toy_bb_start']
toy_bb_end = params['toy_bb_end']

# convert the birkbeck data to list of correct and incorrect words
def get_bb_groups(url):
    global bb_length

    # birkbeck has
    # total words : 42269
    # correct words : 6136
    # misspelled words : 36133
    cw_filepath = f"{path_to_cache}/{cw_filename}"
    iw_filepath = f"{path_to_cache}/{iw_filename}"

    # if data already exists, then lazy load
    if os.path.exists(cw_filepath):
        cw = read_file(cw_filepath)
        iw = read_file(iw_filepath)
    else:
        bb_corpus = request.urlopen(url).read().decode("utf-8")
        cw, iw = split_data(bb_corpus, "$")

        save_file(cw, cw_filepath)
        save_file(iw, iw_filepath)

    if toy : iw = iw[toy_bb_start : toy_bb_end + 1]
    bb_length = len(iw)
    return cw, iw


# convert the wordnet corpus to an indexed list
# if already present, return from cache
def get_wordnet_index(output=None):
    global wn_length

    if not output:
        output = "cache/wordnet_index.pkl"
    if os.path.exists(output):
        wordnet = read_file(output)
    else:
        # download the wordnet corpus
        nltk.download("wordnet")
        wordnet = list(wn.words(lang="eng"))
        save_file(wordnet, output)

    if toy: wordnet = wordnet[toy_wn_start:toy_wn_end + 1]
    wn_length = len(wordnet)
    return wordnet


# split the data into groups of words separated by words starting with the character char
def split_data(data, char):
    iw = []
    cw = {} # dict to store the mapping between incorrect words and their corresponding correct word
    parent = None

    lines = data.split("\n")

    for line in lines:
        word = line.strip()
        if word.startswith(char):
            parent = word[1:]
        else:
            iw.append(word)
            cw[word] = parent
    return cw, iw

# iw_chunk = indices of the chunk
def get_k_nearest_words_in_chunk(iw_chunk, wordnet,  k=10):

    iw_chunk_matrix = []

    for i, iw in enumerate(iw_chunk):
        iw_chunk_matrix.append([])
        for j, wn in tqdm(enumerate(wordnet)):
            d = lv.distance(iw, wn)
            # insertion sort can be given here
            iw_chunk_matrix[i].append((j, d))
        iw_chunk_matrix[i] = sorted(iw_chunk_matrix[i], key = lambda x: x[1])[:k]

    return iw_chunk_matrix

def process_chunk(iw_chunk, wordnet):
    # Process the chunk and return the result
    return get_k_nearest_words_in_chunk(iw_chunk, wordnet)

def get_iw_matrix(iw, wordnet):

    iw_matrix_filepath = f'{path_to_cache}/{iw_matrix_filename}'
    if os.path.exists(iw_matrix_filepath): return read_file(iw_matrix_filepath)

    if batched:
        iw_chunks = chunk_data(np.arange(len(iw)), num_processes)

        # Create a multiprocessing pool with the desired number of processes
        with multiprocessing.Pool(processes=len(iw_chunks)) as pool:
            results = []
            for i, iw_chunk in enumerate(iw_chunks):
                start = iw_chunk[0]
                end = iw_chunk[-1]
                results.append(pool.apply_async(process_chunk, args=(iw[start:end + 1], wordnet)))
                print(f'i = {i}, process_chunk')

            # Collect the results from the multiprocessing pool
            iw_matrix_chunks = [result.get() for result in results]

        # Concatenate the processed chunks to form iw_matrix
        for i, iw_matrix_chunk in enumerate(iw_matrix_chunks):
            iw_matrix = iw_matrix_chunk if i == 0 else iw_matrix + iw_matrix_chunk
        print_matrix(iw_matrix)

    # save file
    save_file(iw_matrix, iw_matrix_filepath)
    return iw_matrix


### utils

# Function to chunk the data, num_chunks = num_processes
def chunk_data(data_indices, num_chunks):
    chunk_size = len(data_indices) // num_chunks
    chunks = [
        data_indices[i : i + chunk_size]
        for i in range(0, len(data_indices), chunk_size)
    ]
    return chunks

# save as pickle
def save_file(data, output):
    # save the file given the output
    with open(output, "wb") as f:
        pickle.dump(data, f)
    print(f"\n saved file at : {output}\n")


def read_file(input):
    with open(input, "rb") as f:
        return pickle.load(f)


# pretty print the med_matrix
def print_matrix(med_matrix=None):
    for i in range(len(med_matrix)):
        print(f"{med_matrix[i]}")
    print()