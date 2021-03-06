import os
import time

import common as c

POLL_TIME = 60  # every minute
REPO_LOCATION = f'../{c.TARGET}/'
CURRENT_COMMIT = None


def init_repo():
    global CURRENT_COMMIT
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'reset', '--hard'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'clean', '-df'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'checkout', 'master'])
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'pull'])


def fuzz_current_commit(commit_sha):
    new_result_index = int(max(os.listdir('/srv/results/real'))) + 1
    new_result_index = f'{new_result_index:04d}'
    c.run_cmd_enable_output(['mkdir', f'/srv/results/real/{new_result_index}'])
    c.configure_settings(new_result_index, 'real', commit=commit_sha, timeout='10m')
    c.run_cmd_enable_output(['rm', '-rf', './tools/captain/workdir', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['mkdir', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['cp', '-a', f'{REPO_LOCATION}.', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['cp', f'./targets/{c.TARGET}/src/abilist.txt', f'./targets/{c.TARGET}/repo'])
    c.run_cmd_enable_output(['./run.sh'], cwd='./tools/captain/')
    c.log_info('The fuzzing process has finished.')
    c.log_info('Gathering results...')
    c.save_coverage_statistics(new_result_index, 'real')
    c.save_nr_crashes(new_result_index, 'real')
    c.save_new_corpus()
    c.log_info(f'The results of this fuzzing campaign were stored in /srv/results/real/{new_result_index}/.')


def check_for_new_commits():
    global CURRENT_COMMIT
    c.run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'pull'])
    most_recent_commit = c.get_stdout(
        c.run_cmd_capture_output(['git', '-C', REPO_LOCATION, 'log', '-1', '--format="%H"']))
    if most_recent_commit != CURRENT_COMMIT:
        c.log_info(f'Starting the fuzzing process for new commit {most_recent_commit}!')
        fuzz_current_commit(most_recent_commit)
        CURRENT_COMMIT = most_recent_commit
        return True
    return False


if __name__ == '__main__':
    try:
        init_repo()
        c.initialize_seed_corpus()
        while True:
            start = time.time()
            new = check_for_new_commits()
            stop = time.time()
            elapsed = int(stop - start)
            if new:
                c.log_info(f'Fuzzing commit {CURRENT_COMMIT} took {elapsed}s.')
            else:
                c.log_info(f'No new commits found. Sleeping for {POLL_TIME - elapsed}s...')
                time.sleep(POLL_TIME - elapsed)
    except KeyboardInterrupt:
        print(f'\nINFO: Program was interrupted by the user.')
