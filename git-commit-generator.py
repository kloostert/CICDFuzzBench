import os
import random
import subprocess
import sys
import time

import schedule

REPO_LOCATION = './targets/openssl/repo/'
PATCH_LOCATION = './targets/openssl/patches/bugs/'
BUGS = []
BUGS_ACTIVE = []


def checkout_base():
    print('Checking out 728d03b576f360e72bbddc7e751433575430af3b')
    subprocess.run(['git', '-C', REPO_LOCATION, 'reset', '--hard'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    subprocess.run(['git', '-C', REPO_LOCATION, 'clean', '-df'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    ret_val = subprocess.run(['git', '-C', REPO_LOCATION, 'checkout', '728d03b576f360e72bbddc7e751433575430af3b'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('Return value:', ret_val.returncode)
    if ret_val.returncode != 0:
        print('ERROR: Checking out the base commit did not work properly...')
        sys.exit(1)


def find_patches():
    try:
        for file in os.listdir(PATCH_LOCATION):
            if file.endswith('.patch'):
                BUGS.append(os.path.join(PATCH_LOCATION, file))
                BUGS_ACTIVE.append(False)
    except Exception as e:
        print('ERROR:', e)
        sys.exit(1)


def introduce_or_fix_bug(bug_index):
    if BUGS_ACTIVE[bug_index]:
        print('Including bugfix', BUGS[bug_index])
        ret_val = subprocess.run(['patch', '-p1', '-R', '-d', REPO_LOCATION, '-i', BUGS[bug_index]],
                                 stdout=subprocess.DEVNULL)
        print('Return value:', ret_val.returncode)
        if ret_val.returncode == 0:
            BUGS_ACTIVE[bug_index] = False
        else:
            print(f'ERROR: Bug {BUGS[bug_index]} is active yet it could not be patched...')
            sys.exit(ret_val.returncode)
    else:
        print('Including bug', BUGS[bug_index])
        ret_val = subprocess.run(['patch', '-p1', '-d', REPO_LOCATION, '-i', BUGS[bug_index]],
                                 stdout=subprocess.DEVNULL)
        print('Return value:', ret_val.returncode)
        if ret_val.returncode == 0:
            BUGS_ACTIVE[bug_index] = True
        else:
            print(f'ERROR: Bug {BUGS[bug_index]} is inactive yet it could not be included...')
            sys.exit(ret_val.returncode)


def generate_commit():
    bug_idx = random.randint(0, len(BUGS) - 1)
    introduce_or_fix_bug(bug_idx)


if __name__ == '__main__':
    checkout_base()
    find_patches()
    schedule.every(1).seconds.do(generate_commit)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print(f'\nProgram was interrupted by the user.\nBUGS =\n{BUGS}\nBUGS_ACTIVE =\n{BUGS_ACTIVE}')