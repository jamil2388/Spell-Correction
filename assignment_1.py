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
    bb_groups = F.get_bb_groups('https://www.dcs.bbk.ac.uk/~roger/missp.dat') # bb = birkbeck as list
    wordnet = F.get_wordnet_index('cache/wordnet_index.pkl')

    F.get_med_matrix(bb_groups, wordnet)

    # spelling part
    correct_spellings = []
    incorrect_spellings = []