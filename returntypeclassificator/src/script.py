import subprocess
import sys
import pathlib
import json

subprocess.check_call([sys.executable, "-m", "pip", "install", "javalang"])

import javalang

def getMethods(types_list):
    results = []
    
    for t in types_list:
        if type(t) == javalang.tree.MethodDeclaration:
            if type(t.return_type) == type(None):
                results.append(t.name+"; "+str(t.return_type))
            else:
                results.append(t.name+"; "+str(t.return_type.name))
        if type(t) == javalang.tree.ClassDeclaration:
            results += getMethods(t.body)
    
    return results


path = pathlib.Path(__file__).parent.resolve()

with open(str(path)+'/currentFile.java', 'r') as file:
    lines = file.read()

    tree = javalang.parse.parse(lines)
    methods_list = getMethods(tree.types)

    output_dict = {key.strip(): value.strip() for pair in methods_list for key, value in [pair.split(';')]}

    json_output = json.dumps(output_dict, separators=(',', ':'))

    print(json_output)