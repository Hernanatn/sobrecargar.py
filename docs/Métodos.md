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