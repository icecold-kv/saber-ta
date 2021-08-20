import json
import time
import argparse

from datetime import datetime
from pathlib import Path

_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Tool to verify order of messages in a log file.')

    parser.add_argument(
        'log_file',
        metavar='<LOG FILE>',
        type=str,
        default='merged.jsonl',
        help='path to log file',
    )

    return parser.parse_args()


def _timestamp(line):
    timestamp = json.loads(line)['timestamp']
    return datetime.strptime(timestamp, _TIMESTAMP_FORMAT)


def _check_order(file: Path) -> bool:
    print(f"checking order in {file.name}...")
    with file.open('r', encoding='utf-8') as fh:
        first = fh.readline()
        for second in fh:
            if _timestamp(second) < _timestamp(first):
                print('Wrong order detected:\n', first, second)
                return False
            first = second
    print(f"{file.name} is sorted by ascending timestamps")
    return True


def main() -> None:
    args = _parse_args()

    t0 = time.time()
    log_file = Path(args.log_file)
    _check_order(log_file)
    print(f"finished in {time.time() - t0:0f} sec")


if __name__ == '__main__':
    main()
