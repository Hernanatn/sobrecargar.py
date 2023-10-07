from sobrecargar import sobrecargar


class AP: ...

class Sebi(AP): ...
class Jauns(AP): ...

class AP():

    def __init__(self, nombre : str) -> None:
        self.nombre = nombre


    @sobrecargar
    def saludo(self, nombreOtro : str) -> None:
        print(f"Hola {nombreOtro}, me llamo {self.nombre}")

    @sobrecargar
    def saludo(self, x : int) -> None:
        print(f"es int {x=}")


    @sobrecargar
    def saludo(self, nombreOtro : str, carino : int) -> None:
        match carino:

            case 0:
                print(f"Y VO QUIEN SO? Plantate gato, no me dicen {self.nombre} por nada.")
            
            case 2:
                print(f"Hola {nombreOtro}, me llamo {self.nombre}")

            case _:
                pass