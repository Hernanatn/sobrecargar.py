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
__version__ = "1.0"
__email__ = "herni@cajadeideas.ar"

__all__ = ['sobrecargar', 'overload']

from inspect import signature as obtenerfirma, Signature as Firma, Parameter as Parámetro, currentframe as marcoActual, getframeinfo as obtenerInfoMarco
from types import MappingProxyType
from typing import Callable as Llamable, TypeVar as TipoVariable, Iterator as Iterador, ItemsView as VistaElementos, Any as Cualquiera, List as Lista, Tuple as Tupla, Iterable, Generic as Genérico, Optional as Opcional, Unpack as Desempacar, Union, get_origin as obtenerOrigen, get_args as obtenerArgumentos
from collections.abc import Sequence as Sequencia, Mapping as Mapeo
from collections import namedtuple as tuplanominada
from functools import partial as parcial
from sys import modules as módulos, version_info as info_versión
from itertools import zip_longest as zipearmáslargo
from os.path import abspath as rutaAbsoluta

if info_versión < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self
    
if info_versión < (3, 9):
    raise ImportError("Modulo 'sobrecargar' 'overloading' requiere Python 3.9 o superior.")
    
class _SobrecargaDiferida(type):
    """Metaclase que se encarga de inicilizar las sobrecargas de forma diferida, sól oexiste para manejar el caso de sobrecargas a métodos de clase/instancia.
    Al decorar una función/método con @sobrecargar, en vez de crearse una instancia de `sobrecargar`, se crea una instancia de `sobrecargar_Diferida`, la cual 
    se comporta *como si* fuera `sobrecargar` y retiene todo el estado necesario para construir la verdadera isntancia más adelante, recién la primera vez que 
    se llama `()` la función o método sobrecargado se instacia propiamente.
    """
    def __init__(clase, nombre, ancestros, diccionario):
        super().__init__(nombre,ancestros,diccionario)

        class _Diferida(object): 
            def __new__(cls, posicionales, nominales):
                objeto = clase.__new__(clase,*posicionales,*nominales)
                if not hasattr(objeto, "_Diferida__parametros_iniciales") or getattr(objeto, "_Diferida__parametros_iniciales") is None:
                    objeto.__parametros_iniciales = []
                objeto.__parametros_iniciales.append((posicionales,nominales))
                objeto.__class__ = cls
                return objeto

            def __inicializar__(self):
                iniciales = self.__parametros_iniciales
                del self.__dict__['_Diferida__parametros_iniciales']
                super().__setattr__('__class__',clase)
                for posicionales,nominales in iniciales:
                    self.__init__(*posicionales,**nominales)
            def __get__(self, obj, tipoObj):
                self.__inicializar__()
                return self.__get__(obj,tipoObj)
            def __call__(self, *posicionales,**nominales):
                self.__inicializar__()
                return self.__call__(*posicionales,**nominales)
    
        _Diferida.__name__ = f"{clase.__name__}_Diferida"
        _Diferida.__qualname__ = f"{clase.__qualname__}_Diferida"
        clase._Diferida = _Diferida
        
    def __call__(cls, *posicionales, **nominales):    
        return cls._Diferida(posicionales, nominales)
    
    def __instancecheck__(cls, instancia):
        return super().__instancecheck__(instancia) or isinstance(instancia, cls._Diferida)

    def __subclasscheck__(cls, subclase):
        return super().__subclasscheck__(subclase) or (subclase == cls._Diferida)


import __main__

