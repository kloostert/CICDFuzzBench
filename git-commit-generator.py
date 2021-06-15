import os
import random
import subprocess
import sys
import time

FUZZ_TIME = 600
REPO_LOCATION = '../openssl/'
PATCH_LOCATION = '../cometfuzz/targets/openssl/patches/bugs/'
BUGS = []
BUGS_ACTIVE = []


def log_info(entry):
    print(f'INFO: {entry}')


def log_error(entry):
    print(f'ERROR: {entry}')


def run_cmd_disable_output(command_array, **kwargs):
    return subprocess.run(command_array, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)


def run_cmd_enable_output(command_array, **kwargs):
    return subprocess.run(command_array, **kwargs)


def checkout_base():
    log_info('Checking out the base commit 728d03b576f360e72bbddc7e751433575430af3b.')
    run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'reset', '--hard'])
    run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'clean', '-df'])
    run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'checkout', 'master'])
    run_cmd_disable_output(['git', '-C', REPO_LOCATION, 'checkout', '728d03b576f360e72bbddc7e751433575430af3b'])


def find_patches():
    try:
        for file in os.listdir(PATCH_LOCATION):
            if file.endswith('.patch'):
                BUGS.append(os.path.join(PATCH_LOCATION, file))
                BUGS_ACTIVE.append(False)
    except Exception as e:
        log_error('The patches were not found!')
        log_error(e)
        sys.exit(1)


def introduce_or_fix_bug(bug_index):
    if BUGS_ACTIVE[bug_index]:
        log_info(f'Including bugfix {BUGS[bug_index]}.')
        code = run_cmd_disable_output(['patch', '-p1', '-R', '-d', REPO_LOCATION, '-i', BUGS[bug_index]]).returncode
        if code == 0:
            BUGS_ACTIVE[bug_index] = False
        else:
            log_error(f'Bug {BUGS[bug_index]} is active yet it could not be patched...')
            sys.exit(code)
    else:
        log_info(f'Including bugfix {BUGS[bug_index]}.')
        code = run_cmd_disable_output(['patch', '-p1', '-d', REPO_LOCATION, '-i', BUGS[bug_index]]).returncode
        if code == 0:
            BUGS_ACTIVE[bug_index] = True
        else:
            log_error(f'Bug {BUGS[bug_index]} is inactive yet it could not be included...')
            sys.exit(code)


def fuzz_commit():
    log_info('Starting the fuzzing process!')
    run_cmd_enable_output(['rm', '-rf', './tools/captain/workdir', './targets/openssl/repo'])
    run_cmd_enable_output(['rm', '-rf', './tools/captain/results.json', './tools/captain/final.json'])
    run_cmd_enable_output(['mkdir', './targets/openssl/repo'])
    run_cmd_enable_output(['cp', '-a', '../openssl/.', './targets/openssl/repo'])
    run_cmd_enable_output(['cp', './targets/openssl/src/abilist.txt', './targets/openssl/repo'])
    run_cmd_enable_output(['./run.sh'], cwd='./tools/captain/')
    run_cmd_disable_output(['python3.8', 'gather_results.py', 'workdir/', 'results.json'], cwd='./tools/captain/')
    run_cmd_enable_output(['python3.8', 'gather_detected.py'], cwd='./tools/captain/')
    new_result_index = int(max(os.listdir('/srv/results/artificial'))) + 1
    run_cmd_enable_output(['mkdir', f'/srv/results/artificial/{new_result_index}'])
    run_cmd_enable_output(['cp', './tools/captain/results.json', './tools/captain/final.json',
                           f'/srv/results/artificial/{new_result_index}'])


def generate_fuzz_commit():
    bug_idx = random.randint(0, len(BUGS) - 1)
    introduce_or_fix_bug(bug_idx)
    fuzz_commit()


def print_bug_status():
    active = 0
    for i in range(len(BUGS)):
        if BUGS_ACTIVE[i]:
            log_info(f'{BUGS[i][-12:-6]} ACTIVE')
            active += 1
        else:
            log_info(f'{BUGS[i][-12:-6]} INACTIVE')
    log_info(f'Active bugs: {active}\tInactive bugs: {len(BUGS) - active}\tTotal bugs: {len(BUGS)}')


if __name__ == '__main__':
    random.seed(14)  # for reproducibility
    try:
        checkout_base()
        find_patches()
        while True:
            start = time.time()
            generate_fuzz_commit()
            stop = time.time()
            elapsed = int(stop - start)
            if elapsed < FUZZ_TIME:
                log_info(f'Sleeping for {FUZZ_TIME - elapsed}s...')
                time.sleep(FUZZ_TIME - elapsed)
            else:
                log_info(f'The fuzzing effort went into overtime ({elapsed}s)!')
    except KeyboardInterrupt:
        print(f'\nProgram was interrupted by the user.')
        print_bug_status()
