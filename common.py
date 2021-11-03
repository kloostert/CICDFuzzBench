import datetime
import json
import os
import subprocess
import sys

TARGET = 'openssl'
DEFAULT_TIMEOUT = '10m'
DEFAULT_FUZZERS = '(aflplusplus honggfuzz libfuzzer)'
DEFAULT_TARGETS = '(asn1parse bignum server client x509)'


def log_info(entry):
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}] (INFO) {entry}')


def log_error(entry):
    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}] (ERROR) {entry}')


def run_cmd_disable_output(command_array, **kwargs):
    return subprocess.run(command_array, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)


def run_cmd_enable_output(command_array, **kwargs):
    return subprocess.run(command_array, **kwargs)


def run_cmd_capture_output(command_array, **kwargs):
    return subprocess.run(command_array, capture_output=True, text=True, **kwargs)


def get_stdout(result):
    return result.stdout.strip('\n"')


def save_coverage_statistics(result_index, experiment_type):
    logfiles = []
    stats = {'libfuzzer': {}, 'honggfuzz': {}, 'aflplusplus': {}}
    try:
        for filename in os.listdir('./tools/captain/workdir/log/'):
            if 'container.log' in filename:
                logfiles.append(os.path.join('./tools/captain/workdir/log/', filename))
    except Exception as e:
        log_error(e)

    for logfile in logfiles:
        try:
            with open(logfile, 'r') as log:
                target = logfile.split('_')
                subtarget = f'{target[1]}-{target[2]}'
                temp = []
                stat = []
                if target[0].endswith('libfuzzer'):
                    for line in log:
                        if 'Fuzz target sha256: ' in line:
                            lib_sha = line.split()[3]
                        if ' corpus size: ' in line:
                            temp.append(line.split(':')[1].strip())
                        if 'oom/timeout/crash:' in line:
                            stat.append(line)
                    start = stat[0].split()
                    stop = stat[-1].split()
                    stats['libfuzzer'][subtarget] = {}
                    stats['libfuzzer'][subtarget]['start'] = {'coverage': start[2], 'features': start[4],
                                                              'corpus': start[6], 'exec/s': start[8], 'time': start[12]}
                    stats['libfuzzer'][subtarget]['stop'] = {'coverage': stop[2], 'features': stop[4],
                                                             'corpus': stop[6], 'exec/s': stop[8], 'time': stop[12]}
                    stats['libfuzzer'][subtarget]['corpus'] = {'start': temp[0], 'min': temp[1], 'stop': temp[2]}
                    stats['libfuzzer'][subtarget]['sha'] = lib_sha
                elif target[0].endswith('honggfuzz'):
                    for line in log:
                        if 'Fuzz target sha256: ' in line:
                            hongg_sha = line.split()[3]
                        if ' corpus size: ' in line:
                            temp.append(line.split(':')[1].strip())
                        if 'Summary iterations:' in line:
                            stat.append(line)
                    stop = stat[0].split()
                    stats['honggfuzz'][subtarget] = {'coverage_percent': stop[9].split(':')[1],
                                                     'guard_nb': stop[8].split(':')[1],
                                                     'new_units': stop[6].split(':')[1],
                                                     'exec/s': stop[3].split(':')[1], 'time': stop[2].split(':')[1],
                                                     'start_corp': temp[0], 'min_corp': temp[1], 'stop_corp': temp[2],
                                                     'sha': hongg_sha}
                elif target[0].endswith('aflplusplus'):
                    for line in log:
                        if 'Fuzz target sha256: ' in line:
                            afl_sha = line.split()[3]
                        if ' corpus size: ' in line:
                            temp.append(line.split(':')[1].strip())
                        if 'A coverage of ' in line:
                            stat.append(line)
                    stop = stat[0].split()
                    stats['aflplusplus'][subtarget] = {'coverage_percent': stop[12].split('%')[0][1:],
                                                       'covered_edges': stop[4], 'total_edges': stop[10],
                                                       'inputs': stop[14],
                                                       'start_corp': temp[0], 'min_corp': temp[1], 'stop_corp': temp[2],
                                                       'sha': afl_sha}
        except Exception as e:
            log_error(e)
    with open(f'/srv/results/{experiment_type}/{result_index}/coverage_results', 'w') as f:
        json.dump(stats, f, indent=4)


