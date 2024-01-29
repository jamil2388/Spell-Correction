# this package contains functions for finding the average s@k from Birkbrek to Wordnet
import nltk
from nltk.corpus import wordnet as wn
import Levenshtein as lv
import re
import pandas as pd
from tqdm import tqdm
import pickle

# local libs
import utils.functionals as F

if __name__ == '__main__':


    # bb = birkbeck
    bb_group = F.load_bb_groups('https://www.dcs.bbk.ac.uk/~roger/missp.dat') # bb = birkbeck as list
    wordnet = F.get_wordnet_index('cache/wordnet_index.pkl')


    for i in tqdm(range(0, len(bb), 2)):
        print(f'w1 : {bb[i]}, w2 : {bb[i + 1]}')

    # subset = re.
    for w in tqdm(wordnet):
        if(w.islower()):
            continue
        d = lv.distance('desie', w)
        print(f'desie, w : {w}, d : {d}')

    # spelling part
    correct_spellings = []
    incorrect_spellings = []