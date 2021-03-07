#!/usr/bin/env python3

import sys

from multiprocessing import Process, Queue
from pathlib import Path
from zipfile import ZipFile


def test_proc(dir_path, queue):
    while True:
        zip_path = queue.get()
        if zip_path is None:
            queue.put(None)
            break

        rel_path = zip_path.relative_to(dir_path)
        zip_file = ZipFile(zip_path, 'r', allowZip64=True)

        result = zip_file.testzip()
        if result is None:
            print(f'[+] {rel_path}')
        else:
            print(f'[-] {rel_path}, {result}')


def main():
    if len(sys.argv) < 2:
        print('usage: test-zip.py [path to directory] [proc count]')
        return

    dir_path = Path(sys.argv[1]).absolute()
    if not dir_path.exists():
        print('[-] directory does not exist')
        return

    proc_count = 1  # optimized for hdd
    if len(sys.argv) >= 3:
        proc_count = int(sys.argv[2])

    procs = []
    queue = Queue()
    for _ in range(proc_count):
        proc = Process(target=test_proc, args=(dir_path, queue,))
        proc.start()
        procs.append(proc)

    for zip_path in dir_path.glob('**/*.zip'):
        queue.put(zip_path)
    queue.put(None)

    for proc in procs:
        proc.join()


if __name__ == '__main__':
    main()
