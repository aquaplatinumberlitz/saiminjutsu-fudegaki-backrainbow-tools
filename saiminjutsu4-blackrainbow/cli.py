import argparse
import json
from pathlib import Path
from SCE import SCE
from MED import MED

argp = argparse.ArgumentParser()
subp = argp.add_subparsers(help="possible subcommands", dest="cmd")

jsonp = subp.add_parser("json", help="extract strings from a script file to a json file")
jsonp.add_argument("input", help="input script file")
jsonp.add_argument("output", help="output json file")

parsep = subp.add_parser("parse", help="parse a script file from its binary format to a text format")
parsep.add_argument("input", help="input binary script file")
parsep.add_argument("-o", "--output", help="output text file")

compilep = subp.add_parser("compile", help="compile a script file from its text format to a binary format")
compilep.add_argument("input", help="input text script file")
compilep.add_argument("-o", "--output", help="output binary file")
compilep.add_argument("--h2f", default=False, action="store_true", help="convert half-width characters to full-width characters")

for p in [jsonp, parsep, compilep]:
    p.add_argument("-e", "--encoding", default="utf8", help="encoding of the file (default: utf8)")

unpackmedp = subp.add_parser("unpack", help="unpack a MED file")
unpackmedp.add_argument("input", help="input MED file")

packmedp = subp.add_parser("pack", help="pack a MED file")

if __name__ == "__main__":
    args = argp.parse_args()
    match args.cmd:
        case "json":
            with open(args.input, "rb") as f:
                scenario = SCE.read_binary(f)
            with open(args.output, "w", encoding=args.encoding) as f:
                json.dump(scenario.strings, f, ensure_ascii=False, indent=4)

        case "parse":
            if args.output:
                output = args.output
            else:
                output = f"intermediate_file\{Path(args.input).name}.script"
            with open(args.input, "rb") as f:
                scenario = SCE.read_binary(f)
            with open(output, "w", encoding=args.encoding) as f:
                f.write(scenario.to_text())

        case "compile":
            if args.output:
                output = args.output
            else:
                output = Path("output") / f"{Path(args.input).name.rsplit('.', 1)[0]}"
    
            with open(args.input, "r", encoding=args.encoding) as f:
                scenario = SCE.read_text(f, h2f=args.h2f)
            with open(output, "wb") as f:
                f.write(scenario.to_bytes())
        
        case "unpack":
            MED.unpack(args.input, "input")

        case "pack":
            MED.repack()
