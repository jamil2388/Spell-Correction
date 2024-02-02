import os

settings = {
    # 'num_cpu_cores' : os.cpu_count() - 4,
    'num_cpu_cores' : 2,
    'path_to_cache' : 'cache',
    'bb_groups_filename' : 'bb_groups.pkl',
    'toy' : 1,      # 1 => True
    'batched' : 1,  # 1 => True
    # need to be determined by the script find_threads
    # maximum went upto 371298 after 5 mins. The time needed to call up so many threads
    # should also be considered
    # 'num_threads' : 20000,
    'num_threads' : 2,
}