"""
===============
sobrecargar.py
===============
Sobrecarga de métodos y funciones para Python 3.

* Repositorio del proyecto: https://github.com/Hernanatn/sobrecargar.py
* Documentación: https://github.com/Hernanatn/sobrecargar.py/blob/master/README.MD

Derechos de autor (c) 2023 Hernán A. Teszkiewicz Novick. Distribuído bajo licencia MIT.
Hernan ATN | herni@cajadeideas.ar 
"""

__author__ = "Hernan ATN"
__copyright__ = "(c) 2023, Hernán A. Teszkiewicz Novick."
__license__ = "MIT"
__version__ = "0.1"
__email__ = "herni@cajadeideas.ar"

__all__ = ['sobrecargar', 'overload']

from inspect import signature, Signature, Parameter, ismethod
from typing import Callable, TypeVar, Iterator, ItemsView, OrderedDict, Self, Any
from collections.abc import Sequence, Mapping
from collections import namedtuple
from functools import partial
from sys import modules, version_info
from itertools import zip_longest
import __main__

if version_info < (3, 9):
    raise ImportError("Modulo 'sobrecargar' 'overloading' rqueire Python 3.9 o superior.")
    
    # Interfaz Pública 
class sobrecargar:
    """
    Clase que actúa como decorador de tipo-función, permitiendo definir múltiples
    versiones de una función o método con diferentes conjuntos de parámetros y tipos.
    Esto permite crear una sobrecarga de funciones similar a la que se encuentra en
    lenguajes de programación estáticamente tipados, como C++.

    Atributos de Clase:
        _sobrecargadas (dict): Un diccionario que mantiene un registro de las instancias
        de 'sobrecargar' creadas para cada función o método decorado. Las claves son los
        nombres de las funciones o métodos, y los valores son las instancias de 'sobrecargar'.

    Atributos de Instancia:
        sobrecargas (dict): Un diccionario que almacena las sobrecargas definidas para
        la función o método decorado. Las claves son objetos Signature que representan
        las firmas de las sobrecargas, y los valores son las funciones o métodos
        correspondientes.
    """
    _sobrecargadas : dict[str, 'sobrecargar'] = {}

    def __new__(cls, funcion : Callable)-> 'sobrecargar':
        """
        Constructor. Se crea una única instancia por nombre de función.
        Args:
            funcion (Callable): La función o método que se va a decorar.
        Returns:
            sobrecargar: La instancia de la clase 'sobrecargar' asociada al nombre de la función provista.
        """

        nombre : str = cls.__nombreCompleto(funcion)
        if nombre not in cls._sobrecargadas.keys(): 
            cls._sobrecargadas[nombre] = super().__new__(sobrecargar) 
        return  cls._sobrecargadas[nombre]

    def __init__(self,funcion : Callable) -> None:
        """
        Inicializador. Se encarga de inicializar el diccionario
        de sobrecargas (si no hay ya uno) y registrar en él la versión actual de la función o método decorado.

        Args:
            funcion (Callable): La función o método decorado.
        """
       
        if not hasattr(self,'sobrecargas'):
            self.sobrecargas : dict[Signature, Callable] = {}

        firma : Signature
        funcionSubyacente : Callable
        firma, funcionSubyacente = sobrecargar.__desenvolver(funcion)

        if type(self).__esMetodo(funcion):
            clase : type = type(self).__devolverClase(funcion)
            for ancestro in clase.__mro__:
                for base in ancestro.__bases__:
                    if base is object : break
                    nombreCompletoMetodo : str = f"{base.__module__}.{base.__name__}.{funcion.__name__}"
                    if nombreCompletoMetodo in type(self)._sobrecargadas.keys():
                        sobrecargaBase : 'sobrecargar' = type(self)._sobrecargadas[nombreCompletoMetodo]
                        self.sobrecargas.update(sobrecargaBase.sobrecargas)

        self.sobrecargas[firma] = funcionSubyacente
            
    def __call__(self,*posicionales, **nominales) -> Any:
        """
        Método  que permite que la instancia del decorador sea llamada como
        una función. El motor del módulo. Se encarga de validar los parámetros
        proporcionados y construir una tupla de 'candidatos' de las funciones
        que se adecúan a los parámetros propocionados. Prioriza la sobrecarga
        que mejor se ajusta a los tipos y cantidad de argumentos. Si varios
        candidatos coinciden, propaga el resultado del más específico. 

        Args:
            *posicionales: Argumentos posicionales pasados a la función o método.
            **nominales: Argumentos nominales pasados a la función o método.

        Returns:
            Any: El resultado de la versión seleccionada de la función o método decorado.

        Raises:
            TypeError: Si no existe una sobrecarga compatible para los parámetros
            proporcionados.
        """
        _T = TypeVar("_T")
        Candidato : namedtuple = namedtuple('Candidato',['puntaje','objetoFuncion',"firmaFuncion"])
        candidatos : List[Candidato] = []

        def validarContenedor(valor : _T, parametroContenedor : Parameter) -> int | bool:
            puntajeTipo : int = 0

            anotacionContenedor : _T = parametroContenedor.annotation

            if not hasattr(anotacionContenedor,"__origin__") or not hasattr(anotacionContenedor,"__args__") :
                puntajeTipo += 1
                return puntajeTipo

            if not issubclass(type(valor),anotacionContenedor.__origin__): 
                return False
            argumentosContenedor : Tuple[_T] = anotacionContenedor.__args__
            tieneElipsis : bool = Ellipsis in argumentosContenedor
            tieneUnicoTipo : bool = len(argumentosContenedor) == 1 or tieneElipsis

            if tieneElipsis:
                listaAuxiliarContenedor : list = list(argumentosContenedor)
                listaAuxiliarContenedor[1] = listaAuxiliarContenedor[0]
                argumentosContenedor = tuple(listaAuxiliarContenedor)

            if tieneUnicoTipo:
                iteradorTipos : Iterator = zip_longest((type(t) for t in valor),argumentosContenedor,fillvalue=argumentosContenedor[0])
            else:
                iteradorTipos : Iterator = zip_longest((type(t) for t in valor),argumentosContenedor)

            if not issubclass(type(valor[0]), argumentosContenedor[0]):
                return False

            for tipoRecibido, tipoEsperado in iteradorTipos:
                if tipoEsperado == None : 
                    return False
                if tipoRecibido == tipoEsperado:
                    puntajeTipo += 2               
                elif issubclass(tipoRecibido,tipoEsperado):
                    puntajeTipo += 1
                else:
                    return False
            return puntajeTipo

        def validarTipoParametro(valor : _T, parametroFuncion : Parameter) -> int | bool:
            puntajeTipo : int = 0
            #print(parametroFuncion)
            tipoEsperado : _T = parametroFuncion.annotation 
            tipoRecibido : _T = type(valor)

            esNoTipado : bool = (tipoEsperado == Any)
            porDefecto : _T = parametroFuncion.default
            esNulo : bool = valor is None and porDefecto is None

            esPorDefecto : bool = valor is None and porDefecto is not parametroFuncion.empty
            paramEsSelf : bool =  parametroFuncion.name=='self' or parametroFuncion.name=='cls'
            
            paramEsVariable   : bool = parametroFuncion.kind == parametroFuncion.VAR_POSITIONAL or parametroFuncion.kind == parametroFuncion.VAR_KEYWORD  
            paramEsContenedor : bool = hasattr(tipoEsperado,"__origin__") or (issubclass(tipoEsperado, Sequence) and not issubclass(tipoEsperado,str)) or issubclass(tipoEsperado, Mapping) 


            if paramEsVariable and paramEsContenedor:
                esDistintoTipo : bool = not issubclass(tipoRecibido,tipoEsperado.__args__[0]) 
            elif paramEsContenedor:
                esDistintoTipo : bool = not validarContenedor(valor,parametroFuncion)
            else:
                esDistintoTipo : bool = not issubclass(tipoRecibido, tipoEsperado) 
            
            
            if not esNoTipado and not esNulo and not paramEsSelf and not esPorDefecto and esDistintoTipo:
                return False
            elif paramEsVariable and not paramEsContenedor: 
                puntajeTipo += 1
            else:
                if paramEsVariable and paramEsContenedor:
                    if tipoRecibido == tipoEsperado.__args__[0]:
                        puntajeTipo +=2
                    elif issubclass(tipoRecibido,tipoEsperado.__args__[0]):
                        puntajeTipo +=1  
                elif paramEsContenedor:
                    puntajeTipo += validarContenedor(valor,parametroFuncion)
                elif tipoRecibido == tipoEsperado:
                    puntajeTipo += 4
                elif issubclass(tipoRecibido,tipoEsperado):
                    puntajeTipo += 3
                elif esPorDefecto:  
                    puntajeTipo += 2
                elif esNulo or paramEsSelf or esNoTipado:
                    puntajeTipo += 1

            return puntajeTipo

        def validarFirma(parametrosFuncion : OrderedDict[str,Parameter], cantidadPosicionales : int, iteradorPosicionales : Iterator[tuple], vistaNominales : ItemsView) -> int |bool:
            puntajeFirma : int = 0

            for valorPosicional, nombrePosicional in iteradorPosicionales:
                estePuntaje: int | bool = validarTipoParametro(valorPosicional,parametrosFuncion[nombrePosicional])
                if estePuntaje:
                    puntajeFirma += estePuntaje 
                else:
                    return False
            
            for nombreNominal, valorNominal in vistaNominales:
                if nombreNominal not in parametrosFuncion: return False
                estePuntaje: int | bool = validarTipoParametro(valorNominal,parametrosFuncion[nombreNominal])
                if estePuntaje:
                    puntajeFirma += estePuntaje 
                else:
                    return False

            
            return puntajeFirma

        for firma, funcion in self.sobrecargas.items():

            puntajeLongitud : int = 0
            
            parametrosFuncion : OrderedDict[str,Parameter] = firma.parameters
            
            cantidadPosicionales    : int = len(parametrosFuncion) if type(self).__tieneVarPos(parametrosFuncion) else len(posicionales) 
            cantidadNominales       : int = len({nom : nominales[nom] for nom in parametrosFuncion if nom in nominales}) if (type(self).__tieneVarNom(parametrosFuncion) or type(self).__tieneSoloNom(parametrosFuncion)) else len(nominales)
            cantidadPorDefecto      : int = type(self).__tienePorDefecto(parametrosFuncion) if type(self).__tienePorDefecto(parametrosFuncion) else 0
            iteradorPosicionales : Iterator[tuple[_T,str]] = zip(posicionales, list(parametrosFuncion)[:cantidadPosicionales]) 
            vistaNominales : ItemsView[str,_T] = nominales.items()


            
            if (len(parametrosFuncion) == 0 or not (type(self).__tieneVariables(parametrosFuncion) or type(self).__tienePorDefecto(parametrosFuncion))) and len(parametrosFuncion) != (len(posicionales) + len(nominales)): continue             
        
            if len(parametrosFuncion) - (cantidadPosicionales + cantidadNominales) == 0 and not(type(self).__tieneVariables(parametrosFuncion) or type(self).__tienePorDefecto(parametrosFuncion)):
                puntajeLongitud += 3
            elif len(parametrosFuncion) - (cantidadPosicionales + cantidadNominales) == 0:
                puntajeLongitud += 2
            elif (0 <= len(parametrosFuncion) - (cantidadPosicionales + cantidadNominales) <= cantidadPorDefecto) or (type(self).__tieneVariables(parametrosFuncion)):
                puntajeLongitud += 1
            else:
                continue

            
            puntajeValidacionFirma : int | bool = validarFirma(parametrosFuncion,cantidadPosicionales,iteradorPosicionales,vistaNominales) 
            if puntajeValidacionFirma:
                esteCandidato : Candidato = Candidato(puntaje=(puntajeLongitud+2*puntajeValidacionFirma),objetoFuncion=funcion,firmaFuncion=firma)
                candidatos.append(esteCandidato)
                #return funcion(*posicionales,**nominales)
            else:
                continue
        if candidatos:
            
            if len(candidatos)>1:
                candidatos.sort(key= lambda c: c.puntaje, reverse=True)
            mejorFuncion = candidatos[0].objetoFuncion
            return mejorFuncion(*posicionales,**nominales)
        else:
            raise TypeError(f"[ERROR] No existen sobrecargas de {funcion.__name__} para los parámetros provistos:\n {[type(posicional) for posicional in posicionales]} {[(k,type(nominal)) for k,nominal in nominales.items()]}\n Sobrecargas soportadas: {[dict(fir.parameters) for fir in self.sobrecargas.keys()]}")
    
    def __get__(self, obj, tipoObj) -> 'MetodoSobrecargado':
        #
        class MetodoSobrecargado:
            __call__ = partial(self.__call__, obj) if obj is not None else partial(self.__call__, tipoObj)

        return MetodoSobrecargado()


    # Interfaz Privada 

    @staticmethod
    def __desenvolver(funcion : Callable) -> tuple[Signature, Callable]:
        while hasattr(funcion, '__func__'):
            funcion = funcion.__func__
        while hasattr(funcion, '__wrapped__'):
            funcion = funcion.__wrapped__

        firma : Signature = signature(funcion)
        return (firma,funcion)

    @staticmethod
    def __nombreCompleto(funcion : Callable) -> str :
        return f"{funcion.__module__}.{funcion.__qualname__}"

    @staticmethod
    def __esMetodo(funcion : Callable) -> bool :
        return funcion.__name__ != funcion.__qualname__ and "<locals>" not in funcion.__qualname__.split(".")

    @staticmethod
    def esAnidada(funcion : Callable) -> bool:
        return funcion.__name__ != funcion.__qualname__ and "<locals>" in funcion.__qualname__.split(".")

    @staticmethod
    def __devolverClase(metodo : Callable) -> type:
        #rint(f"[DEBUG] LLAMADA A devolverclase {metodo.__qualname__}")
        return getattr(modules[metodo.__module__],metodo.__qualname__.split(".")[0])


    @staticmethod
    def __tieneVariables(parametrosFuncion : OrderedDict[str,Parameter]) -> bool:
        for parametro in parametrosFuncion.values():
            if sobrecargar.__tieneVarNom(parametrosFuncion) or sobrecargar.__tieneVarPos(parametrosFuncion): return True
        return False

    @staticmethod
    def __tieneVarPos(parametrosFuncion : OrderedDict[str,Parameter]) -> bool:
        for parametro in parametrosFuncion.values():
            if parametro.kind == Parameter.VAR_POSITIONAL: return True
        return False

    @staticmethod
    def __tieneVarNom(parametrosFuncion : OrderedDict[str,Parameter]) -> bool:
        for parametro in parametrosFuncion.values():
            if parametro.kind == Parameter.VAR_KEYWORD: return True
        return False

    @staticmethod
    def __tienePorDefecto(parametrosFuncion : OrderedDict[str,Parameter]) -> int | bool:
        cuentaDefecto : int = 0
        for parametro in parametrosFuncion.values():
            if parametro.default != parametro.empty: cuentaDefecto+=1
        return cuentaDefecto if cuentaDefecto else False 
    
    @staticmethod
    def __tieneSoloNom(parametrosFuncion : OrderedDict[str,Parameter]) -> bool:
        for parametro in parametrosFuncion.values():
            if parametro.kind == Parameter.KEYWORD_ONLY: return True
        return False

