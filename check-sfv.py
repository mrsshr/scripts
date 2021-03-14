#!/usr/bin/env python3

import sys
from binascii import crc32
from pathlib import Path

def main(args):
    top_dir_path = Path(args[1])
    if not top_dir_path.is_dir():
        raise NotADirectoryError(top_dir_path)

    for sfv_path in top_dir_path.rglob('*.sfv'):
        dir_path = sfv_path.parent

        sfv_content = sfv_path.read_text('utf-8')

        total = 0
        ok = 0
        fail = 0

        for line in sfv_content.splitlines():
            line = line.strip()
            if len(line) == 0:
                continue
            if line.startswith(';'):
                continue

            try:
                total += 1

                checksum_index = line.rfind(' ')
                if checksum_index < 0:
                    raise ValueError(line)

                file_path = dir_path / line[:checksum_index].strip().replace('\\', '/')
                checksum_expected = int(line[checksum_index+1:], 16)

                checksum = 0
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(64 * 1024), b''):
                        checksum = crc32(chunk, checksum)

                if checksum != checksum_expected:
                    raise ValueError(f'{file_path}: checksum mismatch ({checksum:08x} != {checksum_expected:08x})')

                ok += 1
            except (ValueError, FileNotFoundError) as e:
                print(f'{e}')

                fail += 1

        print(f'{sfv_path}: total {total} ok {ok} fail {fail}')


if __name__ == '__main__':
    main(sys.argv)
