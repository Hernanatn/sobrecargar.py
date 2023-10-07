from sobrecargar import sobrecargar

class calculadora: ...
class calcuHija(calculadora): ...
class calcuNieta(calcuHija): ...

class calculadora:

    @sobrecargar
    def potencia(self,x : int, y: int) -> int:
        return x**y

    @sobrecargar
    def potencia(self,x: float, y : str) -> str:
        mensaje = f"QUE HACES LOCO COMO VAS A ELEVAR {x} a una palabra??? {y=}"
        return mensaje

    @sobrecargar
    @classmethod
    def metClass(cls, x: int)-> str:
        return f"es Int {x=}"

    @sobrecargar
    @classmethod
    def metClass(cls, y: str)-> str:
        return f"es str {y=}"

class calcuHija(calculadora):

    @sobrecargar
    def potencia(self,x: int, y : tuple[str,...]) -> str:

        cadenas = y
        return f"{[z*x for z in cadenas]}"


    @sobrecargar
    def potencia(self,x: int, y : tuple[int,...]) -> int:

        nums = y
        return sum([x**z for z in nums])

class calcuNieta(calcuHija): 
    @sobrecargar
    def potencia(self, x : tuple[int]) -> int:
        nums = x
        return sum([y**y for y in nums])

def main():
    calMadre = calculadora()
    calHija = calcuHija()
    calNieta = calcuNieta()

    print(f"{calculadora.metClass(5)=}")
    print(f'{calculadora.metClass("hola")=}')
    print(f"{tuple[str,...].__args__=}")
    print(f'{calMadre.potencia(7,2)=}')
    print(f'{calMadre.potencia(1.0,"juan")=}')
    print(f'{calHija.potencia(8,3)=}') # No produce error ya que `clacuHija` hereda de `calculadora`
    print(f'{calHija.potencia(4.0,"martin")=}')
    print(f'{calHija.potencia(2,("juan","pedro","pablo"))=}')
    print(f'{calHija.potencia(2,(1,2,3))=}')
    try:
        print(f'{calMadre.potencia(9,("juana","pedro","pablo"))=}') # Produce error ya que `calculadora` no posee una sobrecargar que tome int, tuple[str]
    except TypeError as e:
        print(e)
    print(f'{calNieta.potencia(7,2)=}')
    print(f'{calNieta.potencia(1.0,"juan")=}')
    print(f'{calNieta.potencia(8,3)=}')
    print(f'{calNieta.potencia(4.0,"martin")=}')
    print(f'{calNieta.potencia(2,("juan","pedro","pablo"))=}')
    print(f'{calNieta.potencia(2,(1,2,3))=}')
    print(f'{calNieta.potencia((1,2,3))=}')

if __name__ == '__main__':
    main()