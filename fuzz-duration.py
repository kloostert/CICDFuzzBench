import json
import os
import sys
import time

import common as c


TARGET = ''
REPO_LOCATION = ''
SETUP_LOCATION = ''
PATCH_LOCATION = ''
EXPERIMENT_TYPE = 'artificial'
BUGS = []
BUGS_ACTIVE = []
DURATIONS = []
ITERATIONS = 0
BASE_COMMITS = {'libpng':       'a37d4836519517bdce6cb9d956092321eca3e73b',
                'libsndfile':   '86c9f9eb7022d186ad4d0689487e7d4f04ce2b29',
                'libtiff':      'c145a6c14978f73bb484c955eb9f84203efcb12e',  # additional fetch step!
                'libxml2':      'ec6e3efb06d7b15cf5a2328fabd3845acea4c815',
                'lua':          'dbdc74dc5502c2e05e1c1e2ac894943f418c8431',
                'openssl':      '3bd5319b5d0df9ecf05c8baba2c401ad8e3ba130',  # additional fetch step!
                'php':          'bc39abe8c3c492e29bc5d60ca58442040bbf063b',  # additional fetch step!
                'poppler':      '1d23101ccebe14261c6afc024ea14f29d209e760',  # additional fetch step!
                'sqlite3':      '0000000000000000000000000000000000000000'   # no git!
                }


def checkout_base():
    c.log_info(f'Checking out the base commit {BASE_COMMITS[TARGET]}.')
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'reset', '--hard'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'clean', '-df'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'checkout', 'master'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'checkout', BASE_COMMITS[TARGET]])


def apply_setup_patches():
    try:
        for file in os.listdir(SETUP_LOCATION):
            if file.endswith('.patch'):
                if c.run_cmd_disable_output(['patch', '-p1', '-d', REPO_LOCATION, '-i',
                                             os.path.join(SETUP_LOCATION, file)]).returncode == 0:
                    c.log_info(f'Setup patch {file} has been applied successfully.')
                else:
                    c.log_error(f'Setup patch {file} could not be applied!')
                    sys.exit(1)
    except Exception as e:
        c.log_error('There are no setup patches for this target.')


def find_and_apply_patches():
    try:
        for file in os.listdir(PATCH_LOCATION):
            if file.endswith('.patch'):
                BUGS.append(os.path.join(PATCH_LOCATION, file))
                BUGS_ACTIVE.append(False)
    except Exception as e:
        c.log_error('The patches were not found!')
        c.log_error(e)
        sys.exit(1)

    for idx in range(len(BUGS)):
        introduce_or_fix_bug(idx)


def introduce_or_fix_bug(bug_index):
    if BUGS_ACTIVE[bug_index]:
        c.log_info(f'Including bugfix {BUGS[bug_index]}.')
        code = c.run_cmd_disable_output(['patch', '-p1', '-R', '-d', REPO_LOCATION, '-i', BUGS[bug_index]]).returncode
        if code == 0:
            BUGS_ACTIVE[bug_index] = False
        else:
            c.log_error(f'Bug {BUGS[bug_index]} is active yet it could not be patched...')
            sys.exit(code)
    else:
        c.log_info(f'Including bug {BUGS[bug_index]}.')
        code = c.run_cmd_disable_output(['patch', '-p1', '-d', REPO_LOCATION, '-i', BUGS[bug_index]]).returncode
        if code == 0:
            BUGS_ACTIVE[bug_index] = True
        else:
            c.log_error(f'Bug {BUGS[bug_index]} is inactive yet it could not be included...')
            sys.exit(code)


