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
__version__ = "4.0.0"
__email__ = "herni@cajadeideas.ar"

__all__ = ['sobrecargar', 'overload']

from inspect import signature as obtenerfirma, Signature as Firma, Parameter as Parámetro, currentframe as marcoActual, getframeinfo as obtenerInfoMarco, isclass as esClase
from types import MappingProxyType
from typing import Callable as Llamable, TypeVar as TipoVariable, Iterator as Iterador, ItemsView as VistaElementos, Any as Cualquiera, List as Lista, Tuple as Tupla, Iterable, Generic as Genérico, Optional as Opcional, Unpack as Desempacar, Union, get_origin as obtenerOrigen, get_args as obtenerArgumentos, Literal
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
    Clase que actúa como decorador de funciones, permitiendo definir múltiples
    versiones de una función o método con diferentes conjuntos de parámetros y tipos.
    Esto permite crear una sobrecarga de funciones (i.e., despachado dinámico según los argumentos provistos).

    Atributos de Clase:
        _sobrecargadas (dict): Un diccionario que mantiene un registro de las instancias
        de '_sobrecargar' creadas para cada función o método decorado. Las claves son los
        nombres de las funciones o métodos, y los valores son las instancias de '_sobrecargar'.

    Atributos de Instancia:
        sobrecargas (dict): Un diccionario que almacena las sobrecargas definidas para
        la función o método decorado. Las claves son objetos Firma que representan
        las firmas de las sobrecargas, y los valores son las funciones o métodos
        correspondientes.

        __cache (dict): diccionario que asocia tipos de parametros en la llamada con el 
        objeto subyacente de la función a llamar. optimización inocente que reduce el
        costo asociado con llamadas subsiguientes. Muy útil para bucles.  

        __debug (Llamable): lambda que imprime información de diagnóstico si la sobrecarga
        se inicializó en modo debug, de lo contrario no hace nada. 
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

    def __init__(self,función : Llamable,*, cache : bool = True, debug : bool = False) -> None:
        """
        Inicializador. Se encarga de inicializar el diccionario
        de sobrecargas (si no hay ya uno) y registrar en él la versión actual de la función o método decorado.

        Args:
            función (Llamable): La función o método decorado.
            cache (bool): Opción que indica si la sobrecarga debe almacenar un caché.
            debug (bool): Opción que indica si la sobrecarga debe inicializarse en modo debug.
        """

        if not hasattr(self,'sobrecargas'):
            self.sobrecargas : dict[Firma, Llamable] = {}
        if not hasattr(self,'_sobrecargar__nombre') or not hasattr(self,'_sobrecargar__nombre_completo'):
            self.__nombre_completo = self.__nombreCompleto(función)
            self.__nombre = función.__name__

        self.__cache : Opcional[dict[tuple[tuple[type[Cualquiera], ...], tuple[tuple[str, type[Cualquiera]], ...]], Llamable[..., Cualquiera]]] = self.__cache if hasattr(self,"_sobrecargar__cache") and self.__cache is not None else {} if cache else None
        self.__debug : Llamable[[str], None] | Llamable[[str], Llamable[[Cualquiera], None] | None] = self.__debug if hasattr(self,"_sobrecargar__debug") and self.__debug is not None else lambda msj: print(f"[DEBUG] {msj}") if debug else lambda msj: None

        firma : Firma
        funcionSubyacente : Llamable
        firma, funcionSubyacente = _sobrecargar.__desenvolver(función)
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
                        if hasattr(sobrecargaBase,'__inicializar__'): getattr(sobrecargaBase,'__inicializar__')()
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

        Si la sobrecarga se inicializó con la opción `cache`, 

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
                func = self.__cache[parametros]
                self.__debug(
                        f"Llamada en caché para {self.__nombre}"
                        f"\n\tParámetros provistos:"
                        f"\n\t- Posicionales: {', '.join(f"{type(p).__name__} [{repr(p)}]" for p in posicionales)}"
                        f"\n\t- Nominales: {', '.join(f'{k}: {type(v).__name__}  [{v}]' for k, v in nominales.items())}"
                        f"\n\tFirma en caché: {obtenerfirma(func)}"
                    )

                return func(*posicionales,**nominales)
            
        
        self.__debug(
                f"Inicia selección de candidatos para {self.__nombre}"
                f"\n\tParámetros provistos:"
                f"\n\t- Posicionales: {', '.join(f"{type(p).__name__} [{repr(p)}]" for p in posicionales)}"
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

        def validarContenedor(valor: _C, parametroContenedor: Parámetro) -> int | bool:
            tipoEsperado = parametroContenedor.annotation

            if not _sobrecargar.__verificarTipoCompuesto(valor, tipoEsperado):
                return False

            # Si pasó la validación, podemos puntuar según la precisión
            tipo_base, tipo_param = _sobrecargar.__desenvolverTipoCompuesto(tipoEsperado)
            
            if tipo_param is None:
                return 2  # solo se validó el contenedor, sin tipo interno

            elementos = list(valor) if isinstance(valor, Iterable) else []
            if not elementos:
                return 2  # sin elementos, no se puede evaluar más

            if isinstance(valor, dict):
                claves = list(valor.keys())
                valores = list(valor.values())
                tipo_clave, tipo_valor = tipo_param
                puntaje = sum(2 if type(k) == tipo_clave else 1 for k in claves if isinstance(k, tipo_clave)) + \
                        sum(2 if type(v) == tipo_valor else 1 for v in valores if isinstance(v, tipo_valor))
                return puntaje if puntaje > 0 else False

            tipos_esperados = tipo_param if isinstance(tipo_param, tuple) else (tipo_param,)
            if isinstance(valor, tuple) and len(tipos_esperados) == len(valor):
                puntaje = 0
                for val, tipo_esp in zip(valor, tipos_esperados):
                    if type(val) == tipo_esp:
                        puntaje += 2
                    elif isinstance(val, tipo_esp):
                        puntaje += 1
                    else:
                        return False
                return puntaje

            # Para listas, sets, etc.
            tipo_dominante = tipos_esperados[0]
            puntaje = 0
            for val in elementos:
                if type(val) == tipo_dominante:
                    puntaje += 2
                elif isinstance(val, tipo_dominante):
                    puntaje += 1
                else:
                    return False

            return puntaje if puntaje > 0 else False

        def validarTipoParametro(valor: _T, parametroFuncion: Parámetro) -> int | bool:
            puntajeTipo: int = 0

            tipoEsperado = parametroFuncion.annotation
            tipoRecibido = type(valor)

            esNoTipado = (tipoEsperado == Cualquiera) or tipoEsperado == parametroFuncion.empty
            porDefecto = parametroFuncion.default
            esNulo = valor is None and porDefecto is None
            esPorDefecto = valor is None and porDefecto is not parametroFuncion.empty
            paramEsSelf = parametroFuncion.name in {"self", "cls"}
            paramEsVarPos = parametroFuncion.kind == parametroFuncion.VAR_POSITIONAL
            paramEsVarNom = parametroFuncion.kind == parametroFuncion.VAR_KEYWORD

            numericoCompatible = (
                esClase(tipoEsperado)
                and (
                    issubclass(tipoEsperado, complex) and issubclass(tipoRecibido, (float, int))
                    or issubclass(tipoEsperado, float) and issubclass(tipoRecibido, int)
                )
            )

            if paramEsVarPos and obtenerOrigen(tipoEsperado) is Desempacar:
                tipoEsperadoInterno = obtenerArgumentos(tipoEsperado)[0]
                if not all(_sobrecargar.__verificarTipoCompuesto(arg, tipoEsperadoInterno) for arg in valor):
                    return False
                puntajeTipo += 4
                return puntajeTipo + len(valor)  # más largo, más específico
            elif paramEsVarPos and obtenerOrigen(tipoEsperado) in (Tupla,tuple) :
                tipoEsperado = tipoEsperado
                if _sobrecargar.__verificarTipoCompuesto(valor, tipoEsperado):
                    puntajeTipo+=1
            elif paramEsVarPos:
                
                tipoEsperado = Tupla[tipoEsperado]
                if _sobrecargar.__verificarTipoCompuesto(valor, tipoEsperado):
                    puntajeTipo+=1

            if paramEsVarNom and obtenerOrigen(tipoEsperado) is Desempacar:

                tipoEsperadoDict = obtenerArgumentos(tipoEsperado)[0]
                if not isinstance(valor, dict):
                    return False

                for k, v in valor.items():
                    if not _sobrecargar.__verificarTipoCompuesto(k, str) or \
                    not _sobrecargar.__verificarTipoCompuesto(v, tipoEsperadoDict[str]):
                        return False
                puntajeTipo += 4
                return puntajeTipo + len(valor)
            elif paramEsVarNom and parametroFuncion.annotation is parametroFuncion.empty:
                puntajeTipo+=1
                
            esDistintoTipo = not (
                _sobrecargar.__verificarTipoCompuesto(valor, tipoEsperado)
                or numericoCompatible
            )
            if not esNoTipado and not esNulo and not paramEsSelf and not esPorDefecto and esDistintoTipo:
                return False

            if _sobrecargar.__verificarTipoCompuesto(valor, tipoEsperado):
                puntajeTipo += 10
                if type(valor) == tipoEsperado:
                    puntajeTipo += 5
            elif numericoCompatible:
                puntajeTipo += 3
            elif esPorDefecto:
                puntajeTipo += 2
            elif esNulo or paramEsSelf or esNoTipado:
                puntajeTipo += 1
            else:
                return False

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
            iteradorPosicionales : Iterador[tuple[Cualquiera,str]] = _sobrecargar.__armarIteradorPosicionales(posicionales, parametrosFuncion)
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
            self.__debug(                
                f"\tParámetros provistos" 
                f"\n\t- Posicionales: {', '.join(p.__name__ for p in map(type, posicionales))}"
                f"\n\t- Nominales: {', '.join(f'{k}: {type(v).__name__}' for k, v in nominales.items())}"
                f"\n\tCandidatos: \n\t- {"\n\t- ".join(' | '.join([str(i) for i in c if not callable(i)]) for c in candidatos)}"
            )
            mejorFuncion = candidatos[0].objetoFuncion
            if self.__cache is not None:
                parametros = (
                    tuple(type(p) for p in posicionales), 
                    tuple((n, type(v)) for n, v in nominales.items()),
                )
                self.__cache.update({
                    parametros : mejorFuncion
                })
            return mejorFuncion(*posicionales,**nominales)
        else:
            marco_actual = marcoActual()
            archivo = __file__
            linea = 425
            if marco_actual:
                marco_llamada = marco_actual.f_back if marco_actual.f_back else marco_actual
                info_llamada = obtenerInfoMarco(marco_llamada)
                if info_llamada.code_context and "return self.__call__(*posicionales,**nominales)" in info_llamada.code_context and info_llamada.function == "__call__":
                    marco_llamada = marco_llamada.f_back if marco_llamada.f_back else marco_llamada
                    info_llamada = obtenerInfoMarco(marco_llamada) 
                
                archivo = info_llamada.filename
                linea = info_llamada.lineno
            raise TypeError(
                f"[ERROR] No se pudo llamar a {función.__name__} en {rutaAbsoluta(archivo)}:{linea} " 
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

    @staticmethod
    def __desenvolverTipoCompuesto(tipoAnotado: Cualquiera) -> Tupla[Union[type, Tupla[type, ...]], Union[None, type, Tupla[type, ...]]]:
        """
        Desenvuelve un tipo anotado en una tupla:
        (tipo_base, tipo_parametrico)

        - tipo_base: puede ser un tipo o una tupla de tipos (ej. Union)
        - tipo_parametrico: tipos internos del contenedor si aplica, o None
        """
        origen = obtenerOrigen(tipoAnotado)
        args = obtenerArgumentos(tipoAnotado)

        if origen is Literal:
            return Literal, args

        if origen is Union:
            tipos_base = []
            tipos_param = []
            for arg in args:
                base, param = _sobrecargar.__desenvolverTipoCompuesto(arg)
                if isinstance(base, tuple):
                    tipos_base.extend(base)
                else:
                    tipos_base.append(base)
                if param is not None:
                    if isinstance(param, tuple):
                        tipos_param.extend(param)
                    else:
                        tipos_param.append(param)
            return tuple(set(tipos_base)), tuple(set(tipos_param)) if tipos_param else None

        elif origen is not None:
            tipo_param = args
            if len(tipo_param) == 1:
                tipo_param = tipo_param[0]
            return origen, tipo_param if isinstance(tipo_param, tuple) else (tipo_param,)

        elif isinstance(tipoAnotado, type):
            return tipoAnotado, None

        return object, None

    @staticmethod
    def __verificarTipoCompuesto(valor: Cualquiera, tipo: Cualquiera) -> bool:
        """
        Verifica si un valor coincide con un tipo, incluyendo contenedores y tipos anidados.
        """
        origen = obtenerOrigen(tipo)
        args = obtenerArgumentos(tipo)

        if tipo is Cualquiera:
            return True
        if origen is None or isinstance(tipo, type):
            return isinstance(valor, tipo)

        if origen is Literal:
            return valor in args


        if origen is Union:
            return any(_sobrecargar.__verificarTipoCompuesto(valor, sub) for sub in args)

        if origen is tuple:
            if not isinstance(valor, tuple):
                return False
            if len(args) == 1 or len(args) == 2 and args[1] is Ellipsis:
                # Tupla[T] o Tupla[T, ...] 
                return all(_sobrecargar.__verificarTipoCompuesto(v, args[0]) for v in valor)
            if len(args) != len(valor):
                return False
            return all(_sobrecargar.__verificarTipoCompuesto(v, t) for v, t in zip(valor, args))


        if origen in (list, set, frozenset):
            if not isinstance(valor, origen):
                return False
            [subtipo] = args
            return all(_sobrecargar.__verificarTipoCompuesto(v, subtipo) for v in valor)

        if origen is dict:
            if not isinstance(valor, dict) or len(args) != 2:
                return False
            tipo_clave, tipo_valor = args

            return all(
                _sobrecargar.__verificarTipoCompuesto(k, tipo_clave) and
                _sobrecargar.__verificarTipoCompuesto(v, tipo_valor)
                for k, v in valor.items()
            )

        try:
            return isinstance(valor, tipo)
        except TypeError:
            return False

    @staticmethod
    def __armarIteradorPosicionales(posicionales, parametrosFuncion):
        nombres = list(parametrosFuncion)
        resultado = []
        i = 0
        for nombre in nombres:
            parametro = parametrosFuncion[nombre]
            if parametro.kind == parametro.VAR_POSITIONAL:
                # al llegar a *args, le doy el resto de posicionales
                resultado.append((tuple(posicionales[i:]), nombre))
                break
            if i < len(posicionales):
                resultado.append((posicionales[i], nombre))
                i += 1
            else:
                break
        return iter(resultado)



def sobrecargar(*args, cache : bool = True, debug : bool = False) ->Llamable:
    """Decorador de funciones que las transforma en sobrecargas.  
    **Parametros:** 
        :param typing.Callable f: la función que se desea sobrecargar.
        :param bool cache: indica si se debe almacenar un caché del despacho, pequeña optimización. Por defecto: True.  
        :param bool debug: indica si se debe imprimir información de diagnóstico. Por defecto: False.  
    
    **Retorna:**  
        :param typing.Callable: el decorador.
    ---  
    """

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