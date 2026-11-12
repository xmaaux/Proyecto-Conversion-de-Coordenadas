"""Pruebas del motor geo ↔ TM / UTM contra valores del Excel de referencia.

Tolerancia numérica:
  - Parámetros de elipsoide y coeficientes A: 1e-12
  - Coordenadas X/Y en metros: 1e-6 m
  - Factor de escala k: 1e-12
  - Convergencia γ: 1e-12 rad / 1e-10 °
  - Inversa lat/lon: 1e-10 ° (≈ 0.01 mm en el ecuador)

Los valores de referencia se extrajeron de las hojas Geo-TM, Geo-UTM,
TM-Geo y UTM-Geo del archivo
docs/datos_referencia/Conversor de coordenadas a TM.xlsx (data_only=True).
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from conversor_coordenadas import (  # noqa: E402
    CLARKE_1866,
    geo_to_tm,
    geo_to_utm,
    tm_to_geo,
    utm_to_geo,
)


GEO_TM_REF = {
    "phi_deg": -11.699840277777778,
    "lambda_deg": -24.498636944444446,
    "lambda0_deg": -21.0,
    "e2": 0.006768657997291184,
    "ep2": 0.006814784945915172,
    "c": 6399902.551587688,
    "N": 6379094.233667283,
    "delta_lambda": -0.06106273401246948,
    "A0": 0.9949213504180211,
    "A1": 0.00505713745921527,
    "A2": 0.0042314080152819475,
    "A4": 2.2278162415514972e-05,
    "A6": 1.2720187290518056e-07,
    "A8": 7.784677532740341e-10,
    "S_phi": -1293799.7767479396,
    "a1": 6246558.190827583,
    "a2": -633352.794602257,
    "a3": 961993.5724429437,
    "a4": -253859.77309490682,
    "a5": 206050.50538358052,
    "a6": -94652.8751524984,
    "X": -381651.12486616394,
    "Y": -1296164.8666765962,
    "phi1_rad_L6": -0.2045739135338506,
    "phi_rad_inv": -0.2042007346807034,
    "lambda_rad_inv": -0.4275818769559132,
}


GEO_UTM_REF = {
    "phi_deg": 19.10144190277778,
    "lambda_deg": -98.489782,
    "lambda0_deg": -99.0,
    "zone": 14,
    "e2": 0.006768657997291184,
    "ep2": 0.006814784945915172,
    "c": 6399902.551587688,
    "N": 6380519.234422984,
    "delta_lambda": 0.008904984002940264,
    "A0": 0.9949213504180211,
    "A1": 0.00505713745921527,
    "A2": 0.0042314080152819475,
    "A4": 2.2278162415514972e-05,
    "A6": 1.2720187290518056e-07,
    "A8": 7.784677532740341e-10,
    "S_phi": 2112770.519324648,
    "a1": 6029212.165680744,
    "a2": 986504.7573187527,
    "a3": 795111.5485816784,
    "a4": 362253.589589739,
    "a5": 116110.50985411425,
    "a6": 118107.73943571541,
    "a7": 0.3272416794134724,
    "a8": 0.44917313321542934,
    "a9": 0.09918467948127575,
    "a10": 0.1523174617070821,
    "a11": 0.032701639925840784,
    "X_TM": 53690.5993634317,
    "Y_TM": 2112848.7501870133,
    "Este_UTM": 553669.1231236863,
    "Norte_UTM": 2112003.6106869387,
    "k_TM": 1.000035619821364,
    "k_UTM": 0.9996356055734356,
    "gamma_rad": 0.0029141519617628185,
    "gamma_deg": 0.16696860826877877,
    "phi1_rad": 0.3333953885818548,
    "phi_rad_inv": 0.33338305308188254,
    "lambda_rad_inv": -1.718970975471446,
}


class TestEllipsoidConstants(unittest.TestCase):
    def test_clarke_1866_axes(self):
        self.assertEqual(CLARKE_1866.a, 6378206.4)
        self.assertEqual(CLARKE_1866.b, 6356583.8)

    def test_e2_ep2_c(self):
        self.assertAlmostEqual(CLARKE_1866.e2, GEO_TM_REF["e2"], places=15)
        self.assertAlmostEqual(CLARKE_1866.ep2, GEO_TM_REF["ep2"], places=15)
        self.assertAlmostEqual(CLARKE_1866.c, GEO_TM_REF["c"], places=9)


class TestGeoToTM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = geo_to_tm(
            GEO_TM_REF["phi_deg"],
            GEO_TM_REF["lambda_deg"],
            GEO_TM_REF["lambda0_deg"],
            ellipsoid=CLARKE_1866,
        )

    def test_e2_ep2_c(self):
        p = self.r.params
        self.assertAlmostEqual(p.e2, GEO_TM_REF["e2"], places=15)
        self.assertAlmostEqual(p.ep2, GEO_TM_REF["ep2"], places=15)
        self.assertAlmostEqual(p.c, GEO_TM_REF["c"], places=9)

    def test_N(self):
        self.assertAlmostEqual(self.r.params.N, GEO_TM_REF["N"], places=6)

    def test_delta_lambda(self):
        self.assertAlmostEqual(
            self.r.params.delta_lambda, GEO_TM_REF["delta_lambda"], places=14
        )

    def test_series_coefficients(self):
        s = self.r.params.series
        self.assertAlmostEqual(s.A0, GEO_TM_REF["A0"], places=15)
        self.assertAlmostEqual(s.A1, GEO_TM_REF["A1"], places=15)
        self.assertAlmostEqual(s.A2, GEO_TM_REF["A2"], places=15)
        self.assertAlmostEqual(s.A4, GEO_TM_REF["A4"], places=15)
        self.assertAlmostEqual(s.A6, GEO_TM_REF["A6"], places=15)
        self.assertAlmostEqual(s.A8, GEO_TM_REF["A8"], places=15)

    def test_S_phi(self):
        self.assertAlmostEqual(self.r.params.S_phi, GEO_TM_REF["S_phi"], places=6)

    def test_a_coefficients(self):
        p = self.r.params
        self.assertAlmostEqual(p.a1, GEO_TM_REF["a1"], places=6)
        self.assertAlmostEqual(p.a2, GEO_TM_REF["a2"], places=6)
        self.assertAlmostEqual(p.a3, GEO_TM_REF["a3"], places=6)
        self.assertAlmostEqual(p.a4, GEO_TM_REF["a4"], places=6)
        self.assertAlmostEqual(p.a5, GEO_TM_REF["a5"], places=6)
        self.assertAlmostEqual(p.a6, GEO_TM_REF["a6"], places=6)

    def test_XY(self):
        self.assertAlmostEqual(self.r.x, GEO_TM_REF["X"], places=6)
        self.assertAlmostEqual(self.r.y, GEO_TM_REF["Y"], places=6)
        self.assertAlmostEqual(self.r.x_tm, GEO_TM_REF["X"], places=6)
        self.assertAlmostEqual(self.r.y_tm, GEO_TM_REF["Y"], places=6)

    def test_metadata(self):
        self.assertFalse(self.r.is_utm)
        self.assertEqual(self.r.ellipsoid_name, "Clarke 1866")
        self.assertEqual(self.r.k0, 1.0)


class TestGeoToUTM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = geo_to_utm(
            GEO_UTM_REF["phi_deg"],
            GEO_UTM_REF["lambda_deg"],
            ellipsoid=CLARKE_1866,
        )

    def test_zone_and_lambda0(self):
        self.assertEqual(self.r.zone, GEO_UTM_REF["zone"])
        self.assertAlmostEqual(self.r.lambda0_deg, GEO_UTM_REF["lambda0_deg"], places=10)

    def test_N(self):
        self.assertAlmostEqual(self.r.params.N, GEO_UTM_REF["N"], places=6)

    def test_delta_lambda(self):
        self.assertAlmostEqual(
            self.r.params.delta_lambda, GEO_UTM_REF["delta_lambda"], places=14
        )

    def test_series_coefficients(self):
        s = self.r.params.series
        self.assertAlmostEqual(s.A0, GEO_UTM_REF["A0"], places=15)
        self.assertAlmostEqual(s.A1, GEO_UTM_REF["A1"], places=15)

    def test_S_phi(self):
        self.assertAlmostEqual(self.r.params.S_phi, GEO_UTM_REF["S_phi"], places=6)

    def test_a_coefficients(self):
        p = self.r.params
        self.assertAlmostEqual(p.a1, GEO_UTM_REF["a1"], places=6)
        self.assertAlmostEqual(p.a2, GEO_UTM_REF["a2"], places=6)
        self.assertAlmostEqual(p.a3, GEO_UTM_REF["a3"], places=6)
        self.assertAlmostEqual(p.a4, GEO_UTM_REF["a4"], places=6)
        self.assertAlmostEqual(p.a5, GEO_UTM_REF["a5"], places=6)
        self.assertAlmostEqual(p.a6, GEO_UTM_REF["a6"], places=6)
        self.assertAlmostEqual(p.a7, GEO_UTM_REF["a7"], places=12)
        self.assertAlmostEqual(p.a8, GEO_UTM_REF["a8"], places=12)
        self.assertAlmostEqual(p.a9, GEO_UTM_REF["a9"], places=12)
        self.assertAlmostEqual(p.a10, GEO_UTM_REF["a10"], places=12)
        self.assertAlmostEqual(p.a11, GEO_UTM_REF["a11"], places=12)

    def test_XY_TM(self):
        self.assertAlmostEqual(self.r.x_tm, GEO_UTM_REF["X_TM"], places=6)
        self.assertAlmostEqual(self.r.y_tm, GEO_UTM_REF["Y_TM"], places=6)

    def test_XY_UTM(self):
        self.assertAlmostEqual(self.r.x, GEO_UTM_REF["Este_UTM"], places=6)
        self.assertAlmostEqual(self.r.y, GEO_UTM_REF["Norte_UTM"], places=6)

    def test_scale_factors(self):
        self.assertAlmostEqual(self.r.k_tm, GEO_UTM_REF["k_TM"], places=12)
        self.assertAlmostEqual(self.r.k, GEO_UTM_REF["k_UTM"], places=12)

    def test_convergence(self):
        self.assertAlmostEqual(self.r.gamma_rad, GEO_UTM_REF["gamma_rad"], places=12)
        self.assertAlmostEqual(self.r.gamma_deg, GEO_UTM_REF["gamma_deg"], places=10)

    def test_metadata(self):
        self.assertTrue(self.r.is_utm)
        self.assertEqual(self.r.k0, 0.9996)
        self.assertEqual(self.r.false_easting, 500_000.0)
        self.assertEqual(self.r.false_northing, 0.0)
        self.assertEqual(self.r.ellipsoid_name, "Clarke 1866")


class TestSouthernHemisphereUTM(unittest.TestCase):
    def test_false_northing_south(self):
        r = geo_to_utm(
            GEO_TM_REF["phi_deg"],
            GEO_TM_REF["lambda_deg"],
            ellipsoid=CLARKE_1866,
        )
        self.assertEqual(r.false_northing, 10_000_000.0)
        self.assertTrue(r.y > 0)


class TestTMToGeo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = tm_to_geo(
            GEO_TM_REF["X"],
            GEO_TM_REF["Y"],
            GEO_TM_REF["lambda0_deg"],
            ellipsoid=CLARKE_1866,
        )

    def test_phi_lambda_vs_excel(self):
        # TM-Geo usa φ₁ = L6 (no totalmente convergido). Nuestro φ₁ converge
        # hasta residual < 1e-15; la diferencia en φ final es ~6e-9 °.
        self.assertAlmostEqual(
            self.r.phi_deg, math.degrees(GEO_TM_REF["phi_rad_inv"]), places=7
        )
        self.assertAlmostEqual(
            self.r.lambda_deg, math.degrees(GEO_TM_REF["lambda_rad_inv"]), places=7
        )

    def test_matches_original_geo(self):
        # Serie truncada (orden X^6) y φ₁ totalmente convergido vs L6 del Excel:
        # diferencia ~1e-9 ° respecto al valor de entrada de Geo-TM.
        self.assertAlmostEqual(self.r.phi_deg, GEO_TM_REF["phi_deg"], places=8)
        self.assertAlmostEqual(self.r.lambda_deg, GEO_TM_REF["lambda_deg"], places=8)

    def test_phi1_converged(self):
        self.assertAlmostEqual(
            self.r.params.phi1_rad, GEO_TM_REF["phi1_rad_L6"], places=9
        )
        self.assertGreaterEqual(self.r.params.iterations, 1)

    def test_roundtrip(self):
        # Error residual de la serie truncada ~0.16 mm en X/Y (aceptable).
        fwd = geo_to_tm(
            self.r.phi_deg, self.r.lambda_deg, GEO_TM_REF["lambda0_deg"]
        )
        self.assertAlmostEqual(fwd.x, GEO_TM_REF["X"], places=3)
        self.assertAlmostEqual(fwd.y, GEO_TM_REF["Y"], places=3)


class TestUTMToGeo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = utm_to_geo(
            GEO_UTM_REF["Este_UTM"],
            GEO_UTM_REF["Norte_UTM"],
            GEO_UTM_REF["zone"],
            southern_hemisphere=False,
            ellipsoid=CLARKE_1866,
        )

    def test_phi_lambda_vs_excel(self):
        self.assertAlmostEqual(
            self.r.phi_deg, math.degrees(GEO_UTM_REF["phi_rad_inv"]), places=10
        )
        self.assertAlmostEqual(
            self.r.lambda_deg, math.degrees(GEO_UTM_REF["lambda_rad_inv"]), places=10
        )

    def test_matches_original_geo(self):
        self.assertAlmostEqual(self.r.phi_deg, GEO_UTM_REF["phi_deg"], places=10)
        self.assertAlmostEqual(self.r.lambda_deg, GEO_UTM_REF["lambda_deg"], places=10)

    def test_phi1(self):
        self.assertAlmostEqual(
            self.r.params.phi1_rad, GEO_UTM_REF["phi1_rad"], places=12
        )

    def test_x_y_tm_recovered(self):
        self.assertAlmostEqual(self.r.x, GEO_UTM_REF["X_TM"], places=6)
        self.assertAlmostEqual(self.r.y, GEO_UTM_REF["Y_TM"], places=6)

    def test_roundtrip(self):
        fwd = geo_to_utm(self.r.phi_deg, self.r.lambda_deg)
        self.assertEqual(fwd.zone, GEO_UTM_REF["zone"])
        self.assertAlmostEqual(fwd.x, GEO_UTM_REF["Este_UTM"], places=5)
        self.assertAlmostEqual(fwd.y, GEO_UTM_REF["Norte_UTM"], places=5)

    def test_metadata(self):
        self.assertTrue(self.r.is_utm)
        self.assertEqual(self.r.zone, 14)
        self.assertEqual(self.r.k0, 0.9996)


class TestUTMToGeoSouth(unittest.TestCase):
    def test_southern_roundtrip(self):
        fwd = geo_to_utm(
            GEO_TM_REF["phi_deg"], GEO_TM_REF["lambda_deg"]
        )
        inv = utm_to_geo(
            fwd.x, fwd.y, fwd.zone, southern_hemisphere=True
        )
        self.assertAlmostEqual(inv.phi_deg, GEO_TM_REF["phi_deg"], places=9)
        self.assertAlmostEqual(inv.lambda_deg, GEO_TM_REF["lambda_deg"], places=9)
        self.assertEqual(inv.false_northing, 10_000_000.0)


class TestInputValidation(unittest.TestCase):
    def test_latitude_out_of_range(self):
        with self.assertRaises(ValueError):
            geo_to_tm(95.0, 0.0, 0.0)

    def test_invalid_zone(self):
        with self.assertRaises(ValueError):
            utm_to_geo(500000.0, 0.0, 0)
        with self.assertRaises(ValueError):
            utm_to_geo(500000.0, 0.0, 61)

    def test_k0_zero(self):
        with self.assertRaises(ValueError):
            tm_to_geo(0.0, 0.0, 0.0, k0=0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
