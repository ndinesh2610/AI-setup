import argparse
import re
from collections import Counter
from pathlib import Path


def get_word_counts(text):
    words = re.findall(r"\b[\w']+\b", text.lower())
    return Counter(words)


def main():
    parser = argparse.ArgumentParser(
        description="Find the top N most frequent words in a text file"
    )

    parser.add_argument("file", help="Input text file")
    parser.add_argument(
        "-n", "--top", type=int, default=10, help="Number of top words to display"
    )

    args = parser.parse_args()

    if args.top <= 0:
        parser.error("N must be greater than zero")

    try:
        text = Path(args.file).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}")
        return 1

    word_counts = get_word_counts(text)

    for word, count in word_counts.most_common(args.top):
        print(f"{word}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
