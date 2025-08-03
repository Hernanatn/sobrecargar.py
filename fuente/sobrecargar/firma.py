import typing as t
import inspect as ins

class _OpcionesFirma(t.TypedDict, total=False):
    follow_wrapped: bool
    globals: t.Optional[dict[str, t.Any]] 
    locals: t.Optional[dict[str, t.Any]] 
    eval_str: bool

class Firma(ins.Signature):
    def _hash_basis(self : t.Self):
        params, kwonly = [], []
        for p in self.parameters.values():
            default = p.default
            if default is not ins._empty:
                default = _congelar(default)
            entry = (p.name, p.kind, p.annotation, default)
            (kwonly if p.kind == ins.Parameter.KEYWORD_ONLY else params).append(entry)
        return (tuple(params), frozenset(kwonly), self.return_annotation)

    def __hash__(self):
        return hash(self._hash_basis())

    @classmethod
    def desdeFuncion(
        cls,
        f : t.Callable,
        *,
        follow_wrapped: bool = True,
        globals: dict | None = None,
        locals: dict | None = None,
        eval_str: bool = False
    ) -> "Firma":
        """
        Fabrica una Firma parcheada a partir de cualquier t.Callable,
        delegando en ins.signature todo el análisis de parámetros.
        """
        sig = ins.signature(
            f,
            follow_wrapped=follow_wrapped,
            globals=globals,
            locals=locals,
            eval_str=eval_str
        )
        return cls(
            parameters=list(sig.parameters.values()),
            return_annotation=sig.return_annotation,
        )

def obtenerFirma(f : t.Callable, **opciones: t.Unpack[_OpcionesFirma]) -> Firma:
    return Firma.desdeFuncion(f, **opciones)

def _congelar(obj : object) -> object:
    if isinstance(obj, dict):
        return frozenset((k, _congelar(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return tuple(_congelar(v) for v in obj)
    elif isinstance(obj, set):
        return frozenset(_congelar(v) for v in obj)
    else:
        return obj