overload = sobrecargar



if __name__ == '__main__': print(__doc__)

"""
Licencia MIT

Derechos de autor (c) 2023 Hernán A. Teszkiewicz Novick

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
de este software y los archivos de documentación asociados (el "Software"), para utilizar
el Software sin restricción, incluyendo, sin limitación, los derechos
para usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y / o vender
copias del Software, y para permitir a las personas a quienes se les proporcione el Software
hacerlo, sujeto a las siguientes condiciones:

El aviso de derechos de autor anterior y este aviso de permiso se incluirán en todos
las copias o partes sustanciales del Software.

EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O
IMPLÍCITA, INCLUYENDO, PERO NO LIMITADO A, LAS GARANTÍAS DE COMERCIALIZACIÓN,
ADECUACIÓN PARA UN PROPÓSITO PARTICULAR Y NO INFRACCIÓN. EN NINGÚN CASO
LOS TITULARES DE LOS DERECHOS DE AUTOR O LOS AUTORES SERÁN RESPONSABLES DE
NINGUNA RECLAMACIÓN, DAÑOS U OTRAS RESPONSABILIDADES, YA SEA EN UNA ACCIÓN DE
CONTRATO, AGRAVIO O DE CUALQUIER OTRA NATURALEZA, DERIVADAS DE, FUERA DE O EN CONEXIÓN CON EL
SOFTWARE O EL USO U OTROS VERSIONES, DISTRIBUCIONES Y ACUERDOS CONCERNIENTES AL SOFTWARE.
"""