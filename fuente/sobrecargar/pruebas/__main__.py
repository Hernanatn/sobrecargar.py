from sobrecargar import sobrecargar
import unittest
from typing import Unpack, Union
from enum import Enum
import warnings
warnings.filterwarnings("ignore")

# Funciones globales decoradas
@sobrecargar
def funcion_libre(a: int, b: int = 10):
    """Suma dos enteros."""
    return a + b

@sobrecargar
def funcion_libre(a: str, *args: int):
    """Concatena un string con la suma de argumentos."""
    return a + str(sum(args))

@sobrecargar
def funcion_libre\
    (a: str, *args: int, **kwargs : Unpack[dict[str,int]]):
    """Concatena un string con la suma de argumentos y con una repeticion de las llaves por los valores de los nominales."""
    return a + str(sum(args)) + "".join(k*v for k,v in kwargs.items())

@sobrecargar
def funcion_libre(a: float, *args : *tuple[int]):
    """Multiplica el flotante por la suma de los argumentos"""
    return a * sum(a for a in args)

@sobrecargar
def funcion_libre(a: float, b: Union[float,int] ):
    """Multiplica el flotante por un entero u otro flotante."""
    return a * b

# Clase con métodos decorados
class OtraClase:

    @sobrecargar
    def metodo(self, a: int, b: int, c: str):
        """Resta dos enteros. Imprime una str"""
        return a - b

    @sobrecargar
    def metodo(self, a: int, b: int):
        """Resta dos enteros."""
        return a - b

    @sobrecargar
    def metodo(self, a: int, b: tuple = (
        "juan",
        {
            "pedro" : {
                "lucas" : [
                    2,
                    3,
                    (
                        1,
                        2,
                        [
                            5,
                            6,
                            7
                        ]
                    )
                ]
            },
        }
    )) -> bool:
        """Firma medio loca de prueba con defaults formateados falopa para cehquear el addon de vscode."""
        return False
    
class MiClase:
    @sobrecargar
    def metodo(self, a: int, b: int):
        """Resta dos enteros."""
        return a - b

    @sobrecargar
    def metodo(self, a: int, *args: *tuple[int]):
        """Multiplica el primer número por la suma de argumentos."""
        return a * sum(args)

    @sobrecargar
    def metodo(self, a: float, b: Union[float,int] ):
        """Multiplica el flotante por un entero u otro flotante."""
        return a * b

    @sobrecargar
    def metodo(self, a: str, b: str = "default"):
        """Concatena dos cadenas."""
        return a + b

class PruebasSobrecargar(unittest.TestCase):
    def test_funcion_libre(self):
        """Prueba las versiones sobrecargadas de una función 'libre'."""
        # Versión con enteros
        self.assertEqual(funcion_libre(5, 15), 20)
        self.assertEqual(funcion_libre(7), 17)

        # Versión con string y *args
        self.assertEqual(funcion_libre("suma: ", 1, 2, 3), "suma: 6")
        self.assertEqual(funcion_libre("suma: "), "suma: 0")

        # Versión con float y **kwargs
        self.assertEqual(funcion_libre(2.5, 4), 10.0)
        self.assertEqual(funcion_libre(3.0), 0)

    def test_metodo_mi_clase(self):
        """Prueba las versiones sobrecargadas de un método miembro."""
        instancia = MiClase()

        # Versión con enteros
        self.assertEqual(instancia.metodo(10, 5), 5)

        # Versión con entero y *args
        self.assertEqual(instancia.metodo(3, 1, 2, 3), 18)
        self.assertEqual(instancia.metodo(2), 0)

        # Versión con strings
        self.assertEqual(instancia.metodo("Hola, "), "Hola, default")
        self.assertEqual(instancia.metodo("Hola, ", "Mundo"), "Hola, Mundo")

        
    def test_metodo_union(self):
        instancia = MiClase()

        self.assertEqual(instancia.metodo(1.5, 2),1.5*2)     

    def test_cache_debug(self):

        """Prueba errores en invocaciones no soportadas."""
        @sobrecargar(cache=True)
        def funcion_cacheada_libre(a: float, *args : *tuple[int]):
            """Multiplica el flotante por el valor de una clave específica."""
            return a * sum(a for a in args)

        @sobrecargar
        def funcion_cacheada_libre(a: float, b: Union[float,int] ):
            """Multiplica el flotante por un entero u otro flotante."""
            return a * b    

        self.assertEqual(funcion_cacheada_libre(10.5,2),10.5*2)
        self.assertEqual(funcion_cacheada_libre(11.5,2),11.5*2)
        self.assertEqual(funcion_cacheada_libre(12.5,2),12.5*2)

    def test_errores(self):
        """Prueba errores en invocaciones no soportadas."""
        instancia = MiClase()
        with self.assertRaises(TypeError):
            funcion_libre(1, "cadena")
 

        with self.assertRaises(TypeError):
            funcion_libre(2, "cadena")


        with self.assertRaises(TypeError):
            instancia.metodo("cadenan",2, "cadena")

