# Documentación del Proyecto: Conversor de Coordenadas Geodésicas (Python)

Este conjunto de documentos define la arquitectura, requisitos, motor matemático y el flujo de **Vibe Coding** multi-IA. ChatGPT actuará como orquestador usando esta especificación como fuente única de verdad.

## Documento 1: PRD.md (Product Requirements Document)

### 1. Resumen del Proyecto

Desarrollo de un motor de transformación de coordenadas geodésicas a **Transverse Mercator (TM)** y **UTM** en **Python puro**, enfocado en alto rendimiento para procesar un flujo constante y masivo de datos (lotes de coordenadas decimales). La interfaz visual y el procesamiento deben tomar como referencia el diseño estilo **INEGI (TRANINV)** y la exactitud matemática del libro de cálculo en Excel (`Conversor de coordenadas a TM.xlsx`).

### 2. Objetivos Principales

* **Precisión Absoluta:** Replicar exactamente el comportamiento y las fórmulas de las hojas de Excel (`Geo-TM`, `TM-Geo`, `Geo-UTM`, `UTM-Geo`) sin variaciones en constantes de elipsoides ni coeficientes.

* **Procesamiento Eficiente:** Diseñado en Python puro para soportar listas masivas, lecturas de archivos (CSV, JSON) y flujos continuos (streaming).

* **UI/UX de Referencia:** Interfaz tipo consola/web simplificada inspirada en TRANINV (INEGI):

  * 2 cajas de entrada para **Latitud (**$\phi$**)** y **Longitud (**$\lambda$**)** en formato decimal.

  * Generación de tablas ordenadas con resultados finales e intermedios.

### 3. Requisitos Funcionales

1. **Entrada de Datos:**

   * Recepción de coordenadas en **grados decimales** (ej. Latitud: `19.012296`, Longitud: `-98.214419`).

   * Selección de elipsoide de referencia (por defecto: **Clarke 1866**).

   * Selección o cálculo del **Meridiano Central (**$\lambda_0$**)** y **Zona UTM**.

2. **Transformación Bidireccional:**

   * Geodésicas ($\phi, \lambda$) $\rightarrow$ TM / UTM ($X, Y$).

   * TM / UTM ($X, Y$) $\rightarrow$ Geodésicas ($\phi, \lambda$).

