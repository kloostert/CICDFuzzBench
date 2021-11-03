import json
import os
import sys
import time

import common as c

REPO_LOCATION = f'../{c.TARGET}/'
PATCH_LOCATION = f'../cometfuzz/targets/{c.TARGET}/patches/bugs/'
BUGS = []
BUGS_ACTIVE = []
DURATIONS = ['1m', '5m', '10m', '15m', '20m', '30m', '1h', '8h']
ITERATIONS = 5


def checkout_base():
    c.log_info('Checking out the base commit 728d03b576f360e72bbddc7e751433575430af3b.')
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'reset', '--hard'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'clean', '-df'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'checkout', 'master'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'checkout', '728d03b576f360e72bbddc7e751433575430af3b'])


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
    new_result_index = int(max(os.listdir('/srv/results/artificial'))) + 1
    new_result_index = f'{new_result_index:04d}'
    c.run_cmd_enable_output(['mkdir', f'/srv/results/artificial/{new_result_index}'])
    c.configure_settings(new_result_index, 'artificial', timeout=timeout)
    c.run_cmd_enable_output(['rm', '-rf', './tools/captain/workdir', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['rm', '-rf', './tools/captain/benchd_results', './tools/captain/final_results'])
    c.run_cmd_enable_output(['mkdir', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['cp', '-a', f'{REPO_LOCATION}.', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['cp', f'./targets/{c.TARGET}/src/abilist.txt', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['./run.sh'], cwd='./tools/captain/')
    c.log_info('The fuzzing process has finished.')
    c.log_info('Gathering results...')
    c.run_cmd_disable_output(['python3.8', 'gather_results.py', 'workdir/', 'benchd_results'], cwd='./tools/captain/')
    c.run_cmd_enable_output(['python3.8', 'gather_detected.py'], cwd='./tools/captain/')
    c.run_cmd_enable_output(['cp', './tools/captain/benchd_results', './tools/captain/final_results',
                             f'/srv/results/artificial/{new_result_index}'])
    save_bug_status(new_result_index)
    c.save_coverage_statistics(new_result_index, 'artificial')
    c.save_nr_crashes(new_result_index, 'artificial')
    c.save_new_corpus()
    c.log_info(f'The results of this fuzzing campaign were stored in /srv/results/artificial/{new_result_index}/.')


def save_bug_status(result_index):
    bug_status = {'active': [], 'inactive': []}
    active = 0
    for i in range(len(BUGS)):
        if BUGS_ACTIVE[i]:
            bug_status['active'].append(BUGS[i][-12:-6])
            active += 1
        else:
            bug_status['inactive'].append(BUGS[i][-12:-6])
    bug_status['nr_active_bugs'] = active
    bug_status['nr_inactive_bugs'] = len(BUGS) - active
    bug_status['nr_total_bugs'] = len(BUGS)
    with open(f'/srv/results/artificial/{result_index}/bug_status', 'w') as f:
        json.dump(bug_status, f, indent=4)


if __name__ == '__main__':
    try:
        checkout_base()
        find_and_apply_patches()
        for duration in DURATIONS:
            c.log_info(f'Starting the run with a duration of {duration}.')
            # c.empty_seed_corpus()
            c.initialize_seed_corpus()
            for i in range(ITERATIONS):
                c.log_info(f'Starting iteration {i + 1} of {ITERATIONS} for the duration of {duration}.')
                start = time.time()
                fuzz_commit(duration)
                stop = time.time()
                c.log_info(
                    f'Iteration {i + 1} of {ITERATIONS} for the duration of {duration} took {int(stop - start)}s.')
    except KeyboardInterrupt:
        print(f'\nProgram was interrupted by the user.')
