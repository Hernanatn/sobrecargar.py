import * as vscode from 'vscode';
import { ParseadorSobrecargar } from './parseador';
import { ProveedorFirmasSobrecargadas } from './proveedor_de_firmas';

let parser: ParseadorSobrecargar;

export function activate(context: vscode.ExtensionContext) {
    console.log('Sobrecargar-vscode activada!');
    
    // Inicializa parser
    parser = new ParseadorSobrecargar();
    
    // Registra proveedor de firmas
    const proveedor_de_firmas = new ProveedorFirmasSobrecargadas(parser);
    
    // Register hover provider for Python files
    context.subscriptions.push(
        vscode.languages.registerHoverProvider(
            { language: 'python' },
            proveedor_de_firmas
        )
    );
    
    // registra ayuda de firmas en python
    context.subscriptions.push(
        vscode.languages.registerSignatureHelpProvider(
            { language: 'python' },
            proveedor_de_firmas,
            '(', ','  // disparadores
        )
    );
    
    // navegación -- ROTO
    context.subscriptions.push(
        vscode.commands.registerCommand('sobrecargar.nextSignature', () => {
            vscode.commands.executeCommand('editor.action.nextSignature');
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('sobrecargar.previousSignature', () => {
            vscode.commands.executeCommand('editor.action.prevSignature');
        })
    );
    
    
    context.subscriptions.push(
        vscode.commands.registerTextEditorCommand('sobrecargar.cycleSignatures', (editor) => {
            vscode.commands.executeCommand('editor.action.nextSignature');
        })
    );
    
    
    const watchForChanges = () => {
        vscode.workspace.textDocuments.forEach(document => {
            if (document.languageId === 'python') {
                parser.parsearDocumento(document);
            }
        });
    };
    
    // Parsear todos al iniciar
    watchForChanges();
    
    // si se abre un doc .py parsear
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(document => {
            if (document.languageId === 'python') {
                parser.parsearDocumento(document);
            }
        })
    );
    
    // tambien al guardar
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(document => {
            if (document.languageId === 'python') {
                parser.parsearDocumento(document);
            }
        })
    );
    
    // tambien al editar
    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument(event => {
            const document = event.document;
            if (document.languageId === 'python') {
                // dale un cacho de espera
                clearTimeout(parseTimeout);
                parseTimeout = setTimeout(() => {
                    parser.parsearDocumento(document);
                }, 500); // 500ms debounce
            }
        })
    );
    
    
    let parseTimeout: NodeJS.Timeout;
    
    
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.text = '$(symbol-class) Sobrecargar';
    statusBarItem.tooltip = 'Sobrecargar-vsc activada';
    statusBarItem.command = 'sobrecargar.showOverloads'; // Make the status bar item clickable
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    
    
    const refreshCommand = vscode.commands.registerCommand(
        'sobrecargar.refreshOverloads',
        () => {
            parser.clearCache();
            watchForChanges();
            vscode.window.showInformationMessage('Sobrecargar-vsc refrescada');
        }
    );
    context.subscriptions.push(refreshCommand);
    

    const showOverloadsCommand = vscode.commands.registerCommand(
        'sobrecargar.showOverloads',
        async () => {
            const overloads = parser.getOverloadedFunctions();
            if (overloads.length === 0) {
                vscode.window.showInformationMessage('No se encontraron sobrecargas en el espacio de trabajo activo');
                return;
            }
            
            
            const overloadsByFile: { [key: string]: OverloadItem[] } = {};
            
            overloads.forEach(overload => {
                const uri = vscode.Uri.parse(overload.uri_documento);
                const filePath = uri.fsPath;
                
                if (!overloadsByFile[filePath]) {
                    overloadsByFile[filePath] = [];
                }
                
                
                const label = overload.nombre_clase 
                    ? `${overload.nombre_clase}.${overload.name}`
                    : overload.name;
                
                const item: OverloadItem = {
                    label,
                    description: `${overload.firmas.length} sobrecargas`,
                    detail: path.basename(filePath),
                    overload,
                    resourceUri: uri
                };
                
                overloadsByFile[filePath].push(item);
            });
            
            
            const quickPickItems: OverloadItem[] = [];
            
            Object.keys(overloadsByFile).sort().forEach(filePath => {
                const fileItems = overloadsByFile[filePath];
                
                
                quickPickItems.push({
                    label: path.basename(filePath),
                    kind: vscode.QuickPickItemKind.Separator
                } as OverloadItem);
                
                
                quickPickItems.push(...fileItems.sort((a, b) => a.label.localeCompare(b.label)));
            });
            
            const selected = await vscode.window.showQuickPick(quickPickItems, {
                placeHolder: 'Seleccione una sobrecarga a la cual navegar',
                matchOnDescription: true,
                matchOnDetail: true
            });
            
            if (selected && selected.overload) {
                const uri = vscode.Uri.parse(selected.overload.uri_documento);
                const firstSignature = selected.overload.firmas[0];
                
                vscode.window.showTextDocument(uri).then(editor => {
                    
                    editor.selection = new vscode.Selection(
                        firstSignature.range.start,
                        firstSignature.range.start
                    );
                    editor.revealRange(firstSignature.range);
                });
            }
        }
    );
    context.subscriptions.push(showOverloadsCommand);
    
    // Register a command to show signature help at current position
    const showSignatureHelpCommand = vscode.commands.registerCommand(
        'sobrecargar.showSignatureHelp',
        () => {
            vscode.commands.executeCommand('editor.action.triggerParameterHints');
        }
    );
    context.subscriptions.push(showSignatureHelpCommand);
}


interface OverloadItem extends vscode.QuickPickItem {
    overload?: any;
    resourceUri?: vscode.Uri;
    kind?: vscode.QuickPickItemKind;
}


import * as path from 'path';

export function deactivate() {
    console.log('Sobrecargar-vsc desactivada!');
}
