"""Selector de conversión, elipsoide y campos de entrada dinámicos con validación."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, Optional

from conversor_coordenadas.ellipsoids import CLARKE_1866, ELLIPSOIDS


class ConversionForm(ttk.LabelFrame):
    """Formulario dinámico adaptado a la dirección de conversión seleccionada."""

    def __init__(
        self,
        parent: tk.Widget,
        on_convert: Callable[[], None],
        *,
        style: Optional[str] = None,
    ) -> None:
        super().__init__(parent, text=" Parámetros de Entrada ", padding=12, style=style)
        self.on_convert = on_convert

        # Variables de control de UI
        self.mode_var = tk.StringVar(value="Geo → TM")
        self.ellipsoid_var = tk.StringVar(value=CLARKE_1866.name)
        self.hemi_var = tk.StringVar(value="Norte")

        # Variables para almacenamiento de entradas del usuario
        self.entries: Dict[str, tk.StringVar] = {
            "lat": tk.StringVar(value="19.012296"),
            "lon": tk.StringVar(value="-98.214419"),
            "lambda0": tk.StringVar(value="-99.0"),
            "zone": tk.StringVar(value="14"),
            "x": tk.StringVar(value="500000.0"),
            "y": tk.StringVar(value="2100000.0"),
            "easting": tk.StringVar(value="500000.0"),
            "northing": tk.StringVar(value="2100000.0"),
        }

        self._build_ui()
        self.update_fields()

    def _build_ui(self) -> None:
        lbl_mode = ttk.Label(self, text="Dirección de Conversión:")
        lbl_mode.grid(row=0, column=0, sticky="w", pady=4, padx=5)

        modes = ["Geo → TM", "Geo → UTM", "TM → Geo", "UTM → Geo"]
        self.combo_mode = ttk.Combobox(
            self, textvariable=self.mode_var, values=modes, state="readonly", width=20
        )
        self.combo_mode.grid(row=0, column=1, sticky="ew", pady=4, padx=5)
        self.combo_mode.bind("<<ComboboxSelected>>", lambda e: self.update_fields())

        lbl_ell = ttk.Label(self, text="Elipsoide de Referencia:")
        lbl_ell.grid(row=0, column=2, sticky="w", pady=4, padx=(15, 5))

        ell_names = sorted(ELLIPSOIDS.keys())
        self.combo_ell = ttk.Combobox(
            self, textvariable=self.ellipsoid_var, values=ell_names, state="readonly", width=22
        )
        self.combo_ell.grid(row=0, column=3, sticky="ew", pady=4, padx=5)

        self.dynamic_frame = ttk.Frame(self)
        self.dynamic_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=8)

        self.btn_calc = ttk.Button(
            self, text="Calcular Transformación", command=self.on_convert, style="Accent.TButton"
        )
        self.btn_calc.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(5, 0), padx=5)

        for col in range(4):
            self.columnconfigure(col, weight=1)

    def update_fields(self) -> None:
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

        mode = self.mode_var.get()

        for col in range(4):
            self.dynamic_frame.columnconfigure(col, weight=1)

        if mode == "Geo → TM":
            self._add_field(0, 0, "Latitud (φ) [° decimales]:", "lat")
            self._add_field(0, 2, "Longitud (λ) [° decimales]:", "lon")
            self._add_field(1, 0, "Meridiano Central (λ₀) [°]:", "lambda0")
        elif mode == "Geo → UTM":
            self._add_field(0, 0, "Latitud (φ) [° decimales]:", "lat")
            self._add_field(0, 2, "Longitud (λ) [° decimales]:", "lon")
            self._add_field(1, 0, "Zona UTM (1-60, opcional):", "zone")
        elif mode == "TM → Geo":
            self._add_field(0, 0, "Coordenada X (Este) [m]:", "x")
            self._add_field(0, 2, "Coordenada Y (Norte) [m]:", "y")
            self._add_field(1, 0, "Meridiano Central (λ₀) [°]:", "lambda0")
        elif mode == "UTM → Geo":
            self._add_field(0, 0, "Este / Easting (X) [m]:", "easting")
            self._add_field(0, 2, "Norte / Northing (Y) [m]:", "northing")
            self._add_field(1, 0, "Zona UTM (1-60):", "zone")

            lbl_hemi = ttk.Label(self.dynamic_frame, text="Hemisferio:")
            lbl_hemi.grid(row=1, column=2, sticky="w", pady=3, padx=(15, 5))
            cb_hemi = ttk.Combobox(
                self.dynamic_frame,
                textvariable=self.hemi_var,
                values=["Norte", "Sur"],
                state="readonly",
                width=18,
            )
            cb_hemi.grid(row=1, column=3, sticky="ew", pady=3, padx=5)

    def _add_field(self, row: int, col: int, label_text: str, key: str) -> None:
        lbl = ttk.Label(self.dynamic_frame, text=label_text)
        lbl.grid(row=row, column=col, sticky="w", pady=3, padx=5 if col == 0 else (15, 5))
        ent = ttk.Entry(self.dynamic_frame, textvariable=self.entries[key], width=20)
        ent.grid(row=row, column=col + 1, sticky="ew", pady=3, padx=5)

    def _parse_float(self, field_name: str, raw_val: str) -> float:
        val_str = raw_val.strip()
        if not val_str:
            raise ValueError(f"El campo '{field_name}' no puede estar vacío.")
        try:
            val = float(val_str)
        except ValueError:
            raise ValueError(f"El valor '{val_str}' en '{field_name}' no es un número válido.")
        if not math.isfinite(val):
            raise ValueError(f"El valor en '{field_name}' debe ser un número finito.")
        return val

    def get_data(self) -> Dict[str, Any]:
        mode = self.mode_var.get()
        ellipsoid = self.ellipsoid_var.get()
        data: Dict[str, Any] = {"mode": mode, "ellipsoid": ellipsoid}

        if mode == "Geo → TM":
            lat = self._parse_float("Latitud (φ)", self.entries["lat"].get())
            lon = self._parse_float("Longitud (λ)", self.entries["lon"].get())
            lambda0 = self._parse_float("Meridiano Central (λ₀)", self.entries["lambda0"].get())

            if not (-90.0 <= lat <= 90.0):
                raise ValueError(f"La Latitud debe estar entre -90° y 90° (valor ingresado: {lat}).")
            if not (-180.0 <= lon <= 180.0):
                raise ValueError(f"La Longitud debe estar entre -180° y 180° (valor ingresado: {lon}).")
            if not (-180.0 <= lambda0 <= 180.0):
                raise ValueError(f"El Meridiano Central debe estar entre -180° y 180° (valor ingresado: {lambda0}).")

            data.update({"lat": lat, "lon": lon, "lambda0": lambda0})

        elif mode == "Geo → UTM":
            lat = self._parse_float("Latitud (φ)", self.entries["lat"].get())
            lon = self._parse_float("Longitud (λ)", self.entries["lon"].get())

            if not (-90.0 <= lat <= 90.0):
                raise ValueError(f"La Latitud debe estar entre -90° y 90° (valor ingresado: {lat}).")
            if not (-180.0 <= lon <= 180.0):
                raise ValueError(f"La Longitud debe estar entre -180° y 180° (valor ingresado: {lon}).")

            zone_str = self.entries["zone"].get().strip()
            zone = None
            if zone_str:
                try:
                    zone = int(zone_str)
                except ValueError:
                    raise ValueError(f"La Zona UTM debe ser un número entero (valor ingresado: '{zone_str}').")
                if not (1 <= zone <= 60):
                    raise ValueError(f"La Zona UTM debe estar comprendida entre 1 y 60 (valor ingresado: {zone}).")

            data.update({"lat": lat, "lon": lon, "zone": zone})

        elif mode == "TM → Geo":
            x = self._parse_float("Coordenada X (Este)", self.entries["x"].get())
            y = self._parse_float("Coordenada Y (Norte)", self.entries["y"].get())
            lambda0 = self._parse_float("Meridiano Central (λ₀)", self.entries["lambda0"].get())

            if not (-180.0 <= lambda0 <= 180.0):
                raise ValueError(f"El Meridiano Central debe estar entre -180° y 180° (valor ingresado: {lambda0}).")

            data.update({"x": x, "y": y, "lambda0": lambda0})

        elif mode == "UTM → Geo":
            easting = self._parse_float("Este (Easting)", self.entries["easting"].get())
            northing = self._parse_float("Norte (Northing)", self.entries["northing"].get())
            zone_str = self.entries["zone"].get().strip()

            if not zone_str:
                raise ValueError("El campo 'Zona UTM' es obligatorio en UTM → Geo.")
            try:
                zone = int(zone_str)
            except ValueError:
                raise ValueError(f"La Zona UTM debe ser un número entero (valor ingresado: '{zone_str}').")
            if not (1 <= zone <= 60):
                raise ValueError(f"La Zona UTM debe estar comprendida entre 1 y 60 (valor ingresado: {zone}).")

            data.update({
                "easting": easting,
                "northing": northing,
                "zone": zone,
                "southern_hemisphere": (self.hemi_var.get() == "Sur"),
            })

        return data