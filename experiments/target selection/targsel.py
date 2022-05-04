#!/usr/bin/env python3

import os
import subprocess
import sys

TARGET = ''
PREFIX = ''
FUZZER_DIR = ''
COMMIT = ''
COMMITS = []

def run_cmd(command_array, **kwargs):
    return subprocess.run(command_array, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)


def run_cmd_warn_msg(command, message, **kwargs):
    if run_cmd(command, **kwargs).returncode != 0:
        print(f'WARNING: {message}')


def run_cmd_error_msg(command, message, **kwargs):
    code = run_cmd(command, **kwargs).returncode
    if code != 0:
        print(f'ERROR: {message}')
        sys.exit(code)


def get_output(command_array, **kwargs):
    return subprocess.run(command_array, capture_output=True, text=True, **kwargs).stdout.strip('\n"')


def get_sqlite3_commits():
    global COMMITS
    with open(f'{PREFIX}/commits', 'r') as file:
        lines = file.readlines()
        for line in lines:
            COMMITS.append(line[0:8])


def compile_targets():
    targets = []
    if TARGET == 'poppler':
        run_cmd_warn_msg([f'{PREFIX}/../../poppler_compile.sh'], "Could not compile fuzz targets!")
    else:
        run_cmd_warn_msg([f'{PREFIX}_compile.sh'], "Could not compile fuzz targets!")
        if TARGET == 'lua':
            run_cmd_error_msg(['git', '-C', PREFIX, 'checkout', '.'], "Could not do git checkout .!")
    if TARGET == 'php':
        for file in os.listdir(FUZZER_DIR):
            if 'php-fuzz-' in file:
                targets.append(file)
    if TARGET == 'openssl':
        for file in os.listdir(FUZZER_DIR):
            if '.' not in file:
                if '-test' not in file:
                    if 'corp' not in file:
                        targets.append(file)
    if TARGET == 'sqlite3':
        if 'fuzzcheck' in os.listdir(FUZZER_DIR):
            targets.append('fuzzcheck')
    if TARGET == 'poppler':
        if 'pdftoppm' in os.listdir(FUZZER_DIR):
            targets.append('pdftoppm')
        if 'pdfimages' in os.listdir(FUZZER_DIR):
            targets.append('pdfimages')
    if TARGET == 'lua':
        if 'lua' in os.listdir(FUZZER_DIR):
            targets.append('lua')
    if TARGET == 'libxml2':
        if 'xmllint' in os.listdir(FUZZER_DIR):
            targets.append('xmllint')
    if TARGET == 'libsndfile':
        if 'sndfile_fuzzer' in os.listdir(FUZZER_DIR):
            targets.append('sndfile_fuzzer')
    if TARGET == 'libpng':
        if 'libpng_read_fuzzer' in os.listdir(FUZZER_DIR):
            targets.append('libpng_read_fuzzer')
    if TARGET == 'libtiff':
        if 'tiffcp' in os.listdir(FUZZER_DIR):
            targets.append('tiffcp')
        if 'tiff_read_rgba_fuzzer' in os.listdir(FUZZER_DIR):
            targets.append('tiff_read_rgba_fuzzer')
    return targets

    
def hash(targets):
    hashes = {}
    for target in targets:
        hashes[target] = get_output(['sha256sum', target], cwd=FUZZER_DIR).split()[0]
    return hashes

    
def compare_hashes(new_hashes, old_hashes):
    equal = 0
    for target in new_hashes:
        if target in old_hashes:
            if new_hashes[target] == old_hashes[target]:
                equal += 1
    return equal

    
def checkout_parent(targets = []):
    global COMMIT, COMMITS
    if TARGET == 'sqlite3':
        run_cmd(['rm', '-rf', 'sqlite.tar.gz', 'repo'], cwd=PREFIX)
        if COMMIT == '':
            COMMIT = COMMITS[1]
        else: 
            COMMIT = COMMITS[COMMITS.index(COMMIT) + 1]
        run_cmd_error_msg(['curl', f'https://www.sqlite.org/src/tarball/{COMMIT}/SQLite-{COMMIT}.tar.gz', '-o', 'sqlite.tar.gz'], "Could not curl parent commit!", cwd=PREFIX)
        run_cmd(['mkdir', '-p', 'repo'], cwd=PREFIX)
        run_cmd_error_msg(['tar', '-C', 'repo', '--strip-components=1', '-xzf', 'sqlite.tar.gz'], "Could not curl parent commit!", cwd=PREFIX)
    else:
        if TARGET not in ['poppler', 'lua']:
            run_cmd_error_msg(['make', 'clean'], "Could not make clean!", cwd=PREFIX)
        run_cmd_error_msg(['git', '-C', PREFIX, 'checkout', 'HEAD^1'], "Could not checkout parent commit!")
    for target in targets:
        run_cmd(['rm', target], cwd=FUZZER_DIR)


def get_commit_hash():
    if TARGET == 'sqlite3':
        return COMMIT
    return get_output(['git', '-C', PREFIX, 'log', '-1', '--format="%H"'])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <library>')
        sys.exit()
    if sys.argv[1] not in ['php', 'openssl', 'sqlite3', 'poppler', 'lua', 'libxml2', 'libsndfile', 'libpng', 'libtiff']:
        print('<library> has to be one of [php, openssl, sqlite3, poppler, lua, libxml2, libsndfile, libpng, libtiff]')
        sys.exit()

    TARGET = sys.argv[1]
    PREFIX = f'/home/ubuntu/targsel/{TARGET}'
    if TARGET == 'php':
        FUZZER_DIR = f'{PREFIX}/sapi/fuzzer/'
    if TARGET == 'openssl':
        FUZZER_DIR = f'{PREFIX}/fuzz/'
    if TARGET == 'sqlite3':
        FUZZER_DIR = f'{PREFIX}/repo/'
        COMMIT = ''
        get_sqlite3_commits()
        checkout_parent()
    if TARGET == 'poppler':
        FUZZER_DIR = PREFIX
        PREFIX = f'{PREFIX}/{TARGET}'
    if TARGET == 'libsndfile':
        FUZZER_DIR = f'{PREFIX}/ossfuzz/'
    if TARGET in ['lua', 'libxml2', 'libpng', 'libtiff']:
        FUZZER_DIR = PREFIX

    iteration = 0
    equal_hashes = 0
    total_hashes = 0
    percentage = 0.0
    fuzz_targets = []
    hashes = {}

    try:
        while True:
            fuzz_targets = compile_targets()
            for target in fuzz_targets:
                if target not in hashes:
                    hashes[target] = ''
            new_hashes = hash(fuzz_targets)
            equal_hashes += compare_hashes(new_hashes, hashes)
            if iteration != 0:
                total_hashes += len(fuzz_targets)
            if total_hashes != 0:
                percentage = equal_hashes / total_hashes * 100
            commit = get_commit_hash()
            print(f'iteration={iteration} \t commit={commit} \t equal={equal_hashes} \t total={total_hashes} \t percentage={percentage}')
            checkout_parent(fuzz_targets)
            hashes = new_hashes
            iteration += 1
    except KeyboardInterrupt:
        print(f'\nINFO: Program was interrupted by the user.')