def save_sha(result_index, experiment_type):
    logfiles = []
    stats = {'libfuzzer': {}, 'honggfuzz': {}, 'aflplusplus': {}}
    try:
        for filename in os.listdir('./tools/captain/workdir/log/'):
            if 'container.log' in filename:
                logfiles.append(os.path.join('./tools/captain/workdir/log/', filename))
    except Exception as e:
        log_error(e)

    for logfile in logfiles:
        try:
            with open(logfile, 'r') as log:
                target = logfile.split('_')
                subtarget = f'{target[1]}-{target[2]}'
                if target[0].endswith('libfuzzer'):
                    for line in log:
                        if 'Fuzz target sha256: ' in line:
                            lib_sha = line.split()[3]
                    stats['libfuzzer'][subtarget] = lib_sha
                elif target[0].endswith('honggfuzz'):
                    for line in log:
                        if 'Fuzz target sha256: ' in line:
                            hongg_sha = line.split()[3]
                    stats['honggfuzz'][subtarget] = hongg_sha
                elif target[0].endswith('aflplusplus'):
                    for line in log:
                        if 'Fuzz target sha256: ' in line:
                            afl_sha = line.split()[3]
                    stats['aflplusplus'][subtarget] = afl_sha
        except Exception as e:
            log_error(e)
    with open(f'/srv/results/{experiment_type}/{result_index}/sha', 'w') as f:
        json.dump(stats, f, indent=4)


def save_nr_crashes(result_index, experiment_type):
    crashes = {'libfuzzer': {}, 'honggfuzz': {}, 'aflplusplus': {}}
    try:
        for dirname in os.listdir(f'./tools/captain/workdir/ar/aflplusplus/{TARGET}/'):
            nr_crashes = len(
                os.listdir(f'./tools/captain/workdir/ar/aflplusplus/{TARGET}/{dirname}/0/findings/crashes/'))
            if nr_crashes > 0:
                nr_crashes -= 1
            crashes['aflplusplus'][f'{TARGET}-{dirname}'] = nr_crashes
    except Exception as e:
        log_error(e)

    try:
        for dirname in os.listdir(f'./tools/captain/workdir/ar/libfuzzer/{TARGET}/'):
            nr_crashes = len(os.listdir(f'./tools/captain/workdir/ar/libfuzzer/{TARGET}/{dirname}/0/findings/'))
            crashes['libfuzzer'][f'{TARGET}-{dirname}'] = nr_crashes
    except Exception as e:
        log_error(e)

    try:
        for dirname in os.listdir(f'./tools/captain/workdir/ar/honggfuzz/{TARGET}/'):
            nr_crashes = len(os.listdir(f'./tools/captain/workdir/ar/honggfuzz/{TARGET}/{dirname}/0/findings/'))
            if nr_crashes > 0:
                nr_crashes -= 1
            crashes['honggfuzz'][f'{TARGET}-{dirname}'] = nr_crashes
    except Exception as e:
        log_error(e)

    with open(f'/srv/results/{experiment_type}/{result_index}/nr_crashes', 'w') as f:
        json.dump(crashes, f, indent=4)


