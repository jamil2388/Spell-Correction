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

    # download the wordnet corpus
    nltk.download('wordnet')
    wordnet = list(wn.words(lang='eng'))
    wordnet_df = pd.DataFrame(wordnet)

    # bb = birkbeck
    bb_dict = F.load_bb_dict('https://www.dcs.bbk.ac.uk/~roger/missp.dat') # bb = birkbeck as list



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