class SobrecargaDiferida(type):

    def __init__(clase, nombre, ancestros, diccionario):
        super().__init__(nombre,ancestros,diccionario)

        class _Diferida(object): 
            def __new__(cls, posicionales, nominales):
                print(clase,cls,posicionales,nominales)
                objeto = clase.__new__(clase,*posicionales,*nominales)
                if not hasattr(objeto, "_Diferida__parametros_iniciales") or getattr(objeto, "_Diferida__parametros_iniciales") is None:
                    objeto.__parametros_iniciales = []
                objeto.__parametros_iniciales.append((posicionales,nominales))
                objeto.__class__ = cls
                return objeto

            def __inicializar__(self):
                iniciales = self.__parametros_iniciales
                del self.__dict__['_Diferida__parametros_iniciales']
                super().__setattr__('__class__',clase)
                for posicionales,nominales in iniciales:
                    self.__init__(*posicionales,**nominales)
            def __get__(self, obj, tipoObj):
                self.__inicializar__()
                return self.__get__(obj,tipoObj)
            def __call__(self, *posicionales,**nominales):
                self.__inicializar__()
                return self.__call__(*posicionales,**nominales)
    
        _Diferida.__name__ = f"{clase.__name__}_Diferida"
        _Diferida.__qualname__ = f"{clase.__qualname__}_Diferida"
        clase._Diferida = _Diferida
        
    def __call__(cls, *posicionales, **nominales):    
        return cls._Diferida(posicionales, nominales)
    
    def __instancecheck__(cls, instancia):
        return super().__instancecheck__(instancia) or isinstance(instancia, cls._Diferida)

    def __subclasscheck__(cls, subclase):
        return super().__subclasscheck__(subclase) or (subclase == cls._Diferida)
