import * as vscode from 'vscode';
//import * as fetch from 'node-fetch';
const fetch = require('node-fetch');

function selectionText(editor: vscode.TextEditor, selection: vscode.Selection) {
    return editor.document.getText(selection);
}

function confirm(message: string, options: string[]) {
    return new Promise((resolve, reject) => {
        return vscode.window.showInformationMessage(message, ...options).then(resolve);
    });
}

async function pred(data: any) {
	const response = await fetch(
		"https://api-inference.huggingface.co/models/UDE-SE/BERTForReturnTypeClassification",
		{
			headers: { Authorization: "Bearer XXX_TOKEN_XXX" },
            method: "POST",
			body: JSON.stringify(data),
		}
	);
	const result = await response.json();
	return result;
}

export let predDisposable = vscode.commands.registerCommand('returntypes-predictor.predict', async function () {    
    let editor = vscode.window.activeTextEditor;
    if (!editor) {
        return ''; // No open text editor
    }

    let selection = editor.selection;
    
    // get the selected method name
    let methodName = selectionText(editor, selection);
    if (methodName == '') return;

    // predict
    let p = await pred({"inputs": methodName}).then((response: [[{ score: number; label: string; }]]) => {
        console.log(JSON.stringify(response));
        //vscode.window.showInformationMessage('Predict: ' + JSON.stringify(response));
        return response
    });

    // Error while model is not available {"error":"Model .../ReturnTypes-Predictor is currently loading","estimated_time":20}
    if (JSON.stringify(p).includes("is currently loading")) {
        vscode.window.showErrorMessage("The model is currently loading, please try again!")
        return;
    }

    if (JSON.stringify(p).includes("error")) {
        vscode.window.showErrorMessage("The model is currently not available: "+JSON.stringify(p))
        return;
    }

    //convert labels to ['None', 'number', 'boolean', 'object', 'string', 'collection']
    var scores: number[] = [];
    var labels: string[] = [];

    p[0].forEach((elem: { score: number; label: string; }) => {
        scores.push(elem.score);
        switch (elem.label) {
            case "LABEL_0":
                labels.push("Object")
                break;
            case "LABEL_1":
                labels.push("void")
                break;
            case "LABEL_2":
                labels.push("int/float/double/Integer/Byte")
                break;
            case "LABEL_3":
                labels.push("boolean")
                break;
            case "LABEL_4":
                labels.push("String")
                break;
            case "LABEL_5":
                labels.push("Object[]")
                break;
            default:
                break;
        }
    });

    let index_of_max = scores.indexOf(Math.max(...scores));
    let prediction = labels[index_of_max]
    let pred_score = Math.round(scores[index_of_max] * 100)

    //insert prediction into code
    confirm("Shall the following predicted return type '"+prediction+"' ("+pred_score+" %) be inserted?", ["yes", "no"])
        .then((option) => {
            switch(option) {
                case "yes":
                    //vscode.window.showInformationMessage('YES: ' + methodName);

                    editor?.insertSnippet(new vscode.SnippetString(prediction+" "), selection.start)

                    break;
                case "no":
                    //vscode.window.showInformationMessage('NO: ' + methodName);
                    break;
            }
        })

});

export let analyzeDisposable = vscode.commands.registerCommand('returntypes-predictor.analyze', async function () {
    vscode.window.showInformationMessage('Analysing...');
    
    const methodRegex = /(?:public|private|protected)?\s+(?:static\s+)?(\w+(?:<\w+>)?)\s+(\w+)\s*\([^\)]*\)\s*(?:throws\s+\w+(?:\s*,\s*\w+)*)?\s*\{/g;
    const methodInfos: { name: string, returnType: string, returnTypeGroup: string}[] = [];
    
    let match: RegExpExecArray | null;

    let editor = vscode.window.activeTextEditor;
    if (!editor) {
        return ''; // No open text editor
    }

    let text = editor.document.getText();

    while ((match = methodRegex.exec(text)) !== null) {
        let returnType = match[1];
        let returnTypeGroup: string;

        switch (returnType.toLowerCase()) {
            case 'void':
            case 'none':
                returnTypeGroup = 'None';
                break;
            case 'int':
            case 'float':
            case 'long':
            case 'double':
            case 'integer':
            case 'byte':
                returnTypeGroup = 'number';
                break;
            case 'boolean':
                returnTypeGroup = 'boolean';
                break;
            case 'string':
            case 'char':
                returnTypeGroup = 'string';
                break;
            case 'collection':
            case 'array':
            case 'list':
            case 'arraylist':
            case 'set':
                returnTypeGroup = 'collection';
                break;
            default:
                returnTypeGroup = 'object';

        }

        methodInfos.push({ name: match[2], returnType: returnType, returnTypeGroup: returnTypeGroup});
    }

    var analyze_score = 0;

    for (const methodinfo of methodInfos) {
        let given_return_type_group = methodinfo['returnTypeGroup'];
        let method_name = methodinfo['name'];

        // predict
        let p = await pred({"inputs": method_name}).then((response: [[{ score: number; label: string; }]]) => {
            //console.log(JSON.stringify(response));
            //vscode.window.showInformationMessage('Predict: ' + JSON.stringify(response));
            return response
        });

        // Error while model is not available {"error":"Model .../ReturnTypes-Predictor is currently loading","estimated_time":20}
        if (JSON.stringify(p).includes("is currently loading")) {
            vscode.window.showErrorMessage("The model is currently loading, please try again!\n ErrorMessage: "+JSON.stringify(p))
            break;
        }
        else if (JSON.stringify(p).includes("error")) {
                vscode.window.showErrorMessage("The model is currently not available: "+JSON.stringify(p))
                return;
            }
            else {

                var scores: number[] = [];
                var labels: string[] = [];

                p[0].forEach((elem: { score: number; label: string; }) => {
                    scores.push(elem.score);
                    switch (elem.label) {
                        case "LABEL_0":
                            labels.push("object")
                            break;
                        case "LABEL_1":
                            labels.push("None")
                            break;
                        case "LABEL_2":
                            labels.push("number")
                            break;
                        case "LABEL_3":
                            labels.push("boolean")
                            break;
                        case "LABEL_4":
                            labels.push("string")
                            break;
                        case "LABEL_5":
                            labels.push("collection")
                            break;
                        default:
                            break;
                    }
            });

            let index_of_max = scores.indexOf(Math.max(...scores));
            let prediction = labels[index_of_max];
            let pred_score = Math.round(scores[index_of_max] * 100);

            console.log('method name', method_name);
            console.log('prediction', prediction, pred_score);
            console.log('given', given_return_type_group);

            if (prediction == given_return_type_group) {
                analyze_score += 1;
            }

        }


    };

    console.log('analyze score', analyze_score);
    console.log('total ammount', methodInfos.length)

    vscode.window.showInformationMessage(analyze_score+' out of '+methodInfos.length+' return types are classfied correct.');

});

module.exports = {
    predDisposable,
    analyzeDisposable
}
