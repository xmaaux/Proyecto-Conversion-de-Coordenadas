"""Motor matemático de conversión geodésica ↔ TM / UTM.

Fórmulas e implementaciones tomadas de las hojas Geo-TM, Geo-UTM,
TM-Geo y UTM-Geo del Excel de referencia y de docs/PROJECT_DOCS.md.

Todas las funciones son puras (sin estado).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from .ellipsoids import CLARKE_1866, Ellipsoid


# ---------------------------------------------------------------------------
# Estructuras de resultado (directa)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SeriesCoefficients:
    """Coeficientes A del desarrollo en serie de Gauss-Krüger (en términos de e'²)."""

    A0: float
    A1: float
    A2: float
    A4: float
    A6: float
    A8: float


@dataclass(frozen=True)
class IntermediateParams:
    """Parámetros intermedios que la interfaz debe mostrar en tablas."""

    e2: float          # e²
    ep2: float         # e'²
    c: float           # radio polar de curvatura
    N: float           # radio de curvatura de la primera vertical
    delta_lambda: float  # Δλ en radianes
    series: SeriesCoefficients
    a1: float
    a2: float
    a3: float
    a4: float
    a5: float
    a6: float
    a7: float          # sin(φ) — para convergencia
    a8: float
    a9: float
    a10: float
    a11: float
    S_phi: float       # arco de meridiano S(φ)


@dataclass(frozen=True)
class ConversionResult:
    """Resultado estructurado de geo → TM o geo → UTM."""

    phi_deg: float
    lambda_deg: float
    lambda0_deg: float
    x: float
    y: float
    k: float
    gamma_rad: float
    gamma_deg: float
    params: IntermediateParams
    ellipsoid_name: str
    is_utm: bool = False
    zone: Optional[int] = None
    k0: float = 1.0
    false_easting: float = 0.0
    false_northing: float = 0.0
    x_tm: Optional[float] = None
    y_tm: Optional[float] = None
    k_tm: Optional[float] = None


# ---------------------------------------------------------------------------
# Estructuras de resultado (inversa)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InverseIntermediateParams:
    """Intermedios de la conversión inversa TM/UTM → geo."""

    e2: float
    ep2: float
    c: float
    series: SeriesCoefficients
    phi1_rad: float       # latitud de pie (footpoint) en radianes
    N1: float             # N evaluado en φ₁
    b1: float
    b2: float
    b3: float
    b4: float
    b5: float
    b6: float
    iterations: int      # iteraciones usadas para φ₁


@dataclass(frozen=True)
class InverseResult:
    """Resultado estructurado de TM/UTM → geodésicas."""

    phi_deg: float
    lambda_deg: float
    lambda0_deg: float
    x: float              # X TM de entrada (o recuperado desde UTM)
    y: float              # Y TM de entrada (o recuperado desde UTM)
    params: InverseIntermediateParams
    ellipsoid_name: str
    is_utm: bool = False
    zone: Optional[int] = None
    easting: Optional[float] = None
    northing: Optional[float] = None
    k0: float = 1.0
    false_easting: float = 0.0
    false_northing: float = 0.0


# ---------------------------------------------------------------------------
# Funciones auxiliares puras (compartidas)
# ---------------------------------------------------------------------------

def _series_coefficients(ep2: float) -> SeriesCoefficients:
    """Coeficientes A₀…A₈ exactamente como en el Excel (C16–C21).

    Se calculan en función de e'² (segunda excentricidad al cuadrado).
    """
    ep = ep2
    A0 = 1 - (3 / 4) * ep * (
        1 - (15 / 16) * ep * (
            1 - (35 / 36) * ep * (
                1 - (63 / 64) * ep * (
                    1 - (99 / 100) * ep
                )
            )
        )
    )
    A1 = (3 / 4) * ep * (
        1 - (25 / 16) * ep * (
            1 - (77 / 60) * ep * (
                1 - (837 / 704) * ep * (
                    1 - (2123 / 1860) * ep
                )
            )
        )
    )
    A2 = (5 / 8) * ep * (
        1 - (139 / 144) * ep * (
            1 - (1087 / 1112) * ep * (
                1 - (513427 / 521760) * ep
            )
        )
    )
    A4 = (35 / 72) * (ep ** 2) * (
        1 - (125 / 64) * ep * (
            1 - (221069 / 150000) * ep
        )
    )
    A6 = (105 / 256) * (ep ** 3) * (1 - (1179 / 400) * ep)
    A8 = (231 / 640) * (ep ** 4)
    return SeriesCoefficients(A0=A0, A1=A1, A2=A2, A4=A4, A6=A6, A8=A8)


def _meridian_arc(phi_rad: float, c: float, series: SeriesCoefficients) -> float:
    """Arco de meridiano S(φ) = c·A₀·φ − c·A₁·sinφ·cosφ·(1 + A₂·sin²φ + …).

    Fórmulas exactas de C23–C25 (directa) / M-columna (inversa) del Excel.
    """
    sin_phi = math.sin(phi_rad)
    cos_phi = math.cos(phi_rad)
    sin2 = sin_phi * sin_phi

    term0 = series.A0 * c * phi_rad
    term1 = (
        series.A1 * c * sin_phi * cos_phi
        * (
            1
            + series.A2 * sin2
            + series.A4 * sin2 ** 2
            + series.A6 * sin2 ** 3
            + series.A8 * sin2 ** 4
        )
    )
    return term0 - term1


def _tm_coefficients(
    phi_rad: float,
    N: float,
    ep2: float,
) -> Tuple[float, float, float, float, float, float, float, float, float, float, float]:
    """Coeficientes a₁…a₁₁ para X, Y, k y γ (directa)."""
    sin_phi = math.sin(phi_rad)
    cos_phi = math.cos(phi_rad)
    cos2 = cos_phi * cos_phi
    cos4 = cos2 * cos2
    cos6 = cos4 * cos2

    a1 = N * cos_phi
    a2 = 0.5 * a1 * sin_phi
    a3 = (1 / 6) * a1 * (-1 + 2 * cos2 + ep2 * cos4)
    a4 = (1 / 12) * a2 * (-1 + 6 * cos2 + 9 * ep2 * cos4 + 4 * ep2 * ep2 * cos6)
    a5 = (1 / 120) * a1 * (
        1 - 20 * cos2 + (24 - 58 * ep2) * cos4 + 72 * ep2 * cos6
    )
    a6 = (1 / 360) * a2 * (1 - 60 * cos2 + 120 * cos4)

    a7 = sin_phi
    a8 = 0.5 * cos2 * (1 + ep2 * cos2)
    a9 = (1 / 3) * sin_phi * cos2 * (
        1 + 3 * ep2 * cos2 + 2 * ep2 * ep2 * cos4
    )
    a10 = (1 / 24) * cos2 * (
        -4 + (9 - 28 * ep2) * cos2 + 42 * ep2 * cos4
    )
    a11 = (1 / 15) * sin_phi * cos2 * (-1 + 3 * cos2)

    return a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11


def _utm_zone_and_central_meridian(lambda_deg: float) -> Tuple[int, float]:
    """Zona UTM (1–60) y meridiano central en grados."""
    zone = min(60, int((lambda_deg + 180) / 6) + 1)
    lambda0 = zone * 6 - 183
    return zone, float(lambda0)


def _footpoint_latitude(
    y: float,
    c: float,
    series: SeriesCoefficients,
    *,
    max_iter: int = 12,
    tol: float = 1e-15,
) -> Tuple[float, int]:
    """Latitud de pie φ₁ por iteración (hojas TM-Geo / UTM-Geo, columnas L/M/N).

    Inicial: φ₁ = Y / (A₀ · c)
    Actualización: φ₁ ← φ₁ + (Y − B(φ₁)) / (A₀ · c)
    donde B(φ) es el arco de meridiano _meridian_arc.

    El Excel fija 9 filas de iteración; aquí se itera hasta convergencia
    (residual < tol) o max_iter. Con Clarke 1866 suele converger en ≤ 7.
    """
    a0c = series.A0 * c
    if a0c == 0.0:
        raise ValueError("A0·c es cero; no se puede calcular latitud de pie")

    phi1 = y / a0c
    for i in range(1, max_iter + 1):
        b = _meridian_arc(phi1, c, series)
        residual = y - b
        phi1 = phi1 + residual / a0c
        if abs(residual) < tol:
            return phi1, i
    return phi1, max_iter


def _inverse_series_coefficients(
    phi1_rad: float,
    N1: float,
    ep2: float,
) -> Tuple[float, float, float, float, float, float]:
    """Coeficientes b₁…b₆ de la inversa (C26–C31 de TM-Geo / UTM-Geo)."""
    sin_p = math.sin(phi1_rad)
    cos_p = math.cos(phi1_rad)
    cos2 = cos_p * cos_p
    cos4 = cos2 * cos2
    cos6 = cos4 * cos2

    b1 = 1.0 / (N1 * cos_p)
    b2 = -0.5 * b1 * b1 * sin_p * cos_p * (1.0 + ep2 * cos2)
    b3 = -(1.0 / 6.0) * b1 ** 3 * (2.0 - cos2 + ep2 * cos4)
    b4 = (
        -(1.0 / 12.0)
        * b1 * b1
        * b2
        * (
            3.0
            + (2.0 - 9.0 * ep2) * cos2
            + 10.0 * ep2 * cos4
            - 4.0 * ep2 * ep2 * cos6
        )
    )
    b5 = (
        (1.0 / 120.0)
        * b1 ** 5
        * (
            24.0
            - 20.0 * cos2
            + (1.0 + 8.0 * ep2) * cos4
            - 2.0 * ep2 * cos6
        )
    )
    b6 = (1.0 / 360.0) * b1 ** 4 * b2 * (45.0 + 16.0 * cos4)

    return b1, b2, b3, b4, b5, b6


# ---------------------------------------------------------------------------
# API pública: geo → TM / UTM  (sin cambios de firma)
# ---------------------------------------------------------------------------

def geo_to_tm(
    phi_deg: float,
    lambda_deg: float,
    lambda0_deg: float,
    *,
    ellipsoid: Optional[Ellipsoid] = None,
    k0: float = 1.0,
    false_easting: float = 0.0,
    false_northing: float = 0.0,
) -> ConversionResult:
    """Conversión geodésica (φ, λ) → Transverse Mercator (X, Y)."""
    if ellipsoid is None:
        ellipsoid = CLARKE_1866

    if not math.isfinite(phi_deg) or not math.isfinite(lambda_deg) or not math.isfinite(lambda0_deg):
        raise ValueError("phi_deg, lambda_deg y lambda0_deg deben ser finitos")
    if abs(phi_deg) > 90.0:
        raise ValueError(f"Latitud fuera de rango [-90, 90]: {phi_deg}")

    phi_rad = math.radians(phi_deg)
    lambda_rad = math.radians(lambda_deg)
    lambda0_rad = math.radians(lambda0_deg)
    delta_lambda = lambda_rad - lambda0_rad

    e2 = ellipsoid.e2
    ep2 = ellipsoid.ep2
    c = ellipsoid.c

    sin_phi = math.sin(phi_rad)
    N = ellipsoid.a / math.sqrt(1.0 - e2 * sin_phi * sin_phi)

    series = _series_coefficients(ep2)
    S_phi = _meridian_arc(phi_rad, c, series)

    a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11 = _tm_coefficients(
        phi_rad, N, ep2
    )

    dl = delta_lambda
    dl2 = dl * dl
    dl3 = dl2 * dl
    dl4 = dl2 * dl2
    dl5 = dl4 * dl
    dl6 = dl4 * dl2

    x_tm = a1 * dl + a3 * dl3 + a5 * dl5
    y_tm = S_phi + a2 * dl2 + a4 * dl4 + a6 * dl6
    k_tm = 1.0 + a8 * dl2 + a10 * dl4
    gamma_rad = a7 * dl + a9 * dl3 + a11 * dl5
    gamma_deg = math.degrees(gamma_rad)

    x = false_easting + k0 * x_tm
    y = false_northing + k0 * y_tm
    k = k0 * k_tm

    params = IntermediateParams(
        e2=e2,
        ep2=ep2,
        c=c,
        N=N,
        delta_lambda=delta_lambda,
        series=series,
        a1=a1, a2=a2, a3=a3, a4=a4, a5=a5, a6=a6,
        a7=a7, a8=a8, a9=a9, a10=a10, a11=a11,
        S_phi=S_phi,
    )

    return ConversionResult(
        phi_deg=phi_deg,
        lambda_deg=lambda_deg,
        lambda0_deg=lambda0_deg,
        x=x,
        y=y,
        k=k,
        gamma_rad=gamma_rad,
        gamma_deg=gamma_deg,
        params=params,
        ellipsoid_name=ellipsoid.name,
        is_utm=False,
        zone=None,
        k0=k0,
        false_easting=false_easting,
        false_northing=false_northing,
        x_tm=x_tm,
        y_tm=y_tm,
        k_tm=k_tm,
    )


def geo_to_utm(
    phi_deg: float,
    lambda_deg: float,
    *,
    ellipsoid: Optional[Ellipsoid] = None,
    zone: Optional[int] = None,
) -> ConversionResult:
    """Conversión geodésica (φ, λ) → UTM."""
    if ellipsoid is None:
        ellipsoid = CLARKE_1866

    if zone is None:
        zone, lambda0_deg = _utm_zone_and_central_meridian(lambda_deg)
    else:
        if not (1 <= zone <= 60):
            raise ValueError(f"Zona UTM inválida: {zone}")
        lambda0_deg = zone * 6 - 183

    false_northing = 10_000_000.0 if phi_deg < 0 else 0.0

    result = geo_to_tm(
        phi_deg,
        lambda_deg,
        lambda0_deg,
        ellipsoid=ellipsoid,
        k0=0.9996,
        false_easting=500_000.0,
        false_northing=false_northing,
    )

    return ConversionResult(
        phi_deg=result.phi_deg,
        lambda_deg=result.lambda_deg,
        lambda0_deg=result.lambda0_deg,
        x=result.x,
        y=result.y,
        k=result.k,
        gamma_rad=result.gamma_rad,
        gamma_deg=result.gamma_deg,
        params=result.params,
        ellipsoid_name=result.ellipsoid_name,
        is_utm=True,
        zone=zone,
        k0=0.9996,
        false_easting=500_000.0,
        false_northing=false_northing,
        x_tm=result.x_tm,
        y_tm=result.y_tm,
        k_tm=result.k_tm,
    )


# ---------------------------------------------------------------------------
# API pública: TM / UTM → geo
# ---------------------------------------------------------------------------

def tm_to_geo(
    x: float,
    y: float,
    lambda0_deg: float,
    *,
    ellipsoid: Optional[Ellipsoid] = None,
    k0: float = 1.0,
    false_easting: float = 0.0,
    false_northing: float = 0.0,
) -> InverseResult:
    """Conversión Transverse Mercator (X, Y) → geodésicas (φ, λ).

    Sigue las fórmulas de la hoja TM-Geo del Excel de referencia:
      1. Recuperar coordenadas TM puras: X' = (X − FE)/k0, Y' = (Y − FN)/k0
      2. Iterar latitud de pie φ₁ a partir de Y'
      3. Evaluar b₁…b₆ en φ₁
      4. φ = φ₁ + b₂ X'² + b₄ X'⁴ + b₆ X'⁶
         λ = λ₀ + b₁ X' + b₃ X'³ + b₅ X'⁵
    """
    if ellipsoid is None:
        ellipsoid = CLARKE_1866

    if not all(math.isfinite(v) for v in (x, y, lambda0_deg, k0)):
        raise ValueError("x, y, lambda0_deg y k0 deben ser finitos")
    if k0 == 0.0:
        raise ValueError("k0 no puede ser cero")

    # Coordenadas TM puras (sin k0 ni falsos orígenes)
    x_tm = (x - false_easting) / k0
    y_tm = (y - false_northing) / k0

    e2 = ellipsoid.e2
    ep2 = ellipsoid.ep2
    c = ellipsoid.c
    series = _series_coefficients(ep2)

    phi1, n_iter = _footpoint_latitude(y_tm, c, series)

    sin_p1 = math.sin(phi1)
    N1 = ellipsoid.a / math.sqrt(1.0 - e2 * sin_p1 * sin_p1)

    b1, b2, b3, b4, b5, b6 = _inverse_series_coefficients(phi1, N1, ep2)

    x2 = x_tm * x_tm
    x3 = x2 * x_tm
    x4 = x2 * x2
    x5 = x4 * x_tm
    x6 = x4 * x2

    phi_rad = phi1 + b2 * x2 + b4 * x4 + b6 * x6
    lambda_rad = math.radians(lambda0_deg) + b1 * x_tm + b3 * x3 + b5 * x5

    params = InverseIntermediateParams(
        e2=e2,
        ep2=ep2,
        c=c,
        series=series,
        phi1_rad=phi1,
        N1=N1,
        b1=b1, b2=b2, b3=b3, b4=b4, b5=b5, b6=b6,
        iterations=n_iter,
    )

    return InverseResult(
        phi_deg=math.degrees(phi_rad),
        lambda_deg=math.degrees(lambda_rad),
        lambda0_deg=lambda0_deg,
        x=x_tm,
        y=y_tm,
        params=params,
        ellipsoid_name=ellipsoid.name,
        is_utm=False,
        zone=None,
        easting=None,
        northing=None,
        k0=k0,
        false_easting=false_easting,
        false_northing=false_northing,
    )


def utm_to_geo(
    easting: float,
    northing: float,
    zone: int,
    *,
    southern_hemisphere: bool = False,
    ellipsoid: Optional[Ellipsoid] = None,
) -> InverseResult:
    """Conversión UTM (Este, Norte, zona) → geodésicas (φ, λ).

    Sigue la hoja UTM-Geo:
      X_TM = (Este − 500000) / 0.9996
      Y_TM = (Norte − FN) / 0.9996   con FN = 10⁷ si hemisferio sur
      λ₀   = zona·6 − 183
    y luego la misma inversa que tm_to_geo.
    """
    if ellipsoid is None:
        ellipsoid = CLARKE_1866

    if not (1 <= zone <= 60):
        raise ValueError(f"Zona UTM inválida: {zone}")
    if not math.isfinite(easting) or not math.isfinite(northing):
        raise ValueError("easting y northing deben ser finitos")

    lambda0_deg = float(zone * 6 - 183)
    false_northing = 10_000_000.0 if southern_hemisphere else 0.0

    result = tm_to_geo(
        easting,
        northing,
        lambda0_deg,
        ellipsoid=ellipsoid,
        k0=0.9996,
        false_easting=500_000.0,
        false_northing=false_northing,
    )

    return InverseResult(
        phi_deg=result.phi_deg,
        lambda_deg=result.lambda_deg,
        lambda0_deg=result.lambda0_deg,
        x=result.x,
        y=result.y,
        params=result.params,
        ellipsoid_name=result.ellipsoid_name,
        is_utm=True,
        zone=zone,
        easting=easting,
        northing=northing,
        k0=0.9996,
        false_easting=500_000.0,
        false_northing=false_northing,
    )
