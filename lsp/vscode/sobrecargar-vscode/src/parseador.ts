import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export interface FirmaFuncion {
    nombre: string;
    cadena_parametros: string;
    tipo_retorno: string | undefined;
    docstring: string | undefined;
    rango: vscode.Range;
    nombre_clase?: string; 
}

export interface FuncionSobrecargada {
    name: string;
    firmas: FirmaFuncion[];
    uri_documento: string;
    nombre_clase?: string; 
}

export class ParseadorSobrecargar {
    private funciones_sobrecargadas: Map<string, FuncionSobrecargada> = new Map();
    
    constructor() {}

    public parsearDocumento(document: vscode.TextDocument): FuncionSobrecargada[] {
        const texto = document.getText();
        const lineas = texto.split(/\r?\n/);
    
        const resultado: FuncionSobrecargada[] = [];
        const firmas_temp: Map<string, FirmaFuncion[]> = new Map();
    
        let en_import = false;
        let se_importo_sobrecargar = false;
        let aliases_import: string[] = ['sobrecargar', 'overload'];
    
        
        for (let i = 0; i < lineas.length; i++) {
            const linea = lineas[i].trim();
    
            if (linea.startsWith('import ') || linea.startsWith('from ')) {
                en_import = true;
    
                
                if (linea.includes('sobrecargar')) {
                    se_importo_sobrecargar = true;
    
                    
                    const match = linea.match(/from\s+sobrecargar\s+import\s+(\w+)(?:\s+as\s+(\w+))?/);
                    if (match && match[2]) {
                        aliases_import.push(match[2]);
                    }
                }
            } else if (en_import && linea === '') {
                en_import = false;
            }
        }
    
        if (!se_importo_sobrecargar) {
            return [];
        }
    
        
        let decoradorActual: string | null = null;
        let currentFunctionName: string | null = null;
        let nombre_clase_actual: string | null = null;
        let inClass = false;
        let indentacion_clase = -1;
    
        for (let i = 0; i < lineas.length; i++) {
            const linea = lineas[i];
            const lineaRecortada = linea.trim();
    
            
            if (lineaRecortada.startsWith('class ')) {
                const classMatch = lineaRecortada.match(/class\s+(\w+)(?:\s*\([^)]*\))?\s*:/);
                if (classMatch) {
                    nombre_clase_actual = classMatch[1];
                    inClass = true;
                    indentacion_clase = linea.search(/\S/);
                }
            } 
            
            else if (inClass && lineaRecortada !== '') {
                const indentacion_actual = linea.search(/\S/);
                if (indentacion_actual <= indentacion_clase && 
                    !lineaRecortada.startsWith('@') && 
                    !lineaRecortada.startsWith('def ') &&
                    !lineaRecortada.startsWith('class ')) {
                    inClass = false;
                    nombre_clase_actual = null;
                    indentacion_clase = -1;
                }
            }
    
            
            if (lineaRecortada.startsWith('@')) {
                const decoratorMatch = lineaRecortada.match(/@(\w+)(?:\(.*\))?/);
                if (decoratorMatch && aliases_import.includes(decoratorMatch[1])) {
                    decoradorActual = decoratorMatch[1];
                }
            }
            else if (decoradorActual && lineaRecortada.startsWith('def ')) {
                let functionDefLines = [linea];
                let def_completa = lineaRecortada.endsWith(':');
                
                let continuationLine = (
                    !def_completa ||                 
                    lineaRecortada.endsWith('\\') ||   
                    lineaRecortada.endsWith('\\\r\n') ||   
                    lineaRecortada.endsWith('\\\n') ||   
                    lineaRecortada.endsWith(',') ||    
                    lineaRecortada.endsWith('(') ||    
                    lineaRecortada.endsWith('=')       
                );
    
                let j = i + 1;
    
                
                while ((!def_completa || continuationLine) && j < lineas.length) {
                    const nextLine = lineas[j];
                    const nextTrimmed = nextLine.trim();
    
                    functionDefLines.push(nextLine);
    
                    
                    
                    if (nextTrimmed.endsWith(':')) {
                        def_completa = true;
                        continuationLine = false;
                    } else if (
                        nextTrimmed.endsWith('\\') ||
                        nextTrimmed.endsWith('\\') ||
                        nextTrimmed.endsWith('\\\n') ||
                        nextTrimmed.endsWith('\\\r\n') ||
                        nextTrimmed.endsWith(',') ||
                        nextTrimmed.endsWith(',\n') ||
                        nextTrimmed.endsWith(',\r\n') ||
                        nextTrimmed.endsWith('(') ||
                        nextTrimmed.endsWith('(\n') ||
                        nextTrimmed.endsWith('(\r\n') ||
                        nextTrimmed.endsWith('=') ||
                        nextTrimmed.endsWith('=\\') ||
                        nextTrimmed.endsWith('=\n') ||
                        nextTrimmed.endsWith('= {\n') ||
                        nextTrimmed.endsWith('= (\n') ||
                        nextTrimmed.endsWith('= [\n') ||
                        nextTrimmed.endsWith('=\r\n') ||
                        nextTrimmed.endsWith('=')
                    ) {
                        continuationLine = true;
                    } else {
                        continuationLine = false;
                    }
    
                    j++;
                }
    
                
                const functionDef = functionDefLines.map(linea => linea.replace("\\","").trim()).join(' ');
    
                
                const functionMatch = functionDef.match(/def\s+(\w+)\s*\((.*)\)(?:\s*->\s*([^:]+))?\s*:/);
    
                if (functionMatch) {
                    const functionName = functionMatch[1];
                    const parameters = functionMatch[2].trim();
                    const tipo_retorno = functionMatch[3] ? functionMatch[3].trim() : undefined;
    
                    currentFunctionName = functionName;
    
                    
                    const startPosition = new vscode.Position(i, 0);
                    const endPosition = new vscode.Position(i + functionDefLines.length - 1, 
                                                           functionDefLines[functionDefLines.length - 1].length);
                    const rango = new vscode.Range(startPosition, endPosition);
    
                    
                    const funcKey = nombre_clase_actual ? `${nombre_clase_actual}.${functionName}` : functionName;
    
                    if (!firmas_temp.has(funcKey)) {
                        firmas_temp.set(funcKey, []);
                    }
    
                    
                    let docstring: string | undefined = undefined;
                    if (j < lineas.length) {
                        const nextLine = lineas[j].trim();
                        if (nextLine.startsWith('"""') || nextLine.startsWith("'''")) {
                            const docstringLines: string[] = [];
                            let docEnd = false;
                            let k = j;

                            while (k < lineas.length) {
                                docstringLines.push(lineas[k].trim());
                                if (lineas[k].trim().endsWith('"""') || lineas[k].trim().endsWith("'''")) {
                                    docEnd = true;
                                    break;
                                }
                                k++;
                            }

                            if (docEnd) {
                                docstring = docstringLines.join('\n');
                                j = k + 1;  
                            }
                        }
                    }

                    
                    firmas_temp.get(funcKey)!.push({
                        nombre: functionName,
                        cadena_parametros: parameters,
                        tipo_retorno: tipo_retorno,
                        rango: rango,
                        nombre_clase: nombre_clase_actual || undefined,
                        docstring: docstring
                    });
    
                    
                    decoradorActual = null;
                    i = j - 1;
                }
            }
        }
    
        
        for (const [key, firmas] of firmas_temp.entries()) {
            if (firmas.length > 1) {  
                const name = firmas[0].nombre;
                const nombre_clase = firmas[0].nombre_clase;
    
                
                const docUriKey = nombre_clase 
                    ? `${document.uri.toString()}:${nombre_clase}:${name}` 
                    : `${document.uri.toString()}:${name}`;
    
                const overloadedFunc: FuncionSobrecargada = {
                    name,
                    firmas,
                    uri_documento: document.uri.toString(),
                    nombre_clase
                };
    
                resultado.push(overloadedFunc);
                this.funciones_sobrecargadas.set(docUriKey, overloadedFunc);
            }
        }
    
