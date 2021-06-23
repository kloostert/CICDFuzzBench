import os
import time

import common as c

FUZZ_TIME = 600
POLL_TIME = 60
REPO_LOCATION = '../openssl/'
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
    c.run_cmd_enable_output(['rm', '-rf', './tools/captain/workdir'])
    c.run_cmd_enable_output(['rm', '-rf', './targets/openssl/repo'])
    c.run_cmd_enable_output(['mkdir', './targets/openssl/repo'])
    c.run_cmd_enable_output(['cp', '-a', '../openssl/.', './targets/openssl/repo'])
    c.run_cmd_enable_output(['cp', './targets/openssl/src/abilist.txt', './targets/openssl/repo'])
    c.run_cmd_enable_output(['./run.sh'], cwd='./tools/captain/')
    c.log_info('The fuzzing process has finished.')
    c.log_info('Gathering results...')
    new_result_index = int(max(os.listdir('/srv/results/real'))) + 1
    new_result_index = f'{new_result_index:04d}'
    c.run_cmd_enable_output(['mkdir', f'/srv/results/real/{new_result_index}'])
    c.run_cmd_enable_output(
        ['cp', './tools/captain/captainrc', f'/srv/results/real/{new_result_index}/fuzzer_settings'])
    c.run_cmd_enable_output(
        ['cp', './targets/openssl/configrc', f'/srv/results/real/{new_result_index}/fuzzed_targets'])
    c.save_coverage_statistics(new_result_index, 'real')
    c.save_nr_crashes(new_result_index, 'real')
    c.log_info(f'The results of this fuzzing campaign were stored in /srv/results/real/{new_result_index}/.')


def check_for_new_commits():
    global CURRENT_COMMIT
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'pull'])
    most_recent_commit = c.get_stdout(
        c.run_cmd_capture_output(['git', '-C', REPO_LOCATION, 'log', '-1', '--format="%H"']))
    if most_recent_commit != CURRENT_COMMIT:
        c.log_info(f'Starting the fuzzing process for new commit {most_recent_commit}!')
        fuzz_current_commit()
        CURRENT_COMMIT = most_recent_commit
        return True
    return False


if __name__ == '__main__':
    try:
        init_repo()
        while True:
            start = time.time()
            new = check_for_new_commits()
            stop = time.time()
            elapsed = int(stop - start)
            if new:
                if elapsed < FUZZ_TIME:
                    c.log_info(f'Fuzzing took {elapsed}s. Sleeping for {FUZZ_TIME - elapsed}s...')
                    time.sleep(FUZZ_TIME - elapsed)
                else:
                    c.log_info(f'The fuzzing effort went into overtime ({elapsed}s)!')
            else:
                c.log_info(f'No new commits found. Sleeping for {POLL_TIME - elapsed}s...')
                time.sleep(POLL_TIME - elapsed)
    except KeyboardInterrupt:
        print(f'\nINFO: Program was interrupted by the user.')
