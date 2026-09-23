"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║              SLV — Análisis de Estabilidad de Taludes y Bancos                   ║
║              Stack: tkinter · matplotlib · numpy                                 ║
║              Autores: Luciano Soto · Sebastián Venegas · Vicente Muñoz           ║
║              551603 — Python Aplicado a la Minería                               ║
║              Universidad de Concepción                                           ║
╚══════════════════════════════════════════════════════════════════════════════════╝

Interfaz principal. El motor de cálculo vive en los módulos:
    falla_plana.py        → análisis y gráfico de falla plana
    falla_cuna2.py        → análisis y gráfico de falla por cuña
    falla_volcamiento.py  → análisis y gráfico de falla por volcamiento
    falla_circular3.py    → análisis y gráfico de falla circular (dovelas)

Esta capa sólo se encarga de: pedir datos, validarlos, invocar el módulo
correspondiente y mostrar resultado + figura. No contiene fórmulas.
"""

import os
import math
import tkinter as tk
from tkinter import Button, Radiobutton, Tk, IntVar, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from falla_plana import analisis_falla_plana, plot_slope
import falla_cuna2 as fc2
from falla_volcamiento import (analisis_falla_volcamiento,
                               dibujar_triangulos as plot_volcamiento)
from falla_circular3 import analisis_falla_circular, visualizar_falla_circular


# ─────────────────────────────────────────────────────────────────────────────
#  IDENTIDAD E IMAGEN CORPORATIVA
# ─────────────────────────────────────────────────────────────────────────────
APP_NOMBRE      = "SLV"
APP_SUBTITULO   = "Análisis de Estabilidad de Taludes"
APP_VERSION     = "1.0"
AUTORES         = ["Luciano Soto", "Sebastián Venegas", "Vicente Muñoz"]
RAMO_CODIGO     = "551603"
RAMO_NOMBRE     = "Python Aplicado a la Minería"
INSTITUCION     = "Universidad de Concepción"
ANIO            = "2026"
LOGO_ARCHIVO    = "slv_logo.png"
EMBLEMA_ARCHIVO = "slv_emblema.png"

# Paleta extraída del logotipo SLV.
# Se mantiene un esquema claro porque las figuras de matplotlib generadas por
# los módulos de cálculo usan fondo blanco: un tema oscuro obligaría a
# reescribirlos y rompería la coherencia visual de los gráficos.
AZUL_MARINO    = "#0D2340"   # azul marino del logo — títulos
AZUL_ACERO     = "#1F4E79"   # azul acero — color primario
AZUL_MEDIO     = "#4A90B8"   # azul medio — acentos
TURQUESA       = "#2E8B96"   # turquesa — acciones secundarias
GRIS_GRAFITO   = "#3D4548"   # gris grafito del logo
COLOR_FONDO    = "#EDF2F7"
COLOR_PANEL    = "#FFFFFF"
COLOR_TEXTO    = "#1F2933"
COLOR_BORDE    = "#CBD5E1"
COLOR_GRAFICO  = "#F8FAFC"


def cargar_imagen(archivo: str, ancho: int, color_fondo: str):
    """
    Devuelve la imagen escalada a `ancho` px, o None si no se puede cargar.
    Usa Pillow si está disponible (mejor calidad y manejo de transparencia);
    si no, recurre a PhotoImage con submuestreo entero.
    """
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), archivo)
    if not os.path.exists(ruta):
        return None
    try:
        from PIL import Image, ImageTk
        img = Image.open(ruta).convert("RGBA")
        alto = int(img.height * ancho / img.width)
        img = img.resize((ancho, alto), Image.LANCZOS)
        c = color_fondo.lstrip("#")
        fondo = Image.new("RGBA", img.size,
                          (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255))
        return ImageTk.PhotoImage(Image.alpha_composite(fondo, img))
    except Exception:
        pass
    try:
        img = tk.PhotoImage(file=ruta)
        factor = max(1, img.width() // ancho)
        return img.subsample(factor, factor)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  VENTANA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
root = Tk()
root.title(f"{APP_NOMBRE} — {APP_SUBTITULO}")
root.geometry("1290x900")
root.minsize(1100, 720)
root.configure(bg=COLOR_FONDO)

try:
    root.iconbitmap("slv.ico")
except tk.TclError:
    pass

root.option_add("*Font", "Arial 10")
root.option_add("*Label.Background", COLOR_PANEL)
root.option_add("*Label.Foreground", COLOR_TEXTO)
root.option_add("*Radiobutton.Background", COLOR_PANEL)
root.option_add("*Radiobutton.Foreground", COLOR_TEXTO)
root.option_add("*Radiobutton.SelectColor", COLOR_FONDO)
root.option_add("*Button.Font", "Arial 10 bold")
root.option_add("*Button.Background", AZUL_ACERO)
root.option_add("*Button.Foreground", "white")
root.option_add("*Entry.Background", COLOR_GRAFICO)

style = ttk.Style()
try:
    style.theme_use("clam")
except tk.TclError:
    pass
# En "clam" el bisel se dibuja con lightcolor/darkcolor/bordercolor; si no se
# igualan a la paleta, la pestaña inactiva se ve gris claro descolgada.
style.configure("SLV.TNotebook", background=COLOR_FONDO,
                bordercolor=COLOR_BORDE, lightcolor=COLOR_FONDO,
                darkcolor=COLOR_FONDO, borderwidth=0, tabmargins=[2, 5, 2, 0])
style.configure("SLV.TNotebook.Tab", padding=(20, 9),
                font=("Arial", 10, "bold"),
                background=COLOR_FONDO, foreground=GRIS_GRAFITO,
                bordercolor=COLOR_BORDE, lightcolor=COLOR_FONDO,
                darkcolor=COLOR_FONDO, borderwidth=0)
style.map("SLV.TNotebook.Tab",
          background=[("selected", COLOR_PANEL), ("!selected", COLOR_FONDO)],
          foreground=[("selected", AZUL_ACERO), ("!selected", GRIS_GRAFITO)],
          lightcolor=[("selected", COLOR_PANEL), ("!selected", COLOR_FONDO)],
          darkcolor=[("selected", COLOR_PANEL), ("!selected", COLOR_FONDO)],
          expand=[("selected", [1, 1, 1, 0])])


# ── Barra de encabezado con el logotipo ──
encabezado = tk.Frame(root, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE,
                      highlightthickness=1)
encabezado.pack(fill="x", padx=12, pady=(12, 0))

logo_encabezado = cargar_imagen(EMBLEMA_ARCHIVO, 52, COLOR_PANEL)
if logo_encabezado is not None:
    tk.Label(encabezado, image=logo_encabezado,
             bg=COLOR_PANEL).pack(side="left", padx=(14, 10), pady=8)

bloque_titulo = tk.Frame(encabezado, bg=COLOR_PANEL)
bloque_titulo.pack(side="left", pady=8)
tk.Label(bloque_titulo, text=APP_NOMBRE, bg=COLOR_PANEL, fg=AZUL_MARINO,
         font=("Arial", 20, "bold")).pack(anchor="w")
tk.Label(bloque_titulo, text=APP_SUBTITULO, bg=COLOR_PANEL, fg=GRIS_GRAFITO,
         font=("Arial", 10)).pack(anchor="w")

tk.Label(encabezado, text=f"{RAMO_CODIGO} · {RAMO_NOMBRE}", bg=COLOR_PANEL,
         fg=AZUL_MEDIO, font=("Arial", 9)).pack(side="right", padx=16)


# ── Pestañas ──
notebook = ttk.Notebook(root, style="SLV.TNotebook")
notebook.pack(fill="both", expand=True, padx=12, pady=12)

tab_analisis = tk.Frame(notebook, bg=COLOR_FONDO)
tab_creditos = tk.Frame(notebook, bg=COLOR_FONDO)
notebook.add(tab_analisis, text="Análisis")
notebook.add(tab_creditos, text="Créditos")


# ─────────────────────────────────────────────────────────────────────────────
#  PESTAÑA CRÉDITOS
# ─────────────────────────────────────────────────────────────────────────────
tarjeta = tk.Frame(tab_creditos, bg=COLOR_PANEL, padx=50, pady=40,
                   highlightbackground=COLOR_BORDE, highlightthickness=1)
tarjeta.place(relx=0.5, rely=0.5, anchor="center")

logo_creditos = cargar_imagen(LOGO_ARCHIVO, 170, COLOR_PANEL)
if logo_creditos is not None:
    tk.Label(tarjeta, image=logo_creditos, bg=COLOR_PANEL).pack(pady=(0, 6))
else:
    tk.Label(tarjeta, text=APP_NOMBRE, bg=COLOR_PANEL, fg=AZUL_MARINO,
             font=("Arial", 40, "bold")).pack(pady=(0, 6))

tk.Label(tarjeta, text=APP_SUBTITULO, bg=COLOR_PANEL, fg=AZUL_MARINO,
         font=("Arial", 16, "bold")).pack()
tk.Label(tarjeta, text=f"Versión {APP_VERSION} · {ANIO}", bg=COLOR_PANEL,
         fg=GRIS_GRAFITO, font=("Arial", 10)).pack(pady=(2, 18))

tk.Frame(tarjeta, bg=AZUL_MEDIO, height=2, width=330).pack(pady=(0, 18))

tk.Label(tarjeta, text="DESARROLLADO POR", bg=COLOR_PANEL, fg=AZUL_ACERO,
         font=("Arial", 10, "bold")).pack(pady=(0, 8))
for autor in AUTORES:
    tk.Label(tarjeta, text=autor, bg=COLOR_PANEL, fg=COLOR_TEXTO,
             font=("Arial", 13)).pack(pady=1)

tk.Frame(tarjeta, bg=COLOR_BORDE, height=1, width=330).pack(pady=18)

tk.Label(tarjeta, text="PROYECTO DESARROLLADO PARA LA ASIGNATURA",
         bg=COLOR_PANEL, fg=AZUL_ACERO, font=("Arial", 10, "bold")).pack(pady=(0, 8))
tk.Label(tarjeta, text=f"{RAMO_CODIGO} — {RAMO_NOMBRE}", bg=COLOR_PANEL,
         fg=COLOR_TEXTO, font=("Arial", 12, "bold")).pack()
tk.Label(tarjeta, text=INSTITUCION, bg=COLOR_PANEL, fg=GRIS_GRAFITO,
         font=("Arial", 11)).pack(pady=(4, 0))


# ─────────────────────────────────────────────────────────────────────────────
#  PESTAÑA ANÁLISIS — estructura de dos paneles
# ─────────────────────────────────────────────────────────────────────────────
frame_izq = tk.Frame(tab_analisis, padx=20, pady=20, bg=COLOR_PANEL,
                     highlightbackground=COLOR_BORDE, highlightthickness=1)
frame_izq.pack(side="left", fill="y", padx=(0, 12))
frame_izq.columnconfigure(0, weight=0)
frame_izq.columnconfigure(1, weight=1)

frame_der = tk.Frame(tab_analisis, padx=20, pady=20, bg=COLOR_PANEL,
                     highlightbackground=COLOR_BORDE, highlightthickness=1)
frame_der.pack(side="right", fill="both", expand=True)

tk.Label(frame_der, text="RESULTADOS", fg=AZUL_ACERO,
         font=("Arial", 12, "bold")).pack(pady=(6, 6))

lbl_resultado = tk.Label(frame_der,
                         text="Seleccione un tipo de falla e ingrese los parámetros.",
                         justify="left", bg=COLOR_PANEL, fg=COLOR_TEXTO,
                         font=("Consolas", 10))
lbl_resultado.pack(anchor="w", padx=10)


def mostrar_resultado(texto):
    lbl_resultado.config(text=texto)


frame_grafico = tk.Frame(frame_der, bg=COLOR_GRAFICO, bd=1, relief="solid")
frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)

canvas_grafico = None


def mostrar_figura(fig):
    """Embebe una figura de matplotlib en frame_grafico, reemplazando la anterior."""
    global canvas_grafico
    if canvas_grafico is not None:
        canvas_grafico.get_tk_widget().destroy()
    fig.set_size_inches(7, 5.2)
    fig.patch.set_facecolor(COLOR_GRAFICO)   # integra la figura con el panel
    try:
        # Al reescalar la figura los títulos quedan fuera del lienzo;
        # tight_layout los reacomoda al nuevo tamaño.
        fig.tight_layout()
    except Exception:
        pass
    canvas_grafico = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas_grafico.draw()
    canvas_grafico.get_tk_widget().pack(fill="both", expand=True)


tk.Label(frame_izq, text="SELECCIONA EL TIPO DE FALLA", fg=AZUL_ACERO,
         font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3,
                                          sticky="w", pady=(0, 10))

var = IntVar(value=0)
frame_campos = tk.Frame(frame_izq, bg=COLOR_PANEL)
data = {}


def limpiar_campos():
    for widget in frame_campos.winfo_children():
        widget.destroy()
    data.clear()


def construir_campos(campos):
    """Crea las filas Etiqueta / Entry / Unidad y devuelve el número de filas."""
    limpiar_campos()
    frame_campos.grid(row=6, column=0, columnspan=3, sticky="w")
    for i, (etiqueta, clave, unidad) in enumerate(campos):
        tk.Label(frame_campos, text=etiqueta).grid(row=i, column=0, sticky="e",
                                                   padx=5, pady=4)
        e = tk.Entry(frame_campos, width=11, relief="solid", bd=1)
        e.grid(row=i, column=1, padx=5, pady=4)
        tk.Label(frame_campos, text=unidad, fg=GRIS_GRAFITO).grid(row=i, column=2,
                                                                  sticky="w")
        data[clave] = e
    return len(campos)


def botones_accion(fila, validar, calcular, graficar):
    """Coloca los tres botones de acción bajo los campos."""
    Button(frame_campos, text="Validar", command=validar, width=16,
           relief="flat", bg=GRIS_GRAFITO).grid(row=fila, column=0, columnspan=3,
                                                pady=(12, 3))
    Button(frame_campos, text="Calcular", command=calcular, width=16,
           relief="flat", bg=AZUL_ACERO).grid(row=fila + 1, column=0, columnspan=3,
                                              pady=3)
    Button(frame_campos, text="Graficar", command=graficar, width=16,
           relief="flat", bg=TURQUESA).grid(row=fila + 2, column=0, columnspan=3,
                                            pady=3)


def leer_numeros(enteros=()):
    """Convierte todos los campos a float; los de `enteros` a int."""
    try:
        v = {k: float(e.get()) for k, e in data.items()}
        for clave in enteros:
            v[clave] = int(v[clave])
    except ValueError:
        messagebox.showerror("Error", "Todos los campos deben contener números válidos.")
        return None
    return v


def error(msg):
    messagebox.showerror("Error", msg)
    return None


# ─────────────────────────────────────────────────────────
#  FALLA PLANA
# ─────────────────────────────────────────────────────────
def mostrar_falla_plana():
    campos = [
        ("Altura del talud",       "altura",             "m"),
        ("Cohesión",               "cohesion",           "MPa"),
        ("Densidad",               "densidad",           "t/m³"),
        ("Ángulo de fricción",     "friccion",           "°"),
        ("Manteo plano de falla",  "manteo_plano_falla", "°"),
        ("Manteo del talud",       "manteo_talud",       "°"),
        ("Profundidad",            "profundidad",        "m"),
        ("Rumbo del talud",        "rumbo_talud",        "°"),
        ("Rumbo plano de falla",   "rumbo_plano_falla",  "°"),
    ]
    n = construir_campos(campos)

    def obtener_valores():
        v = leer_numeros()
        if v is None:
            return None
        if v["altura"] <= 0:
            return error("La altura debe ser un número positivo.")
        if v["cohesion"] < 0:
            return error("La cohesión no puede ser negativa.")
        if v["densidad"] <= 0:
            return error("La densidad debe ser un número positivo.")
        if not 0 <= v["friccion"] <= 90:
            return error("Fricción debe estar entre 0 y 90°.")
        if not 0 <= v["manteo_plano_falla"] <= 90:
            return error("Manteo plano de falla debe estar entre 0 y 90°.")
        if not 0 <= v["manteo_talud"] <= 90:
            return error("Manteo del talud debe estar entre 0 y 90°.")
        if v["profundidad"] <= 0:
            return error("La profundidad debe ser un número positivo.")
        if not 0 <= v["rumbo_talud"] < 360:
            return error("Rumbo del talud debe estar entre 0 y 360°.")
        if not 0 <= v["rumbo_plano_falla"] < 360:
            return error("Rumbo plano de falla debe estar entre 0 y 360°.")
        return v

    def calcular():
        v = obtener_valores()
        if v is None:
            return
        r = analisis_falla_plana(v)
        mostrar_resultado(f"Tipo: Falla Plana\n\n{r['resultado']}\n{r['mensaje']}")

    def graficar():
        v = obtener_valores()
        if v is None:
            return
        fig = plot_slope(v["manteo_plano_falla"], v["manteo_talud"],
                         v["altura"], show=False)
        mostrar_figura(fig)

    botones_accion(n, obtener_valores, calcular, graficar)


# ─────────────────────────────────────────────────────────
#  FALLA POR CUÑA
# ─────────────────────────────────────────────────────────
def mostrar_falla_cuna():
    campos = [
        ("Manteo talud",            "dip_talud",            "°"),
        ("Ángulo de fricción",      "friction",             "°"),
        ("Manteo plano de falla 1", "dip_plano1",           "°"),
        ("Dip direction plano 1",   "dip_direction_plano1", "°"),
        ("Manteo plano de falla 2", "dip_plano2",           "°"),
        ("Dip direction plano 2",   "dip_direction_plano2", "°"),
        ("Ángulo β",                "beta",                 "°"),
    ]
    n = construir_campos(campos)

    def obtener_valores():
        v = leer_numeros()
        if v is None:
            return None
        if not 0 <= v["dip_talud"] <= 90:
            return error("Manteo del talud debe estar entre 0 y 90°.")
        if not 0 <= v["friction"] < 90:
            return error("Fricción debe estar entre 0 y 90°.")
        if not 0 < v["dip_plano1"] < 90:
            return error("Manteo plano 1 debe estar entre 0 y 90°.")
        if not 0 <= v["dip_direction_plano1"] < 360:
            return error("Dip direction plano 1 debe estar entre 0 y 360°.")
        if not 0 < v["dip_plano2"] < 90:
            return error("Manteo plano 2 debe estar entre 0 y 90°.")
        if not 0 <= v["dip_direction_plano2"] < 360:
            return error("Dip direction plano 2 debe estar entre 0 y 360°.")
        if not 0 < v["beta"] < 90:
            return error("Ángulo β debe estar entre 0 y 90°.")
        return v

    def calcular():
        v = obtener_valores()
        if v is None:
            return
        try:
            n1 = fc2.normal_desde_dip_dipdir(v["dip_plano1"], v["dip_direction_plano1"])
            n2 = fc2.normal_desde_dip_dipdir(v["dip_plano2"], v["dip_direction_plano2"])
            xi = fc2.angulo_entre_normales(n1, n2)
            li = fc2.linea_interseccion(n1, n2)
            psi = fc2.psi_i_desde_linea(li)
            fs = fc2.factor_seguridad_cuna(v["beta"], xi, v["friction"], psi)
            estado = ("Potencialmente inestable"
                      if v["dip_talud"] > psi > v["friction"]
                      else ("Estable" if fs >= 1.0 else "Inestable"))
            mostrar_resultado(
                f"Tipo: Falla por Cuña\n\n"
                f"ξ     = {xi:.3f}°\n"
                f"ψᵢ    = {psi:.3f}°\n"
                f"FS    = {fs:.4f}\n"
                f"Estado: {estado}"
            )
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))

    def graficar():
        v = obtener_valores()
        if v is None:
            return
        try:
            n1 = fc2.normal_desde_dip_dipdir(v["dip_plano1"], v["dip_direction_plano1"])
            n2 = fc2.normal_desde_dip_dipdir(v["dip_plano2"], v["dip_direction_plano2"])
            xi = fc2.angulo_entre_normales(n1, n2)
            mostrar_figura(fc2.plot_angulo_cuna(v["beta"], xi, show=False))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    botones_accion(n, obtener_valores, calcular, graficar)


# ─────────────────────────────────────────────────────────
#  FALLA POR VOLCAMIENTO
# ─────────────────────────────────────────────────────────
def mostrar_falla_volcamiento():
    campos = [
        ("Ángulo de fricción",        "friccion",     "°"),
        ("Manteo del talud",          "manteo_talud", "°"),
        ("Altura del talud",          "altura",       "m"),
        ("Buzamiento plano de falla", "buzamiento",   "°"),
    ]
    n = construir_campos(campos)

    def obtener_valores():
        v = leer_numeros()
        if v is None:
            return None
        if not 0 <= v["friccion"] <= 90:
            return error("Fricción debe estar entre 0 y 90°.")
        if not 0 <= v["manteo_talud"] <= 90:
            return error("Manteo del talud debe estar entre 0 y 90°.")
        if v["altura"] <= 0:
            return error("La altura debe ser un número positivo.")
        if not 0 <= v["buzamiento"] <= 90:
            return error("El buzamiento debe estar entre 0 y 90°.")
        return v

    def calcular():
        v = obtener_valores()
        if v is None:
            return
        try:
            r = analisis_falla_volcamiento(v["friccion"], v["manteo_talud"],
                                           v["altura"], v["buzamiento"])
            mostrar_resultado(f"Tipo: Falla por Vuelco\n\n"
                              f"Estado: {r['estado']}\n{r['mensaje']}")
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))

    def graficar():
        v = obtener_valores()
        if v is None:
            return
        try:
            mostrar_figura(plot_volcamiento(v["altura"], v["manteo_talud"],
                                            v["buzamiento"], show=False))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    botones_accion(n, obtener_valores, calcular, graficar)


# ─────────────────────────────────────────────────────────
#  FALLA CIRCULAR
# ─────────────────────────────────────────────────────────
def mostrar_falla_circular():
    campos = [
        ("Altura del talud",     "altura",          "m"),
        ("Cohesión",             "cohesion",        "kPa"),
        ("Ángulo de fricción",   "friction",        "°"),
        ("Ángulo del talud",     "angulo_talud",    "°"),
        ("Peso específico",      "peso_especifico", "kN/m³"),
        ("Radio de falla",       "radio",           "m"),
        ("Número de dovelas",    "dovelas",         "—"),
        ("Profundidad",          "profundidad",     "m"),
        ("Origen X de la falla", "coordenada_X",    "m"),
    ]
    n = construir_campos(campos)

    def obtener_valores():
        v = leer_numeros(enteros=("dovelas",))
        if v is None:
            return None
        if v["altura"] <= 0:
            return error("La altura debe ser un número positivo.")
        if v["cohesion"] < 0:
            return error("La cohesión no puede ser negativa.")
        if not 0 < v["friction"] < 90:
            return error("Fricción debe estar entre 0 y 90°.")
        if not 0 < v["angulo_talud"] < 90:
            return error("Ángulo del talud debe estar entre 0 y 90°.")
        if v["peso_especifico"] <= 0:
            return error("El peso específico debe ser un número positivo.")
        if v["radio"] <= 0:
            return error("El radio debe ser un número positivo.")
        if v["dovelas"] <= 1:
            return error("El número de dovelas debe ser mayor que 1.")
        if v["profundidad"] <= 0:
            return error("La profundidad debe ser un número positivo.")
        return v

    def calcular():
        v = obtener_valores()
        if v is None:
            return
        try:
            r = analisis_falla_circular(v["altura"], v["cohesion"], v["friction"],
                                        v["angulo_talud"], v["peso_especifico"],
                                        v["radio"], v["dovelas"], v["profundidad"])
            mostrar_resultado(
                f"Tipo: Falla Circular\n\n"
                f"FS                 = {r['FS']:.4f}\n"
                f"Momento resistente = {r['Mr_total']:.4f}\n"
                f"Momento actuante   = {r['M_total']:.4f}"
            )
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))

    def graficar():
        v = obtener_valores()
        if v is None:
            return
        try:
            ancho = v["altura"] / math.tan(math.radians(v["angulo_talud"]))
            mostrar_figura(visualizar_falla_circular(
                v["radio"], v["altura"], v["dovelas"], v["angulo_talud"],
                ancho, v["coordenada_X"], show=False))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    botones_accion(n, obtener_valores, calcular, graficar)


# ─────────────────────────────────────────────────────────
#  SELECTOR DE TIPO DE FALLA
# ─────────────────────────────────────────────────────────
opciones = [
    ("Falla Plana",      1, mostrar_falla_plana),
    ("Falla por Cuña",   2, mostrar_falla_cuna),
    ("Falla por Vuelco", 3, mostrar_falla_volcamiento),
    ("Falla Circular",   4, mostrar_falla_circular),
]
for fila, (texto, valor, comando) in enumerate(opciones, start=1):
    Radiobutton(frame_izq, text=texto, variable=var, value=valor,
                command=comando, activebackground=COLOR_PANEL,
                font=("Arial", 10)).grid(row=fila, column=0, columnspan=3,
                                         sticky="w", pady=3)


if __name__ == "__main__":
    root.mainloop()
