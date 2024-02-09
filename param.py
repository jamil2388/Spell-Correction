import os

settings = {
    # 'num_cpu_cores' : os.cpu_count() - 4,
    "num_cpu_cores": os.cpu_count(),
    "path_to_cache": "cache",
    "cw_filename": "cw.pkl", # cw is a dict storing the mapping from incorrect words to correct words in bb
    "iw_filename": "iw.pkl", # iw is a list storing only the incorrect words of bb
    "iw_matrix_filename": "iw_matrix.pkl", # iw_matrix stores the k_nearest word indices in tuples
    "toy": 0,  # 1 => True for using a subset of data defined in the toy section below
    "batched": 1,  # 1 => True for using multiprocessing with num_cpu_cores

    ## For toy testing
    "toy_wn_start":300, # start index for toy data
    "toy_wn_end":312,
    "toy_bb_start":200,
    "toy_bb_end":206,
}
