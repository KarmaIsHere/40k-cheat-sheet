import json, argparse, sys, pathlib

#!/usr/bin/env python3

def main():
    p = argparse.ArgumentParser(description="Read JSON file and print to stdout")
    p.add_argument("file", nargs="?", default="-", help="Path to JSON file or - for stdin")
    p.add_argument("-k", "--key", help="Top-level key to print (dot-separated for nested)")
    p.add_argument("-i", "--indent", type=int, default=2, help="Pretty-print indent (0 for compact)")
    args = p.parse_args()

    try:
        text = sys.stdin.read() if args.file == "-" else pathlib.Path(args.file).read_text(encoding="utf-8")
        data = json.loads(text)
        if args.key:
            for part in args.key.split("."):
                data = data[part]
        if args.indent:
            if args.file == "-":
                print(json.dumps(data, ensure_ascii=False, indent=args.indent))
            else:
                pathlib.Path(args.file).write_text(
                    json.dumps(data, ensure_ascii=False, indent=args.indent),
                    encoding="utf-8",
                )
        else:
            print(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    except FileNotFoundError:
        sys.exit(f"File not found: {args.file}")
    except json.JSONDecodeError as e:
        sys.exit(f"Invalid JSON: {e}")
    except Exception as e:
        sys.exit(str(e))

if __name__ == "__main__":
    main()