class _sobrecargar(metaclass=_SobrecargaDiferida):
    """
    Clase que actúa como decorador de tipo-función, permitiendo definir múltiples
    versiones de una función o método con diferentes conjuntos de parámetros y tipos.
    Esto permite crear una sobrecarga de funciones similar a la que se encuentra en
    lenguajes de programación estáticamente tipados, como C++.

    Atributos de Clase:
        _sobrecargadas (dict): Un diccionario que mantiene un registro de las instancias
        de '_sobrecargar' creadas para cada función o método decorado. Las claves son los
        nombres de las funciones o métodos, y los valores son las instancias de '_sobrecargar'.

    Atributos de Instancia:
        sobrecargas (dict): Un diccionario que almacena las sobrecargas definidas para
        la función o método decorado. Las claves son objetos Firma que representan
        las firmas de las sobrecargas, y los valores son las funciones o métodos
        correspondientes.
    """
    _sobrecargadas : dict[str, '_sobrecargar'] = {}

    def __new__(cls, función : Llamable, *posicionales,**nominales)-> '_sobrecargar':
        """
        Constructor. Se crea una única instancia por nombre de función.
        Args:
            función (Llamable): La función o método que se va a decorar.
        Returns:
            _sobrecargar: La instancia de la clase '_sobrecargar' asociada al nombre de la función provista.
        """

        nombre : str = cls.__nombreCompleto(función)
        if nombre not in cls._sobrecargadas.keys(): 
            cls._sobrecargadas[nombre] = super().__new__(_sobrecargar)
            cls._sobrecargadas[nombre].__nombre = función.__name__
            cls._sobrecargadas[nombre].__nombre_completo = nombre

        return  cls._sobrecargadas[nombre]

    def __init__(self,función : Llamable,*, cache : bool = False, debug : bool = False) -> None:
        """
        Inicializador. Se encarga de inicializar el diccionario
        de sobrecargas (si no hay ya uno) y registrar en él la versión actual de la función o método decorado.

        Args:
            función (Llamable): La función o método decorado.
        """

        if not hasattr(self,'sobrecargas'):
            self.sobrecargas : dict[Firma, Llamable] = {}

        self.__cache : Opcional[dict[tuple[tuple[type[Cualquiera], ...], tuple[tuple[str, type[Cualquiera]]]], Llamable[..., Cualquiera]]] = self.__cache if hasattr(self,"_sobrecargar__cache") and self.__cache is not None else {} if cache else None
        self.__debug = self.__debug if hasattr(self,"_sobrecargar__debug") and self.__debug is not None else lambda msj: print(f"[DEBUG] {msj}") if debug else lambda msj: None

        firma : Firma
        funcionSubyacente : Llamable
        firma, funcionSubyacente = _sobrecargar.__desenvolver(función)

        self.__debug(f"Sobrecarga registrada para: {self.__nombre}. Firma: {firma}")
        if type(self).__esMetodo(función):
            clase : type = type(self).__devolverClase(función)
            self.__debug(f"{self.__nombre} es un método de {clase}.")
            for ancestro in clase.__mro__:
                for base in ancestro.__bases__:
                    if base is object : break
                    nombreCompletoMetodo : str = f"{base.__module__}.{base.__name__}.{función.__name__}"
                    if nombreCompletoMetodo in type(self)._sobrecargadas.keys():
                        sobrecargaBase : '_sobrecargar' = type(self)._sobrecargadas[nombreCompletoMetodo]
                        self.sobrecargas.update(sobrecargaBase.sobrecargas)

        self.sobrecargas[firma] = funcionSubyacente
        if not self.__doc__: self.__doc__ = ""
        self.__doc__ += f"\n{función.__doc__ or ''}"
            
    def __call__(self,*posicionales, **nominales) -> Cualquiera:
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
            Cualquiera: El resultado de la versión seleccionada de la función o método decorado.

        Raises:
            TypeError: Si no existe una sobrecarga compatible para los parámetros
            proporcionados.
        """

        if self.__cache is not None:
            parametros = (
                tuple(type(p) for p in posicionales), 
                tuple((n, type(v)) for n, v in nominales.items()),
            )
            if parametros in self.__cache.keys():
                func = self.__cache.get(parametros)
                self.__debug(
                        f"Llamada en caché para {self.__nombre}"
                        f"\n\tParámetros provistos:"
                        f"\n\t- Posicionales: {', '.join(f"{type(p).__name__} [{p}]" for p in posicionales)}"
                        f"\n\t- Nominales: {', '.join(f'{k}: {type(v).__name__}  [{v}]' for k, v in nominales.items())}"
                        f"\n\tFirma en caché: {obtenerfirma(func)}"
                    )

                return func(*posicionales,**nominales)
            
        
        self.__debug(
                f"Inicia selección de candidatos para {self.__nombre}"
                f"\n\tParámetros provistos:"
                f"\n\t- Posicionales: {', '.join(f"{type(p).__name__} [{p}]" for p in posicionales)}"
                f"\n\t- Nominales: {', '.join(f'{k}: {type(v).__name__} [{v}]' for k, v in nominales.items())}"
                f"\n\tSobrecargas soportadas:"
                f"\n"+"\n".join(
                    f"\t- {', '.join(f'{v}' for v in dict(fir.parameters).values())}"
                    for fir in self.sobrecargas.keys()
                )
            )

        _C = TipoVariable("_C", bound=Sequencia)
        _T = TipoVariable("_T", bound=Cualquiera)
        Candidato : Tupla = tuplanominada('Candidato',['puntaje','objetoFuncion',"firmaFuncion"])
        candidatos : Lista[Candidato] = []

        def validarContenedor(valor : _C, parametroContenedor : Parámetro) -> int | bool:
            puntajeTipo : int = 0

            anotacionContenedor = parametroContenedor.annotation

            if not hasattr(anotacionContenedor,"__origin__") or not hasattr(anotacionContenedor,"__args__") :
                puntajeTipo += 1
                return puntajeTipo

            if obtenerOrigen(anotacionContenedor) is Union :
                if not issubclass(type(valor),obtenerArgumentos(anotacionContenedor)):
                    return False
            elif not issubclass(type(valor),anotacionContenedor.__origin__): 
                return False
            argumentosContenedor : Tupla[type[_C]] = anotacionContenedor.__args__
            tieneElipsis : bool = Ellipsis in argumentosContenedor
            tieneUnicoTipo : bool = len(argumentosContenedor) == 1 or tieneElipsis

            if tieneElipsis:
                listaAuxiliarContenedor : list = list(argumentosContenedor)
                listaAuxiliarContenedor[1] = listaAuxiliarContenedor[0]
                argumentosContenedor = tuple(listaAuxiliarContenedor)

            iteradorTipos : Iterador
            if tieneUnicoTipo:
                iteradorTipos = zipearmáslargo((type(t) for t in valor),argumentosContenedor,fillvalue=argumentosContenedor[0])
            else:
                iteradorTipos = zipearmáslargo((type(t) for t in valor),argumentosContenedor)

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

        def validarTipoParametro(valor : _T, parametroFuncion : Parámetro) -> int | bool:
            puntajeTipo : int = 0

            tipoEsperado = parametroFuncion.annotation 
            tipoRecibido : type[_T] = type(valor)

            esNoTipado : bool = (tipoEsperado == Cualquiera)
            porDefecto : _T = parametroFuncion.default
            esNulo : bool = valor is None and porDefecto is None

            esPorDefecto : bool = valor is None and porDefecto is not parametroFuncion.empty
            paramEsSelf : bool =  parametroFuncion.name=='self' or parametroFuncion.name=='cls'
            
            paramEsVarPos   : bool = parametroFuncion.kind == parametroFuncion.VAR_POSITIONAL 
            paramEsVarNom   : bool = parametroFuncion.kind == parametroFuncion.VAR_KEYWORD  
            paramEsVariable   : bool = paramEsVarPos or paramEsVarNom
            paramEsUnion : bool = hasattr(tipoEsperado,"__origin__") and obtenerOrigen(tipoEsperado) is Union
            paramEsContenedor : bool = (hasattr(tipoEsperado,"__origin__") or (issubclass(tipoEsperado, Sequencia) and not issubclass(tipoEsperado,str)) or issubclass(tipoEsperado, Mapeo)) and not paramEsUnion

            esDistintoTipo : bool
            if paramEsVariable and paramEsContenedor and paramEsVarPos:
                tipoEsperado = tipoEsperado.__args__[0] if obtenerOrigen(type(tipoEsperado)) is Desempacar else tipoEsperado
                esDistintoTipo = not issubclass(tipoRecibido,tipoEsperado.__args__[0]) 
            elif paramEsVariable and paramEsContenedor and paramEsVarNom:
                tipoEsperado = tipoEsperado.__args__[0] if obtenerOrigen(type(tipoEsperado)) is Desempacar else tipoEsperado
                esDistintoTipo = not issubclass(tipoRecibido,tipoEsperado.__args__[1]) 
            elif paramEsUnion:
                esDistintoTipo = not issubclass(tipoRecibido,obtenerArgumentos(tipoEsperado))
            elif paramEsContenedor:
                esDistintoTipo = not validarContenedor(valor,parametroFuncion)
            else:
                esDistintoTipo = not issubclass(tipoRecibido, tipoEsperado) 
            
            
            if not esNoTipado and not esNulo and not paramEsSelf and not esPorDefecto and esDistintoTipo:
                return False
            elif paramEsVariable and not paramEsContenedor: 
                puntajeTipo += 1
            else:
                if paramEsVariable and paramEsContenedor and paramEsVarPos:
                    if tipoRecibido == tipoEsperado.__args__[0]:
                        puntajeTipo +=2
                    elif issubclass(tipoRecibido,tipoEsperado.__args__[0]):
                        puntajeTipo +=1  
                elif paramEsVariable and paramEsContenedor and paramEsVarNom:
                    if tipoRecibido == tipoEsperado.__args__[1]:
                        puntajeTipo +=2
                    elif issubclass(tipoRecibido,tipoEsperado.__args__[1]):
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

        def validarFirma(parametrosFuncion : MappingProxyType[str,Parámetro], cantidadPosicionales : int, iteradorPosicionales : Iterador[tuple], vistaNominales : VistaElementos) -> int |bool:
            puntajeFirma : int = 0

            estePuntaje : int | bool
            for valorPosicional, nombrePosicional in iteradorPosicionales:
                estePuntaje = validarTipoParametro(valorPosicional,parametrosFuncion[nombrePosicional])
                if estePuntaje:
                    puntajeFirma += estePuntaje 
                else:
                    return False
            
            for nombreNominal, valorNominal in vistaNominales:
                if nombreNominal not in parametrosFuncion and type(self).__tieneVarNom(parametrosFuncion):
                    varNom : Parámetro | None = next((p for p in parametrosFuncion.values() if p.kind == p.VAR_KEYWORD),None)
                    if varNom is not None:
                        estePuntaje = validarTipoParametro(valorNominal,varNom)
                    else:
                        return False
                elif nombreNominal not in parametrosFuncion:
                        return False
                else:
                    estePuntaje = validarTipoParametro(valorNominal,parametrosFuncion[nombreNominal])
                if estePuntaje:
                    puntajeFirma += estePuntaje 
                else:
                    return False

            
            return puntajeFirma

        for firma, función in self.sobrecargas.items():

            puntajeLongitud : int = 0
            
            parametrosFuncion : MappingProxyType[str,Parámetro] = firma.parameters
            
            cantidadPosicionales    : int = len(parametrosFuncion) if type(self).__tieneVarPos(parametrosFuncion) else len(posicionales) 
            cantidadNominales       : int = len({nom : nominales[nom] for nom in parametrosFuncion if nom in nominales}) if (type(self).__tieneVarNom(parametrosFuncion) or type(self).__tieneSoloNom(parametrosFuncion)) else len(nominales)
            cantidadPorDefecto      : int = type(self).__tienePorDefecto(parametrosFuncion) if type(self).__tienePorDefecto(parametrosFuncion) else 0
            iteradorPosicionales : Iterador[tuple[Cualquiera,str]] = zip(posicionales, list(parametrosFuncion)[:cantidadPosicionales]) 
            vistaNominales : VistaElementos[str,Cualquiera] = nominales.items()
            
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
                esteCandidato : Candidato = Candidato(puntaje=(puntajeLongitud+2*puntajeValidacionFirma),objetoFuncion=función,firmaFuncion=firma)
                candidatos.append(esteCandidato)
            else:
                continue
        if candidatos:
            if len(candidatos)>1:
                candidatos.sort(key= lambda c: c.puntaje, reverse=True)
            self.__debug(f"Candidatos: \n\t- {"\n\t- ".join(' | '.join([str(i) for i in c if not callable(i)]) for c in candidatos)}")
            mejorFuncion = candidatos[0].objetoFuncion
            if self.__cache is not None:
                parametros = (
                    tuple(type(p) for p in posicionales),
                    tuple(tuple(n, type(v)) for n, v in nominales.items()),
                )
                self.__cache.update({
                    parametros : mejorFuncion
                })
            return mejorFuncion(*posicionales,**nominales)
        else:
            marco_llamada = marcoActual().f_back
            info_llamada = obtenerInfoMarco(marco_llamada)
            if "return self.__call__(*posicionales,**nominales)" in info_llamada.code_context and info_llamada.function == "__call__":
                info_llamada = marco_llamada.f_back
            raise TypeError(
                f"[ERROR] No se pudo llamar a {función.__name__} en {rutaAbsoluta(info_llamada.filename)}:{info_llamada.lineno} " 
                f"\n\tParámetros provistos" 
                f"\n\t- Posicionales: {', '.join(p.__name__ for p in map(type, posicionales))}"
                f"\n\t- Nominales: {', '.join(f'{k}: {type(v).__name__}' for k, v in nominales.items())}"
                f"\n"
                f"\n\tSobrecargas soportadas:\n"
                +"\n".join(
                    f"\t- {', '.join(f'{v}' for v in dict(fir.parameters).values())}"
                    for fir in self.sobrecargas.keys()
                )
            )
    
    def __get__(self, obj, tipoObj):
        class MetodoSobrecargado:
            __doc__ = self.__doc__
            __call__ = parcial(self.__call__, obj) if obj is not None else parcial(self.__call__, tipoObj)

        return MetodoSobrecargado()







    @staticmethod
    def __desenvolver(función : Llamable) -> tuple[Firma, Llamable]:
        while hasattr(función, '__func__'):
            función = función.__func__
        while hasattr(función, '__wrapped__'):
            función = función.__wrapped__

        firma : Firma = obtenerfirma(función)
        return (firma,función)

    @staticmethod
    def __nombreCompleto(función : Llamable) -> str :
        return f"{función.__module__}.{función.__qualname__}"

    @staticmethod
    def __esMetodo(función : Llamable) -> bool :
        return función.__name__ != función.__qualname__ and "<locals>" not in función.__qualname__.split(".")

    @staticmethod
    def __esAnidada(función : Llamable) -> bool:
        return función.__name__ != función.__qualname__ and "<locals>" in función.__qualname__.split(".")

    @staticmethod
    def __devolverClase(metodo : Llamable) -> type:
        import __main__
        return getattr(módulos[metodo.__module__],metodo.__qualname__.split(".")[0])


    @staticmethod
    def __tieneVariables(parametrosFuncion : MappingProxyType[str,Parámetro]) -> bool:
        for parametro in parametrosFuncion.values():
            if _sobrecargar.__tieneVarNom(parametrosFuncion) or _sobrecargar.__tieneVarPos(parametrosFuncion): return True
        return False

    @staticmethod
    def __tieneVarPos(parametrosFuncion : MappingProxyType[str,Parámetro]) -> bool:
        for parametro in parametrosFuncion.values():
            if parametro.kind == Parámetro.VAR_POSITIONAL: return True
        return False

    @staticmethod
    def __tieneVarNom(parametrosFuncion : MappingProxyType[str,Parámetro]) -> bool:
        for parametro in parametrosFuncion.values():
            if parametro.kind == Parámetro.VAR_KEYWORD: return True
        return False

    @staticmethod
    def __tienePorDefecto(parametrosFuncion : MappingProxyType[str,Parámetro]) -> int | bool:
        cuentaDefecto : int = 0
        for parametro in parametrosFuncion.values():
            if parametro.default != parametro.empty: cuentaDefecto+=1
        return cuentaDefecto if cuentaDefecto else False 
    
    @staticmethod
    def __tieneSoloNom(parametrosFuncion : MappingProxyType[str,Parámetro]) -> bool:
        for parametro in parametrosFuncion.values():
            if parametro.kind == Parámetro.KEYWORD_ONLY: return True
        return False


def sobrecargar(*args, cache : bool = False, debug : bool = False):
    if args and callable(args[0]):
        return _sobrecargar(args[0],cache=cache,debug=debug)
    def decorador(f):
        if debug:
            info_llamada = obtenerInfoMarco( marcoActual().f_back)
            print(
                f"[DEBUG] Sobrecarga de función."
                f"\n\t{f.__name__} en {rutaAbsoluta(info_llamada.filename)}:{info_llamada.lineno}"
                f"\n\t- {cache = }"
                f"\n\t- {debug = }"
            )
        return _sobrecargar(f,cache=cache,debug=debug)
    return decorador
overload = sobrecargar


if __name__ == '__main__': 
    print(__doc__)    
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