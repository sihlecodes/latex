import re
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dry", action="store_true")
parser.add_argument("files", nargs="+")

args = parser.parse_args()

paragraph = re.compile(r"[A-Z].+$")
# paragraph = re.compile(r"^$")

for file in args.files:
    new_lines = []
    
    if not args.dry:
        shutil.copy(file, file + ".bak")
    
    with open(file) as f:
        lines = f.readlines()
        total_lines = len(lines) - 1
        lnum = 0
        open_environments = 0
        made_changes = False
        
        for lnum in range(total_lines):
            current_line = lines[lnum]
            next_line = lines[lnum + 1]
            
            if current_line.startswith("\\begin"):
                open_environments += 1
                
            elif current_line.startswith("\\end"):
                open_environments -= 1
                
            if open_environments == 0 and paragraph.match(current_line) and next_line.strip():
                current_line += "\033[38;5;154m>> NEWLINE HERE >>\033[0m" if args.dry else "\n"
                made_changes = True

            new_lines.append(current_line)
        
        # add the final line of the file
        new_lines.append(lines[lnum+1])
    
    if made_changes:
        if args.dry:
            for current_line in new_lines:
                print(current_line.strip())
        else:
            with open(file, "w") as f:
                f.writelines(new_lines)
    else:
        print("\033[38;5;214m>> NO CHANGES MADE >>\033[0m")