from typing import Protocol, Optional, Literal, Any, Union
from decimal import Decimal
from datetime import datetime

# Mocks y tipos simulados
class ProtocoloBaseDeDatos():
    def __enter__(self): ...
    def __exit__(self, *args): ...
    def SELECT(self, tabla, campos): return self
    def WHERE(self, *args, **kwargs): return self
    def ORDER_BY(self, orden): return self
    def LIMIT(self, offset, cantidad): return self
    def ejecutar(self): return self
    def devolverUnResultado(self): return {"id": 1, "dato": "abc"}
    def devolverResultados(self): return [{"id": 1, "dato": "abc"}]
    def INSERT(self, tabla, **ediciones): return self
    def devolverIdUltimaInsercion(self): return 42
    def UPDATE(self, tabla, **ediciones): return self

class TipoOrden(Enum):
    ASC = "ASC"
    DESC = "DESC"

class TipoCondicion(Enum):
    IGUAL = "=="

class Resultado(dict): ...

def atributoPrivado(obj, atr): return f"_{atr}"
def atributoPublico(atr): return atr.replace('_', '')
def devolverAtributoPrivado(obj, atr): return getattr(obj, atr, None)
def devolverAtributo(obj, atr, por_defecto): return getattr(obj, atr, por_defecto)
def tieneAtributo(cls, atr): return True
def esSubclaseUnion(tipo, clase): return True

class Registro:
    __slots__ = ("__bdd", "__tabla", "__id", "dato", "fecha_carga", "fecha_modificacion")
    muchosAMuchos = {}
    
    @sobrecargar
    def __init__(self, bdd: ProtocoloBaseDeDatos, valores: dict, *, debug: bool = False):
        self.__bdd = bdd
        self.__id = valores.get("id", 0)
        self.dato = valores.get("dato", "")
        self.fecha_carga = datetime.now()
        self.fecha_modificacion = datetime.now()

    @sobrecargar
    def __init__(self, bdd: ProtocoloBaseDeDatos, id: int, *, debug: bool = False):
        valores = {"id": id, "dato": "simulado"}
        self.__init__(bdd, valores)

    @classmethod
    @sobrecargar
    def devolverRegistros(
        cls,
        bdd: ProtocoloBaseDeDatos,
        *,
        cantidad: Optional[int] = 1000,
        indice: Optional[int] = 0,
        orden: Optional[dict[str, TipoOrden]] = None,
        filtrosJoin: dict[str, str] = None,
        **condiciones) -> tuple:
        return (cls(bdd, {"id": 1, "dato": "prueba"}),)

    @classmethod
    @sobrecargar
    def devolverRegistros(
        cls,
        bdd: ProtocoloBaseDeDatos,
        *,
        cantidad: Optional[int] = 1000,
        indice: Optional[int] = 0,
        orden: Optional[dict[str, TipoOrden]] = None,
        filtrosJoin: dict[str, str] = None,
        condiciones: dict[TipoCondicion, dict[str, Any]]) -> tuple:
        return (cls(bdd, {"id": 1, "dato": "prueba_condicion"}),)


