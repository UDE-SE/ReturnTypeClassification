from datasets import Dataset
import json
import json
import glob
import javalang
from javalang.parser import JavaSyntaxError

selected_return_types = ['None', 'Number', 'Boolean', 'String', 'Object', 'Collection'] # increasing complexity https://docs.oracle.com/javase/tutorial/java/nutsandbolts/datatypes.html

def get_selected_return_type(s: str):
    if s == None:
        return 'None'
    s = s.lower()
    if s == 'void' or s == 'none':
        return 'None'
    if s == 'int' or s == 'float' or s == 'long' or s == 'double' or s == 'integer' or s == 'byte':
        return 'Number'
    if s == 'boolean':
        return 'Boolean'
    if s == 'string' or s == 'char':
        return 'String'
    if s == 'collection' or s == 'array' or s == 'list' or s == 'arraylist' or s == 'set' or s.endswith('[]') \
        or s.startswith('collection<') or s.startswith('array<') or s.startswith('list<') or s.startswith('arraylist<') or s.startswith('set<'):
        return 'Collection'
    return 'Object'

def getMethods(types_list):
    results = []
    
    for t in types_list:
        if type(t) == javalang.tree.MethodDeclaration:
            if type(t.return_type) == type(None):
                results.append((t.name, str(t.return_type)))
            else:
                results.append((t.name, str(t.return_type.name)))
        if type(t) == javalang.tree.ClassDeclaration:
            results += getMethods(t.body)
    
    return results

def extract_return_type(code, method_name):
    methods = []

    code = code.replace('@Nullable ', '')
    code = code.replace('@NonNull ', '')

    try:

        index_with_space = code.find(method_name+' (')
        if index_with_space == -1:
            index_with_space = math.inf
        index_without_space = code.find(method_name+'(')
        if index_without_space == -1:
            index_without_space = math.inf
        split_index = min(index_with_space, index_without_space)
        if split_index == math.inf:
            split_index = code.find(method_name)
        previous_part = code[:split_index]
        wrapped_code = "class Class {\n" + previous_part + " " + method_name + "(){};}"
        tree = javalang.parse.parse(wrapped_code)
        methods = getMethods(tree.types) # methods := [(method_name, returntype)]
    except JavaSyntaxError as pe:
        print(f"ParsingError in: {method_name} - {pe.description} - {pe.at}")
        return None
    except Exception as e:
        print(f"ParsingError in: {method_name}, {e}")
        return None
    
    if len(methods) == 0:
        print(f"FOUND NO METHOD: {methods}")
        return None

    if len(methods) > 1:
        for method in methods:
            if method[0] == method_name:
                return method[1]
    return methods[0][1]


def parse_files_into_dict(given_file_list):
    for file in given_file_list:
        with open(file) as json_file:
            lines = json_file.readlines()
            for i, line in enumerate(lines):
                method_json = json.loads(line)
                original_string = method_json['original_string']
                method_name = method_json['func_name'].split('.')[-1]
                return_type = None
                try:
                    return_type = extract_return_type(original_string, method_name)
                except:
                    print(file, i, method_name)
                    print(original_string.split(' '+method_name+'(')[0].split(' '))
                method_return_type = get_selected_return_type(return_type)
                if method_return_type not in return_types:
                    return_types.append(method_return_type)
                if method_name not in method_dict.keys():
                    method_dict[method_name]=[method_return_type]
                else:
                    tmp_list = method_dict[method_name]
                    tmp_list.append(method_return_type)
                    method_dict[method_name] = tmp_list

def most_frequent(List):
    count_dict = {}

    for value in List:
        if value in count_dict:
            count_dict[value] += 1
        else:
            count_dict[value] = 1

    max_count = max(count_dict.values())
    mode_value = None

    for key, value in count_dict.items():
        if value == max_count:
            if mode_value is None or selected_return_types.index(key) > selected_return_types.index(mode_value):
                mode_value = key
    return mode_value

################################################################################

method_dict = {}
return_types = []

train_files_list = glob.glob('CodeSearchNet/java/final/jsonl/train/*.jsonl', recursive=True)
test_files_list = glob.glob('CodeSearchNet/java/final/jsonl/test/*.jsonl', recursive=True)
valid_files_list = glob.glob('CodeSearchNet/java/final/jsonl/valid/*.jsonl', recursive=True)
files_list = train_files_list + test_files_list + valid_files_list

parse_files_into_dict(files_list)

method_dict_most_rt = {}
for key in method_dict.keys():
    l = method_dict[key]
    l.sort()
    method_dict_most_rt[key] = most_frequent(l)

for rt in return_types:
    counter = 0
    for key in method_dict_most_rt.keys():
        if rt == method_dict_most_rt[key]:
            counter += 1
    print(rt, counter)

method_names = method_dict_most_rt.keys()
return_type_classes = [selected_return_types.index(x) for x in list(method_dict_most_rt.values())]

ds = Dataset.from_dict({"text": method_names, "label": return_type_classes})

ds = ds.train_test_split(test_size=0.2, shuffle=True)

ds.save_to_disk("methods_with_returntypes.hf")