from sobrecargar import sobrecargar
import unittest
from typing import Unpack

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
def funcion_libre(a: float, *args : Unpack[tuple[int]]):
    """Multiplica el flotante por el valor de una clave específica."""
    return a * sum(a for a in args)

# Clase con métodos decorados
class MiClase:...
class MiClase:
    @sobrecargar
    def metodo(self, a: int, b: int):
        """Resta dos enteros."""
        return a - b

    @sobrecargar
    def metodo(self, a: int, *args: Unpack[tuple[int]]):
        """Multiplica el primer número por la suma de argumentos."""
        return a * sum(args)

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

    def test_errores(self):
        """Prueba errores en invocaciones no soportadas."""
        with self.assertRaises(TypeError):
            funcion_libre(1, "cadena")
        with self.assertRaises(TypeError):
            MiClase().metodo(1.5, 2)

if __name__ == "__main__":
    unittest.main()