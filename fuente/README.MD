
# Sobrecargar

## Descripción
`sobrecargar` es un módulo de Python que incluye una única clase homonima, la cual provee la implementación de un @decorador universal, que permite definir múltiples versiones de una función o método con diferentes conjuntos de parámetros y tipos. Esto permite crear una sobrecarga de funciones similar a la que se encuentra en otros lenguajes de programación, como C++.

## Uso Básico
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

### Decorar un método de una clase:
Para decorar métodos internos de clases se debe proveer una firma previa para el tipo.

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
