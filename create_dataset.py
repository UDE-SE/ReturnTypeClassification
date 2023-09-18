from datasets import Dataset
import json
import json
import glob

selected_return_types = ['None', 'number', 'boolean', 'string', 'object', 'collection']

def get_selected_return_type(s: str):
    s = s.lower()
    if s == 'void' or s == 'none':
        return 'None'
    if s == 'int' or s == 'float' or s == 'long' or s == 'double' or s == 'integer' or s == 'byte':
        return 'number'
    if s == 'boolean':
        return 'boolean'
    if s == 'string' or s == 'char':
        return 'string'
    if s == 'collection' or s == 'array' or s == 'list' or s == 'arraylist' or s == 'set' or s.endswith('[]'):
        return 'collection'
    return 'object'

def extract_return_type(code, method_name):
    # NOTE: this breaks some special return types which contain spaces which are not coverred here
    # example which will not work: Map<String, String>
    code = code.replace('\t', ' ')
    parts = code.split(' '+method_name+'(')[0].split(' ')
    return parts[-1]

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