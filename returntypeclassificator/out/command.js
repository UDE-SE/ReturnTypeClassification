"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.analyzeDisposable = exports.predDisposable = exports.disposable = void 0;
const vscode = require("vscode");
//import * as fetch from 'node-fetch';
const fetch = require('node-fetch');
const child_process_1 = require("child_process");
const fs = require('fs');
function selectionText(editor, selection) {
    return editor.document.getText(selection);
}
function confirm(message, options) {
    return new Promise((resolve, reject) => {
        return vscode.window.showInformationMessage(message, { modal: true }, ...options).then(resolve);
    });
}
async function pred(data) {
    const response = await fetch("https://api-inference.huggingface.co/models/UDE-SE/CodeBERTForReturnTypeClassification", {
        headers: { Authorization: "Bearer XXX_TOKEN_XXX" },
        method: "POST",
        body: JSON.stringify(data),
    });
    const result = await response.json();
    return result;
}
exports.disposable = vscode.commands.registerCommand('returntypes-predictor.helloWorld', async function () {
    vscode.window.showInformationMessage('Hello there from returntypes predictor!');
});
exports.predDisposable = vscode.commands.registerCommand('returntypes-predictor.predict', async function () {
    let editor = vscode.window.activeTextEditor;
    if (!editor) {
        return ''; // No open text editor
    }
    let selection = editor.selection;
    // get the selected method name
    let methodName = selectionText(editor, selection);
    if (methodName == '')
        return;
    // predict
    let p = await pred({ "inputs": methodName }).then((response) => {
        return response;
    });
    // Error while model is not available {"error":"Model .../ReturnTypes-Predictor is currently loading","estimated_time":20}
    if (JSON.stringify(p).includes("is currently loading")) {
        vscode.window.showErrorMessage("The model is currently loading, please try again!");
    }
    //convert labels to ['None', 'number', 'boolean', 'object', 'string', 'collection']
    var scores = [];
    var labels = [];
    p[0].forEach((elem) => {
        scores.push(elem.score);
        switch (elem.label) {
            case "LABEL_0":
                labels.push("void");
                break;
            case "LABEL_1":
                labels.push("int/float/double/Integer/Byte");
                break;
            case "LABEL_2":
                labels.push("boolean");
                break;
            case "LABEL_3":
                labels.push("String");
                break;
            case "LABEL_4":
                labels.push("Object");
                break;
            case "LABEL_5":
                labels.push("Object[]");
                break;
            default:
                break;
        }
    });
    const sortedByValue = scores.sort((a, b) => b - a);
    const top3Indices = sortedByValue.map(value => scores.indexOf(value)).slice(0, 3);
    const options = top3Indices.map(index => `${labels[index]} (${Math.round(scores[index] * 100)}%)`);
    confirm("Shall one of the following predicted return types be inserted?", options).then((option) => {
        switch (option) {
            case options[0]:
                editor?.insertSnippet(new vscode.SnippetString(options[0].split(' ')[0] + " "), selection.start);
                break;
            case options[1]:
                editor?.insertSnippet(new vscode.SnippetString(options[1].split(' ')[0] + " "), selection.start);
                break;
            case options[2]:
                editor?.insertSnippet(new vscode.SnippetString(options[2].split(' ')[0] + " "), selection.start);
                break;
        }
    });
});
exports.analyzeDisposable = vscode.commands.registerCommand('returntypes-predictor.analyze', async function () {
    let editor = vscode.window.activeTextEditor;
    if (!editor) {
        return ''; // No open text editor
    }
    let text = editor.document.getText();
    const temp_filePath = __dirname + '/currentFile.java';
    // Write to the file
    fs.writeFile(temp_filePath, text, (err) => {
        if (err) {
            console.error('Error writing to file:', err);
        }
        else {
            console.log('Content has been written to the file successfully!');
        }
    });
    let filepath = __dirname + '/script.py';
    const command = 'python3 ' + filepath;
    const childProcess = (0, child_process_1.spawn)(command, { shell: true });
    // Capture the output of the command
    let commandOutput = '';
    childProcess.stdout.on('data', (data) => {
        commandOutput += data.toString();
    });
    childProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
    });
    childProcess.on('close', async (code) => {
        console.log(`Command exited with code ${code}`);
        if (code === 0) {
            // Parse the output as JSON
            try {
                console.log('commandOutput: ' + commandOutput);
                const lines = commandOutput.split('\n');
                const lastLine = lines[lines.length - 2];
                const resultDictionary = JSON.parse(lastLine);
                var counter = 0;
                const methodInfos = [];
                Object.entries(resultDictionary).forEach(([key, value]) => {
                    counter += 1;
                    let returnTypeGroup;
                    switch (String(value).toLowerCase()) {
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
                            returnTypeGroup = 'Number';
                            break;
                        case 'boolean':
                            returnTypeGroup = 'Boolean';
                            break;
                        case 'string':
                        case 'char':
                            returnTypeGroup = 'String';
                            break;
                        case 'collection':
                        case 'array':
                        case 'list':
                        case 'arraylist':
                        case 'set':
                            returnTypeGroup = 'Collection';
                            break;
                        default:
                            returnTypeGroup = 'Object';
                    }
                    methodInfos.push({ name: key, returnType: String(value), returnTypeGroup: returnTypeGroup });
                });
                var analyze_score = 0;
                var wrong_classifications = [];
                var successful_analyze = true;
                for (const methodinfo of methodInfos) {
                    let given_return_type_group = methodinfo['returnTypeGroup'];
                    let method_name = methodinfo['name'];
                    // predict
                    let p = await pred({ "inputs": method_name }).then((response) => {
                        return response;
                    });
                    // Error while model is not available {"error":"Model .../ReturnTypes-Predictor is currently loading","estimated_time":20}
                    if (JSON.stringify(p).includes("is currently loading")) {
                        vscode.window.showErrorMessage("The model is currently loading, please try again!\n ErrorMessage: " + JSON.stringify(p));
                        successful_analyze = false;
                        break;
                    }
                    else {
                        var scores = [];
                        var labels = [];
                        p[0].forEach((elem) => {
                            scores.push(elem.score);
                            switch (elem.label) {
                                case "LABEL_0":
                                    labels.push("None");
                                    break;
                                case "LABEL_1":
                                    labels.push("Number");
                                    break;
                                case "LABEL_2":
                                    labels.push("Boolean");
                                    break;
                                case "LABEL_3":
                                    labels.push("String");
                                    break;
                                case "LABEL_4":
                                    labels.push("Object");
                                    break;
                                case "LABEL_5":
                                    labels.push("Collection");
                                    break;
                                default:
                                    break;
                            }
                        });
                        const sortedByValue = scores.sort((a, b) => b - a);
                        const topIndices = sortedByValue.map(value => scores.indexOf(value));
                        const options = topIndices.map(index => `${labels[index]} (${Math.round(scores[index] * 100)}%) `);
                        if (options[0].split(' ')[0] == given_return_type_group) {
                            analyze_score += 1;
                        }
                        else {
                            wrong_classifications.push([method_name, given_return_type_group, options]);
                        }
                    }
                }
                ;
                if (successful_analyze == true) {
                    console.log('analyze score', analyze_score);
                    console.log('total ammount', methodInfos.length);
                    var message_text = "";
                    for (let w_c of wrong_classifications) {
                        message_text = message_text + `method_name: ${w_c[0]}\ngiven: ${w_c[1]}\nprediction: ${w_c[2]}\n\n`;
                    }
                    vscode.window.showInformationMessage(`${analyze_score} out of ${methodInfos.length} return types are classfied correct.\nThe missclassified methods are listed in console.`, { modal: true });
                    // vscode.window.showInformationMessage(`The following methods are classified wrong:\n${message_text}`);
                    console.log(message_text);
                }
            }
            catch (error) {
                console.error('Error parsing JSON:', error);
            }
        }
        else {
            console.error('Command failed');
        }
    });
});
module.exports = {
    disposable: exports.disposable,
    predDisposable: exports.predDisposable,
    analyzeDisposable: exports.analyzeDisposable
};
//# sourceMappingURL=command.js.map