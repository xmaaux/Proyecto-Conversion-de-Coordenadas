"""Ventana principal y conexión entre la interfaz y el motor de conversión."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from ..core import geo_to_tm, geo_to_utm, tm_to_geo, utm_to_geo
from ..ellipsoids import get_ellipsoid
from .forms import ConversionForm
from .tables import ResultTables


class MainApplication(tk.Tk):
    """Ventana principal del conversor de coordenadas geodésicas."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Conversor de Coordenadas Geodésicas (TM / UTM)")
        self.geometry("960x700")
        self.minsize(850, 600)

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(".", font=("Segoe UI", 9))
        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 14, "bold"),
            foreground="#1e3a8a",
        )
        style.configure(
            "SubHeader.TLabel",
            font=("Segoe UI", 9, "italic"),
            foreground="#4b5563",
        )
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=6)

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=(15, 10, 15, 5))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Conversor de Coordenadas Geodésicas (TM / UTM)",
            style="Header.TLabel",
        ).pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Transformaciones directas e inversas con parámetros de cálculo",
            style="SubHeader.TLabel",
        ).pack(anchor=tk.W)
        ttk.Separator(header, orient="horizontal").pack(fill=tk.X, pady=(8, 0))

        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        self.form = ConversionForm(container, on_convert=self.handle_calculation)
        self.form.pack(fill=tk.X, pady=(0, 10))

        self.results_view = ResultTables(container)
        self.results_view.pack(fill=tk.BOTH, expand=True)

    def handle_calculation(self) -> None:
        """Lee el formulario, ejecuta la conversión seleccionada y muestra el resultado."""
        try:
            data = self.form.get_data()
            mode = data["mode"]
            ellipsoid = get_ellipsoid(data["ellipsoid"])

            if mode == "Geo → TM":
                result = geo_to_tm(
                    phi_deg=data["lat"],
                    lambda_deg=data["lon"],
                    lambda0_deg=data["lambda0"],
                    ellipsoid=ellipsoid,
                )
                self.results_view.display_results(result)

            elif mode == "Geo → UTM":
                result = geo_to_utm(
                    phi_deg=data["lat"],
                    lambda_deg=data["lon"],
                    ellipsoid=ellipsoid,
                    zone=data["zone"],
                )
                self.results_view.display_results(result)

            elif mode == "TM → Geo":
                result = tm_to_geo(
                    x=data["x"],
                    y=data["y"],
                    lambda0_deg=data["lambda0"],
                    ellipsoid=ellipsoid,
                )
                self.results_view.display_results(result)

            elif mode == "UTM → Geo":
                result = utm_to_geo(
                    easting=data["easting"],
                    northing=data["northing"],
                    zone=data["zone"],
                    southern_hemisphere=data["southern_hemisphere"],
                    ellipsoid=ellipsoid,
                )
                self.results_view.display_results(result)

            else:
                raise ValueError(f"Tipo de conversión desconocido: {mode}")

        except ValueError as exc:
            self.results_view.clear()
            messagebox.showerror("Revisa los datos", str(exc), parent=self)
        except Exception as exc:
            self.results_view.clear()
            messagebox.showerror(
                "Error de cálculo",
                f"No se pudo completar la conversión:\n{exc}",
                parent=self,
            )


def main() -> None:
    """Crea y ejecuta la aplicación gráfica."""
    MainApplication().mainloop()


if __name__ == "__main__":
    main()
