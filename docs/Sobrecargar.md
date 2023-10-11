# Sobrecargar

## Descripción
`sobrecargar` es un módulo de Python que incluye una única clase homonima, la cual provee la implementación de un @decorador universal, que permite definir múltiples versiones de una función o método con diferentes conjuntos de parámetros y tipos. Esto permite crear una sobrecarga de funciones similar a la que se encuentra en otros lenguajes de programación, como C++.

## Interfaz Pública
### Decorar una función:
Se puede emplear tanto `@sobrecargar` como `@overload` para decorar funciones o métodos.

```python
from sobrecargar import sobrecargar

@sobrecargar
def mi_funcion(parametro1: int, parametro2: str):
    # Código de la primera versión de la función
    ...

@sobrecargar
def mi_funcion(parametro1: float):
    # Código de la segunda versión de la función
    ...
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