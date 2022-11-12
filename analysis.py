import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import io
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier, XGBRegressor
from sklearn.linear_model import LinearRegression, BayesianRidge
from PIL import Image
from tools import replace_forbidden_symbols
import os
import warnings


warnings.filterwarnings('ignore')


def plot_to_pil(func, *args, extra=lambda g: None, **kwargs):
    plt.figure()
    g = func(*args, **kwargs)
    extra(g)
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='jpg')
    to_save = Image.open(img_buffer)
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png',
        transparent=True, bbox_inches='tight')
    to_show = Image.open(img_buffer)
    return to_show, to_save


def to_text(lines):
    return '\n'.join(lines)


def zscore_bounds(col, threshold=3):
    std = col.std()
    mean = col.mean()
    lower_bound = -std * threshold + mean
    upper_bound = std * threshold + mean
    return lower_bound, upper_bound


def quantiles_bounds(col):
    Q1, Q3 = col.quantile(.25), col.quantile(.75)
    lb = Q1 - 1.5 * (Q3 - Q1)
    ub = Q3 + 1.5 * (Q3 - Q1)
    return lb, ub


def quick_bounds(col):
    lb1, ub1 = quantiles_bounds(col)
    lb2, ub2 = zscore_bounds(col, threshold=5)
    return (lb1 + lb2) / 2, (ub1 + ub2) / 2


def hist_with_bounds(arr, lb, ub, n_bins):
    sns.histplot(arr, bins=n_bins)
    y_lim = plt.gca().get_ylim()[1]
    for x0 in [lb, ub]:
        plt.vlines(ymin=0, ymax=y_lim / 3, x=x0, color='red', linestyles='dotted')


def clamp(val, min_, max_):
    return max(min(val, max_), min_)


def make_header(header):
    return header + '\n' + '-' * 10


def dropna_for2(col1, col2):
    mask = (~col1.isna()) & (~col2.isna())
    col1 = col1[mask]
    col2 = col2[mask]
    return col1.reset_index(drop=True), col2.reset_index(drop=True)


def stats(estimators, results, col1_name, col2_name, x, y):
    try:
        for lbl, estim in estimators.items():
            scores = cross_val_score(estim(), x, y, cv=3)
            stats = np.array([scores.min(), scores.max(), scores.mean()]) * 100
            label = f'{col1_name} -> {col2_name}' + ' | Min: {:.2f}% Max: {:.2f}% Mean: {:.2f}%'.format(*stats)
            results[f'Попытка предсказания [{lbl}]'] = plot_to_pil(sns.barplot, x=np.arange(1, 4),
                y=scores, extra=lambda x: plt.title(label))
    except:
        pass


def top_bottom(col, results, header, prop_name, element_header, min_log=3, max_log=6):
    if type(col) != pd.Series:
        col = pd.Series(col)
    n_unique = col.nunique()
    value_counts = col.value_counts()

    if col.nunique() < min_log * 2:
        return
    
    border = min(int(n_unique / 2), max_log)
    iterations = list(range(border)) + list(range(len(value_counts) - border, len(value_counts)))

    all_rows = [f'{i + 1}. {element_header} "{value_counts.index[i]}" -> {value_counts.values[i]}' +
            ' ({:.2f}%)'.format(value_counts.values[i] / len(col)) for i in iterations]
    
    results[prop_name] = to_text(
        [make_header(header)] + all_rows[:border] +
        ['...\n', make_header('Конец списка:')] + all_rows[border:])


def cut_too_long_labels(labels, max_len=16):
    new_labels = []
    for label in labels:
        label = str(label)
        if len(label) > max_len:
            new_labels.append(label[:max_len - 3] + '...')
        else:
            new_labels.append(label)
    return new_labels


