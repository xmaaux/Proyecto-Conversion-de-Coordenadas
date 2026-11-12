"""Tablas de visualización con ttk.Treeview para resultados finales e intermedios."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, List, Tuple, Union

from conversor_coordenadas.core import ConversionResult, InverseResult


class ResultTables(ttk.Frame):
    """Contenedor desplegable con tablas para resultados finales y parámetros intermedios."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)

        # --- Tabla 1: Resultados Finales ---
        frame_final = ttk.LabelFrame(self, text=" Resultados Finales ", padding=8)
        frame_final.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        frame_final.columnconfigure(0, weight=1)
        frame_final.rowconfigure(0, weight=1)

        self.tree_final = ttk.Treeview(
            frame_final,
            columns=("param", "value", "unit"),
            show="headings",
            selectmode="browse",
            height=5,
        )
        self.tree_final.heading("param", text="Parámetro Final")
        self.tree_final.heading("value", text="Valor Calculado")
        self.tree_final.heading("unit", text="Unidad")

        self.tree_final.column("param", width=280, anchor="w")
        self.tree_final.column("value", width=380, anchor="e")
        self.tree_final.column("unit", width=120, anchor="w")

        scroll_final = ttk.Scrollbar(frame_final, orient="vertical", command=self.tree_final.yview)
        self.tree_final.configure(yscrollcommand=scroll_final.set)

        self.tree_final.grid(row=0, column=0, sticky="nsew")
        scroll_final.grid(row=0, column=1, sticky="ns")

        # --- Tabla 2: Parámetros Intermedios ---
        frame_inter = ttk.LabelFrame(self, text=" Parámetros Intermedios del Desarrollo ", padding=8)
        frame_inter.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        frame_inter.columnconfigure(0, weight=1)
        frame_inter.rowconfigure(0, weight=1)

        self.tree_inter = ttk.Treeview(
            frame_inter,
            columns=("param", "value", "desc"),
            show="headings",
            selectmode="browse",
            height=10,
        )
        self.tree_inter.heading("param", text="Símbolo / Coeficiente")
        self.tree_inter.heading("value", text="Valor Intermedio")
        self.tree_inter.heading("desc", text="Descripción / Fórmula")

        self.tree_inter.column("param", width=180, anchor="w")
        self.tree_inter.column("value", width=300, anchor="e")
        self.tree_inter.column("desc", width=320, anchor="w")

        scroll_inter = ttk.Scrollbar(frame_inter, orient="vertical", command=self.tree_inter.yview)
        self.tree_inter.configure(yscrollcommand=scroll_inter.set)

        self.tree_inter.grid(row=0, column=0, sticky="nsew")
        scroll_inter.grid(row=0, column=1, sticky="ns")

    def clear(self) -> None:
        """Limpia todos los registros de las dos tablas."""
        for item in self.tree_final.get_children():
            self.tree_final.delete(item)
        for item in self.tree_inter.get_children():
            self.tree_inter.delete(item)

    def display_results(self, result: Union[ConversionResult, InverseResult]) -> None:
        """Formatea y carga el objeto de resultado en las tablas de la interfaz."""
        self.clear()

        def fmt(val: Any, prec: int = 8) -> str:
            if isinstance(val, float):
                return f"{val:.{prec}f}"
            return str(val) if val is not None else "-"

        # Distinguir Conversión Directa vs Inversa
        if isinstance(result, ConversionResult):
            # Resultados Finales (Geo → TM / UTM)
            final_data: List[Tuple[str, str, str]] = [
                ("Coordenada Este (X)", fmt(result.x, 4), "m"),
                ("Coordenada Norte (Y)", fmt(result.y, 4), "m"),
                ("Factor de Escala (k)", fmt(result.k, 8), "-"),
                ("Convergencia (γ rad)", fmt(result.gamma_rad, 8), "rad"),
                ("Convergencia (γ deg)", fmt(result.gamma_deg, 6), "° decimales"),
            ]
            if result.is_utm:
                final_data.append(("Zona UTM", str(result.zone), "-"))
                final_data.append(("Falso Este / Norte", f"{result.false_easting:.0f} / {result.false_northing:.0f}", "m"))

            for row in final_data:
                self.tree_final.insert("", "end", values=row)

            # Parámetros Intermedios (a₁…a₁₁ + series)
            p = result.params
            inter_data: List[Tuple[str, str, str]] = [
                ("Elipsoide", result.ellipsoid_name, "Elipsoide de referencia"),
                ("e²", fmt(p.e2, 10), "Primera excentricidad al cuadrado"),
                ("e'²", fmt(p.ep2, 10), "Segunda excentricidad al cuadrado"),
                ("c", fmt(p.c, 4), "Radio polar de curvatura (m)"),
                ("N", fmt(p.N, 4), "Radio curvatura primera vertical (m)"),
                ("Δλ", fmt(p.delta_lambda, 10), "Diferencia de longitud (rad)"),
                ("S(φ)", fmt(p.S_phi, 4), "Arco de meridiano (m)"),
                ("A₀", fmt(p.series.A0, 10), "Coeficiente de serie Gauss-Krüger"),
                ("A₁", fmt(p.series.A1, 10), "Coeficiente de serie Gauss-Krüger"),
                ("A₂", fmt(p.series.A2, 10), "Coeficiente de serie Gauss-Krüger"),
                ("A₄", fmt(p.series.A4, 10), "Coeficiente de serie Gauss-Krüger"),
                ("A₆", fmt(p.series.A6, 10), "Coeficiente de serie Gauss-Krüger"),
                ("A₈", fmt(p.series.A8, 10), "Coeficiente de serie Gauss-Krüger"),
                ("a₁", fmt(p.a1, 8), "Coeficiente expansión serie TM"),
                ("a₂", fmt(p.a2, 8), "Coeficiente expansión serie TM"),
                ("a₃", fmt(p.a3, 8), "Coeficiente expansión serie TM"),
                ("a₄", fmt(p.a4, 8), "Coeficiente expansión serie TM"),
                ("a₅", fmt(p.a5, 8), "Coeficiente expansión serie TM"),
                ("a₆", fmt(p.a6, 8), "Coeficiente expansión serie TM"),
                ("a₇ [sin(φ)]", fmt(p.a7, 8), "Coeficiente para convergencia"),
                ("a₈", fmt(p.a8, 8), "Coeficiente para factor de escala"),
                ("a₉", fmt(p.a9, 8), "Coeficiente para convergencia"),
                ("a₁₀", fmt(p.a10, 8), "Coeficiente para factor de escala"),
                ("a₁₁", fmt(p.a11, 8), "Coeficiente para convergencia"),
            ]
            for row in inter_data:
                self.tree_inter.insert("", "end", values=row)

        elif isinstance(result, InverseResult):
            # Resultados Finales (TM / UTM → Geo)
            final_data = [
                ("Latitud (φ)", fmt(result.phi_deg, 8), "° decimales"),
                ("Longitud (λ)", fmt(result.lambda_deg, 8), "° decimales"),
                ("Meridiano Central (λ₀)", fmt(result.lambda0_deg, 4), "° decimales"),
                ("X_TM recuperado", fmt(result.x, 4), "m"),
                ("Y_TM recuperado", fmt(result.y, 4), "m"),
            ]
            if result.is_utm:
                final_data.insert(0, ("Zona UTM", str(result.zone), "-"))

            for row in final_data:
                self.tree_final.insert("", "end", values=row)

            # Parámetros Intermedios (b₁…b₆ + latitud de pie)
            p = result.params
            inter_data = [
                ("Elipsoide", result.ellipsoid_name, "Elipsoide de referencia"),
                ("e²", fmt(p.e2, 10), "Primera excentricidad al cuadrado"),
                ("e'²", fmt(p.ep2, 10), "Segunda excentricidad al cuadrado"),
                ("c", fmt(p.c, 4), "Radio polar de curvatura (m)"),
                ("A₀", fmt(p.series.A0, 10), "Coeficiente de serie Gauss-Krüger"),
                ("φ₁ (Footpoint)", fmt(p.phi1_rad, 10), "Latitud de pie (rad)"),
                ("N₁", fmt(p.N1, 4), "N evaluado en latitud de pie (m)"),
                ("Iteraciones φ₁", str(p.iterations), "Iteraciones para convergencia"),
                ("b₁", fmt(p.b1, 10), "Coeficiente serie inversa (λ)"),
                ("b₂", fmt(p.b2, 10), "Coeficiente serie inversa (φ)"),
                ("b₃", fmt(p.b3, 10), "Coeficiente serie inversa (λ)"),
                ("b₄", fmt(p.b4, 10), "Coeficiente serie inversa (φ)"),
                ("b₅", fmt(p.b5, 10), "Coeficiente serie inversa (λ)"),
                ("b₆", fmt(p.b6, 10), "Coeficiente serie inversa (φ)"),
            ]
            for row in inter_data:
                self.tree_inter.insert("", "end", values=row)