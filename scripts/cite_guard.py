import re
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dry", action="store_true")
parser.add_argument("files", nargs="+")

args = parser.parse_args()

eol_cite_pattern = re.compile(r"(?<!\()(\\cite\{[^}]+?})(?!\))(\.|$)")
caption_pattern = re.compile(r"(?P<pre>.+\\caption\{)(?P<body>.+)(?P<post>})")

def colourize(text, colour_code="154"):
    return f"\033[38;5;{colour_code}m{text}\033[0m"

for file in args.files:
    new_lines = []
    made_changes = False
    
    if not args.dry:
        shutil.copy(file, file + ".bak")
    
    with open(file) as f:
        for line in f:
            caption_match = caption_pattern.search(line)
            eol_cite_sub = r"(\1)\2"

            if args.dry:
                eol_cite_sub = colourize(eol_cite_sub)
            
            eol_cite_matched = eol_cite_pattern.search(line)
            caption_eol_cite_matched = caption_match and eol_cite_pattern.match(caption_match["body"])

            if not made_changes:
                made_changes = eol_cite_matched or caption_eol_cite_matched
            
            if eol_cite_matched:
                line = eol_cite_pattern.sub(eol_cite_sub, line)

            if caption_eol_cite_matched:
                new_caption_body = eol_cite_pattern.sub(eol_cite_sub, caption_match["body"])
                line = caption_match["pre"] + new_caption_body + caption_match["post"]                
            
            new_lines.append(line)
    
    if made_changes:
        if args.dry:
            for line in new_lines:
                print(line.rstrip())
        else:
            with open(file, "w") as f:
                f.writelines(new_lines)
    
    else:
        print(colourize(f">> NO CHANGES MADE in `{file}` >>", 214))