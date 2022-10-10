#!/usr/bin/python3

import json
from scipy.stats import mannwhitneyu

DEBUG = False
metrics = ['reached', 'triggered', 'detected']
iter = 10
runs = ['5 minutes', '10 minutes', '15 minutes', '20 minutes', '30 minutes', '1 hours', '2 hours', '4 hours', '8 hours']
libs = {'php': 15, 'openssl': 17, 'sqlite3': 15, 'poppler': 59, 'lua': 14,
        'libxml2': 43, 'libpng': 106, 'libtiff': 37, 'libsndfile': 50}

for metric in metrics:
    print(f'\n{metric}:\n')
    nrofbugs = {}
    for i in range(len(runs)):
        if DEBUG:
            print(runs[i])
        nrofbugs[runs[i]] = []
        for lib in libs:
            dir = f"./{lib}/"
            start = libs[lib] + iter * i
            stop = libs[lib] + iter * (i + 1)
            if DEBUG:
                print('->', dir, start, stop)
            for j in range(start, stop):
                with open(f'{dir}{j:04d}/final_results', 'r') as file:
                    data = json.load(file)
                bugs = []
                for fuzzer in data[metric]:
                    for bug in data[metric][fuzzer]:
                        bugs.append(bug)
                nrofbugs[runs[i]].append(len(set(bugs)))
        if DEBUG:
            print(nrofbugs, 'length:', len(nrofbugs[runs[i]]))

    for run in range(len(runs) - 1):
        res = mannwhitneyu(nrofbugs[runs[run+1]], nrofbugs[runs[run]], alternative="greater", method="auto")
        print(runs[run+1], metric, 'more bugs than', runs[run], 'TRUE' if res.pvalue < 0.05 else 'FALSE', res, round(res.pvalue,3))
    print()

    res = mannwhitneyu(nrofbugs['5 minutes'], nrofbugs['10 minutes'], alternative="less", method="auto")
    print('5 minutes', metric, 'less bugs than 10 minutes', 'TRUE' if res.pvalue < 0.05 else 'FALSE', res, round(res.pvalue,3))
    for run in runs:
        if run not in ['5 minutes', '10 minutes']:
            res = mannwhitneyu(nrofbugs[run], nrofbugs['10 minutes'], alternative="greater", method="auto")
            print(run, metric, 'more bugs than 10 minutes', 'TRUE' if res.pvalue < 0.05 else 'FALSE', res, round(res.pvalue,3))
    for run in runs:
        if 'minutes' not in run:
            res = mannwhitneyu(nrofbugs[run], nrofbugs['30 minutes'], alternative="greater", method="auto")
            print(run, metric, 'more bugs than 30 minutes', 'TRUE' if res.pvalue < 0.05 else 'FALSE', res, round(res.pvalue,3))
    res = mannwhitneyu(nrofbugs['4 hours'], nrofbugs['2 hours'], alternative="greater", method="auto")
    print('4 hours', metric, 'more bugs than 2 hours', 'TRUE' if res.pvalue < 0.05 else 'FALSE', res, round(res.pvalue,3))
    res = mannwhitneyu(nrofbugs['8 hours'], nrofbugs['2 hours'], alternative="greater", method="auto")
    print('8 hours', metric, 'more bugs than 2 hours', 'TRUE' if res.pvalue < 0.05 else 'FALSE', res, round(res.pvalue,3))
