import torch
from transformers import Trainer, AutoTokenizer, DataCollatorWithPadding, TrainingArguments
from datasets import load_from_disk

from custom_model import SantaCoderClassification

from focalloss import *

selected_return_types = ['None', 'number', 'boolean', 'string', 'object', 'collection']
device = torch.device("cuda:0")

class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        # forward pass
        old_loss, logits = model(**inputs)
        
        # compute custom loss
        class_weights = torch.tensor([1/(56753/191712), 1/(10646/191712), 1/(13755/191712), 1/(14766/191712), 1/(90419/191712), 1/(5363/191712)])
        class_weights = class_weights.to(device)
        
        loss_fct = FocalLoss(gamma=2, alpha=class_weights)

        loss = loss_fct(logits.view(-1, 6), labels.view(-1)) # 6 = num of labels
        return (loss, logits) if return_outputs else loss

dataset = load_from_disk("methods_with_returntypes.hf")

tokenizer = AutoTokenizer.from_pretrained("bigcode/santacoder", trust_remote_code=True)

def preprocess_function(examples):
    return tokenizer(examples['text'], truncation=True)

tokenized_dataset = dataset.map(preprocess_function, batched=True)
tokenizer.pad_token = tokenizer.eos_token

for e in [1, 3, 5, 10]:

    model = SantaCoderClassification()
    model.to(device)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)


    num_epochs = e

    training_args = TrainingArguments(
        output_dir=f"model/santacoder-returntype-{num_epochs}",
        learning_rate=2e-5,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=32,
        num_train_epochs=num_epochs,
        weight_decay=0.01,
        save_total_limit = 3,
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