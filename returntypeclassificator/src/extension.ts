import * as vscode from 'vscode';

let command = require('./command');

export function activate(context: vscode.ExtensionContext) {

	console.log('Congratulations, your extension "returntypes-predictor" is now active!');

	context.subscriptions.push(command.disposable);
	context.subscriptions.push(command.predDisposable);
	context.subscriptions.push(command.analyzeDisposable);
}

exports.activate = activate;

function deactivate() {
}

exports.deactivate = deactivate;