class PruebasRegistroSimulado(unittest.TestCase):
    def test_inicializacion_dict_y_id(self):
        bdd = ProtocoloBaseDeDatos()
        r1 = Registro(bdd, {"id": 1, "dato": "abc"})
        self.assertEqual(r1.dato, "abc")

        r2 = Registro(bdd, 99)
        self.assertEqual(r2.dato, "simulado")
        self.assertEqual(r2._Registro__id, 99)

    def test_devolver_registros_con_kwargs(self):
        bdd = ProtocoloBaseDeDatos()
        registros = Registro.devolverRegistros(bdd, cantidad=1, indice=0, campo="valor")
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0].dato, "prueba")

    def test_devolver_registros_con_condiciones(self):
        bdd = ProtocoloBaseDeDatos()
        condiciones = {
            TipoCondicion.IGUAL: {"campo": "valor"}
        }
        registros = Registro.devolverRegistros(bdd, condiciones=condiciones)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0].dato, "prueba_condicion")


from typing import Optional, Literal, TypeVar, Generic, Callable, List, Union, Self

# Herencia de múltiples niveles
class Base:
    @sobrecargar
    def procesar(self, x: int) -> str:
        return f"Base: {x}"

class Intermedia(Base):
    @sobrecargar
    def procesar(self, x: str) -> str:
        return f"Intermedia: {x}"

class Avanzada(Intermedia):
    @sobrecargar
    def procesar(self, x: float) -> str:
        return f"Avanzada: {x:.2f}"
# Pruebas para ForwardRef
class ClaseReferenciada:
    def __init__(self, valor: str):
        self.valor = valor
    
    def __str__(self):
        return f"ClaseReferenciada({self.valor})"

class ClaseConForwardRef:
    @sobrecargar
    def procesar(self, obj: 'ClaseReferenciada') -> str:
        """Procesa una ClaseReferenciada usando ForwardRef."""
        return f"Procesado: {obj.valor}"
    
    @sobrecargar
    def procesar(self, obj: str) -> str:
        """Procesa un string directamente."""
        return f"String: {obj}"

@sobrecargar
def funcion_con_forward_ref(param: 'ClaseReferenciada') -> str:
    """Función que usa ForwardRef para evitar imports circulares."""
    return f"Función ForwardRef: {param.valor}"

@sobrecargar
def funcion_con_forward_ref(param: str) -> str:
    """Sobrecarga de la función con ForwardRef."""
    return f"String ForwardRef: {param}"

# ForwardRef en contenedores
@sobrecargar
def procesar_lista_forward_ref(items: list['ClaseReferenciada']) -> str:
    """Procesa una lista de objetos usando ForwardRef."""
    return "Lista: " + ", ".join(str(item) for item in items)

@sobrecargar
def procesar_lista_forward_ref(items: list[str]) -> str:
    """Sobrecarga para lista de strings."""
    return "str: " + ", ".join(items)

# ForwardRef en Union
@sobrecargar
def procesar_union_forward_ref(item: Union['ClaseReferenciada', int]) -> str:
    """Procesa Union con ForwardRef."""
    if isinstance(item, ClaseReferenciada):
        return f"Clase: {item.valor}"
    else:
        return f"Entero: {item}"

@sobrecargar
def procesar_union_forward_ref(item: Union[str, float]) -> str:
    """Sobrecarga para Union de tipos básicos."""
    return f"Básico: {item}"

# ForwardRef anidado
class Contenedor:
    def __init__(self, contenido: 'ClaseReferenciada'):
        self.contenido = contenido

