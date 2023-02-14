import re
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dry", action="store_true")
parser.add_argument("files", nargs="+")

args = parser.parse_args()

def colourize(text, colour_code="154"):
    return f"\033[38;5;{colour_code}m{text}\033[0m"

def load_acronyms(file):
    acronym_pattern = re.compile(r"\\newacronym\{(?P<label>.+)\}\{(?P<acronym>.+)\}\{(?P<description>.+)\}")
    acronyms = {}
    
    with open(file) as f:
        for line in f:
            m = acronym_pattern.match(line)
            if m:
                acronyms[m.group("acronym")] = { "label": m.group("label"), "description": m.group("description") }

    return acronyms

def generate_acrfull_patterns():
    acrfull_patterns = []
    
    for acronym, data in acronyms.items():
        description = data["description"]
        pattern = r"(?P<description>%s)(?P<plural>s?)\s+\((?P<acronym>%s)\2\)" % (description, acronym)
        acrfull_patterns.append(re.compile(pattern, flags=re.IGNORECASE))
    
    return acrfull_patterns

def acrfull_sub(m):
    command = "\\acrfull"

    matched = m.group("description")
    original = acronyms[m.group("acronym")]["description"]
    
    if matched == original.upper():
        command = "\\ACRfull"
    
    elif matched[0] == original[0].upper():
        command = "\\Acrfull"

    if m.group("plural"):
        command += "pl"
    
    label = acronyms[m.group("acronym")]["label"]
    command += f"{{{label}}}"

    if args.dry:
        command = colourize(command, 154)
    return command

def acrshort_sub(m):
    acronym = m.group('acronym')
    
    if acronym not in acronyms:
        if args.dry:
            acronym = colourize(acronym, 196)

        return acronym

    command = "\\acrshort{%s}" % acronyms[acronym]["label"]
    
    if args.dry:
        command = colourize(command, 154)

    return command

acronyms = load_acronyms("content/acronyms.tex")
acrfull_patterns = generate_acrfull_patterns()

acrshort_pattern = re.compile(r"\b(?P<acronym>[A-Z][A-Z0-9\-]+)\b")
ignored_patterns = [
    # comments
    re.compile(r"^\s*%"),

    # section commands
    re.compile(r"^\s*\\(sub){0,2}(section|chapter|paragraph)"),
    
    # captions
    re.compile(r"^\s*\\caption"),
]

for file in args.files:
    open_environments = 0
    new_lines = []
    made_changes = False
    
    if not args.dry:
        shutil.copy(file, file + ".bak")
    
    with open(file) as f:
        for line in f:
            if line.startswith("\\begin"):
                open_environments += 1

            elif line.startswith("\\end"):
                open_environments -= 1

            new_line = line
            
            inside_environment = open_environments > 0
            any_ignored = any(map(lambda p: p.search(line), ignored_patterns))
                        
            if not (any_ignored or inside_environment):
                for pat in acrfull_patterns:
                    if pat.search(new_line):
                        new_line = pat.sub(acrfull_sub, new_line)

                new_line = acrshort_pattern.sub(acrshort_sub, new_line)
                
                if not made_changes and line != new_line:
                    made_changes = True
            
            new_lines.append(new_line)
    
    if made_changes:
        if args.dry:
            for current_line in new_lines:
                print(current_line.strip())
        else:
            with open(file, "w") as f:
                f.writelines(new_lines)
    else:
        print(colourize(f">> NO CHANGES MADE in `{file}` >>", 214))