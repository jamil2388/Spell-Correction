import os

settings = {
    # 'num_cpu_cores' : os.cpu_count() - 4,
    "num_cpu_cores": 2,
    "path_to_cache": "cache",
    "cw_filename": "cw.pkl", # cw is a dict storing the mapping from incorrect words to correct words in bb
    "iw_filename": "iw.pkl", # iw is a list storing only the incorrect words of bb
    "toy": 1,  # 1 => True
    "batched": 1,  # 1 => True
    "toy_wn_start":300, # start index for toy data
    "toy_wn_end":305,
    "toy_bb_start":200,
    "toy_bb_end":206,
}
