"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = void 0;
let command = require('./command');
function activate(context) {
    console.log('Congratulations, your extension "returntypes-predictor" is now active!');
    context.subscriptions.push(command.disposable);
    context.subscriptions.push(command.predDisposable);
    context.subscriptions.push(command.analyzeDisposable);
}
exports.activate = activate;
exports.activate = activate;
function deactivate() {
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map