import math


def analisis_falla_volcamiento(friccion, manteo_talud, altura, buzamiento_plano):
    """Analiza la estabilidad de un talud frente a volcamiento.

    Parámetros:
    - friccion: ángulo de fricción interna del suelo en grados.
    - manteo_talud: manteo del talud en grados.
    - altura: altura del talud en metros.
    - buzamiento_plano: buzamiento del plano de falla en grados.
    """
    if friccion < 0 or friccion >= 90:
        raise ValueError("El ángulo de fricción debe estar entre 0 y 90 grados.")
    if manteo_talud < 0 or manteo_talud >= 90:
        raise ValueError("El manteo del talud debe estar entre 0 y 90 grados.")
    if altura <= 0:
        raise ValueError("La altura debe ser un número positivo.")
    if buzamiento_plano < 0 or buzamiento_plano >= 90:
        raise ValueError("El buzamiento del plano de falla debe estar entre 0 y 90 grados.")

    if buzamiento_plano <= manteo_talud:
        estado = "Inestable no aplicable"
        mensaje = "El plano de falla no es más inclinado que el talud."
    elif 90 - buzamiento_plano > manteo_talud - friccion:
        estado = "Potencialmente inestable"
        mensaje = "El talud es potencialmente inestable bajo condiciones de volcamiento."
    else:
        estado = "Potencialmente estable"
        mensaje = "El talud es potencialmente estable frente a volcamiento."

    return {
        "estado": estado,
        "mensaje": mensaje,
        "friccion": friccion,
        "manteo_talud": manteo_talud,
        "buzamiento_plano": buzamiento_plano,
        "altura": altura,
    }


def dibujar_triangulos(altura, dip_talud, dip_falla, show=True):
    """Dibuja el talud y el plano de falla para análisis de volcamiento."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError("matplotlib es necesario para graficar la falla por volcamiento.") from exc

    if altura <= 0:
        raise ValueError("La altura debe ser un número positivo.")
    if dip_talud <= 0 or dip_talud >= 90:
        raise ValueError("El manteo del talud debe estar entre 0 y 90 grados.")
    if dip_falla <= 0 or dip_falla >= 90:
        raise ValueError("El buzamiento del plano de falla debe estar entre 0 y 90 grados.")
    if dip_falla >= dip_talud:
        raise ValueError("El buzamiento del plano de falla debe ser menor que el manteo del talud para graficar correctamente.")

    ang_talud = math.radians(dip_talud)
    ang_falla = math.radians(dip_falla)
    base_grande = altura / math.tan(ang_talud)
    y_interseccion = base_grande * math.tan(ang_falla)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot([0, base_grande, base_grande, 0], [0, 0, altura, 0], color='black', linewidth=2)
    ax.plot([0, base_grande], [0, y_interseccion], color='black', linewidth=1.5)
    ax.fill([0, base_grande, base_grande], [0, y_interseccion, altura], color='red', alpha=0.5)

    ax.text(base_grande * 0.5, -altura * 0.06, f"Altura = {altura:.2f} m", ha='center', va='top')
    ax.text(base_grande * 0.02, altura * 0.45, f"Dip talud = {dip_talud:.1f}°", ha='left', va='center')
    ax.text(base_grande * 0.98, y_interseccion * 0.25, f"Dip falla = {dip_falla:.1f}°", ha='right', va='center')

    margen = base_grande * 0.1
    ax.set_xlim(-margen, base_grande + margen)
    ax.set_ylim(0, altura * 1.15)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Distancia horizontal (m)')
    ax.set_ylabel('Altura (m)')
    ax.set_title('Falla por volcamiento: talud y plano de falla')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    if show:
        plt.show()

    return fig


def main(
    friccion=None,
    manteo_talud=None,
    altura=None,
    buzamiento_plano=None,
):
    if friccion is None:
        friccion = float(input("Ingrese el ángulo de fricción interna del suelo (en grados): "))
        manteo_talud = float(input("Ingrese el manteo del talud (en grados): "))
        altura = float(input("Ingrese la altura del talud (en metros): "))
        buzamiento_plano = float(input("Ingrese el buzamiento del plano de falla (en grados): "))

    resultado = analisis_falla_volcamiento(friccion, manteo_talud, altura, buzamiento_plano)
    print(resultado["estado"])
    print(resultado["mensaje"])


if __name__ == "__main__":
    main()
