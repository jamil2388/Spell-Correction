import os
import pickle
from urllib import request
import nltk
from nltk.corpus import wordnet as wn
import Levenshtein as lv
from tqdm import tqdm
import numpy as np

num_cpu_cores = os.cpu_count() - 2
path_to_cache = 'cache'
bb_cache_filename = 'bb_groups.pkl'
bb_groups_index_filename = 'bb_groups_index.pkl' # the dictionary to store
toy = True

# convert the birkbeck data to dictionary of correct to misspelled words
def get_bb_groups(url):
    # birkbeck has
    # total words : 42269
    # correct words : 6136
    # misspelled words : 36133
    bb_cache_filepath = f'{path_to_cache}/{bb_cache_filename}'

    # if data already exists, then lazy load
    if(os.path.exists(bb_cache_filepath)):
        with open(bb_cache_filepath, 'rb') as f:
            bb_groups = pickle.load(f)
    else:
        bb_corpus = request.urlopen(url).read().decode('utf-8')
        bb_groups = split_data(bb_corpus, '$')

        with open(bb_cache_filepath,'wb') as f:
            pickle.dump(bb_groups, f)
    return bb_groups

# convert the wordnet corpus to an indexed list
# if already present, return from cache
def get_wordnet_index(output = None):
    if not output : output = 'cache/wordnet_index.pkl'
    if(not os.path.exists(output)):
        # download the wordnet corpus
        nltk.download('wordnet')
        wordnet = list(wn.words(lang='eng'))
        with open(output, 'wb') as f:
            pickle.dump(wordnet, f)
    else:
        with open(output, 'rb') as f:
            wordnet = pickle.load(f)
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

# create levenshtein distance matrix
# for each misspelled word in bb w_i, this will calculate the
# levelshtein distance of each word in wordnet
def create_med_matrix(bb_groups, wordnet, output = None):

    if toy:
        bb_groups = bb_groups[:5]
        wordnet = wordnet[300:305]

    wn_length = len(wordnet) # number of tokens in wordnet
    num_groups_bb = len(bb_groups) # number of rows in bb_groups after grouping

    if not output: output = 'cache/distances.pkl'
    med_matrix = [] # matrix for storing lv distances
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
    batches = np.array_split(rows, num_cpu_cores)

    row = 0
    for batch in batches:
        for b in batch:
            for j in tqdm(range(wn_length)):
                group = med_matrix[row][0][0]
                mw = med_matrix[row][0][1]
                item = bb_groups[group][mw]

                med_matrix[row][j + 1] = (lv.distance(item, wordnet[j]), j)
            # sort the row based on the lv distances
            med_matrix[row][1:] = sorted(med_matrix[row][1:], key = lambda x : x[0])
            row += 1

    print(f'\nmed matrix after sorting : \n')
    for i in rows:
        print(f'{med_matrix[row]}')
    print()




