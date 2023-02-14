import re
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dry", action="store_true")
# parser.add_argument("--ref", required=True)
parser.add_argument("files", nargs="+")

def colourize(text, colour_code="154"):
    return f"\033[38;5;{colour_code}m{text}\033[0m"

def parse_reference_labels(ref_file):
    parsed_labels = []
    label_pattern = re.compile(r"^@\w+{(.+),$")

    with open(ref_file) as f:
        for line in f:
            label_match = label_pattern.match(line)
            if label_match:
                parsed_labels.append(label_match.group(1))
    
    return parsed_labels

if __name__ == "__main__":
    args = parser.parse_args()
    cite_pattern = re.compile(r"\[(\d+)]")

    ignored_patterns = [
        # command argument specifier
        re.compile(r"newcommand\*?\{.+}\[(\d+)]")
    ]
    
    # reference_labels = parse_reference_labels(args.ref)
    reference_labels = parse_reference_labels("references.bib")
    
    cite_sub = lambda m: f"\\cite{{{reference_labels[int(m.group(1))-1]}}}"
    cite_sub_dry = lambda m: colourize(cite_sub(m), 154)
    
    for file in args.files:
        made_changes = False
        new_lines = []
        
        if not args.dry:
            shutil.copy(file, file + ".bak")
    
        with open(file) as f:
            for line in f:
                cite_match = cite_pattern.search(line)
                any_ignored = any(map(lambda p: p.search(line), ignored_patterns))

                if not any_ignored and cite_match:
                    made_changes = True
                
                    if args.dry:
                        line = cite_pattern.sub(cite_sub_dry, line)
                    else:
                        line = cite_pattern.sub(cite_sub, line)
                        
                elif args.dry and any_ignored:
                    line = colourize(line, 196)

                new_lines.append(line)
            
        if made_changes:
            if args.dry:
                for current_line in new_lines:
                    print(current_line.strip())
                    
            else:
                with open(file, "w") as f:
                    f.writelines(new_lines)
        else:
            print(colourize(f">> NO CHANGES MADE in `{file}` >>", 214))