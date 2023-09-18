from transformers import BertForSequenceClassification, BertTokenizerFast, DataCollatorWithPadding, Trainer, TrainingArguments
import torch
from datasets import load_from_disk
import re

import sys
import os

sys.path.append(os.path.abspath('..'))
from focalloss import *

selected_return_types = ['None', 'number', 'boolean', 'string', 'object', 'collection']
device = torch.device("cuda:0")

def split_name_to_sentence(example):
    name = example['text']
    sentence = []
    words = re.findall('((^|[^a-zA-Z])([A-Z]+|[a-z])[a-z]*|[A-Z]+[a-z]*|\d+)', name)
    for w in words:
        word = w[0] if w[0].isalpha() else w[0][1:]
        
        chars = list(word)
        for i, char in enumerate(chars):
            if char.islower():
                if i > 1:
                    sentence.append("".join(chars[0:(i-1)]))
                    sentence.append("".join(chars[(i-1):]))
                    break
                sentence.append(word)
                break
        else:
            sentence.append(word)
    example['text'] = (" ".join(sentence)).lower()
    return example

class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        # forward pass
        outputs = model(**inputs)
        logits = outputs.get('logits')
        # compute custom loss
        class_weights = torch.tensor([1/(56753/191712), 1/(10646/191712), 1/(13755/191712), 1/(14766/191712), 1/(90419/191712), 1/(5363/191712)])
        class_weights = class_weights.to(device)
        
        loss_fct = FocalLoss(gamma=2, alpha=class_weights)

        loss = loss_fct(logits.view(-1, 6), labels.view(-1)) # 6 = num of labels
        return (loss, logits) if return_outputs else loss

dataset = load_from_disk("methods_with_returntypes.hf")

for e in [1, 3, 5, 10]:

    model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=len(selected_return_types))
    model.to(device)

    tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")

    dataset = dataset.map(split_name_to_sentence)

    def preprocess_function(examples):
        return tokenizer(examples['text'], truncation=True)

    tokenized_dataset = dataset.map(preprocess_function, batched=True)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    num_epochs = e

    training_args = TrainingArguments(
        output_dir=f"model/BERT-returntype-{num_epochs}",
        learning_rate=2e-5,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=32,
        num_train_epochs=num_epochs,
        weight_decay=0.01,
        save_total_limit = 3,
        use_mps_device=True,
    )

    trainer = CustomTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["test"],
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()
    print("Training done")

    trainer.evaluate()
    print("Eval done")

    trainer.save_model()
    print("Save done")