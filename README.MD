
# Sobrecargar

## Descripción
`sobrecargar` es un módulo de Python que incluye una única clase homonima, la cual provee la implementación de un @decorador universal, que permite definir múltiples versiones de una función o método con diferentes conjuntos de parámetros y tipos. Esto permite crear una sobrecarga de funciones similar a la que se encuentra en otros lenguajes de programación, como C++.

## Instalación
Puede decargar e instalar `sobrecargar` utilizando el manejador de paquetes `PIP`, según se indica a continuación:

**Ejecute** el siguiente comando en la `terminal`:

``` Bash
pip install sobrecargar
``` 

## Uso Básico
### Decorar una función:
Se puede emplear tanto `@sobrecargar` como `@overload` para decorar funciones o métodos.

```python
from sobrecargar import sobrecargar

@sobrecargar
def mi_funcion(parametro1: int, parametro2: str):
    # Código de la primera versión de la función
    ...

@sobrecarga
def mi_funcion(parametro1: float):
    # Código de la segunda versión de la función
    ...
```

### Decorar un método de una clase:
Dado que `sobrecargar` interfiere con el curso normal de compilación del código de las funciones, y que los métodos (funciones-miembro) suelen definirse al momento de definir la clase, decorar métodos requiere un sintaxis especial. Intentar usar `sobrecargar` de la siguiente forma:
```python
from sobrecargar import overload # 'ovearload' es un alias pre-definido para 'sobrecargar'
class MiClase:
    @overload
    def mi_metodo(self, parametro1: int, parametro2: str):
        # Código de la primera versión del método
        ...

    @overload
    def mi_metodo(self, parametro1: float):
        # Código de la segunda versión del método
        ...
```
Producirá un error del estilo

```
[ERROR] AttributeError: module __main__ does not have a 'MiClase' attribute.
```
Esto sucede porque al momento en que `sobrecargar` intenta crear el diccionario de envíos de las distintas *sobrecargas* de `mi_metodo`, la clase de nombre `MiClase` aún no terminó de ser definida, y por lo tanto el compilador no sabe que existe.

La solución es proveer una firma para la clase *antes* de intentar sobrecargar cualquiera de sus métodos. La firma no requiere más información que el nombre de la clase y su esquema de herencia.

```python
from sobrecargar import overload # 'ovearload' es un alias pre-definido para 'sobrecargar'
class MiClase: pass #Al proveer firma para la clase, se asegura que `sobrecargar` pueda referenciarla en tiempo de compilación

class MiClase:
    @overload
    def mi_metodo(self, parametro1: int, parametro2: str):
        # Código de la primera versión del método
        ...

    @overload
    def mi_metodo(self, parametro1: float):
        # Código de la segunda versión del método
        ...
```

## Ejemplo de Uso
# Función 'libre'
```python
@overload
def suma(a: int, b: int):
    return a + b

@overload
def suma(a: list[int]):
    return sum([x for x in a])

resultado1 = suma(1, 2)  # Llama a la primera versión de la función suma, con parámetros a y b : int
>> 3

resultado2 = suma([1,2,3,4,5])  # Llama a la segunda versión de la función suma, con parámetro a : List[int]
>> 15
```

## Interfaz privada: métodos de `sobrecargar`

### `__new__(cls, funcion: Callable) -> 'sobrecargar'`
Método especial que se encarga de crear una nueva instancia de la clase `sobrecargar` para cada versión de la función o método decorado. Se asegura de que solo haya una instancia de `sobrecargar` por nombre de función.

### `__init__(self, funcion: Callable) -> None`
Constructor de la clase `sobrecargar`. Se encarga de inicializar el diccionario de sobrecargas y registrar la versión actual de la función o método decorado.

### `__call__(self, *posicionales, **nominales)`
Método especial que permite que la instancia del decorador sea llamada como una función. Se encarga de validar los parámetros proporcionados y seleccionar la versión adecuada de la función o método decorado para su ejecución.

### `__get__(self, obj, tipoObj)`
Método especial que se utiliza cuando el decorador se aplica a un método de una clase. Retorna una instancia de `MetodoSobrecargado` que se comporta como el método decorado y permite su llamada.


**Nota**: Esta documentación es un resumen de alto nivel. Para obtener más detalles sobre la implementación y el uso avanzado, se recomienda consultar el código fuente y realizar pruebas adicionales.
