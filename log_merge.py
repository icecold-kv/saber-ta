import re
import time
import argparse

from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Tool to merge two log files into one.')

    parser.add_argument(
        'log1',
        metavar='<LOG1>',
        type=str,
        help='path to first log file',
    )

    parser.add_argument(
        'log2',
        metavar='<LOG2>',
        type=str,
        help='path to second log file',
    )

    parser.add_argument(
        '-o', '--output',
        metavar='<MERGED LOG>',
        type=str,
        default='merged.jsonl',
        help='path to output log file',
    )

    return parser.parse_args()


def _timestamp(line: str) -> str:
    timestamp = re.search(r'"(\d{4}-.+?)"', line).group(1)
    # lesser hours doesn't have leading zeros, so we are adding them
    timestamp = re.sub(r' (\d):', r' 0\g<1>:', timestamp)
    return timestamp


def _merge_logs(log1: Path, log2: Path, output: Path) -> None:
    print(f"merging {log1.name} and {log2.name} to {output.name}...")

    with log1.open('r', encoding='utf-8') as in1, \
            log2.open('r', encoding='utf-8') as in2, \
            output.open('w', encoding='utf-8') as out:
        one, other = in1.readline(), in2.readline()
        while one and other:
            if _timestamp(one) <= _timestamp(other):
                out.write(one)
                one = in1.readline()
            else:
                out.write(other)
                other = in2.readline()
        while one:
            out.write(one)
            one = in1.readline()
        while other:
            out.write(other)
            other = in2.readline()


def main() -> None:
    args = _parse_args()

    t0 = time.time()
    log1 = Path(args.log1)
    log2 = Path(args.log2)
    out = Path(args.output)
    _merge_logs(log1, log2, out)
    print(f"finished in {time.time() - t0:0f} sec")


if __name__ == '__main__':
    main()
