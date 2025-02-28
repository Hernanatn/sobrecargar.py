### Decorar un método de una clase:

> [!TIP]  
> Desde la versión 3.0.2 los métodos (funciones miembro) se *sobrecargan* de la misma forma que las "funciones libres".

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