# ReturnTypeClassification

## Create Data Set and Training
1. Download source files from [CodeSearchNet Challenge](https://github.com/github/CodeSearchNet)
2. Create HuggingFace Dataset [create_dataset.py](create_dataset.py)
3. Train models [BERTForReturnTypeClassification](train_BERTForReturnTypeClassification.py) and [SantaCoderForReturnTypeClassification](train_SantaCoderForReturnTypeClassification.py)
    
## Existing Models   
1. Use trained models from HuggingFace [BERTForReturnTypeClassification](https://huggingface.co/UDE-SE/BERTForReturnTypeClassification) and [SantaCoderForReturnTypeClassification](https://huggingface.co/UDE-SE/SantaCoderForReturnTypeClassification)

## Inference / Analysis
1. Analyse single method names or existing repositories ([example how to use both models](https://huggingface.co/spaces/UDE-SE/ReturnTypePredictor/blob/main/app.py))
2. Check out our [HuggingFace Space](https://huggingface.co/spaces/UDE-SE/ReturnTypePredictor) to see the models running

## License
This repository is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike (CC BY-NC-SA) 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
