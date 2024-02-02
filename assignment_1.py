# this package contains functions for finding the average s@k from Birkbrek to Wordnet
import nltk
import numpy as np
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

    F.get_med_matrix()
    s_at_k = F.calc_s_at_k()
    print(f's@k entries having 1 : \n{np.argwhere(s_at_k == 1)}\n\n')
    print('\n-------------------- Results -----------------------------\n')
    print(f'average s@k for k = 1 : {np.average(s_at_k[:, 0])}')
    print(f'average s@k for k = 5 : {np.average(s_at_k[:, 1])}')
    print(f'average s@k for k = 10 : {np.average(s_at_k[:, 2])}')
    print('\n----------------------------------------------------------\n')