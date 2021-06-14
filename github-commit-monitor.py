import datetime
import subprocess
import sys
import time

import requests

FUZZ_TIME = 600
POLL_TIME = 61
REPO_LOCATION = '../openssl/'
GITHUB_OPENSSL_REPO_EVENTS_LINK = 'https://api.github.com/repos/openssl/openssl/events'
CURRENT_COMMIT = None


def checkout_new_commit():
    subprocess.run(['git', '-C', REPO_LOCATION, 'reset', '--hard'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    subprocess.run(['git', '-C', REPO_LOCATION, 'clean', '-df'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    subprocess.run(['git', '-C', REPO_LOCATION, 'checkout', 'master'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    subprocess.run(['git', '-C', REPO_LOCATION, 'pull'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ret_val = subprocess.run(['git', '-C', REPO_LOCATION, 'checkout', CURRENT_COMMIT],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('Return value:', ret_val.returncode)
    if ret_val.returncode != 0:
        print(f'ERROR: Checking out {CURRENT_COMMIT} did not work properly...')
        sys.exit(1)


def find_new_commit():
    global CURRENT_COMMIT
    new_commit = False
    try:
        print(datetime.datetime.now())
        result = requests.get(url=GITHUB_OPENSSL_REPO_EVENTS_LINK)
        if result.headers['X-RateLimit-Remaining'] == '0':
            print('ERROR: We have exceeded the rate limit for this API (max 60/hour).')
            sys.exit(1)
        events = result.json()
        for event in events:
            if event['type'] == 'PushEvent':
                for commit in event['payload']['commits']:
                    print(commit)
                    if CURRENT_COMMIT != commit['sha']:
                        CURRENT_COMMIT = commit['sha']
                        new_commit = True
                    break
                break
        print('Current commit:', CURRENT_COMMIT)
        return new_commit
    except Exception as e:
        print('ERROR:', e)
        sys.exit(1)


def start_fuzzing():
    subprocess.run(['rm', '-rf', './tools/captain/workdir'])
    subprocess.run(['rm', '-rf', './targets/openssl/repo'])
    subprocess.run(['mkdir', './targets/openssl/repo'])
    subprocess.run(['cp', '-a', '../openssl/.', './targets/openssl/repo'])
    subprocess.run(['cp', './targets/openssl/src/abilist.txt', './targets/openssl/repo'])
    subprocess.run(['./run.sh'], cwd='./tools/captain/')


def fuzz_new_commit():
    if find_new_commit():
        print('Starting the fuzzing process!')
        checkout_new_commit()
        start_fuzzing()
        return True
    return False


if __name__ == '__main__':
    try:
        while True:
            start = time.time()
            fuzzed = fuzz_new_commit()
            stop = time.time()
            elapsed = int(stop - start)
            if fuzzed:
                if elapsed < FUZZ_TIME:
                    print(f'Sleeping for {FUZZ_TIME - elapsed}s...')
                    time.sleep(FUZZ_TIME - elapsed)
                else:
                    print('INFO: The fuzzing effort went into overtime!')
            else:
                print(f'Sleeping for {POLL_TIME - elapsed}s...')
                time.sleep(POLL_TIME - elapsed)
    except KeyboardInterrupt:
        print(f'\nProgram was interrupted by the user.')
