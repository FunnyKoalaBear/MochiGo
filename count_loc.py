"""
count_loc.py – Count the number of lines of code committed by a given author.

Usage:
    python count_loc.py [author]

If no author is provided, defaults to "FunnyKoalaBear".

Output example:
    Lines added   : 2345
    Lines deleted : 0
    Net lines     : 2345

Note: Binary files are excluded from the count because git reports '-' instead
of a numeric line count for them. Only text file line changes are tallied.
"""

import subprocess
import sys


def count_lines_of_code(author: str = "FunnyKoalaBear") -> dict:
    """Return a dict with lines added, deleted, and net for the given author.

    Binary file entries (where git outputs '-') are excluded from the count.
    """
    try:
        result = subprocess.run(
            ["git", "log", f"--author={author}", "--all", "--numstat", "--format="],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"Error: git command failed – {exc.stderr.strip() or exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: git executable not found. Make sure git is installed and on PATH.", file=sys.stderr)
        sys.exit(1)

    added = 0
    deleted = 0

    for line in result.stdout.splitlines():
        parts = line.split("\t")
        # git uses '-' for binary files; skip those entries
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            added += int(parts[0])
            deleted += int(parts[1])

    return {"added": added, "deleted": deleted, "net": added - deleted}


def main():
    author = sys.argv[1] if len(sys.argv) > 1 else "FunnyKoalaBear"
    stats = count_lines_of_code(author)
    print(f"Author        : {author}")
    print(f"Lines added   : {stats['added']}")
    print(f"Lines deleted : {stats['deleted']}")
    print(f"Net lines     : {stats['net']}")


if __name__ == "__main__":
    main()
