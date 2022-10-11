#!/usr/bin/python3

import json

DEBUG = False

iter = 10
runs = ['5 minutes', '10 minutes', '15 minutes', '20 minutes', '30 minutes', '1 hours', '2 hours', '4 hours', '8 hours']
libs = {'php': 15, 'openssl': 17, 'sqlite3': 15, 'poppler': 59, 'lua': 14, 'libxml2': 43, 'libpng': 106, 'libtiff': 37, 'libsndfile': 50}
bugs = {'reached': {}, 'triggered': {}, 'detected': {}}

for metric in bugs:
    if DEBUG:
        print(f'\n{metric}:\n')
    for i in range(len(runs)):
        bugs[metric][runs[i]] = []
        if DEBUG:
            print(runs[i])
        for lib in libs:
            dir = f"./{lib}/"
            start = libs[lib] + iter * i
            stop = libs[lib] + iter * (i + 1)
            if DEBUG:
                print('->', dir, start, stop)
            for j in range(start, stop):
                with open(f'{dir}{j:04d}/final_results', 'r') as file:
                    data = json.load(file)
                for fuzzer in data[metric]:
                    for bug in data[metric][fuzzer]:
                        bugs[metric][runs[i]].append(bug)
        if DEBUG:
            print('bugs[metric][runs[i]] length:', len(bugs[metric][runs[i]]))
            print('set(bugs[metric][runs[i]]) length:', len(set(bugs[metric][runs[i]])))
            print(set(bugs[metric][runs[i]]))
        bugs[metric][runs[i]] = list(set(bugs[metric][runs[i]]))

for metric in bugs:
    print('\n')
    for i in range(len(runs)):
        print()
        data = bugs[metric][runs[i]]
        data.sort()
        print(metric, runs[i], data)
