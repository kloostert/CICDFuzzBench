#!/usr/bin/env python3

from json import dump, load
from os import walk

if __name__ == '__main__':
    detected = {}
    _, _, filenames = next(walk('./workdir/poc/'))
    for f in filenames:
        try:
            fuzzer = f[:f.index('_')]
        except ValueError:
            continue
        bug = f[:-4][-6:]
        try:
            bug.index('_')
        except ValueError:
            if fuzzer not in detected:
                detected[fuzzer] = []
            if bug not in detected[fuzzer]:
                detected[fuzzer].append(bug)

    results = {'reached': {}, 'triggered': {}, 'detected': detected}
    with open('./results.json') as infile:
        bench = load(infile)['results']
        for fuzzer in bench:
            for program in bench[fuzzer]:
                for target in bench[fuzzer][program]:
                    for run in bench[fuzzer][program][target]:
                        for metric in bench[fuzzer][program][target][run]:
                            for bug in bench[fuzzer][program][target][run][metric]:
                                if fuzzer not in results[metric]:
                                    results[metric][fuzzer] = []
                                if bug not in results[metric][fuzzer]:
                                    results[metric][fuzzer].append(bug)

    with open('./final.json', 'w+') as outfile:
        dump(results, outfile, indent=4)
