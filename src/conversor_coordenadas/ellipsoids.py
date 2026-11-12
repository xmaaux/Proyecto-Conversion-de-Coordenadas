"""Elipsoides de referencia para el conversor de coordenadas.

Constantes tomadas de la hoja 'Elipsoide' del Excel de referencia
y de docs/PROJECT_DOCS.md. Clarke 1866 es el predeterminado.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Ellipsoid:
    """Elipsoide de revolución definido por semiejes a y b (metros)."""

    name: str
    a: float  # semieje mayor (m)
    b: float  # semieje menor (m)

    @property
    def e2(self) -> float:
        """Primera excentricidad al cuadrado: e² = (a² - b²) / a²."""
        return (self.a * self.a - self.b * self.b) / (self.a * self.a)

    @property
    def ep2(self) -> float:
        """Segunda excentricidad al cuadrado: e'² = (a² - b²) / b²."""
        return (self.a * self.a - self.b * self.b) / (self.b * self.b)

    @property
    def c(self) -> float:
        """Radio polar de curvatura: c = a² / b."""
        return (self.a * self.a) / self.b


# Valores exactos de la hoja Elipsoide del Excel de referencia.
CLARKE_1866 = Ellipsoid(name="Clarke 1866", a=6378206.4, b=6356583.8)

# Catálogo completo de la hoja Elipsoide (para uso futuro / selección).
ELLIPSOIDS: Dict[str, Ellipsoid] = {
    "Airy 1830": Ellipsoid("Airy 1830", 6377563.396, 6356256.91),
    "Airy Modificado 1965": Ellipsoid("Airy Modificado 1965", 6377340.189, 6356034.4479),
    "Bessel 1841": Ellipsoid("Bessel 1841", 6377397.155, 6356078.96284),
    "Clarke 1866": CLARKE_1866,
    "Clarke 1880": Ellipsoid("Clarke 1880", 6378249.145, 6356514.86955),
    "Fischer 1960": Ellipsoid("Fischer 1960", 6378166.0, 6356784.28),
    "Fischer 1968": Ellipsoid("Fischer 1968", 6378150.0, 6356768.33),
    "GRS80": Ellipsoid("GRS80", 6378137.0, 6356752.31414),
    "Hayford 1909": Ellipsoid("Hayford 1909", 6378388.0, 6356911.94613),
    "Helmert 1906": Ellipsoid("Helmert 1906", 6378200.0, 6356818.17),
    "Hough 1960": Ellipsoid("Hough 1960", 6378270.0, 6356794.343479),
    "Internacional 1909": Ellipsoid("Internacional 1909", 6378388.0, 6356911.94613),
    "Internacional 1924": Ellipsoid("Internacional 1924", 6378388.0, 6356911.94613),
    "Krasovsky 1940": Ellipsoid("Krasovsky 1940", 6378245.0, 6356863.0188),
    "Mercury 1960": Ellipsoid("Mercury 1960", 6378166.0, 6356784.283666),
    "Mercury Modificado 1968": Ellipsoid("Mercury Modificado 1968", 6378150.0, 6356768.337303),
    "Nuevo International 1967": Ellipsoid("Nuevo International 1967", 6378157.5, 6356772.2),
    "Sudamericano 1969": Ellipsoid("Sudamericano 1969", 6378160.0, 6356774.72),
    "Walbeck 1817": Ellipsoid("Walbeck 1817", 6376896.0, 6355834.8467),
    "WGS66": Ellipsoid("WGS66", 6378145.0, 6356759.769356),
    "WGS72": Ellipsoid("WGS72", 6378135.0, 6356750.519915),
    "WGS84": Ellipsoid("WGS84", 6378137.0, 6356752.314245),
}


def get_ellipsoid(name: str = "Clarke 1866") -> Ellipsoid:
    """Devuelve el elipsoide por nombre. Por defecto Clarke 1866."""
    key = name.strip()
    if key not in ELLIPSOIDS:
        raise ValueError(
            f"Elipsoide desconocido: {name!r}. "
            f"Disponibles: {', '.join(sorted(ELLIPSOIDS))}"
        )
    return ELLIPSOIDS[key]