import os
import pickle
from urllib import request
import nltk
from nltk.corpus import wordnet as wn
import Levenshtein as lv

path_to_cache = '../cache'
bb_cache_filename = 'bb_dict_cache.pkl'

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
            current_group = [word[1:]]  # remove the starting dollar sign
        else:
            current_group.append(word)
    # add the last group if it's not empty
    if current_group:
        groups.append(current_group)

    return groups

# create levenshtein distance cache
# for each misspelled word in bb w1, this will calculate the
# levelshtein distance of each word in wordnet in every iteration
def calculate_distance(bb_groups, k = 10, output = None):
    if not output:
        output = '../cache/distances.pkl'
    # dict for storing top k lv distanced words k = 10
    k_nearest_words = {}

    # download the wordnet corpus
    nltk.download('wordnet')
    wordnet = list(wn.words(lang='eng'))
    for group in bb_groups:
        for mw in group[1:]:
            k_nearest_words[mw] = {}
            for w in wordnet:
                if(lv.distance(mw, w) <= k):
                    k_nearest_words[mw][k].append



# convert the birkbeck data to dictionary of correct to misspelled words
def load_bb_groups(url):
    bb_cache_filepath = f'path_to_cache/{bb_cache_filename}'

    # if data already exists, then lazy load
    if(os.path.exists(bb_cache_filepath)):
        with open(bb_cache_filepath, 'rb') as f:
            bb_groups = pickle.load(f)
    else:
        bb_corpus = request.urlopen(url).read().decode('utf-8')
        bb_groups = split_data(bb_corpus, '$')

        for group in bb_groups:
            pass


        # process the data to dict


        with open(bb_cache_filepath,'wb') as f:
            pickle.dump(bb_dict, f)
    return bb_dict