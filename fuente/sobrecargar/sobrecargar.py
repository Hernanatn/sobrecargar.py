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
from functools import partial
from sys import modules, version_info
import __main__

if version_info < (3, 9):
    raise ImportError("Modulo 'sobrecargar' 'overloading' rqueire Python 3.9 o superior.")

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

        nombre : str = cls.nombreCompleto(funcion)
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
        firma, funcionSubyacente = sobrecargar.desenvolver(funcion)

        if type(self).esMetodo(funcion):
            clase : type = type(self).devolverClase(funcion)
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
        una función. El motor del módulo. Se encarga de validar los parámetros proporcionados y seleccionar
        la versión adecuada de la función o método decorado para su ejecución.

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

        def validarContenedor(valor : _T, anotacionContenedor : Parameter.annotation) -> bool:
            if type(valor) != anotacionContenedor.__origin__ : return False

            argumentosContenedor : Tuple[_T] = anotacionContenedor.__args__

            iteradorTipos : Iterator = zip((type(valor[0]),),(argumentosContenedor[0],)) if Ellipsis in argumentosContenedor else zip((type(t) for t in valor),argumentosContenedor)
            
            for tipoRecibido, tipoEsperado in iteradorTipos:
                if tipoRecibido != tipoEsperado : return False
            return True
            
        def validarTipoParametro(valor : _T, parametroFuncion : Parameter) -> bool:
            tipoEsperado : _T = parametroFuncion.annotation 
            tipoRecibido : _T = type(valor)

            porDefecto : _T = parametroFuncion.default
            esNulo : bool = valor is None and porDefecto is None 
            esPorDefecto : bool = valor is None and porDefecto is not parametroFuncion.empty
            paramEsSelf : bool =  parametroFuncion.name=='self' or parametroFuncion.name=='cls'
            
            paramEsContenedor : bool = hasattr(tipoEsperado,"__origin__") and hasattr(tipoEsperado,"__args__")

            esDistintoTipo : bool = not validarContenedor(valor,tipoEsperado) if paramEsContenedor else tipoRecibido != tipoEsperado 
            return False if not esNulo and not paramEsSelf and not esPorDefecto and esDistintoTipo else True

        def validarMultiples(parametrosFuncion : Parameter, cantidadPosicionales : int, iteradorPosicionales : Iterator[tuple], vistaNominales : ItemsView):
            for valorPosicional, nombrePosicional in iteradorPosicionales:
                if validarTipoParametro(valorPosicional,parametrosFuncion[nombrePosicional]): continue
                else: return False

            for nombreNominal, valorNominal in vistaNominales:
                if validarTipoParametro(valorNominal,parametrosFuncion[nombreNominal]): continue
                else: return False
            return True

        for firma, funcion in self.sobrecargas.items():
            parametrosFuncion : OrderedDict[str,Parameter] = firma.parameters
            cantidadPosicionales : int = len(posicionales)
            iteradorPosicionales : Iterator[tuple[_T,str]] = zip(posicionales, list(parametrosFuncion)[:cantidadPosicionales])
            vistaNominales : ItemsView[str,_T] = nominales.items()

            if (len(parametrosFuncion) == 0 or not tieneVariables(parametrosFuncion))and len(parametrosFuncion) != (len(posicionales) + len(nominales)): continue             

            if validarMultiples(parametrosFuncion,cantidadPosicionales,iteradorPosicionales,vistaNominales):
                return funcion(*posicionales,**nominales)
            else:
                continue
        else:
            raise TypeError(f"[ERROR] No existen sobrecargas de {funcion.__name__} para los parámetros provistos:\n {[type(posicional) for posicional in posicionales]} {[type(nominal) for nominal in nominales.values()]}\n Sobrecargas soportadas: {[dict(fir.parameters) for fir in self.sobrecargas.keys()]}")
    
    def __get__(self, obj, tipoObj) -> 'MetodoSobrecargado':
        class MetodoSobrecargado:
            __call__ = partial(self.__call__, obj) if obj is not None else partial(self.__call__, tipoObj)
        return MetodoSobrecargado()

    @staticmethod
    def desenvolver(funcion : Callable) -> tuple[Signature, Callable]:
        while hasattr(funcion, '__func__'):
            funcion = funcion.__func__
        while hasattr(funcion, '__wrapped__'):
            funcion = funcion.__wrapped__

        firma : Signature = signature(funcion)
        return (firma,funcion)

    @staticmethod
    def nombreCompleto(funcion : Callable) -> str :
        return f"{funcion.__module__}.{funcion.__qualname__}"

    @staticmethod
    def esMetodo(funcion : Callable) -> bool :
        return funcion.__name__ != funcion.__qualname__ and "<locals>" not in funcion.__qualname__.split(".")

    @staticmethod
    def esAnidada(funcion : Callable) -> bool:
        return funcion.__name__ != funcion.__qualname__ and "<locals>" in funcion.__qualname__.split(".")

    @staticmethod
    def devolverClase(metodo : Callable) -> type:
        return getattr(modules[metodo.__module__],metodo.__qualname__.split(".")[0])

    @staticmethod
    def tieneVariables(parametrosFuncion : OrderedDict[str,Parameter]) -> bool:
        for parametro in parametrosFuncion.values():
            if parametro.kind == Parameter.VAR_POSITIONAL or parametro.kind == Parameter.VAR_KEYWORD: return True
        return False 

overload = sobrecargar


if __name__ == '__main__': print(__doc__)

"""
Licencia MIT

Derechos de autor (c) 2023 Hernán A. Teszkiewicz Novick

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
de este software y los archivos de documentación asociados (el "Software"), para tratar
el Software sin restricción, incluyendo, sin limitación, los derechos
para usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y / o vender
copias del Software, y para permitir a las personas a quienes se les proporcione el Software
hacerlo, sujeto a las siguientes condiciones:

El aviso de derechos de autor anterior y este aviso de permiso se incluirán en todos
las copias o partes sustanciales del Software.

EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O
IMPLÍCITO, INCLUYENDO, PERO NO LIMITADO A, LAS GARANTÍAS DE COMERCIABILIDAD,
ADECUACIÓN PARA UN PROPÓSITO PARTICULAR Y NO INFRACCIÓN. EN NINGÚN CASO
LOS TITULARES DE LOS DERECHOS DE AUTOR O LOS AUTORES SERÁN RESPONSABLES DE
NINGUNA RECLAMACIÓN, DAÑOS U OTRAS RESPONSABILIDADES, YA SEA EN UNA ACCIÓN DE
CONTRATO, AGRAVIO O DE OTRO MODO, DERIVADAS DE, FUERA DE O EN CONEXIÓN CON EL
SOFTWARE O EL USO U OTROS ACUERDOS EN EL SOFTWARE.
"""