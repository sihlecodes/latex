from copy import deepcopy
import re
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dry", action="store_true")
parser.add_argument("--ref", required=True)
parser.add_argument("files", nargs="+")

args = parser.parse_args()

class Reference(object):
    def __init__(self, name):
        self.data = []
        self.name = name
    
    def __repr__(self):
        return f"Reference({''.join(self.data)})"

    def append(self, line):
        self.data.append(line)

def parse_references(ref_file):
    parsed_references = {}

    start_pattern = re.compile(r"^@\w+{(.+),$")
    close_pattern = re.compile(r"^\}$") 

    current_reference = None
    
    with open(ref_file) as f:
        for line in f:
            start_pattern_match = start_pattern.match(line)
            close_pattern_match = close_pattern.match(line)
            
            if start_pattern_match:
                if not current_reference:
                    current_reference = Reference(start_pattern_match.group(1))
                else:
                    raise Exception("unclosed reference!")
            
            if current_reference:
                current_reference.append(line.strip() if close_pattern_match else line)
            
            if close_pattern_match:
                parsed_references[current_reference.name] = current_reference
                current_reference = None
    
    return parsed_references

def parse_citations(tex_file):
    ordered_references = []
    citation_pattern = re.compile(r"\\cite\{(.+?)\}")

    with open(tex_file) as f:
        for line in f:
            for cite in citation_pattern.findall(line):
                cite_parts = re.split(r",\s*", cite)
                
                for part in cite_parts:
                    if part not in ordered_references:
                        ordered_references.append(part)

    return ordered_references

if __name__ == "__main__":
    parsed_references = parse_references(args.ref)
    ordered_references = []
    global_citations_order = []

    for file in args.files:
        for cite in parse_citations(file):
            if cite not in global_citations_order:
                global_citations_order.append(cite)

    for cite in global_citations_order:
        ordered_references += parsed_references.pop(cite).data
        ordered_references.append("\n\n")
    
    remaining_references = deepcopy(parsed_references)
    
    for ref in remaining_references:
        ordered_references += parsed_references.pop(ref).data
        ordered_references.append("\n\n")
        
    if not args.dry:
        shutil.copy(args.ref, args.ref + ".bak")

        with open(args.ref, 'w') as f:
            f.writelines(ordered_references)
    else:
        for line in ordered_references:
            print(line.rstrip())