import argparse
import json
import sys

from .core import top_words


def main(argv=None):
    p = argparse.ArgumentParser(prog="wordstat")
    p.add_argument("file")
    p.add_argument("-n", "--top", type=int, default=5)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    with open(args.file, encoding="utf-8") as f:
        result = top_words(f.read(), args.top)
    if args.json:
        print(json.dumps(result))
    else:
        for word, count in result:
            print(f"{word}\t{count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
