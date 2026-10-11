from dataclasses import dataclass, field


@dataclass(frozen=True)
class Model:
    id: str
    backend_id: str = ''
    locality: str = 'unknown'


@dataclass(frozen=True)
class ProviderStatus:
    route_id: str
    available: bool
    reason: str = ''
    models: tuple[Model, ...] = field(default_factory=tuple)
    streaming: bool = False
    images: bool = False
