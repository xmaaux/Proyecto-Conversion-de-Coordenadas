"""Punto de inicio de la aplicación de escritorio (Tkinter).

Configura las rutas del entorno e inicia la interfaz gráfica del conversor de coordenadas.
"""

import os
import sys

# Agregar el directorio 'src' al path de Python para permitir importaciones absolutas
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from conversor_coordenadas.ui.app import main


if __name__ == "__main__":
    main()