def plot_classes(col, results, max_plots=5, header='BARPLOT', minvpp=8, maxvpp=16):
    if type(col) != pd.Series:
        col = pd.Series(col)
    n_unique = col.nunique()
    value_counts = col.value_counts()
    vals_per_plot = clamp(int(n_unique / 3) + 1, minvpp, maxvpp)
    max_val = value_counts.max()
    for i in range(0, n_unique // vals_per_plot + 1):
        if i + 1 > max_plots:
            break
        a, b = i * vals_per_plot, (i + 1) * vals_per_plot
        vals = value_counts.values[a:b]
        shorten_index = cut_too_long_labels(value_counts.index[a:b])
        results[f'{header} ({i + 1})'] = plot_to_pil(
            sns.barplot, x=vals, y=shorten_index, extra=lambda g: g.set(xlim=(0, max_val)))


class Analyzer:
    def __init__(self, *data):
        self.analyze(*data)
    
    def analyze(self, col):
        self.results = {}
        
    def save(self, path):
        for k, obj in self.results.items():
            filename = os.path.join(path, replace_forbidden_symbols(k))
            if type(obj) == str:
                with open(filename + '.txt', 'w', encoding='utf8') as f:
                    f.write(obj)
            else:
                img = obj[1]
                img.save(filename + '.jpg')


class NumAnalyzer(Analyzer):
    def analyze(self, col):
        nan_perc = col.isna().sum() / len(col) * 100
        col = col.dropna()
        num_bins = min(len(col) // 3, 50)
        
        logged = np.log(col - col.min() + 5e-3)
        lb, ub = quick_bounds(col)
        l_lb, l_ub = quick_bounds(logged)
        outliers = col[(col < lb) | (col > ub)].index
        l_outliers = logged[(logged < l_lb) | (logged > l_ub)].index

        self.results = {
            'Общая статистика': to_text([
                f'Размер столбца: {len(col)} строк',
                'Содержание NaN значений: {:.2f}%'.format(nan_perc),
                'Среднее значение: {:.2f}'.format(col.mean()),
                'Стандартное отклонение: {:.2f}'.format(col.std()),
                'Минимум: {:.2f}'.format(col.min()),
                'Максимум: {:.2f}'.format(col.max()),
                'Разброс значений: {:.2f}'.format(col.max() - col.min()),
                'Медиана: {:.2f}'.format(col.median()),
                'Квартиль 25%: {:.2f}'.format(col.quantile(.25)),
                'Квартиль 75%: {:.2f}'.format(col.quantile(.75))
            ]),
            'Выбросы': to_text([
                'Содержание выбросов: {:.2f}%'.format(len(outliers) / len(col) * 100),
                'Содержание выбросов LOG: {:.2f}%'.format(len(l_outliers) / len(col) * 100),
                'Нижняя и верхняя границы: {:.2f}; {:.2f}'.format(lb, ub),
                'Нижняя и верхняя границы LOG: {:.2f}; {:.2f}'.format(l_lb, l_ub)
            ]),
            'Гистограмма с выбросами': plot_to_pil(hist_with_bounds, col, lb, ub, num_bins),
            'Гистограмма без выбросов': plot_to_pil(sns.histplot, col.drop(outliers), bins=num_bins),
            'LOG Гистограмма с выбросами': plot_to_pil(hist_with_bounds, logged, l_lb, l_ub, num_bins),
            'LOG Гистограмма без выбросов': plot_to_pil(sns.histplot, logged.drop(l_outliers), bins=num_bins),
            'BOXPLOT': plot_to_pil(sns.boxplot, x=col.drop(outliers))
        }


class CatAnalyzer(Analyzer):
    def analyze(self, col):
        l = len(col)
        nan_perc = col.isna().sum() / l * 100
        col = col.dropna()
        n_unique = col.nunique()
        value_counts = col.value_counts()

        self.results = {
            'Общая статистика': to_text([
                f'Размер столбца: {l} строк',
                'Содержание NaN значений: {:.2f}%'.format(nan_perc),
                f'Количество классов: {n_unique}',
                f'Состояние данных: {"Закодированы" if str(col.dtype).startswith("int") else "Не закодированы"}'
            ])
        }

        top_bottom(col, self.results, 'Топ встречи каждого класса в данных:',
            'Самые выделяющиеся классы', 'Класс')

        plot_classes(col, self.results)


class CatCatAnalyzer(Analyzer):
    def analyze(self, col1, col2):
        col1, col2 = dropna_for2(col1, col2)
        col1_enc = LabelEncoder().fit_transform(col1)
        col2_enc = LabelEncoder().fit_transform(col2)
        n_un1, n_un2 = col1.nunique(), col2.nunique()
        x, y = col1_enc.reshape(-1, 1), col2_enc

        to_predict = {
            'RFC': RandomForestClassifier,
            'XGBC': XGBClassifier,
            'DTC': DecisionTreeClassifier
        }
        pairs = pd.Series([
            (col1[i], col2[i])
            for i in range(len(col1))  
        ])
        pairs_vcperc = pairs.value_counts(normalize=True)

        if n_un1 >= n_un2:
            names = [col1.name, col2.name]
            ratio = n_un1 / n_un2
        else:
            names = [col1.name, col2.name]
            ratio = n_un2 / n_un1

        lack = (pairs_vcperc < .05).sum()
        not_lack = len(pairs_vcperc) - lack

        self.results = {
            'Общая статистика': to_text([
                f'Количество классов колонки "{col1.name}": {n_un1}',
                f'Количество классов колонки "{col2.name}": {n_un2}',
                f'Количество уникальных классовых пар: {len(pairs)}',
                f'Количество классовых пар, находящихся в недостатке (<5%): {lack} [{round(lack / len(pairs_vcperc) * 100)}%]',
                f'Количетсо классовых пар, находящихся в достатке (>=5%): {not_lack} [{round(not_lack / len(pairs_vcperc) * 100)}%]',
                'Доля самой распространённой классовой пары: {:.2f}'.format(pairs_vcperc.iloc[0]),
                f'На каждый класс из колонки "{names[0]}" приходится {round(ratio, 2)} классов из колонки "{names[1]}"'
            ])
        }
        top_bottom(pairs, self.results, f'Топ пар [{col1.name}, {col2.name}]:', 'Топ пар классов', 'Пара')
        plot_classes(pairs, self.results, header=f'Пары классов [{col1.name}, {col2.name}]')
        stats(to_predict, self.results, col1.name, col2.name, x, y)


class NumCatAnalyzer(Analyzer):
    def analyze(self, col1, col2):
        # col1 -> numeric, col2 -> cat
        col1, col2 = dropna_for2(col1, col2)
        df = pd.DataFrame({
            'cat': col2,
            'num': col1
        })
        unique_classes = col2.value_counts().index
        self.results = dict()

        data = []
        
        for cat in unique_classes:
            vals = col1[col2 == cat]
            count = len(vals)
            stats = [vals.min(), vals.max(), vals.mean(),
                vals.std(), vals.median()]
            data.append((cat, count, stats))

        rps = 7

        for i in range(len(data) // rps + 1):
            if i > 5:
                break
            cats = unique_classes[i * rps:(i + 1) * rps]
            subdf = df[df['cat'].isin(cats)]
            self.results[f'Гистограммы классов ({i + 1})'] = plot_to_pil(
                sns.violinplot, extra=lambda g: g.set(xlabel=None, ylabel=None), data=subdf, y='cat', x='num')

        for i in range(len(data) // rps + 1):
            if i > 6:
                break
            start_idx = i * rps
            lines = []
            for j in range(rps):
                k = start_idx + j
                if k >= len(data):
                    break
                lines.append(f'{k + 1}. Класс {data[k][0]} -> {data[k][1]} ({round(data[k][1] / len(col1) * 100, 2)}%)')
                lines.append('& Мин: {:.2f} Макс: {:.2f} Ср.знач: {:.2f} Стд. Откл.: {:.2f} Мед.: {:.2f}'.format(*data[k][2]))
                lines.append('')
            self.results[f'Статистика классов ({i + 1})'] = to_text(lines)

        estimators = {
            'RFC': RandomForestClassifier,
            'XGBC': XGBClassifier,
            'DTC': DecisionTreeClassifier
        }

        stats(estimators, self.results, col1.name, col2.name, col1, col2)


class NumNumAnalyzer(Analyzer):
    def analyze(self, col1, col2):
        col1, col2 = dropna_for2(col1, col2)
        corr1 = np.corrcoef(col1.values, col2.values)[0, 1]
        covar1 = np.cov(col1.values, col2.values)[0, 1]
        c1_lb, c1_ub = zscore_bounds(col1, threshold=5)
        c2_lb, c2_ub = zscore_bounds(col2, threshold=5)
        outliers_indices = np.where(
            (col1 > c1_ub) | (col1 < c1_lb) | (col2 > c2_ub) | (col2 < c2_lb)
        )[0]
        hue = np.array(['Нормальные'] * len(col1))
        hue[outliers_indices] = ['Выбросы'] * len(outliers_indices)
        self.results = dict()
        self.results['График зависимости'] = plot_to_pil(sns.scatterplot, x=col1, y=col2, hue=hue)
        cl_col1, cl_col2 = col1.drop(outliers_indices), col2.drop(outliers_indices)
        corr2 = np.corrcoef(cl_col1.values, cl_col2.values)[0, 1]
        covar2 = np.cov(cl_col1.values, cl_col2.values)[0, 1]
        self.results['График зависимости без выбросов'] = plot_to_pil(sns.scatterplot, x=cl_col1, y=cl_col2)
        for title, data in zip(['Корреляция', 'Ковариация'], [(corr1, corr2), (covar1, covar2)]):
            self.results[title] = plot_to_pil(sns.barplot,
                extra=lambda x: plt.title('До / после очистки данных'),
                y=list(data),
                x=[f'{title} (1)', f'{title} (2)'])
        
        estimators = {
            'XGBR': XGBRegressor,
            'RFR': RandomForestRegressor,
            'LinR': LinearRegression,
            'BRidge': BayesianRidge
        }

        x, y = cl_col1.values.reshape(-1, 1), cl_col2.values
        stats(estimators, self.results, col1.name, col2.name, x, y)