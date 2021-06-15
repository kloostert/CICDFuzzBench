import subprocess
import time

FUZZ_TIME = 600
POLL_TIME = 60
REPO_LOCATION = '../openssl/'
CURRENT_COMMIT = None


def run_cmd_disable_output(command_array, **kwargs):
    return subprocess.run(command_array, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)


def run_cmd_enable_output(command_array, **kwargs):
    return subprocess.run(command_array, **kwargs)


def run_cmd_capture_output(command_array, **kwargs):
    return subprocess.run(command_array, capture_output=True, text=True, **kwargs)


def get_stdout(result):
    return result.stdout.strip('\n"')


def init_repo():
    global CURRENT_COMMIT
    run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'reset', '--hard'])
    run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'clean', '-df'])
    run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'checkout', 'master'])
    run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'pull'])
    CURRENT_COMMIT = get_stdout(run_cmd_capture_output(['git', '-C', REPO_LOCATION, 'log', '-1', '--format="%H"']))
    print(f'INFO: The current commit is {CURRENT_COMMIT}.')


def fuzz_current_commit():
    run_cmd_enable_output(['rm', '-rf', './tools/captain/workdir'])
    run_cmd_enable_output(['rm', '-rf', './targets/openssl/repo'])
    run_cmd_enable_output(['mkdir', './targets/openssl/repo'])
    run_cmd_enable_output(['cp', '-a', '../openssl/.', './targets/openssl/repo'])
    run_cmd_enable_output(['cp', './targets/openssl/src/abilist.txt', './targets/openssl/repo'])
    run_cmd_enable_output(['./run.sh'], cwd='./tools/captain/')


def check_for_new_commits():
    global CURRENT_COMMIT
    run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'pull'])
    most_recent_commit = get_stdout(run_cmd_capture_output(['git', '-C', REPO_LOCATION, 'log', '-1', '--format="%H"']))
    if most_recent_commit != CURRENT_COMMIT:
        print(f'INFO: Starting the fuzzing process for new commit {most_recent_commit}!')
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
                    print(f'INFO: Sleeping for {FUZZ_TIME - elapsed}s...')
                    time.sleep(FUZZ_TIME - elapsed)
                else:
                    print(f'INFO: The fuzzing effort went into overtime ({elapsed}s)!')
            else:
                print(f'INFO: Sleeping for {POLL_TIME - elapsed}s...')
                time.sleep(POLL_TIME - elapsed)
    except KeyboardInterrupt:
        print(f'\nINFO: Program was interrupted by the user.')
