

# Solicitud de datos para el análisis de estabilidad de taludes

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from matplotlib.lines import Line2D


def analisis_falla_plana(data):
    friccion = data["friccion"]
    manteo_plano_falla = data["manteo_plano_falla"]
    manteo_talud = data["manteo_talud"]
    rumbo_talud = data["rumbo_talud"]
    rumbo_plano_falla = data["rumbo_plano_falla"]
    profundidad = data["profundidad"]

    manteo_plano_falla_rad = math.radians(manteo_plano_falla)
    manteo_talud_rad = math.radians(manteo_talud)
    friccion_rad = math.radians(friccion)

    # Criterio cinemático: si la orientación permite el deslizamiento.
    cinematicamente_posible = (
        (manteo_talud > manteo_plano_falla > friccion)
        and (abs(rumbo_talud - rumbo_plano_falla) <= 20)
    )
    if cinematicamente_posible:
        resultado = "Cinemáticamente, el deslizamiento es posible."
    else:
        resultado = "Cinemáticamente, el deslizamiento no es posible."

    largo_falla = data["altura"] / math.sin(manteo_plano_falla_rad)
    largo_talud = data["altura"] / math.sin(manteo_talud_rad)
    largo_triangulo_1 = largo_talud * math.cos(manteo_talud_rad - manteo_plano_falla_rad)
    largo_triangulo_2 = largo_falla - largo_triangulo_1
    altura_triangulos = math.sqrt(largo_talud**2 - largo_triangulo_1**2)
    área_triangulo_1 = (largo_triangulo_1 * altura_triangulos) / 2
    área_triangulo_2 = (largo_triangulo_2 * altura_triangulos) / 2
    área_total = área_triangulo_1 + área_triangulo_2
    masa_total = área_total * data["densidad"] * profundidad * 1000
    peso_total = (masa_total * 9.81) / 1000000
    area_falla = largo_falla * profundidad
    security_factor = (
        (data["cohesion"] * area_falla + peso_total * math.cos(manteo_plano_falla_rad) * math.tan(friccion_rad))
        / (peso_total * math.sin(manteo_plano_falla_rad))
    )
    # El factor de seguridad da el veredicto cuantitativo, coherente con el criterio cinemático.
    veredicto = "estable (FS ≥ 1)" if security_factor >= 1 else "inestable (FS < 1)"
    resultado_fs = f"Factor de seguridad: {security_factor:.2f} → {veredicto}"
    print(resultado)
    print(resultado_fs)
    return {
        "resultado": resultado,
        "factor_seguridad": security_factor,
        "mensaje": resultado_fs,
    }


def plot_slope(manteo_plano_falla, manteo_talud, altura, show=True, start_frac=0.12,):

    # pendientes de las rectas
    tan_wf = math.tan(math.radians(manteo_talud))   # pendiente de la hipotenusa
    tan_wp = math.tan(math.radians(manteo_plano_falla))   # pendiente de la línea de falla
    if abs(tan_wf) < 1e-9:
        raise ValueError("manteo talud (wf) demasiado horizontal")

    crest_x = altura / tan_wf

    fig, ax = plt.subplots(figsize=(8,5))

    # Triángulo: base y talud (sin plano vertical ni relleno)
    ax.plot([0, crest_x], [0, 0], color='k', linewidth=1)
    ax.plot([0, crest_x], [0, altura], color='k', linewidth=2)

    # Línea de falla
    x0 = 0.0
    x_int = crest_x
    y_end = tan_wp * x_int
    ax.plot([x0, x_int], [0, y_end], color='red', linewidth=2)
    # Si la línea de falla queda por encima del talud (no corta el interior), añadir una nota opcional
    if y_end > altura:
        ax.text(crest_x * 0.2, altura * 0.95, 'Plano de falla más inclinado que el talud, no fallará', color='red')

    # Altura
    ax.annotate('', xy=(crest_x + 0.035 * crest_x, 0), xytext=(crest_x + 0.035 * crest_x, altura), arrowprops=dict(arrowstyle='<->'))
    ax.text(crest_x + 0.04 * crest_x, altura / 2, f'H = {altura} m', va='center')

    # Ángulos en la esquina del toe, con más separación
    arc_rx = 0.12 * crest_x
    arc_ry = 0.12 * altura
    arc_wp = Arc((0, 0), width=arc_rx, height=arc_ry, angle=0, theta1=0, theta2=manteo_plano_falla, color='red', lw=2)
    arc_wf = Arc((0, 0), width=arc_rx * 1.8, height=arc_ry * 1.8, angle=0, theta1=0, theta2=manteo_talud, color='green', lw=2)
    ax.add_patch(arc_wp)
    ax.add_patch(arc_wf)

    # colocar etiquetas radialmente fuera de los arcos y separarlas verticalmente
    rad_wp_mid = math.radians(manteo_plano_falla / 2)
    rad_wf_mid = math.radians(manteo_talud / 2)
    shift_wp = 0.06 * crest_x
    shift_wf = 0.02 * crest_x
    label_wp_x = (arc_rx * 0.5) * math.cos(rad_wp_mid) - shift_wp
    label_wp_y = (arc_ry * 0.5) * math.sin(rad_wp_mid) - 0.03 * altura
    label_wf_x = (arc_rx * 1.1) * math.cos(rad_wf_mid) - shift_wf
    label_wf_y = (arc_ry * 1.15) * math.sin(rad_wf_mid) + 0.03 * altura
    # eliminar números del triángulo: solo mostrar las líneas/arcos de ángulo
    # Añadir leyenda que indique a cuántos grados equivale cada color
    legend_handles = [
        Line2D([0], [0], color='red', lw=2, label=f'Plano de falla: {int(manteo_plano_falla)}°'),
        Line2D([0], [0], color='green', lw=2, label=f'Talud: {int(manteo_talud)}°')
    ]
    ax.legend(handles=legend_handles, loc='upper left')

    ax.set_xlim(-0.03 * crest_x, crest_x + 0.18 * crest_x)
    ax.set_ylim(-0.02 * altura, altura + 0.10 * altura)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('m')
    ax.set_ylabel('m')
    ax.set_title('Vista lateral del talud y plano de falla')
    plt.tight_layout()

    if show:
        plt.show()

    return fig


if __name__ == "__main__":
    # El módulo puede ejecutarse de forma independiente si se desea,
    # pero al importarlo no pedirá datos por consola.
    pass



