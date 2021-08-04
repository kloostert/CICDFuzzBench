import os
import time

import common as c

REPO_LOCATION = f'../{c.TARGET}/'
CURRENT_COMMIT = None


def init_repo():
    global CURRENT_COMMIT
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'reset', '--hard'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'clean', '-df'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'checkout', 'master'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'pull'])
    CURRENT_COMMIT = c.get_stdout(c.run_cmd_capture_output(['git', '-C', REPO_LOCATION, 'log', '-1', '--format="%H"']))
    c.log_info(f'The current commit is {CURRENT_COMMIT}.')


def fuzz_current_commit():
    c.log_info(f'Checking the SHA256 for the fuzz targets of commit {CURRENT_COMMIT}...')
    new_result_index = int(max(os.listdir('/srv/results/real'))) + 1
    new_result_index = f'{new_result_index:04d}'
    c.run_cmd_enable_output(['mkdir', f'/srv/results/real/{new_result_index}'])
    c.configure_settings(new_result_index, 'real', commit=CURRENT_COMMIT, timeout='1s')
    c.run_cmd_enable_output(['rm', '-rf', './tools/captain/workdir', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['mkdir', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['cp', '-a', f'{REPO_LOCATION}.', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['cp', f'./targets/{c.TARGET}/src/abilist.txt', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['./run.sh'], cwd='./tools/captain/')
    c.log_info('The fuzzing process has finished.')
    c.log_info('Gathering results...')
    c.save_coverage_statistics(new_result_index, 'real')
    c.save_nr_crashes(new_result_index, 'real')
    c.log_info(f'The results of this fuzzing campaign were stored in /srv/results/real/{new_result_index}/.')


def checkout_prev_commit():
    global CURRENT_COMMIT
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'checkout', 'HEAD^1'])
    CURRENT_COMMIT = c.get_stdout(c.run_cmd_capture_output(['git', '-C', REPO_LOCATION, 'log', '-1', '--format="%H"']))
    c.log_info(f'The current commit is {CURRENT_COMMIT}.')


if __name__ == '__main__':
    try:
        init_repo()
        c.empty_seed_corpus()
        fuzz_current_commit()
        while True:
            start = time.time()
            checkout_prev_commit()
            fuzz_current_commit()
            stop = time.time()
            elapsed = int(stop - start)
            c.log_info(f'Fuzzing commit {CURRENT_COMMIT} took {elapsed}s.')
    except KeyboardInterrupt:
        print(f'\nINFO: Program was interrupted by the user.')