3. **Salida de Resultados:**

   * Retorno estructurado (Diccionarios / DataFrames de Python).

   * Despliegue de parámetros intermedios: $e^2, {e'}^2, c, N, A_0 \dots A_8, \text{Factor de escala } (k), \text{Convergencia } (\gamma)$.

---

## Documento 2: MATH_SPEC.md (Especificación Matemática y Fórmulas)

### 1. Elipsoide de Referencia: Clarke 1866

* **Semieje mayor (**$a$**):** $6378206.400$ m

* **Semieje menor (**$b$**):** $6356583.800$ m

* **Primera excentricidad al cuadrado (**$e^2$**):**
  

  $$
  e^2 = \frac{a^2 - b^2}{a^2}
  $$

* **Segunda excentricidad al cuadrado (**${e'}^2$**):**
  

  $$
  {e'}^2 = \frac{a^2 - b^2}{b^2}
  $$

* **Radio polar de curvatura (**$c$**):**
  

  $$
  c = \frac{a^2}{b}
  $$

### 2. Radios de Curvatura y Parámetros Auxiliares

* **Radio de curvatura de la primera vertical (**$N$**):**
  

  $$
  N = \frac{a}{\sqrt{1 - e^2 \cdot \sin^2(\phi)}}
  $$

* **Diferencia de Longitud con respecto al Meridiano Central (**$\Delta\lambda$**):**
  

  $$
  \Delta\lambda = \lambda - \lambda_0 \quad (\text{convertido a radianes})
  $$

### 3. Coeficientes del Desarrollo en Serie de Gauss/Kruger

Calculados estrictamente conforme al Excel:

* $A_0 = 1 - \frac{3}{4}e^2 + \frac{45}{64}e^4 - \frac{175}{256}e^6 + \dots$

* $A_1 = \frac{3}{4}e^2 - \frac{15}{16}e^4 + \frac{525}{512}e^6 - \dots$

* $A_2 = \frac{15}{64}e^4 - \frac{105}{256}e^6 + \dots$

* $A_4, A_6, A_8$ según las constantes de ajuste de la hoja.

### 4. Salidas Requeridas

* **Coordenada Este (**$X$ **/** $X_{\text{TM}}$**):** Ajustada con el falso Este correspondiente.

* **Coordenada Norte (**$Y$ **/** $Y_{\text{TM}}$**):** Calculada a partir del arco de meridiano $S(\phi)$.

* **Factor de Escala TM / UTM (**$k$**):** Factor de deformación lineal.

* **Convergencia de Meridianos (**$\gamma$**):** En radianes y grados sexagesimales.

---

## Documento 3: ARCHITECTURE.md (Diseño del Sistema en Python)

### 1. Estructura del Proyecto

```
Proyecto-Conversion-de-Coordenadas/
├── docs/
│   └── PROJECT_DOCS.md
├── src/
│   └── conversor_coordenadas/
│       ├── __init__.py
│       ├── ellipsoids.py
│       ├── core.py
│       ├── batch.py
│       └── utils.py
├── tests/
│   ├── test_excel.py
│   └── datos_referencia/
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

### 2. Principios de Código

* **Python Puro:** Uso estricto de la librería estándar de Python (`math`) y opcionalmente `dataclasses` para evitar dependencias pesadas.

* **Inmutabilidad:** Las funciones de cálculo matemático no guardan estado; aceptan entradas numéricas y devuelven estructuras inmutables.

* **Pruebas Automatizadas:** Todo módulo nuevo generado por una IA ejecutora debe validarse ejecutando `pytest` o `unittest` comparando los decimales exactos de la hoja de Excel.

---

## Documento 4: ORCHESTRATOR_RULES.md (Reglas de Orquestación Multi-IA)

### 1. Definición del Equipo de IAs

* **ChatGPT (Orquestador / Tech Lead):** Planifica la arquitectura, subdivide los requerimientos en tareas pequeñas, redacta los prompts exactos para las IAs ejecutoras y revisa los logs/errores del proyecto.
* **Gemini (Ejecutor Frontend / Interfaces / Conversión de Datos):** Encargado de construir las capas de presentación, formateo de salidas tipo tabla estilo INEGI y parseo de entradas en grados decimales.
* **Grok (Ejecutor Backend / Algoritmos Matemáticos / Rendimiento):** Encargado del desarrollo del motor matemático puro (`core.py`), optimización para flujo masivo de datos en Python y paso de fórmulas de Gauss/Kruger.

### 2. Instrucción Directa para el Orquestador (System Prompt para ChatGPT)

> "Actúas como Tech Lead y Orquestador de Software Principal de este proyecto. Tu función es dirigir a las IAs ejecutoras (**Gemini** para interfaz/parseo y **Grok** para el motor matemático/rendimiento en Python puro).
>
> **Reglas Obligatorias:**
>
> 1. Respeta 100% las fórmulas y constantes del archivo `MATH_SPEC.md`. No aproximes ni simplifiques las constantes trigonométricas o los ejes de los elipsoides.
>
> 2. No escribas bloques masivos de código directamente. En su lugar, entrega prompts claros, estructurados e independizados para que yo los copie y ejecute en **Gemini** o **Grok** según corresponda.
>
> 3. Especifica a qué IA ejecutora va dirigido cada prompt (ejemplo: `[PROMPT PARA GROK]` o `[PROMPT PARA GEMINI]`).
>
> 4. Cada ciclo de trabajo debe finalizar solicitando la ejecución de `git status` y sugiriendo el comando `git commit` adecuado.
>
> 5. Diseña la estructura pensando en un flujo masivo y continuo de datos (alto rendimiento en Python puro)."