import math

def normal_desde_dip_dipdir(dip_plano_deg, dip_direction_plano_deg):
    """Calcula la normal unitaria de un plano definido por dip y dip direction.

    Parámetros:
    - dip_deg: ángulo de buzamiento del plano (0 a 90 grados)
    - dip_dir_deg: dirección de buzamiento (azimuth 0-360 desde Norte, en sentido horario)

    Retorna un tuple (nx, ny, nz) con coordenadas en sistema x=Este, y=Norte, z=Arriba.
    """
    dip = math.radians(dip_plano_deg)
    dip_dir = math.radians(dip_direction_plano_deg)

    nx = math.sin(dip) * math.sin(dip_dir)
    ny = math.sin(dip) * math.cos(dip_dir)
    nz = math.cos(dip)

    longitud = math.sqrt(nx * nx + ny * ny + nz * nz)
    if longitud == 0:
        raise ValueError("La normal del plano no puede ser el vector nulo.")

    return nx / longitud, ny / longitud, nz / longitud

def angulo_entre_normales(nA, nB):
    """Calcula ξ como el ángulo entre dos normales unitarias."""
    dot = nA[0] * nB[0] + nA[1] * nB[1] + nA[2] * nB[2]
    dot = max(-1.0, min(1.0, dot))
    return math.degrees(math.acos(dot))

def linea_interseccion(nA, nB):
    """Calcula el vector de la línea de intersección entre dos planos."""
    lx = nA[1] * nB[2] - nA[2] * nB[1]
    ly = nA[2] * nB[0] - nA[0] * nB[2]
    lz = nA[0] * nB[1] - nA[1] * nB[0]
    return lx, ly, lz

def psi_i_desde_linea(l):
    """Calcula ψ_i a partir de la línea de intersección L."""
    lx, ly, lz = l
    horizontal = math.hypot(lx, ly)
    if horizontal == 0:
        raise ValueError("La línea de intersección es vertical, no se puede calcular ψ_i.")
    return math.degrees(math.atan(abs(lz) / horizontal))


def factor_seguridad_cuna(beta_deg, xi_deg, friction_deg, psi_i_deg):
    """Calcula el factor de seguridad FS usando la fórmula del libro."""
    beta = math.radians(beta_deg)
    xi = math.radians(xi_deg)
    phi = math.radians(friction_deg)
    psi_i = math.radians(psi_i_deg)

    if xi_deg <= 0 or xi_deg >= 180:
        raise ValueError("El ángulo ξ debe estar entre 0 y 180 grados.")
    if psi_i_deg <= 0 or psi_i_deg >= 90:
        raise ValueError("El buzamiento ψ_i debe estar entre 0 y 90 grados.")
    if beta_deg < 0 or beta_deg >= 90:
        raise ValueError("El ángulo β debe estar entre 0 y 90 grados.")
    if friction_deg < 0 or friction_deg >= 90:
        raise ValueError("El ángulo de fricción φ debe estar entre 0 y 90 grados.")

    sin_beta = math.sin(beta)
    sin_xi_half = math.sin(xi / 2.0)
    tan_phi = math.tan(phi)
    tan_psi_i = math.tan(psi_i)

    if sin_xi_half == 0:
        raise ValueError("El ángulo ξ/2 no puede ser 0° ni 180°.")
    if tan_psi_i == 0:
        raise ValueError("El buzamiento ψ_i no puede ser 0°.")

    return (sin_beta / sin_xi_half) * (tan_phi / tan_psi_i)


