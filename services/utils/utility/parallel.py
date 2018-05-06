
import numpy as np
import pandas as pd
from multiprocessing import Pool

def parallel_array(func,input_array, num_partitions, num_cores, split_axis=0):
    '''parallel array by splitting dataframe as rows/column,default split as rows'''
    pool = Pool(num_cores)
    arr_splited = np.array_split(input_array, num_partitions, axis=split_axis)
    concated_arr = np.concatenate(pool.map(func, arr_splited), axis=split_axis)
    pool.close()
    pool.join()
    return concated_arr


def parallel_dataframe(func,input_df, num_partitions, num_cores, split_axis=0):
    '''parallel dataframe by splitting dataframe as rows/column,default split as rows'''
    pool = Pool(num_cores,maxtasksperchild=1000)
    df_splited = np.array_split(input_df, num_partitions, axis=split_axis)
    df_concated = pd.concat(pool.map(func, df_splited), axis=split_axis)
    pool.close()
    pool.join()
    return df_concated