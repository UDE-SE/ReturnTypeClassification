import csv
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, BertForSequenceClassification

from custom_model import SantaCoderClassification

selected_return_types = ['None', 'number', 'boolean', 'string', 'object', 'collection']

device = torch.device("cuda:0")

epochs = 1 # or 3,5,10

# SantaCoderForReturnTypeClassification
santa_tokenizer = AutoTokenizer.from_pretrained(f"model/santacoder-returntype-{epochs}", trust_remote_code=True)

MODEL_PATH = f"santacoder-returntype-{epochs}/pytorch_model.bin"
santa_state_dict = torch.load(MODEL_PATH, map_location=torch.device('cuda:0'))
santa_model = SantaCoderClassification()
santa_model.load_state_dict(state_dict=santa_state_dict)

santa_model.to(device)
santa_model.eval()

# BERTForReturnTypeClassification
bert_tokenizer = AutoTokenizer.from_pretrained(f"../BERTFineTuning/model/BERT-returntype-{epochs}", trust_remote_code=True)
bert_model = BertForSequenceClassification.from_pretrained(f"../BERTFineTuning/model/BERT-returntype-{epochs}", num_labels=len(selected_return_types))

bert_model.to(device)
bert_model.eval()

def generate_return_type_withSanta(method_name):

    inputs = santa_tokenizer(method_name, return_tensors="pt", padding=True, return_token_type_ids=False).to(device)

    with torch.no_grad():
        outputs = santa_model(**inputs)

    probs = outputs.softmax(1)
    pred = selected_return_types[probs.argmax()]
    
    return pred, probs.tolist()

def generate_return_type_withBERT(method_name):

    inputs = bert_tokenizer(method_name, return_tensors="pt", padding=True, return_token_type_ids=False).to(device)

    with torch.no_grad():
        outputs = bert_model(**inputs)

    probs = outputs[0].softmax(1)
    pred = selected_return_types[probs.argmax()]
    
    return pred, probs.tolist()

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
    
FILE_NAME = "XYZ" #TODO add file name here (without '.java')
counter = 0

# make sure that generated $FILE_NAME.txt already exists, otherwise parse Java files first

with open(f'{FILE_NAME}.csv', 'w') as out_file:
    writer = csv.writer(out_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    with open(f'{FILE_NAME}.txt', 'r') as in_file:
        lines = in_file.readlines()
        for l in tqdm(lines):
            methods = l.split(': ')[1]
            class_name = l.split(': ')[0]
            method_pairs = methods.replace("[", "").replace("]", "").replace("'", "").replace("\n", "").split(",")
            for mp in method_pairs:
                split = mp.split(";")
                if len(split) > 1:
                    method_name = split[0].lstrip()
                    if method_name in ["clone", "equals", "finalize", "getClass", "hashCode", "notify", "notifyAll", "toString", "wait"]:
                        continue # skip all methods inherit from java.lang.Object
                    if len(method_name ) < 3:
                        continue # skip too short names

                    method_return_type = split[1].lstrip()
                    method_return_class = get_selected_return_type(method_return_type)

                    santa_gen_return_type, santa_probs = generate_return_type_withSanta(method_name)
                    bert_gen_return_type, bert_probs = generate_return_type_withBERT(method_name)

                    writer.writerow([class_name,method_name,method_return_type,method_return_class,repr(bert_gen_return_type)]+bert_probs+[repr(santa_gen_return_type)]+santa_probs)

print(f"number of methods: {counter}")