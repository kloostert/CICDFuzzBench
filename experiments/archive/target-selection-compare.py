import json

RUNS = [[x for x in range(16, 94 + 1)],
        [x for x in range(95, 181 + 1)],
        [x for x in range(183, 269 + 1)],
        [x for x in range(271, 356 + 1)],
        [x for x in range(358, 444 + 1)],
        [x for x in range(446, 532 + 1)],
        [x for x in range(534, 620 + 1)],
        [x for x in range(622, 710 + 1)],
        [x for x in range(712, 798 + 1)],
        [x for x in range(800, 888 + 1)],
        [x for x in range(890, 980 + 1)],
        [x for x in range(982, 1068 + 1)]]


def check_sha_overall():
    cnt_total = 0
    cnt_equal = 0
    missing_targets = 0
    prev_shas = None
    for i in RUNS:
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


def check_sha_per_fuzzer():
    overall = {'libfuzzer': [], 'honggfuzz': [], 'aflplusplus': []}
    cnt_total = {}
    cnt_equal = {}
    missing_targets = {}
    prev_shas = None
    for j in RUNS:
        for i in j:
            with open(f'/srv/results/real/{i:04d}/sha', 'r') as file:
                shas = json.load(file)
            if prev_shas is None:
                prev_shas = shas
                continue
            for fuzzer in shas:
                if fuzzer not in cnt_equal:
                    cnt_equal[fuzzer] = 0
                if fuzzer not in cnt_total:
                    cnt_total[fuzzer] = 0
                if fuzzer not in missing_targets:
                    missing_targets[fuzzer] = 0
                for target in shas[fuzzer]:
                    cnt_total[fuzzer] += 1
                    try:
                        if shas[fuzzer][target] == prev_shas[fuzzer][target]:
                            cnt_equal[fuzzer] += 1
                    except KeyError:
                        missing_targets[fuzzer] += 1
            prev_shas = shas
        print(cnt_equal, cnt_total, missing_targets)
        for fuzzer in overall:
            overall[fuzzer].append(cnt_equal[fuzzer] / cnt_total[fuzzer] * 100)
        cnt_total = {}
        cnt_equal = {}
        missing_targets = {}
    print(overall)


def check_sha_per_target():
    default = {'openssl-bignum': 0, 'openssl-asn1parse': 0, 'openssl-x509': 0, 'openssl-server': 0, 'openssl-client': 0}
    overall = {'openssl-bignum': [], 'openssl-asn1parse': [], 'openssl-x509': [], 'openssl-server': [],
               'openssl-client': []}
    cnt_total = default.copy()
    cnt_equal = default.copy()
    missing_targets = default.copy()
    prev_shas = None
    for j in RUNS:
        for i in j:
            with open(f'/srv/results/real/{i:04d}/sha', 'r') as file:
                shas = json.load(file)
            if prev_shas is None:
                prev_shas = shas
                continue
            for fuzzer in shas:
                for target in shas[fuzzer]:
                    cnt_total[target] += 1
                    try:
                        if shas[fuzzer][target] == prev_shas[fuzzer][target]:
                            cnt_equal[target] += 1
                    except KeyError:
                        missing_targets[target] += 1
            prev_shas = shas
        print(cnt_equal, cnt_total, missing_targets, '\n')
        for target in overall:
            overall[target].append(cnt_equal[target] / cnt_total[target] * 100)
        cnt_total = default.copy()
        cnt_equal = default.copy()
        missing_targets = default.copy()
    print(overall)


if __name__ == '__main__':
    check_sha_per_fuzzer()
    check_sha_per_target()
    equal, total, missing = check_sha_overall()
    print(
        f'Equal hashes: {equal}\tTotal hashes: {total}\tPercentage: {equal / total * 100}%\tMissing targets: {missing}')
