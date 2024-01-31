import os

settings = {
    'num_cpu_cores' : os.cpu_count() - 4,
    'path_to_cache' : 'cache',
    'bb_groups_filename' : 'bb_groups.pkl',
    'toy' : True,
    'batched' : True,
}