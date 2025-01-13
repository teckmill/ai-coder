import * as vscode from 'vscode';
import axios from 'axios';
import { CodeGenerator } from './services/code_generator';

class ChatViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'aiCoderChat';
    private _view?: vscode.WebviewView;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _aiService: AIService
    ) { }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'generate':
                    try {
                        const code = await this._aiService.generateCode(data.prompt, data.model);
                        webviewView.webview.postMessage({ type: 'response', content: code, format: 'code' });
                    } catch (error: any) {
                        webviewView.webview.postMessage({ 
                            type: 'error', 
                            content: error.message || 'Error generating code' 
                        });
                    }
                    break;
                case 'analyze':
                    try {
                        const analysis = await this._aiService.analyzeCode(data.code);
                        webviewView.webview.postMessage({ type: 'response', content: analysis });
                    } catch (error: any) {
                        webviewView.webview.postMessage({ 
                            type: 'error', 
                            content: error.message || 'Error analyzing code' 
                        });
                    }
                    break;
            }
        });
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                :root {
                    --container-padding: 12px;
                    --input-padding: 6px;
                }

                body {
                    padding: 0;
                    margin: 0;
                    width: 100%;
                    height: 100vh;
                    font-family: var(--vscode-font-family);
                    color: var(--vscode-foreground);
                    background: var(--vscode-editor-background);
                    display: flex;
                    flex-direction: column;
                }

                .welcome-view {
                    padding: var(--container-padding);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    height: 100%;
                }

                .welcome-icon {
                    font-size: 48px;
                    color: var(--vscode-textLink-foreground);
                }

                .welcome-title {
                    font-size: 1.2em;
                    font-weight: 600;
                    margin: 0;
                    text-align: center;
                }

                .welcome-description {
                    text-align: center;
                    color: var(--vscode-descriptionForeground);
                    margin: 0;
                    font-size: 0.9em;
                }

                .example-queries {
                    margin-top: 20px;
                    width: 100%;
                }

                .example-query {
                    padding: 8px;
                    margin: 4px 0;
                    background: var(--vscode-textBlockQuote-background);
                    border-radius: 4px;
                    cursor: pointer;
                    transition: background 0.2s;
                    font-size: 0.9em;
                }

                .example-query:hover {
                    background: var(--vscode-list-hoverBackground);
                }

                .chat-container {
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                    max-height: 100vh;
                    overflow: hidden;
                }

                .messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: var(--container-padding);
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }

                .message {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                    animation: fadeIn 0.3s ease-in-out;
                    max-width: 100%;
                    word-wrap: break-word;
                }

                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                .message-header {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    font-size: 0.8em;
                    color: var(--vscode-descriptionForeground);
                }

                .message-avatar {
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    background: var(--vscode-badge-background);
                    color: var(--vscode-badge-foreground);
                }

                .message-content {
                    padding: 8px 12px;
                    border-radius: 8px;
                    background: var(--vscode-textBlockQuote-background);
                    font-size: 0.9em;
                    line-height: 1.5;
                }

                .user-message .message-content {
                    background: var(--vscode-textLink-activeForeground);
                    color: var(--vscode-button-foreground);
                    margin-left: auto;
                    max-width: 80%;
                }

                .ai-message .message-content {
                    background: var(--vscode-textBlockQuote-background);
                    margin-right: auto;
                    max-width: 80%;
                }

                .input-container {
                    padding: var(--container-padding);
                    background: var(--vscode-editor-background);
                    border-top: 1px solid var(--vscode-panel-border);
                }

                .input-wrapper {
                    display: flex;
                    gap: 8px;
                    background: var(--vscode-input-background);
                    border: 1px solid var(--vscode-input-border);
                    border-radius: 4px;
                    padding: 4px;
                }

                textarea {
                    flex: 1;
                    min-height: 20px;
                    max-height: 150px;
                    padding: var(--input-padding);
                    background: transparent;
                    color: var(--vscode-input-foreground);
                    border: none;
                    font-family: inherit;
                    font-size: 0.9em;
                    resize: none;
                    outline: none;
                }

                button {
                    padding: 4px 12px;
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    border-radius: 2px;
                    cursor: pointer;
                    font-size: 0.9em;
                    display: flex;
                    align-items: center;
                    gap: 4px;
                }

                button:hover {
                    background: var(--vscode-button-hoverBackground);
                }

                button:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                pre {
                    background: var(--vscode-textCodeBlock-background);
                    padding: 12px;
                    border-radius: 4px;
                    overflow-x: auto;
                    margin: 8px 0;
                }

                code {
                    font-family: var(--vscode-editor-font-family);
                    font-size: 0.85em;
                }

                .copy-button {
                    position: absolute;
                    right: 8px;
                    top: 8px;
                    padding: 4px 8px;
                    font-size: 0.8em;
                    opacity: 0;
                    transition: opacity 0.2s;
                }

                pre:hover .copy-button {
                    opacity: 1;
                }

                .typing-indicator {
                    display: flex;
                    gap: 4px;
                    padding: 8px;
                    color: var(--vscode-descriptionForeground);
                }

                .typing-dot {
                    width: 4px;
                    height: 4px;
                    border-radius: 50%;
                    background: currentColor;
                    animation: typing 1s infinite;
                }

                .typing-dot:nth-child(2) { animation-delay: 0.2s; }
                .typing-dot:nth-child(3) { animation-delay: 0.4s; }

                @keyframes typing {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-4px); }
                }

                .markdown {
                    line-height: 1.6;
                }

                .markdown p {
                    margin: 0 0 8px 0;
                }

                .markdown ul, .markdown ol {
                    margin: 0;
                    padding-left: 20px;
                }

                .error-message {
                    color: var(--vscode-errorForeground);
                    font-style: italic;
                }
            </style>
        </head>
        <body>
            <div class="chat-container" id="chatContainer">
                <div class="messages" id="messages">
                    <div class="message ai-message">
                        <div class="message-header">
                            <div class="message-avatar">🤖</div>
                            <span>AI Coder</span>
                        </div>
                        <div class="message-content">
                            Hello! I can help you with code generation, analysis, and more. Here are some examples of what you can ask:
                            <ul>
                                <li>Generate a function to sort an array using quicksort</li>
                                <li>Create a React component for a todo list</li>
                                <li>Write a Python class for handling API requests</li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="input-container">
                    <div class="input-wrapper">
                        <select id="modelSelect">
                            <option value="codellama">CodeLlama</option>
                            <option value="ollama">Ollama</option>
                            <option value="gpt-3">GPT-3</option>
                        </select>
                        <textarea 
                            id="prompt" 
                            placeholder="Ask me anything about your code..."
                            rows="1"
                            onInput="this.style.height = 'auto'; this.style.height = this.scrollHeight + 'px';"
                        ></textarea>
                        <button id="send">
                            <span>Send</span>
                            <span style="font-size: 1.2em;">↵</span>
                        </button>
                    </div>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                const messagesContainer = document.getElementById('messages');
                const promptInput = document.getElementById('prompt');
                const sendButton = document.getElementById('send');
                const modelSelect = document.getElementById('modelSelect');

                // Auto-detect and set the default model
                const detectedModel = await detectAvailableModel();
                modelSelect.value = detectedModel;

                function formatCode(code) {
                    return \`<pre><code>\${code}</code><button class="copy-button" onclick="copyCode(this)">Copy</button></pre>\`;
                }

                function copyCode(button) {
                    const code = button.parentElement.querySelector('code').textContent;
                    navigator.clipboard.writeText(code);
                    const originalText = button.textContent;
                    button.textContent = 'Copied!';
                    setTimeout(() => button.textContent = originalText, 2000);
                }

                function addMessage(content, isUser = false, format = 'text') {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = \`message \${isUser ? 'user-message' : 'ai-message'}\`;
                    
                    const header = document.createElement('div');
                    header.className = 'message-header';
                    
                    const avatar = document.createElement('div');
                    avatar.className = 'message-avatar';
                    avatar.textContent = isUser ? '👤' : '🤖';
                    
                    const name = document.createElement('span');
                    name.textContent = isUser ? 'You' : 'AI Coder';
                    
                    header.appendChild(avatar);
                    header.appendChild(name);
                    
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'message-content';
                    
                    if (format === 'code') {
                        contentDiv.innerHTML = formatCode(content);
                    } else if (format === 'error') {
                        contentDiv.innerHTML = \`<span class="error-message">\${content}</span>\`;
                    } else {
                        contentDiv.textContent = content;
                    }
                    
                    messageDiv.appendChild(header);
                    messageDiv.appendChild(contentDiv);
                    messagesContainer.appendChild(messageDiv);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }

                function addTypingIndicator() {
                    const indicator = document.createElement('div');
                    indicator.className = 'typing-indicator';
                    indicator.innerHTML = \`
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    \`;
                    messagesContainer.appendChild(indicator);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    return indicator;
                }

                function sendMessage() {
                    const prompt = promptInput.value.trim();
                    const selectedModel = modelSelect.value;
                    if (!prompt) return;

                    addMessage(prompt, true);
                    const indicator = addTypingIndicator();
                    
                    vscode.postMessage({ type: 'generate', prompt, model: selectedModel });
                    promptInput.value = '';
                    promptInput.style.height = 'auto';
                    sendButton.disabled = true;
                    
                    setTimeout(() => {
                        indicator.remove();
                        sendButton.disabled = false;
                    }, 500);
                }

                sendButton.addEventListener('click', sendMessage);
                
                promptInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                });

                window.addEventListener('message', event => {
                    const message = event.data;
                    const indicator = document.querySelector('.typing-indicator');
                    if (indicator) indicator.remove();
                    
                    switch (message.type) {
                        case 'response':
                            addMessage(message.content, false, message.format || 'text');
                            break;
                        case 'error':
                            addMessage(message.content, false, 'error');
                            break;
                    }
                    sendButton.disabled = false;
                });

                // Focus input on load
                promptInput.focus();
            </script>
        </body>
        </html>`;
    }
}

