from scipy import stats
import pandas as pd
import numpy as np
import re

NULL, NUMERIC, CATEGORICAL, COMPLEX, INDEX, RAW = 'NULL', 'NUM', 'CAT', 'PLEX', 'INDEX', 'RAW'
FORBIDDEN = '<>:"/\\|?*'


def replace_forbidden_symbols(s):
    s = s.replace('"', '')
    for ch in FORBIDDEN:
        s = s.replace(ch, '_')
    return s


def extract_name_with_format(path):
    if '\\' not in path and '/' not in path:
        return path
    i = len(path) - 1
    while i >= 0:
        if path[i] in ['\\', '/']:
            return path[i + 1:]
        i -= 1
    return path


def extract_name(path):
    nwf = extract_name_with_format(path)
    if '.' not in nwf:
        return nwf
    return nwf[:-nwf[::-1].index('.') - 1]


def find_numbers(s):
    s = s.replace(',', '.')
    found = re.findall('(\d*\.\d*|\d+)', s)
    #print(found)
    return [
        float(sample) for sample in found
        if re.search('\d', sample) is not None
    ]


def _check_len_values(len_values, k=0.95, return_mode=False):
    mode = stats.mode(len_values).mode[0]
    result = mode != 0 and len_values.count(mode) / len(len_values) >= k
    return result if not return_mode else (result, mode)


def choose_type(col, k=0.9):
    if len(col) == 0:
        return NULL
    
    unique_ratio = col.nunique() / len(col)

    if str(col.dtype).startswith('float'):
        if np.abs(col - np.floor(col)).sum() == 0:
            col = col.astype('int64')
        else:
            return NUMERIC

    if unique_ratio == 1:
        return INDEX

    if str(col.dtype).startswith('int'):
        if col.nunique() != col.max() - col.min() + 1:
            col = col.astype('float64')
            return NUMERIC
        return CATEGORICAL

    if col.dtype == 'object' and unique_ratio < k:
        return CATEGORICAL

    return RAW


def strweight(s):
    for ch in s:
        if ch not in [' ', '\n']:
            return True
    return False