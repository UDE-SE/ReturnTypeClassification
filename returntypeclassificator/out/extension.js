"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = void 0;
let command = require('./command');
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
function activate(context) {
    context.subscriptions.push(command.predDisposable);
    context.subscriptions.push(command.analyzeDisposable);
}
exports.activate = activate;
exports.activate = activate;
// This method is called when your extension is deactivated
function deactivate() {
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map