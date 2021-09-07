import json
import sys


def check_sha(start_dir, stop_dir):
    cnt_total = 0
    cnt_equal = 0
    missing_targets = 0
    prev_shas = None
    for i in range(start_dir, stop_dir + 1):
        with open(f'/srv/results/real/{i:04d}/sha', 'r') as file:
            shas = json.load(file)
        if prev_shas is None:
            prev_shas = shas
            continue
        for fuzzer in shas:
            for target in shas[fuzzer]:
                cnt_total += 1
                try:
                    if shas[fuzzer][target] == prev_shas[fuzzer][target]:
                        cnt_equal += 1
                except KeyError:
                    missing_targets += 1
        prev_shas = shas
    return cnt_equal, cnt_total, missing_targets


if __name__ == '__main__':
    start = int(sys.argv[1])
    stop = int(sys.argv[2])
    equal, total, missing = check_sha(start, stop)
    print(
        f'Equal hashes: {equal}\tTotal hashes: {total}\tPercentage: {equal / total * 100}%\tMissing targets: {missing}')
