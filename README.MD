# Sobrecargar

[![Hecho por Chaska](https://img.shields.io/badge/hecho_por-Ch'aska-303030.svg)](https://cajadeideas.ar)
[![Versión: 3.1.2](https://img.shields.io/badge/version-v3.1.2-green.svg)](https://github.com/hernanatn/github.com/hernanatn/sobrecargar.py/releases/latest)
[![Versión de Python: 3.9+](https://img.shields.io/badge/Python-3.9_%7C_3.10_%7C_3.11_%7C_3.12_%7C_3.13_%7C_3.14-blue?logo=python)](https://www.python.org/downloads/release/python-3120/)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-lightgrey.svg)](LICENSE)

| Idioma  | Docs   | 
| :---- | ----: |
| :argentina: :es: | [/REAMDE.MD](/README.MD)   |
| :us: | [/REAMDE_en.MD](/README.MD)   |

## Descripción

`sobrecargar` es un módulo de Python que implementa un @decorador universal, permitiendo definir múltiples versiones de una función o método con diferentes conjuntos de parámetros y tipos. Esto habilita la sobrecarga de funciones similar a la que existe en lenguajes como C++, pero adaptada al espíritu de Python.

## Instalación

Puede descargar e instalar `sobrecargar` utilizando el gestor de paquetes `pip`:

```bash
pip install sobrecargar
```

## Uso Básico

### Decorar una función

Se puede emplear tanto `@sobrecargar` como su alias `@overload` para decorar funciones:

```python
from sobrecargar import sobrecargar

@sobrecargar
def procesar(valor: int):
    print(f"Procesando un entero: {valor}")

@sobrecargar
def procesar(valor: str):
    print(f"Procesando una cadena: {valor}")

procesar(42)      # Procesando un entero: 42
procesar("Hola")  # Procesando una cadena: Hola
```

### Decorar un método de una clase

> [!TIP]  
> Desde la versión 3.0.2 los métodos (funciones miembro) se *sobrecargan* de la misma forma que las "funciones libres".

```python
from sobrecargar import sobrecargar

class MiClase:
    @sobrecargar
    def mostrar(self, valor: int):
        print(f"Recibido entero: {valor}")

    @sobrecargar
    def mostrar(self, valor: str):
        print(f"Recibida cadena: {valor}")

obj = MiClase()
obj.mostrar(10)     # Recibido entero: 10
obj.mostrar("Hola") # Recibida cadena: Hola
```

## Ejemplos más complejos

### Función 'libre'

```python
@sobrecargar
def suma(a: int, b: int):
    return a + b

@sobrecargar
def suma(a: list[int]):
    return sum([x for x in a])

resultado1 = suma(1, 2)         # Llama a la primera versión: 3
resultado2 = suma([1,2,3,4,5])  # Llama a la segunda versión: 15
```

### Ejemplo con Caché y Depuración

```python
@sobrecargar(cache=True, debug=True)
def calcular(a: float, *args: int):
    return a * sum(args)

@sobrecargar  # cache=True y debug=True se heredan de la primera sobrecarga
def calcular(a: float, b: float):
    return a * b

floats: Iterable[tuple[float,float]] = ...
for a,b in floats: 
    calcular(a,b)  # En este escenario, la lógica de resolución de sobrecarga
                   # solo se ejecuta en la primera iteración del bucle,
                   # las llamadas subsiguientes solo incurren en el costo de
                   # buscar en la caché de sobrecarga.
```
## Configuración

El decorador `@sobrecargar` acepta los siguientes parámetros de configuración:

| Parámetro | Descripción | Valor por defecto | Desde versión |
|-----------|-------------|------------------|--------------|
| `cache` | Si es `True`, utiliza caché para la resolución de sobrecarga. El caché es sensible no solo a los tipos de los parámetros, sino también al orden en que fueron provistos. | `True` | 3.1.X |
| `debug` | Si es `True`, imprime mensajes de depuración a la consola para: registro de nueva sobrecarga, llamada a la función, caché (si hay), y resolución de candidatos. | `False` | 3.1.X |

> [!NOTE]
> Si cualquiera de las sobrecargas declara un parámetro de configuración, este se aplica a todas ellas.

## Comparación con otras aproximaciones

| Enfoque | Ventajas | Desventajas |
|---------|----------|-------------|
| **Funciones separadas** (`func_int()`, `func_str()`) | Explícito y claro | Duplicación de código, difícil de escalar |
| **`*args` y `**kwargs` con `isinstance`** | Flexible | Requiere verificación manual de tipos, propenso a errores |
| **`typing.overload`** | Ayuda con la validación estática | No afecta la ejecución real, solo es para herramientas |
| **`singledispatch`** | Soportado por la biblioteca estándar | Limitado a dispatch en un único parámetro |
| **`@sobrecargar`** | Fácil de usar, garantiza seguridad de tipos y flexibilidad | Ligero costo en tiempo de ejecución |

## Extensión para VSCode/VSCodium

Para mejorar la experiencia de desarrollo con `sobrecargar`, ofrecemos una extensión oficial para Visual Studio Code y VSCodium que proporciona integración con el Language Server Protocol (LSP).

[![Extensión VSCode/VSCodium](https://img.shields.io/badge/VSCode-Extensión_Oficial-007ACC?logo=visual-studio-code)](https://open-vsx.org/vscode/item?itemName=hernanatn.sobrecargar-vscode)

### Características de la extensión

- **Documentación**: Muestra información detallada sobre cada sobrecarga al pasar el cursor
- **Navegación**: Permite saltar entre las diferentes implementaciones de una función sobrecargada

### Instalación

Puede instalar la extensión directamente desde el marketplace de VSCode/VScodium:

1. Abra VSCode/VSCodium
2. Vaya a la pestaña de extensiones (Ctrl+Shift+X)
3. Busque "sobrecargar" e instálela

Alternativamente, puede descargarla desde [Open VSX Registry](https://open-vsx.org/vscode/item?itemName=hernanatn.sobrecargar-vscode)


## Documentación
Este documento presenta documentación de alto nivel sobre la interfaz pública de `@sobrecarga`. Para obtener más detalles sobre la implementación y el uso avanzado, se recomienda consultar la [documentación completa](/docs) o explorar el código fuente en el repositorio.

## Motivación

### Python tipado y la sobrecarga de funciones

El tipado dinámico de Python, especialmente su filosofía de "duck-typing", constituye una de las características más valiosas del lenguaje. La capacidad de confiar en el intérprete para "seguir adelante" sin restricciones estrictas de tipos hace que el desarrollo en Python sea una experiencia rápida, dinámica y enriquecedora, favoreciendo la iteración rápida.

Sin embargo, el tipado dinámico tiene un costo: analizar estáticamente la **corrección** de un programa se vuelve significativamente más difícil. Es muy complejo para un programador mantener el modelo mental de todos los posibles tipos en tiempo de ejecución que un código está manejando, en cada paso de las ramificaciones del flujo de control para todos los estados posibles del programa.

Tanto la Python Software Foundation como la comunidad en general han tomado nota de este compromiso e introducido numerosas características del lenguaje, bibliotecas y herramientas para abordarlo. Los proyectos de Python se benefician de la existencia de indicadores de tipo (type hints), verificadores de tipos (type checkers), bibliotecas de reflexión en tiempo de ejecución, etc.

Muchos proyectos de Python tipado tarde o temprano encuentran casos de uso para funciones y métodos polimórficos. La sobrecarga de funciones no es solo una conveniencia, sino una necesidad para muchos casos prácticos.

### Estado actual de la sobrecarga en Python

Podemos ver la sobrecarga como un puente entre la filosofía de duck-typing de Python y las pistas de tipo: reintroduce la capacidad de "no preocuparse tanto por los tipos" en el sitio de llamada y facilita el enfoque de "seguir adelante", al tiempo que permite al desarrollador obtener los beneficios de los tipos.

No obstante, el soporte actual para este patrón es deficiente. Es cierto que muchas bibliotecas exponen APIs que están "sobrecargadas más allá del reconocimiento", de modo que *a menudo es imposible determinar qué admiten y qué no sin adivinar*. Este es un problema con la implementación del patrón, no con el patrón en sí.

**El mayor problema con `typing.overload`** es que miente. Ofrece *pistas* para múltiples firmas pero no garantiza nada sobre la implementación que realmente debe manejarlas. De hecho, llamar a código con `typing.overload` a menudo conduce a un gran esfuerzo tratando de entender comprobaciones de tipo ad hoc muy ramificadas dentro de implementaciones catch-all que pueden (y a menudo lo hacen) simplemente no manejar el conjunto de casos que sus firmas dicen que deberían.

`singledispatch` intenta abordar esto, pero funciona para un conjunto muy limitado de casos de uso e introduce una sintaxis de tipado que difiere de la sintaxis de indicadores de tipo ya establecida.

### Nuestra solución

Python tipado llegó para quedarse, y dentro de las bases de código tipadas, el patrón de sobrecarga ofrece muchas ventajas. La prueba está en que, incluso con el estado actual de soporte, la sobrecarga se utiliza ampliamente tanto en la biblioteca estándar como en bibliotecas de terceros populares.

`sobrecargar` ofrece una implementación del patrón que:

- Garantiza la corrección de tipos
- Simplifica la definición de sobrecargas
- Aplica un conjunto coherente de reglas para la selección de sobrecarga
- Ofrece una mejor experiencia de depuración
- Minimiza la sobrecarga de rendimiento

### **¿Por qué usar Sobrecargar?**  

Sobrecargar elimina el código repetitivo y mejora la seguridad al aplicar verificaciones de tipos estrictas en tiempo de ejecución.  

✅ **Conciso** – Define múltiples sobrecargas con un simple decorador.  
✅ **Seguro** – Aplica verificaciones de tipos estrictas en tiempo de ejecución.  
✅ **Eficiente** – Utiliza caché para minimizar el costo del despacho dinámico.  
✅ **Ergonómico** – Admite la sobrecarga de métodos de clase sin requerir definiciones de clase redundantes.  