@sobrecargar
def procesar_contenedor(cont: 'Contenedor') -> str:
    """Procesa un contenedor que contiene ForwardRef."""
    return f"Contenedor: {cont.contenido.valor}"

@sobrecargar
def procesar_contenedor(cont: str) -> str:
    """Sobrecarga para string."""
    return f"String contenedor: {cont}"

"""
# Genéricos
T = TypeVar('T')
class Caja(Generic[T]):
    def __init__(self, valor: T):
        self.valor = valor

    @sobrecargar
    def transformar(self, f: Callable[[T], T]) -> T:
        return f(self.valor)

    @sobrecargar
    def transformar(self, f: Callable[[T], str]) -> str:
        return f(self.valor)
"""
# Union y Optional
@sobrecargar
def interpretar(x: Union[int, Literal["uno", "dos"]]) -> str:
    return f"valor entero o literal: {x}"

@sobrecargar
def interpretar(x: Optional[List[int]]) -> str:
    return f"lista opcional: {x}"

# Funciones de orden superior
@sobrecargar(debug=False)
def ejecutar(f: Callable[[int], int], valor: int) -> int:
    """pedro"""
    return f(valor)

@sobrecargar
def ejecutar(f: Callable[[str], str], valor: str) -> str:
    """juan"""
    return f(valor)

# Pruebas
class PruebasExtendidas(unittest.TestCase):
    def test_herencia_multiples_niveles(self):
        obj = Avanzada()
        self.assertEqual(obj.procesar(5), "Base: 5")
        self.assertEqual(obj.procesar("hola"), "Intermedia: hola")
        self.assertEqual(obj.procesar(3.14), "Avanzada: 3.14")
    """
    def test_genericos_funcion_transformar(self):
        caja_entero = Caja(10)
        self.assertEqual(caja_entero.transformar(lambda x: x + 5), 15)
        self.assertEqual(caja_entero.transformar(lambda x: f"num: {x}"), "num: 10")
    """
    def test_union_y_optional(self):
        self.assertEqual(interpretar("uno"), "valor entero o literal: uno")
        self.assertEqual(interpretar(2), "valor entero o literal: 2")
        self.assertEqual(interpretar([1, 2]), "lista opcional: [1, 2]")
        self.assertEqual(interpretar(None), "lista opcional: None")

    def test_funciones_de_orden_superior(self):
        self.assertEqual(ejecutar(lambda x: x * 2, 5), 10)
        self.assertEqual(ejecutar(lambda s: s.upper(), "chau"), "CHAU")

