"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProveedorFirmasSobrecargadas = void 0;
const vscode = require("vscode");
class ProveedorFirmasSobrecargadas {
    constructor(parser) {
        this.parser = parser;
    }
    // Parte de la interfaz necesaria para vscode
    provideHover(document, position, token) {
        const firmas = this.parser.getFunctionSignatures(document, position);
        if (!firmas || firmas.length === 0) {
            return null;
        }
        const hoverContent = [];
        const mainMarkdown = new vscode.MarkdownString();
        // Contexto de clase si aplica
        const nombre_clase = firmas[0].nombre_clase;
        if (nombre_clase) {
            mainMarkdown.appendMarkdown(`### ${nombre_clase}.${firmas[0].nombre}\n\n`);
        }
        else {
            mainMarkdown.appendMarkdown(`### ${firmas[0].nombre}\n\n`);
        }
        //mainMarkdown.appendMarkdown('#### Sobrecargas soportadas:\n\n');
        for (const signature of firmas) {
            // Format the function signature
            mainMarkdown.appendCodeblock(`def ${signature.nombre}(${this.formatearParametros(signature.cadena_parametros)})${signature.tipo_retorno ? ` -> ${signature.tipo_retorno}` : ''}`, 'python');
            if (signature.docstring) {
                // Formato
                mainMarkdown.appendMarkdown('\n');
                mainMarkdown.appendMarkdown('```\n  ');
                // Sanitizado
                mainMarkdown.appendMarkdown(`${this.sanitizarDocstring(signature.docstring)}\n`);
                mainMarkdown.appendMarkdown('```\n\n');
            }
            else {
                mainMarkdown.appendMarkdown('\n\n');
            }
            mainMarkdown.appendMarkdown('---  \n\n');
        }
        hoverContent.push(mainMarkdown);
        return new vscode.Hover(hoverContent);
    }
    // Formato parametros
    formatearParametros(paramString) {
        // nueva linea?
        if (paramString.length > 40) {
            const params = this.parsearParametros(paramString);
            return params.join(',\n    ');
        }
        return paramString;
    }
    // Parte de la interfaz necesaria para vscode
    provideSignatureHelp(document, position, token, context) {
        // q funcion?
        const text = document.getText();
        const corrimiento = document.offsetAt(position);
        // parentesis
        let corrimiento_parentesis = corrimiento;
        let nivel_parentesis = 0;
        let inicio_nombre_funcion = -1;
        // buscar funcion y parentesis hacia atras
        for (let i = corrimiento; i >= 0; i--) {
            const char = text.charAt(i);
            if (char === ')') {
                nivel_parentesis++;
            }
            else if (char === '(') {
                nivel_parentesis--;
                if (nivel_parentesis < 0) {
                    corrimiento_parentesis = i;
                    break;
                }
            }
        }
        // Now find the function name before the parenthesis
        for (let i = corrimiento_parentesis - 1; i >= 0; i--) {
            const char = text.charAt(i);
            if (/\s/.test(char)) {
                continue;
            }
            else if (/[a-zA-Z0-9_]/.test(char)) {
                let j = i;
                while (j >= 0 && /[a-zA-Z0-9_]/.test(text.charAt(j))) {
                    j--;
                }
                inicio_nombre_funcion = j + 1;
                break;
            }
            else {
                break;
            }
        }
        if (inicio_nombre_funcion < 0) {
            return null;
        }
        const parte_funcion = text.substring(inicio_nombre_funcion, corrimiento_parentesis);
        const partes = parte_funcion.split('.');
        const nombre_funcion = partes[partes.length - 1];
        let objectName = null;
        if (partes.length > 1) {
            // probablemente un método...
            objectName = partes[partes.length - 2];
        }
        const posicion_funcion = document.positionAt(inicio_nombre_funcion);
        let firmas = null;
        if (objectName) {
            const objectPos = new vscode.Position(posicion_funcion.line, posicion_funcion.character - objectName.length - 1);
            firmas = this.parser.getFunctionSignatures(document, posicion_funcion);
        }
        else {
            firmas = this.parser.getFunctionSignatures(document, posicion_funcion);
        }
        if (!firmas || firmas.length === 0) {
            return null;
        }
        const signatureHelp = new vscode.SignatureHelp();
        signatureHelp.signatures = firmas.map((sig, index) => {
            // Fechas... no funciona JA
            const totalSignatures = firmas.length;
            const navigationPrefix = totalSignatures > 1
                ? `${index + 1}/${totalSignatures} ${index > 0 ? '← ' : '  '}`
                : '';
            const navigationSuffix = totalSignatures > 1 && index < totalSignatures - 1
                ? ' →'
                : '';
            const etiqueta_firma = `${navigationPrefix}${sig.nombre}(${sig.cadena_parametros})${sig.tipo_retorno ? ` -> ${sig.tipo_retorno}` : ''}${navigationSuffix}`;
            const documentacion = this.formatearDocstring(sig);
            const firma = new vscode.SignatureInformation(etiqueta_firma, new vscode.MarkdownString(documentacion));
            const params = this.parsearParametros(sig.cadena_parametros);
            firma.parameters = params.map(param => {
                const paramInfo = this.extraerInfoParametros(param, sig.docstring);
                return new vscode.ParameterInformation(param, new vscode.MarkdownString(paramInfo || ''));
            });
            return firma;
        });
        let firma_activa = 0;
        if (context.activeSignatureHelp && context.isRetrigger) {
            firma_activa = context.activeSignatureHelp.activeSignature;
            if (firma_activa >= signatureHelp.signatures.length) {
                firma_activa = 0;
            }
        }
        signatureHelp.activeSignature = firma_activa;
        try {
            const callText = text.substring(corrimiento_parentesis + 1, corrimiento);
            const commaCount = this.contarComasDesbalanceadas(callText);
            signatureHelp.activeParameter = commaCount;
        }
        catch (e) {
            signatureHelp.activeParameter = 0;
        }
        return signatureHelp;
    }
    formatearDocstring(firma) {
        if (!firma.docstring) {
            return '';
        }
        let docstring_limpia = this.sanitizarDocstring(firma.docstring);
        const prefijo_clase = firma.nombre_clase ? `**Class:** ${firma.nombre_clase}\n\n` : '';
        return `${prefijo_clase}**Docstring:**\n\n${docstring_limpia}`;
    }
    sanitizarDocstring(docstring) {
        let limpia = docstring.trim();
        limpia = limpia.split('\n').map(line => line.trim()).join('\n');
        return limpia;
    }
    extraerInfoParametros(param, docstring) {
        if (!docstring) {
            return undefined;
        }
        const paramName = param.split(':')[0].split('=')[0].trim();
        // No sé esto lo armo una LLM... regex medio loco 
        const paramPatterns = [
            // :param name: description (possibly multi-line)
            new RegExp(`:param\\s+${paramName}\\s*:([^:]*)(?::param|:return|$)`, 's'),
            // Parameters:\n    name: description
            new RegExp(`Parameters[\\s\\S]*?\\b${paramName}\\b\\s*:([^\\n]*)(?:\\n\\s*\\w+:|$)`, 's'),
            // name (type): description
            new RegExp(`\\b${paramName}\\b\\s*\\([^)]*\\)\\s*:([^\\n]*)`, 'i'),
            // Args:\n    name: description (possibly multi-line)
            new RegExp(`Args:[\\s\\S]*?\\b${paramName}\\b\\s*:([^:]*)(?:\\n\\s*\\w+:|$)`, 's')
        ];
        for (const pattern of paramPatterns) {
            const match = docstring.match(pattern);
            if (match && match[1]) {
                const description = match[1].trim();
                if (description) {
                    return `**${paramName}**: ${description}`;
                }
            }
        }
        return undefined;
    }
    contarComasDesbalanceadas(text) {
        let contador = 0;
        let nivel_parentesis = 0;
        let nivel_corchetes = 0;
        let nivel_llaves = 0;
        for (const char of text) {
            if (char === '(') {
                nivel_parentesis++;
            }
            else if (char === ')') {
                nivel_parentesis--;
            }
            else if (char === '[') {
                nivel_corchetes++;
            }
            else if (char === ']') {
                nivel_corchetes--;
            }
            else if (char === '{') {
                nivel_llaves++;
            }
            else if (char === '}') {
                nivel_llaves--;
            }
            else if (char === ',' && nivel_parentesis === 0 && nivel_corchetes === 0 && nivel_llaves === 0) {
                contador++;
            }
        }
        return contador;
    }
    parsearParametros(paramString) {
        if (!paramString.trim()) {
            return [];
        }
        const resultado = [];
        let currentParam = '';
        let nivel_parentesis = 0;
        let nivel_corchetes = 0;
        let nivel_llaves = 0;
        for (const char of paramString) {
            if (char === '(') {
                nivel_parentesis++;
                currentParam += char;
            }
            else if (char === ')') {
                nivel_parentesis--;
                currentParam += char;
            }
            else if (char === '[') {
                nivel_corchetes++;
                currentParam += char;
            }
            else if (char === ']') {
                nivel_corchetes--;
                currentParam += char;
            }
            else if (char === '{') {
                nivel_llaves++;
                currentParam += char;
            }
            else if (char === '}') {
                nivel_llaves--;
                currentParam += char;
            }
            else if (char === ',' && nivel_parentesis === 0 && nivel_corchetes === 0 && nivel_llaves === 0) {
                if (currentParam.trim().length > 0) {
                    resultado.push(currentParam.trim());
                }
                currentParam = '';
            }
            else {
                currentParam += char;
            }
        }
        if (currentParam.trim().length > 0) {
            resultado.push(currentParam.trim());
        }
        return resultado;
    }
}
exports.ProveedorFirmasSobrecargadas = ProveedorFirmasSobrecargadas;
