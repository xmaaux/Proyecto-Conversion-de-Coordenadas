"""Ventana principal y orquestación de la aplicación de escritorio Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from conversor_coordenadas.core import geo_to_tm, geo_to_utm, tm_to_geo, utm_to_geo
from conversor_coordenadas.ellipsoids import get_ellipsoid
from conversor_coordenadas.ui.forms import ConversionForm
from conversor_coordenadas.ui.tables import ResultTables


class MainApplication(tk.Tk):
    """Aplicación principal de escritorio."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Conversor de Coordenadas Geodésicas ↔ TM / UTM")
        # Tamaño válido de ventana acorde a requerimientos
        self.geometry("960x700")
        self.minsize(880, 600)

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(".", font=("Segoe UI", 9))
        style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"), foreground="#1a365d")
        style.configure("SubHeader.TLabel", font=("Segoe UI", 9, "italic"), foreground="#4a5568")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"))

    def _build_ui(self) -> None:
        # Contenedor raíz
        main_container = ttk.Frame(self, padding=12)
        main_container.pack(fill="both", expand=True)

        # Encabezado
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 10))

        title_lbl = ttk.Label(
            header_frame,
            text="Conversor de Coordenadas Geodésicas (TM / UTM)",
            style="Header.TLabel",
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ttk.Label(
            header_frame,
            text="Sistema de transformación de coordenadas geodésicas y proyectadas basado en el motor de Gauss-Krüger.",
            style="SubHeader.TLabel",
        )
        subtitle_lbl.pack(anchor="w")

        # Formulario de parámetros
        self.form = ConversionForm(main_container, on_convert=self.process_conversion)
        self.form.pack(fill="x", pady=(0, 10))

        # Tablas de resultados e intermedios
        self.tables = ResultTables(main_container)
        self.tables.pack(fill="both", expand=True)

    def process_conversion(self) -> None:
        """Ejecuta la conversión, valida datos y actualiza la vista."""
        # Limpiar resultados anteriores antes de procesar
        self.tables.clear()

        try:
            data = self.form.get_data()
            ellipsoid = get_ellipsoid(data["ellipsoid"])
            mode = data["mode"]

            if mode == "Geo → TM":
                result = geo_to_tm(
                    phi_deg=data["lat"],
                    lambda_deg=data["lon"],
                    lambda0_deg=data["lambda0"],
                    ellipsoid=ellipsoid,
                )
            elif mode == "Geo → UTM":
                result = geo_to_utm(
                    phi_deg=data["lat"],
                    lambda_deg=data["lon"],
                    ellipsoid=ellipsoid,
                    zone=data["zone"],
                )
            elif mode == "TM → Geo":
                result = tm_to_geo(
                    x=data["x"],
                    y=data["y"],
                    lambda0_deg=data["lambda0"],
                    ellipsoid=ellipsoid,
                )
            elif mode == "UTM → Geo":
                result = utm_to_geo(
                    easting=data["easting"],
                    northing=data["northing"],
                    zone=data["zone"],
                    southern_hemisphere=data["southern_hemisphere"],
                    ellipsoid=ellipsoid,
                )
            else:
                raise ValueError(f"Modo de conversión no reconocido: {mode}")

            # Desplegar resultados
            self.tables.display_results(result)

        except ValueError as err:
            messagebox.showerror("Error de Entrada / Validación", str(err), parent=self)
        except Exception as err:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error inesperado durante el cálculo:\n{err}", parent=self)


def main() -> None:
    """Función de inicio requerida por main.py."""
    app = MainApplication()
    app.mainloop()


if __name__ == "__main__":
    main()