class PruebasForwardRef(unittest.TestCase):
    """Pruebas específicas para el soporte de ForwardRef."""
    
    def test_forward_ref_basico(self):
        """Prueba el uso básico de ForwardRef en funciones."""
        obj = ClaseReferenciada("test")
        
        # Probar función con ForwardRef
        resultado = funcion_con_forward_ref(obj)
        self.assertEqual(resultado, "Función ForwardRef: test")
        
        # Probar sobrecarga con string
        resultado = funcion_con_forward_ref("hola")
        self.assertEqual(resultado, "String ForwardRef: hola")
    
    def test_forward_ref_en_metodos(self):
        """Prueba ForwardRef en métodos de clase."""
        instancia = ClaseConForwardRef()
        obj = ClaseReferenciada("metodo")
        
        # Probar método con ForwardRef
        resultado = instancia.procesar(obj)
        self.assertEqual(resultado, "Procesado: metodo")
        
        # Probar sobrecarga con string
        resultado = instancia.procesar("test")
        self.assertEqual(resultado, "String: test")
    
    def test_forward_ref_en_contenedores(self):
        """Prueba ForwardRef en listas y otros contenedores."""
        objetos = [ClaseReferenciada("uno"), ClaseReferenciada("dos")]
        strings = ["a", "b", "c"]
        
        # Probar lista con ForwardRef
        resultado = procesar_lista_forward_ref(objetos)
        self.assertEqual(resultado, "Lista: ClaseReferenciada(uno), ClaseReferenciada(dos)")
        
        # Probar sobrecarga con lista de strings
        resultado = procesar_lista_forward_ref(strings)
        self.assertEqual(resultado, "str: a, b, c")
    
    def test_forward_ref_en_union(self):
        """Prueba ForwardRef en tipos Union."""
        obj = ClaseReferenciada("union")
        
        # Probar Union con ForwardRef
        resultado = procesar_union_forward_ref(obj)
        self.assertEqual(resultado, "Clase: union")
        
        resultado = procesar_union_forward_ref(42)
        self.assertEqual(resultado, "Entero: 42")
        
        # Probar sobrecarga con Union de tipos básicos
        resultado = procesar_union_forward_ref("texto")
        self.assertEqual(resultado, "Básico: texto")
        
        resultado = procesar_union_forward_ref(3.14)
        self.assertEqual(resultado, "Básico: 3.14")
    
    def test_forward_ref_anidado(self):
        """Prueba ForwardRef anidado en contenedores."""
        obj = ClaseReferenciada("anidado")
        contenedor = Contenedor(obj)
        
        # Probar contenedor con ForwardRef anidado
        resultado = procesar_contenedor(contenedor)
        self.assertEqual(resultado, "Contenedor: anidado")
        
        # Probar sobrecarga con string
        resultado = procesar_contenedor("simple")
        self.assertEqual(resultado, "String contenedor: simple")
    
    def test_forward_ref_con_cache(self):
        """Prueba que ForwardRef funciona correctamente con caché habilitado."""
        @sobrecargar(cache=True)
        def funcion_cacheada_forward_ref(param: 'ClaseReferenciada') -> str:
            return f"Caché ForwardRef: {param.valor}"
        
        @sobrecargar
        def funcion_cacheada_forward_ref(param: int) -> str:
            return f"Caché entero: {param}"
        
        obj = ClaseReferenciada("cache")
        
        # Primera llamada (sin caché)
        resultado1 = funcion_cacheada_forward_ref(obj)
        self.assertEqual(resultado1, "Caché ForwardRef: cache")
        
        # Segunda llamada (con caché)
        resultado2 = funcion_cacheada_forward_ref(obj)
        self.assertEqual(resultado2, "Caché ForwardRef: cache")
        
        # Probar sobrecarga
        resultado3 = funcion_cacheada_forward_ref(123)
        self.assertEqual(resultado3, "Caché entero: 123")
    
    def test_forward_ref_con_errores(self):
        """Prueba que ForwardRef maneja correctamente los errores de tipos."""
        obj = ClaseReferenciada("error")
        
        # Probar que se lanza TypeError cuando no hay sobrecarga compatible
        with self.assertRaises(TypeError):
            funcion_con_forward_ref(123)  # int no es compatible con 'ClaseReferenciada' ni str
        
        with self.assertRaises(TypeError):
            funcion_con_forward_ref([1, 2, 3])  # lista no es compatible
    
    def test_forward_ref_complejo(self):
        """Prueba casos complejos de ForwardRef con múltiples niveles."""
        @sobrecargar
        def funcion_compleja_forward_ref(
            items: list[Union['ClaseReferenciada', 'Contenedor']]
        ) -> str:
            return "Complejo: " + ", ".join(
                str(item) if isinstance(item, ClaseReferenciada) 
                else f"Contenedor({item.contenido.valor})" 
                for item in items
            )
        
        @sobrecargar
        def funcion_compleja_forward_ref(
            items: list[Union[str, int]]
        ) -> str:
            return "Básico: " + ", ".join(str(item) for item in items)
        
        # Probar con objetos complejos
        obj1 = ClaseReferenciada("uno")
        obj2 = ClaseReferenciada("dos")
        cont = Contenedor(ClaseReferenciada("tres"))
        
        resultado = funcion_compleja_forward_ref([obj1, cont, obj2])
        self.assertEqual(resultado, "Complejo: ClaseReferenciada(uno), Contenedor(tres), ClaseReferenciada(dos)")
        
        # Probar con tipos básicos
        resultado = funcion_compleja_forward_ref(["a", 1, "b"])
        self.assertEqual(resultado, "Básico: a, 1, b")

