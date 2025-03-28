from sobrecargar import sobrecargar
from typing import Unpack, Union
from fractions import Fraction
from inspect import signature

class Angulo():
    π : float = 3.1415916535897743
class Radianes(Angulo):...
class Grados(Angulo):...

class Radianes(Angulo):

    @sobrecargar
    def __init__(self, rad : str):
        self.rad = rad
        a,b = Fraction(rad.removesuffix("π")).as_integer_ratio()
        self.magnitud = float(a/b)*self.π
        print(self.magnitud)
        
    @sobrecargar
    def __init__(self, magnitud : float):
        self.magnitud = magnitud
        self.rad = f"{Fraction.from_float(magnitud/self.π).limit_denominator(10)}π"
        print(self.magnitud)

    def __str__(self):
        return self.rad

class Calculadora:...

class Calculadora():
    def __init__(self, modoAngulo: Union['Grados','Radianes'] = 'Grados'):
        self.modo = modoAngulo

 
    def sumar(self,*numeros : Unpack[tuple[int]]):
         return sum([num for num in numeros])

    @sobrecargar
    @classmethod
    def traducirAngulo(cls, angulo : Radianes) -> Grados:
        return Grados(angulo.magnitud * 180/angulo.π)

    @sobrecargar
    @classmethod
    def traducirAngulo(cls, angulo : Grados) -> Radianes:
        return Radianes(angulo.magnitud * angulo.π/180)


def pruebaMetodos():
    print(f"{180/Angulo.π=}")
    angulo = Radianes("2/3π")
    print(angulo)

    angulo2 = Radianes((2/3)*Angulo.π)
    print(angulo2)

    calcu : Calculadora = Calculadora()
    suma : int = (calcu.sumar(4,7,9))
    print(suma)

    print(f"{signature(Calculadora.sumar).parameters['numeros'].kind}")

if __name__ == '__main__':
    pruebaMetodos()
