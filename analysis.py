import csv
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, BertForSequenceClassification, RobertaTokenizer, RobertaForSequenceClassification

selected_return_types = ['None', 'Number', 'Boolean', 'String', 'Object', 'Collection']

device = torch.device("cuda:0")

epochs = 1 # or 3,5,10

# CodeBERTForReturnTypeClassification
codebert_tokenizer = RobertaTokenizer.from_pretrained(f"../CodeBERTFineTuning/model/CodeBERT-returntype-{e}", trust_remote_code=True)
codebert_model = RobertaForSequenceClassification.from_pretrained(f"../CodeBERTFineTuning/model/CodeBERT-returntype-{e}", num_labels=len(selected_return_types))

codebert_model.to(device)
codebert_model.eval()

# BERTForReturnTypeClassification
bert_tokenizer = AutoTokenizer.from_pretrained(f"../BERTFineTuning/model/BERT-returntype-{epochs}", trust_remote_code=True)
bert_model = BertForSequenceClassification.from_pretrained(f"../BERTFineTuning/model/BERT-returntype-{epochs}", num_labels=len(selected_return_types))

bert_model.to(device)
bert_model.eval()

def generate_return_type_withCodeBERT(method_name):

    inputs = codebert_tokenizer(method_name, return_tensors="pt", padding=True, return_token_type_ids=False).to(device)

    with torch.no_grad():
        outputs = codebert_model(**inputs)

    probs = outputs[0].softmax(1)
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

                    codebert_gen_return_type, codebert_probs = generate_return_type_withCodeBERT(method_name)
                    bert_gen_return_type, bert_probs = generate_return_type_withBERT(method_name)

                    writer.writerow([class_name,method_name,method_return_type,method_return_class,repr(bert_gen_return_type)]+bert_probs+[repr(codebert_gen_return_type)]+codebert_probs)

print(f"number of methods: {counter}")