def plot_angulo_cuna(beta_deg, xi_deg, show=True, filename=None):
    """Genera una figura con los ángulos β (derecha) y ξ/2 (izquierda).

    Si show es True, muestra el gráfico en pantalla. Si filename se proporciona,
    también guarda la imagen en un archivo.
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Arc
        from matplotlib.lines import Line2D
    except ImportError as exc:
        raise ImportError("matplotlib es necesario para generar la figura.") from exc

    if beta_deg <= 0 or beta_deg >= 90:
        raise ValueError("El ángulo β debe estar entre 0 y 90 grados.")
    if xi_deg <= 0 or xi_deg >= 180:
        raise ValueError("El ángulo ξ debe estar entre 0 y 180 grados.")

    xi_half = xi_deg / 2.0
    beta_rad = math.radians(beta_deg)
    xi_half_rad = math.radians(xi_half)

    top_y = 1.0
    x_right = math.tan(beta_rad) * top_y
    x_left = -math.tan(xi_half_rad) * top_y

    fig, ax = plt.subplots(figsize=(7, 5))

    # Superficie superior y cuña
    ax.plot([x_left * 1.05, x_right * 1.05], [top_y, top_y], color="black", linewidth=2)
    ax.plot([0.0, x_left], [0.0, top_y], color="black", linewidth=3)
    ax.plot([0.0, x_right], [0.0, top_y], color="black", linewidth=3)

    # Línea interior de la cuña en rojo
    ax.plot([0.0, 0.0], [0.0, top_y], color="red", linewidth=2)

    # Arco de ángulo β solamente
    arc_radius = 0.18
    arc_beta = Arc((0.0, 0.0), arc_radius * 2, arc_radius * 2,
                   angle=90, theta1=0, theta2=beta_deg,
                   color="red", linewidth=2)
    ax.add_patch(arc_beta)

    ax.text(0.12 * math.sin(beta_rad / 2), 0.12 * math.cos(beta_rad / 2), r"$\beta$",
            color="red", fontsize=10, ha="center", va="center")
    ax.text(-0.12 * math.sin(xi_half_rad / 2), 0.12 * math.cos(xi_half_rad / 2), r"$\xi/2$",
            color="red", fontsize=10, ha="center", va="center")

    legend_handles = [
        Line2D([0], [0], color='red', lw=2, label=f'β = {beta_deg:.1f}°'),
        Line2D([0], [0], color='red', lw=2, label=f'ξ/2 = {xi_half:.1f}°')
    ]
    ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.02, 0.98),
              frameon=False, fontsize=10)
    fig.subplots_adjust(right=0.78)

    ax.set_aspect("equal")
    ax.set_xlim(x_left * 1.25, x_right * 1.05)
    ax.set_ylim(-0.15, top_y + 0.15)
    ax.axis("off")
    ax.set_title("Geometría de la cuña con ángulos β y ξ/2", fontsize=14)

    if filename:
        fig.savefig(filename, dpi=200, bbox_inches="tight")
    if show:
        plt.show()

    return fig

def main(
    dip_talud=None,
    dip_plano1=None,
    dip_direction_plano1=None,
    dip_plano2=None,
    dip_direction_plano2=None,
    friction=None,
    beta=None,
):
    if dip_talud is None:
        data = {
            "dip_talud": float(input("Ingrese el dip del talud (en grados): ")),
            "dip_plano1": float(input("Ingrese el dip de la primera falla (en grados): ")),
            "dip_direction_plano1": float(input("Ingrese el dip direction de la primera falla (en grados): ")),
            "dip_plano2": float(input("Ingrese el dip de la segunda falla (en grados): ")),
            "dip_direction_plano2": float(input("Ingrese el dip direction de la segunda falla (en grados): ")),
            "friction": float(input("Ingrese el ángulo de fricción interna (en grados): ")),
            "beta": float(input("Ingrese el ángulo de inclinación de la cuña (β) (en grados): "))
        }
        dip_talud = data["dip_talud"]
        dip_plano1 = data["dip_plano1"]
        dip_direction_plano1 = data["dip_direction_plano1"]
        dip_plano2 = data["dip_plano2"]
        dip_direction_plano2 = data["dip_direction_plano2"]
        friction = data["friction"]
        beta = data["beta"]

    try:
        n1 = normal_desde_dip_dipdir(dip_plano1, dip_direction_plano1)
        n2 = normal_desde_dip_dipdir(dip_plano2, dip_direction_plano2)

        xi = angulo_entre_normales(n1, n2)
        linea = linea_interseccion(n1, n2)
        psi_i = psi_i_desde_linea(linea)

        fs = factor_seguridad_cuna(beta, xi, friction, psi_i)
        potencial_inestable = dip_talud > psi_i > friction
        if potencial_inestable:
            estado = "Potencialmente inestable"
        else:
            estado = "Estable" if fs >= 1.0 else "Inestable"

        print(f"\nξ (ángulo entre planos) = {xi:.3f}°")
        print(f"ψ_i (manteo de la línea de deslizamiento) = {psi_i:.3f}°")
        print(f"FS = {fs:.4f}")
        print(f"Evaluación: {estado}")
        if potencial_inestable:
            print("Condición detectada: Manteo talud > Manteo línea de deslizamiento > Ángulo de fricción interna.")

        try:
            plot_angulo_cuna(beta, xi, show=True)
            print("Gráfico mostrado en pantalla.")
        except ImportError as exc:
            print(f"No se pudo generar el gráfico: {exc}")
        except ValueError as exc:
            print(f"No se pudo generar el gráfico: {exc}")

    except ValueError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
