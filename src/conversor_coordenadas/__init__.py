"""Motor matemático del conversor de coordenadas geodésicas ↔ TM / UTM."""

from .ellipsoids import CLARKE_1866, ELLIPSOIDS, Ellipsoid, get_ellipsoid
from .core import (
    ConversionResult,
    IntermediateParams,
    SeriesCoefficients,
    InverseResult,
    InverseIntermediateParams,
    geo_to_tm,
    geo_to_utm,
    tm_to_geo,
    utm_to_geo,
)

__all__ = [
    "CLARKE_1866",
    "ELLIPSOIDS",
    "Ellipsoid",
    "get_ellipsoid",
    "ConversionResult",
    "IntermediateParams",
    "SeriesCoefficients",
    "InverseResult",
    "InverseIntermediateParams",
    "geo_to_tm",
    "geo_to_utm",
    "tm_to_geo",
    "utm_to_geo",
]

__version__ = "0.2.0"