        return resultado;
    }
    
    
    public getOverloadedFunctions(): FuncionSobrecargada[] {
        return Array.from(this.funciones_sobrecargadas.values());
    }
    
    public getFunctionSignatures(document: vscode.TextDocument, posicion: vscode.Position): FirmaFuncion[] | undefined {
        
        const wordRange = document.getWordRangeAtPosition(posicion);
        if (!wordRange) {
            return undefined;
        }
        
        const functionName = document.getText(wordRange);
        
        
        const linea = document.lineAt(posicion.line).text;
        const prefijo_linea = linea.substring(0, posicion.character);
        
        
        let nombre_objeto: string | null = null;
        const punto_match = prefijo_linea.match(/(\w+)\.\w+$/);
        if (punto_match) {
            nombre_objeto = punto_match[1];
        }
        
        
        let nombre_clase: string | null = null;
        
        if (nombre_objeto) {
            
            nombre_clase = this.findObjectClassType(document, posicion, nombre_objeto);
        } else {
            
            nombre_clase = this.encontrarContextoClaseEnPosicion(document, posicion);
        }
        
        
        if (nombre_clase) {
            const llave_uri_clase = `${document.uri.toString()}:${nombre_clase}:${functionName}`;
            const FuncionSobrecargada = this.funciones_sobrecargadas.get(llave_uri_clase);
            if (FuncionSobrecargada) {
                return FuncionSobrecargada.firmas;
            }
        }
        
        
        const llave_uri_funcion = `${document.uri.toString()}:${functionName}`;
        const FuncionSobrecargada = this.funciones_sobrecargadas.get(llave_uri_funcion);
        
        return FuncionSobrecargada?.firmas;
    }
    
    public encontrarContextoClaseEnPosicion(document: vscode.TextDocument, posicion: vscode.Position): string | null {
        const texto = document.getText();
        const lineas = texto.split(/\r?\n/);
        
        let nombre_clase_actual: string | null = null;
        let indentacion_actual = -1;
        let indentacion_clase = -1;
        
        
        for (let i = posicion.line; i >= 0; i--) {
            const linea = lineas[i];
            const lineaRecortada = linea.trim();
            
            
            if (lineaRecortada === '') {
                continue;
            }
            
            
            const indentacion = linea.search(/\S/);
            if (indentacion === -1) continue;
            
            
            if (indentacion_actual === -1) {
                indentacion_actual = indentacion;
            }
            
            
            if (lineaRecortada.startsWith('class ')) {
                const classMatch = lineaRecortada.match(/^class\s+(\w+)(?:\s*\([^)]*\))?\s*:/);
                if (classMatch) {
                    
                    
                    if (indentacion_actual > indentacion) {
                        nombre_clase_actual = classMatch[1];
                        indentacion_clase = indentacion;
                        break;
                    }
                }
            }
            
            
            
            if (indentacion < indentacion_actual) {
                indentacion_actual = indentacion;
            }
        }
        
        return nombre_clase_actual;
    }
    
    
    private findObjectClassType(document: vscode.TextDocument, posicion: vscode.Position, nombre_objeto: string): string | null {
        const texto = document.getText();
        const lineas = texto.split(/\r?\n/);
        
        
        if (nombre_objeto === 'self') {
            return this.encontrarContextoClaseEnPosicion(document, posicion);
        }
        
        
        
        const assignmentPattern = new RegExp(`${nombre_objeto}\\s*=\\s*([\\w\\.]+)\\(`);
        
        for (let i = 0; i < posicion.line; i++) {
            const match = lineas[i].match(assignmentPattern);
            if (match) {
                
                const constructorName = match[1].split('.').pop() || '';
                
                return constructorName;
            }
        }
        
        return null;
    }
    
    public clearCache(): void {
        this.funciones_sobrecargadas.clear();
    }
}