export async function activate(context: vscode.ExtensionContext) {
    const aiService = new AIService();
    const chatViewProvider = new ChatViewProvider(context.extensionUri, aiService);

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(ChatViewProvider.viewType, chatViewProvider)
    );

    // Register commands
    let generateCode = vscode.commands.registerCommand('ai-coder.generateCode', async () => {
        try {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor!');
                return;
            }

            const prompt = await vscode.window.showInputBox({
                prompt: 'What code would you like to generate?',
                placeHolder: 'E.g., Create a function that sorts an array'
            });

            if (!prompt) return;

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Generating code...",
                cancellable: true
            }, async (progress) => {
                const generatedCode = await aiService.generateCode(prompt, "codellama");
                if (generatedCode) {
                    editor.edit(editBuilder => {
                        const position = editor.selection.active;
                        editBuilder.insert(position, generatedCode);
                    });
                }
            });
        } catch (error: any) {
            vscode.window.showErrorMessage('Failed to generate code: ' + (error.message || 'Unknown error'));
        }
    });

    context.subscriptions.push(generateCode);
}

class AIService {
    private codeGenerator: CodeGenerator;

    constructor() {
        this.codeGenerator = new CodeGenerator();
    }

    async generateCode(prompt: string, model: string): Promise<string> {
        try {
            // Call local Ollama model directly
            const generatedCode = await this.codeGenerator.generate(prompt, model);
            return generatedCode;
        } catch (error: any) {
            throw new Error(`Failed to generate code: ${error.message}`);
        }
    }

    async analyzeCode(code: string): Promise<string> {
        // Placeholder for analyzeCode implementation
        throw new Error('Analyze code functionality not implemented yet.');
    }
}

export function deactivate() {}