def fuzz_commit(timeout):
    c.log_info('Starting the fuzzing process!')
    new_result_index = int(max(os.listdir(f'../results/{TARGET}/{EXPERIMENT_TYPE}'))) + 1
    new_result_index = f'{new_result_index:04d}'
    c.run_cmd_enable_output(['mkdir', f'../results/{TARGET}/{EXPERIMENT_TYPE}/{new_result_index}'])
    c.configure_settings(new_result_index, EXPERIMENT_TYPE, TARGET, timeout=timeout)
    c.run_cmd_enable_output(['rm', '-rf', './tools/captain/workdir', f'./targets/{TARGET}/repo', f'./targets/{TARGET}/freetype2'])
    c.run_cmd_enable_output(['rm', '-rf', './tools/captain/benchd_results', './tools/captain/final_results'])
    c.run_cmd_enable_output(['mkdir', f'./targets/{TARGET}/repo'])
    c.run_cmd_enable_output(['cp', '-a', f'{REPO_LOCATION}.', f'./targets/{TARGET}/repo'])
    if TARGET == 'poppler':
        c.run_cmd_enable_output(['cp', '-a', '../freetype2', f'./targets/{TARGET}/'])
    if TARGET == 'openssl':
        c.run_cmd_enable_output(['cp', f'./targets/openssl/src/abilist.txt', f'./targets/{TARGET}/repo'])
    c.run_cmd_enable_output(['./run.sh'], cwd='./tools/captain/')
    c.log_info('The fuzzing process has finished.')
    c.log_info('Gathering results...')
    c.run_cmd_disable_output(['python3', 'gather_results.py', 'workdir/', 'benchd_results'], cwd='./tools/captain/')
    c.run_cmd_enable_output(['python3', 'gather_detected.py'], cwd='./tools/captain/')
    c.run_cmd_enable_output(['cp', './tools/captain/benchd_results', './tools/captain/final_results',
                             f'../results/{TARGET}/{EXPERIMENT_TYPE}/{new_result_index}'])
    save_bug_status(new_result_index)
    c.save_coverage_statistics(new_result_index, EXPERIMENT_TYPE, TARGET)
    c.save_nr_crashes(new_result_index, EXPERIMENT_TYPE, TARGET)
    c.save_new_corpus(TARGET)
    c.log_info(
        f'The results of this fuzzing campaign were stored in ../results/{TARGET}/{EXPERIMENT_TYPE}/{new_result_index}/.')


def save_bug_status(result_index):
    bug_status = {'active': [], 'inactive': []}
    active = 0
    for j in range(len(BUGS)):
        if BUGS_ACTIVE[j]:
            bug_status['active'].append(BUGS[j][-12:-6])
            active += 1
        else:
            bug_status['inactive'].append(BUGS[j][-12:-6])
    bug_status['nr_active_bugs'] = active
    bug_status['nr_inactive_bugs'] = len(BUGS) - active
    bug_status['nr_total_bugs'] = len(BUGS)
    with open(f'../results/{TARGET}/{EXPERIMENT_TYPE}/{result_index}/bug_status', 'w') as f:
        json.dump(bug_status, f, indent=4)


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            print(f'Usage: $ python3 {sys.argv[0]} <target-library>')
            sys.exit()
        if sys.argv[1] not in BASE_COMMITS:
            print(f'<target-library> has to be one of {list(BASE_COMMITS.keys())}')
            sys.exit()
        TARGET = sys.argv[1]
        DURATIONS = ['5m', '10m', '15m', '20m', '30m', '1h', '2h', '4h', '8h']
        ITERATIONS = 10
        REPO_LOCATION = f'../{TARGET}/'
        SETUP_LOCATION = f'../CometFuzz/targets/{TARGET}/patches/setup/'
        PATCH_LOCATION = f'../CometFuzz/targets/{TARGET}/patches/bugs/'
        # checkout_base()  # disabled, otherwise it overrides manual checkout
        # apply_setup_patches()  # disabled, otherwise it overrides manual set-up
        # find_and_apply_patches()  # disabled, otherwise it overrides manual set-up
        for duration in DURATIONS:
            c.log_info('Cleaning up disk space.')
            c.run_cmd_disable_output(['docker', 'system', 'prune', '-af'])
            c.log_info(f'Starting the run with a duration of {duration}.')
            # c.empty_seed_corpus()  # disabled, use seed corpus (this needs to be generalized before use as well)
            c.initialize_seed_corpus(TARGET)
            for i in range(ITERATIONS):
                c.log_info(f'Starting iteration {i + 1} of {ITERATIONS} for the duration of {duration}.')
                start = time.time()
                fuzz_commit(duration)
                stop = time.time()
                c.log_info(
                    f'Iteration {i + 1} of {ITERATIONS} for the duration of {duration} took {int(stop - start)}s.')
    except KeyboardInterrupt:
        print(f'\nProgram was interrupted by the user.')
