# this package contains functions for finding the average s@k from Birkbrek to Wordnet
import os.path
import numpy as np
import param

# local libs
import utils.functionals as F

if __name__ == '__main__':

    if not os.path.exists('cache'): os.mkdir('cache')


    # bb = birkbeck
    bb_groups = F.get_bb_groups('https://www.dcs.bbk.ac.uk/~roger/missp.dat') # bb = birkbeck as list
    wordnet = F.get_wordnet_index('cache/wordnet_index.pkl')
    batched = param.settings['batched']

    F.get_med_matrix()

    s_at_k = F.get_s_at_k_parallel() if batched else F.calc_s_at_k()

    print(f's@k entries having 1 : \n{np.argwhere(s_at_k == 1).sum()}\n\n')
    print('\n-------------------- Results -----------------------------\n')
    print(f'average s@k for k = 1 : {np.average(s_at_k[:, 0])}')
    print(f'average s@k for k = 5 : {np.average(s_at_k[:, 1])}')
    print(f'average s@k for k = 10 : {np.average(s_at_k[:, 2])}')
    print('\n----------------------------------------------------------\n')