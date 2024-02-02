import os

settings = {
    # 'num_cpu_cores' : os.cpu_count() - 4,
    'num_cpu_cores' : 4,
    'path_to_cache' : 'cache',
    'bb_groups_filename' : 'bb_groups.pkl',
    'toy' : 1,      # 1 => True
    'batched' : 1,  # 1 => True
}