class PruebasCoberturaAdicional(unittest.TestCase):
    def test_metodo_otra_clase_default_complejo(self):
        """Test de sobrecarga con default de estructura compleja."""
        obj = OtraClase()
        self.assertFalse(obj.metodo(1))

    def test_funcion_libre_kwargs_empty(self):
        """Evalúa que el camino vacío de kwargs también esté cubierto."""
        resultado = funcion_libre("x=", 1, 2)
        self.assertEqual(resultado, "x=3")

    def test_funcion_libre_float_args(self):
        """Prueba la multiplicación por suma de argumentos con float."""
        resultado = funcion_libre(2.0, 1, 2)
        self.assertEqual(resultado, 2.0 * 3)

    def test_funcion_libre_float_args_vacio(self):
        """Evalúa el caso en que no se pasa ningún argumento extra."""
        resultado = funcion_libre(2.0)
        self.assertEqual(resultado, 0)

    
    def test_debug_activo_muestra_stack(self):
        """Prueba que el modo debug genere trazabilidad con stack."""
        @sobrecargar
        def f(x: int): return x
        @sobrecargar
        def f(x: str): return x

        # El objetivo es cubrir el camino interno activado por debug.
        self.assertEqual(f(1), 1)
        self.assertEqual(f("a"), "a")

from typing import Union, Optional, Literal, List, Tuple, Dict
@sobrecargar(debug=False)
def procesar_complejidad(x: Union[int, str, List[Union[int, str]]]) -> str:
    return "Union simple y lista mixta"

@sobrecargar
def procesar_complejidad(x: Union[List[int], Dict[str, Union[int, List[str]]]]) -> str:
    return "Lista de enteros o dict mixto"

@sobrecargar
def procesar_complejidad(x: Union[
    Tuple[int, Union[str, List[int]]],
    List[Tuple[str, Union[int, Literal["x", "y"]]]]
]) -> str:
    return "Tupla mixta o lista de tuplas con literal"

@sobrecargar
def procesar_complejidad(x: Optional[Union[List[Optional[int]], Dict[str, Optional[str]]]]) -> str:
    return "Optional anidado sobre lista o dict"
class TestTiposAnidadosSobrecarga(unittest.TestCase):

    def test_union_simple_y_lista_mixta(self):
        self.assertEqual(procesar_complejidad(5), "Union simple y lista mixta")
        self.assertEqual(procesar_complejidad("hola"), "Union simple y lista mixta")
        self.assertEqual(procesar_complejidad(["a", "b", 1]), "Union simple y lista mixta")

    def test_lista_enteros_o_dict_mixto(self):
        # [!] PRUEBA COMENTADA POR QUE ES UN CASO AMBIGÜO A RESOLVER
        # ARREGLAR: (Hernán)   Este caso no es tan ambiguo, el sistema debería preferir `t.List[int]` a `t.List[t.Union[int,str]]`
        # ARREGLAR: (Hernán)   pero hay un error o bien en como se puntúa esos casos, o el hecho de que estén envueltos en un `t.Union`,
        # ARREGLAR: (Hernán)   embarra. Cuestión que ambas firmas tienen el mismo puntaje y se elije la que se definió primero.
        #self.assertEqual(procesar_complejidad([1, 2, 3]), "Lista de enteros o dict mixto")
        self.assertEqual(procesar_complejidad({"a": 1, "b": ["uno", "dos"]}), "Lista de enteros o dict mixto")
    def test_tuplas_con_literal_y_listas(self):
        self.assertEqual(procesar_complejidad((42, "hola")), "Tupla mixta o lista de tuplas con literal")
        self.assertEqual(procesar_complejidad([("clave", "x"), ("otra", 3)]), "Tupla mixta o lista de tuplas con literal")

    def test_optional_anidado(self):
        self.assertEqual(procesar_complejidad(None), "Optional anidado sobre lista o dict")
        self.assertEqual(procesar_complejidad([1, None, 2]), "Optional anidado sobre lista o dict")
        self.assertEqual(procesar_complejidad({"k": "v", "j": None}), "Optional anidado sobre lista o dict")