def configure_settings(result_index, experiment_type, timeout=DEFAULT_TIMEOUT, fuzzers=DEFAULT_FUZZERS,
                       targets=DEFAULT_TARGETS, commit=None):
    settings = {}

    with open('./tools/captain/captainrc', 'r') as file:
        data = file.readlines()
    for idx in range(len(data)):
        if '#' not in data[idx]:
            if 'TIMEOUT=' in data[idx]:
                data[idx] = f'TIMEOUT={timeout}\n'
            if 'FUZZERS=' in data[idx]:
                data[idx] = f'FUZZERS={fuzzers}\n'
            if len(data[idx]) > 1:
                setting = data[idx].split('=')
                settings[setting[0]] = setting[1][:-1]
    with open('./tools/captain/captainrc', 'w') as file:
        file.writelines(data)

    with open(f'./targets/{TARGET}/configrc', 'r') as file:
        data = file.readlines()
    for idx in range(len(data)):
        if 'PROGRAMS=' in data[idx]:
            data[idx] = f'PROGRAMS={targets}\n'
        if len(data[idx]) > 1:
            setting = data[idx].split('=')
            settings[setting[0]] = setting[1][:-1]
    with open(f'./targets/{TARGET}/configrc', 'w') as file:
        file.writelines(data)

    if commit:
        settings['COMMIT'] = commit

    with open(f'/srv/results/{experiment_type}/{result_index}/settings', 'w') as f:
        json.dump(settings, f, indent=4)


def save_new_corpus():
    try:
        for dirname in os.listdir(f'./targets/{TARGET}/corpus/'):
            run_cmd_enable_output(['rm', '-rf', f'./targets/{TARGET}/corpus/{dirname}'])
            run_cmd_enable_output(['mkdir', f'./targets/{TARGET}/corpus/{dirname}'])
    except Exception as e:
        log_error(e)
    try:
        for dirname in os.listdir(f'./tools/captain/workdir/ar/libfuzzer/{TARGET}/'):
            run_cmd_enable_output(['cp', '-a', f'./tools/captain/workdir/ar/libfuzzer/{TARGET}/{dirname}/0/corpus/.',
                                   f'./targets/{TARGET}/corpus/{dirname}/'])
    except Exception as e:
        log_error(e)
    try:
        for dirname in os.listdir(f'./tools/captain/workdir/ar/honggfuzz/{TARGET}/'):
            run_cmd_enable_output(['cp', '-a', f'./tools/captain/workdir/ar/honggfuzz/{TARGET}/{dirname}/0/output/.',
                                   f'./targets/{TARGET}/corpus/{dirname}/'])
    except Exception as e:
        log_error(e)
    try:
        for dirname in os.listdir(f'./tools/captain/workdir/ar/aflplusplus/{TARGET}/'):
            run_cmd_enable_output(
                ['cp', '-a', f'./tools/captain/workdir/ar/aflplusplus/{TARGET}/{dirname}/0/findings/queue/.',
                 f'./targets/{TARGET}/corpus/{dirname}/'])
    except Exception as e:
        log_error(e)


def initialize_seed_corpus():
    log_info('Initializing seed corpus...')
    run_cmd_enable_output(['rm', '-rf', f'./targets/{TARGET}/corpus'])
    if run_cmd_enable_output(['cp', '-r', f'../magma/targets/{TARGET}/corpus', f'./targets/{TARGET}/']).returncode != 0:
        log_error('Seed corpus initialization failed!')
        sys.exit(1)


def empty_seed_corpus():
    log_info('Initializing empty seed corpus...')
    run_cmd_enable_output(['rm', '-rf', f'./targets/{TARGET}/corpus'])
    run_cmd_enable_output(['mkdir', f'./targets/{TARGET}/corpus'])
    run_cmd_enable_output(['mkdir', 'asn1', 'asn1parse', 'bignum', 'client', 'server', 'x509'],
                          cwd=f'./targets/{TARGET}/corpus/')
    run_cmd_enable_output(['cp', 'zero', 'corpus/asn1/0'], cwd=f'./targets/{TARGET}')
    run_cmd_enable_output(['cp', 'zero', 'corpus/asn1parse/0'], cwd=f'./targets/{TARGET}')
    run_cmd_enable_output(['cp', 'zero', 'corpus/bignum/0'], cwd=f'./targets/{TARGET}')
    run_cmd_enable_output(['cp', 'zero', 'corpus/client/0'], cwd=f'./targets/{TARGET}')
    run_cmd_enable_output(['cp', 'zero', 'corpus/server/0'], cwd=f'./targets/{TARGET}')
    run_cmd_enable_output(['cp', 'zero', 'corpus/x509/0'], cwd=f'./targets/{TARGET}')
