# this package contains functions for finding the average s@k from Birkbrek to Wordnet
import os.path
import numpy as np
import param

# local libs
import utils.functionals as F
import time

if __name__ == "__main__":
    global_start_time = time.time()
    if not os.path.exists("cache"):
        os.mkdir("cache")
    batched = param.settings["batched"]

    # bb = birkbeck
    cw, iw = F.get_bb_groups(
        "https://www.dcs.bbk.ac.uk/~roger/missp.dat"
    )  # bb = birkbeck as list
    wordnet = F.get_wordnet_index("cache/wordnet_index.pkl")
    iw_matrix = F.get_iw_matrix(iw, wordnet)

    s_at_k = F.calc_s_at_k(iw, cw, iw_matrix, wordnet)

    # total timing of the entire run
    global_end_time = time.time()
    global_total_time = (global_end_time - global_start_time) / 60
    print('\n---------------- Time Taken ---------------\n')
    print(f'Total Time taken by the entire program : {global_total_time:.4f} minutes')
    print('\n---------------- |||||||||| ---------------\n')

    # print(f"\ns@k entries having 1 : \n{np.argwhere(s_at_k == 1).sum()}\n\n")
    # print("\n-------------------- Results -----------------------------\n")
    # print(f"Average s@k for k = 1 : {np.average(s_at_k[:, 0])}")
    # print(f"Average s@k for k = 5 : {np.average(s_at_k[:, 1])}")
    # print(f"Average s@k for k = 10 : {np.average(s_at_k[:, 2])}")
    # print("\n----------------------------------------------------------\n")
