from transformers import AutoModelForCausalLM, PreTrainedModel, AutoConfig
import torch
import torch.nn as nn

class SantaCoderClassification(PreTrainedModel):
    def __init__(self):
        super(SantaCoderClassification, self).__init__(AutoConfig.from_pretrained("bigcode/santacoder", trust_remote_code=True))

        santamodel = AutoModelForCausalLM.from_pretrained("bigcode/santacoder", trust_remote_code=True)
        baseGPT2CustomModel = list(santamodel.children())[0]
        
        self.base = baseGPT2CustomModel
        self.dropout = nn.Dropout(0.5)
        self.linear = nn.Linear(2048, 6) # output features from santacoder is 2048 and 6 is our number of labels
        self.criterion = nn.CrossEntropyLoss()
        
    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.base(input_ids=input_ids, attention_mask=attention_mask)
        outputs = self.dropout(outputs[0])
        outputs = self.linear(outputs)
        outputs = torch.mean(outputs, dim=1)
        if labels is not None:
            loss = self.criterion(outputs, labels)
            return loss, outputs
        return outputs