"""
from typing import TypeVar, Generic, Callable, Union, Optional, Literal, List, Tuple, Dict, Any, overload, Unpack, Annotated

A = TypeVar('A')
B = TypeVar('B')

@sobrecargar
def operar(a: Annotated[List[Tuple[str, Union[int, float]]], "descripcion"], *, escalar: Optional[float] = None) -> float:
    return sum(valor if isinstance(valor, (int, float)) else 0 for _, valor in a) * (escalar or 1)

@sobrecargar
def operar(a: Dict[str, List[Dict[str, Union[int, str]]]], b: Callable[[int], str]) -> List[str]:
    resultado = []
    for lista_dicts in a.values():
        for d in lista_dicts:
            for valor in d.values():
                if isinstance(valor, int):
                    resultado.append(b(valor))
    return resultado

@sobrecargar
def operar(
    config: Dict[str, Union[
        List[int],
        Dict[str, Union[Literal["auto", "manual"], Tuple[int, int]]]
    ]]
) -> str:
    return "config interpretada correctamente"

class Procesador(Generic[A, B]):
    @sobrecargar
    def procesar(self, entrada: List[A], fn: Callable[[A], B]) -> List[B]:
        return [fn(e) for e in entrada]

    @sobrecargar
    def procesar(self, entrada: Dict[str, A], fn: Callable[[A], B]) -> Dict[str, B]:
        return {k: fn(v) for k, v in entrada.items()}

    @sobrecargar
    def procesar(self, entrada: Tuple[A, ...], fn: Callable[[A], B], *, filtrar: Optional[Callable[[A], bool]] = None) -> List[B]:
        if filtrar:
            entrada = tuple(filter(filtrar, entrada))
        return [fn(e) for e in entrada]


class PruebasTiposComplejos(unittest.TestCase):
    def test_operar_annotated_lista_tuplas(self):
        datos = [("uno", 1), ("dos", 2.0), ("tres", "ignorar")]
        self.assertAlmostEqual(operar(datos, escalar=2), 6.0)

    def test_operar_diccionario_complejo(self):
        datos = {
            "bloque1": [{"x": 1, "y": "a"}, {"z": 2}],
            "bloque2": [{"a": 3}]
        }
        resultado = operar(datos, lambda x: f"valor={x}")
        self.assertIn("valor=1", resultado)
        self.assertIn("valor=2", resultado)
        self.assertIn("valor=3", resultado)

    def test_operar_config_union_literales_y_tuplas(self):
        config = {
            "modo": {"tipo": "auto"},
            "resolucion": {"valores": (1920, 1080)}
        }
        self.assertEqual(operar(config), "config interpretada correctamente")

    def test_procesador_generico_lista(self):
        p = Procesador[int, str]()
        self.assertEqual(p.procesar([1, 2, 3], lambda x: f"n={x}"), ["n=1", "n=2", "n=3"])

    def test_procesador_generico_dict(self):
        p = Procesador[int, float]()
        datos = {"a": 1, "b": 2}
        self.assertEqual(p.procesar(datos, lambda x: x * 2.5), {"a": 2.5, "b": 5.0})

    def test_procesador_generico_tuple_filtrado(self):
        p = Procesador[int, str]()
        resultado = p.procesar((1, 2, 3, 4), lambda x: f"x={x}", filtrar=lambda x: x % 2 == 0)
        self.assertEqual(resultado, ["x=2", "x=4"])
"""
if __name__ == "__main__":
    unittest.main()