import datetime
import subprocess
import sys
import time

import requests
import schedule

REPO_LOCATION = './targets/openssl/repo/'
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


def check_for_commits():
    global CURRENT_COMMIT
    next_commit = None
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
                    if CURRENT_COMMIT == commit['sha'] and next_commit is not None:
                        CURRENT_COMMIT = next_commit
                        checkout_new_commit()
                    next_commit = commit['sha']
        if CURRENT_COMMIT is None and next_commit is not None:
            CURRENT_COMMIT = next_commit
            checkout_new_commit()
        print('Current commit:', CURRENT_COMMIT)
    except Exception as e:
        print('ERROR:', e)
        sys.exit(1)


if __name__ == '__main__':
    check_for_commits()
    schedule.every(61).seconds.do(check_for_commits)
    while True:
        schedule.run_pending()
        time.sleep(1)
