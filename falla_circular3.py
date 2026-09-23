import numpy as np
import math
import matplotlib.pyplot as plt


def analisis_falla_circular(altura, cohesion, friccion, angulo_talud, peso_especifico, radio, dovelas, profundidad, mostrar_pasos=False):
    ancho_talud = altura / np.tan(np.radians(angulo_talud))
    ancho_dovela = ancho_talud / dovelas
    a = ancho_dovela / 2
    Mr_total = 0.0
    M_total = 0.0

    for n in range(dovelas):
        factor_alpha = a / radio
        alpha1 = np.arcsin(factor_alpha)
        alpha = np.degrees(alpha1)
        delta_L = ancho_dovela / np.cos(np.radians(alpha))
        h = a * (np.tan(np.radians(angulo_talud)) - np.tan(np.radians(alpha)))
        peso_dovela = (peso_especifico * delta_L * h * profundidad)
        Mr = (cohesion * delta_L) + (peso_dovela * np.cos(np.radians(alpha)) * np.tan(np.radians(friccion)))
        M = peso_dovela * np.sin(np.radians(alpha))

        a += ancho_dovela
        Mr_total += Mr
        M_total += M
    
    if M_total == 0:
        raise ValueError("El momento actuante total es cero, no se puede calcular el factor de seguridad.")

    Security_factor = Mr_total / M_total

    return {
        "FS": Security_factor,
        "Mr_total": Mr_total,
        "M_total": M_total,
        "radio_ajustado": radio,
    }


def visualizar_falla_circular(radio, altura, dovelas, angulo_talud, ancho_talud, coordenada_X, show=True):
    """Visualiza la falla circular con dovelas.

    Parámetros:
    - radio: radio del círculo de falla (R)
    - altura: altura del talud (H)
    - dovelas: número de dovelas (divisiones)
    - angulo_talud: ángulo del talud en grados
    - ancho_talud: ancho de la base del talud
    """
    fig, ax = plt.subplots(figsize=(14, 10))

    angulo_rad = np.radians(angulo_talud)
    x_inf_izq = ancho_talud
    y_inf_izq = 0
    x_sup = ancho_talud
    y_sup = altura
    x_inf_der = 0
    y_inf_der = 0

    radio_requerido = (ancho_talud**2 + altura**2) / (2 * altura)
    if abs(radio_requerido - radio) > 1e-6:
        radio = radio_requerido

    centro_x = coordenada_X
    centro_y = radio

    theta = np.linspace(0, 2 * np.pi, 200)
    x_circulo = centro_x + radio * np.cos(theta)
    y_circulo = centro_y + radio * np.sin(theta)
    ax.plot(x_circulo, y_circulo, 'r-', linewidth=3)

    talud_x = [x_inf_izq, x_sup, x_inf_der, x_inf_izq]
    talud_y = [y_inf_izq, y_sup, y_inf_der, y_inf_izq]
    ax.fill(talud_x, talud_y, color='tan', alpha=0.4, edgecolor='black', linewidth=2.5)

    ax.plot([x_inf_izq, x_sup], [y_inf_izq, y_sup], 'k-', linewidth=2.5)
    ax.plot([x_sup, x_inf_der], [y_sup, y_inf_der], 'k-', linewidth=2.5)
    ax.plot([x_inf_der, x_inf_izq], [y_inf_der, y_inf_izq], 'k-', linewidth=2.5)

    for i in range(1, dovelas):
        x_dovela = ancho_talud * i / dovelas
        y_hipotenusa = altura * x_dovela / ancho_talud

        if abs(x_dovela) > radio:
            continue

        delta = np.sqrt(max(0.0, radio**2 - x_dovela**2))
        y_circulo_punto = centro_y - delta

        if y_circulo_punto >= y_hipotenusa:
            continue

        ax.plot([x_dovela, x_dovela], [y_hipotenusa, y_circulo_punto], 'b-', linewidth=2, alpha=0.8)

    x_radio = centro_x + radio * np.cos(np.radians(45))
    y_radio = centro_y + radio * np.sin(np.radians(45))
    ax.plot([centro_x, x_radio], [centro_y, y_radio], 'orange', linewidth=3, label=f'Radio (R={radio}m)')
    ax.plot([x_sup, x_sup], [y_inf_izq, y_sup], 'orange', linewidth=3)
    ax.text(x_sup + radio * 0.05, y_sup / 2, f'H={altura}m', fontsize=12, color='orange', fontweight='bold', va='center')
    ax.text(x_inf_der + 0.3, y_inf_der + 0.3, f'α={angulo_talud}°', fontsize=11, color='black', fontweight='bold')

    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('Distancia (m)', fontsize=12)
    ax.set_ylabel('Altura (m)', fontsize=12)
    ax.set_title(
        f'Análisis de Falla Circular por Dovelas\nRadio (R): {radio:.2f}m | Altura (H): {altura:.2f}m | Dovelas: {dovelas} | Ángulo: {angulo_talud}°',
        fontsize=14,
        fontweight='bold'
    )

    margen = radio * 0.15
    ax.set_xlim(-radio - margen, max(radio, ancho_talud) + margen)
    ax.set_ylim(-margen, max(2 * radio, altura) + margen)
    ax.plot(0, 0, 'ko', markersize=8)

    plt.tight_layout()
    if show:
        plt.show()

    return fig