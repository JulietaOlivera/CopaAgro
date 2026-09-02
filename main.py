# ==============================================================================
# LA COPA AGRO - Aplicación de gestión de torneo deportivo
# ==============================================================================
# Versión con interfaz visual personalizada.
#
# IMPORTANTE:
# - La lógica del torneo se mantiene basada en st.session_state.
# - Los datos de ejemplo están marcados para ser reemplazados.
# - Para una versión definitiva con varios usuarios simultáneos se recomienda
#   conectar esta aplicación a una base de datos persistente.
# ==============================================================================

import streamlit as st
from html import escape


# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================

st.set_page_config(
    page_title="La Copa Agro",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

PIN_ADMIN = "JBJ2026"

TRIBUS = {
    "Maíz": {"color": "#35B86B", "dark": "#17643A", "texto": "#FFFFFF"},
    "Trigo": {"color": "#F4C542", "dark": "#9A7410", "texto": "#111111"},
    "Angus": {"color": "#E5484D", "dark": "#8F2228", "texto": "#FFFFFF"},
    "Holando": {"color": "#7B8794", "dark": "#252B32", "texto": "#FFFFFF"},
}

EQUIPOS_POR_TRIBU = {
    "Fútbol Masculino": 3,
    "Fútbol Femenino": 2,
    "Básquet": 2,
    "Vóley Mixto": 1,
}

TAMANO_GRUPO = {
    "Fútbol Masculino": 3,
    "Fútbol Femenino": 4,
    "Básquet": 4,
    "Vóley Mixto": None,
}

LIMITES_MARCADOR = {
    "Fútbol Masculino": 30,
    "Fútbol Femenino": 30,
    "Básquet": 150,
    "Vóley Mixto": 50,
}

CLASIFICADOS_POR_GRUPO = 2
DISCIPLINAS = list(EQUIPOS_POR_TRIBU.keys())
NOMBRES_GRUPOS = ["A", "B", "C", "D", "E", "F"]


# ==============================================================================
# CSS Y COMPONENTES VISUALES
# ==============================================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #0B0D0F;
        --panel: #13171B;
        --panel-2: #1A2025;
        --line: rgba(255,255,255,.10);
        --text: #F4F5F6;
        --muted: #9DA6AE;
        --accent: #F4C542;
    }

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 85% 5%, rgba(244,197,66,.10), transparent 26%),
            radial-gradient(circle at 8% 35%, rgba(53,184,107,.08), transparent 28%),
            var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(11,13,15,.85);
    }

    [data-testid="stSidebar"] {
        background: #101418;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] * {
        font-family: 'Montserrat', sans-serif;
    }

    [data-testid="stSidebar"] .stRadio label {
        padding: 7px 8px;
        border-radius: 8px;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1450px;
    }

    h1, h2, h3, h4 {
        font-family: 'Bebas Neue', sans-serif !important;
        letter-spacing: 1.5px;
        color: #FFFFFF !important;
    }

    h1 {
        font-size: 3.7rem !important;
        line-height: .95 !important;
    }

    h2 {
        font-size: 2.5rem !important;
    }

    h3 {
        font-size: 1.9rem !important;
    }

    p, li, label, .stCaption {
        font-family: 'Montserrat', sans-serif !important;
    }

    .hero {
        position: relative;
        overflow: hidden;
        min-height: 320px;
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 28px;
        padding: 48px;
        margin-bottom: 28px;
        background:
            linear-gradient(120deg, rgba(11,13,15,.98) 10%, rgba(20,27,30,.94) 55%, rgba(25,38,30,.92)),
            linear-gradient(135deg, #12171A, #0B0D0F);
        box-shadow: 0 25px 70px rgba(0,0,0,.30);
    }

    .hero:before {
        content: "";
        position: absolute;
        width: 420px;
        height: 420px;
        right: -130px;
        top: -170px;
        border-radius: 50%;
        border: 70px solid rgba(244,197,66,.10);
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: 70px;
        bottom: -170px;
        border-radius: 50%;
        background: rgba(53,184,107,.08);
    }

    .hero-kicker {
        position: relative;
        z-index: 2;
        color: #F4C542;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .hero-title {
        position: relative;
        z-index: 2;
        font-family: 'Bebas Neue', sans-serif;
        font-size: clamp(64px, 8vw, 116px);
        line-height: .82;
        letter-spacing: 3px;
        color: #FFFFFF;
        margin: 0;
    }

    .hero-subtitle {
        position: relative;
        z-index: 2;
        color: #B7C0C7;
        font-size: 16px;
        margin-top: 18px;
        max-width: 620px;
    }

    .section-label {
        color: #F4C542;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin: 25px 0 10px 2px;
    }

    .tribe-card {
        position: relative;
        overflow: hidden;
        min-height: 185px;
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,.10);
        background: linear-gradient(145deg, #181D21, #101316);
        box-shadow: 0 12px 35px rgba(0,0,0,.18);
    }

    .tribe-card:before {
        content: "";
        position: absolute;
        width: 150px;
        height: 150px;
        right: -55px;
        top: -55px;
        border-radius: 50%;
        background: var(--tribe-color);
        opacity: .13;
    }

    .tribe-name {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 30px;
        letter-spacing: 2px;
        color: #FFFFFF;
    }

    .tribe-points {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 64px;
        line-height: .9;
        margin-top: 20px;
        color: var(--tribe-color);
    }

    .tribe-caption {
        color: #8E989F;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    .sport-card {
        min-height: 145px;
        border-radius: 18px;
        padding: 22px;
        background: #14191D;
        border: 1px solid rgba(255,255,255,.09);
        transition: transform .18s ease, border-color .18s ease;
    }

    .sport-card:hover {
        transform: translateY(-4px);
        border-color: rgba(244,197,66,.45);
    }

    .sport-name {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 29px;
        letter-spacing: 1.5px;
        color: #FFFFFF;
    }

    .sport-meta {
        color: #929BA2;
        font-size: 12px;
        margin-top: 8px;
    }

    .match-card {
        border-radius: 17px;
        padding: 18px 20px;
        background: linear-gradient(145deg, #171C20, #111417);
        border: 1px solid rgba(255,255,255,.09);
        margin-bottom: 12px;
    }

    .match-top {
        display: flex;
        justify-content: space-between;
        color: #7F8991;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.3px;
        margin-bottom: 12px;
    }

    .match-teams {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 12px;
    }

    .team {
        font-weight: 700;
        color: #F1F3F4;
        font-size: 14px;
    }

    .team.right {
        text-align: right;
    }

    .match-score {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 32px;
        color: #F4C542;
        white-space: nowrap;
    }

    .announcement {
        border-left: 4px solid #F4C542;
        border-radius: 0 14px 14px 0;
        background: #171C20;
        padding: 15px 18px;
        margin-bottom: 10px;
        color: #D9DEE2;
    }

    .timeline-item {
        display: grid;
        grid-template-columns: 110px 1fr;
        gap: 18px;
        padding: 18px 0;
        border-bottom: 1px solid rgba(255,255,255,.08);
    }

    .timeline-time {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 25px;
        color: #F4C542;
    }

    .timeline-event {
        color: #E9ECEF;
        font-weight: 600;
        padding-top: 4px;
    }

    .rule-card {
        background: #151A1E;
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 18px;
        padding: 24px;
        min-height: 170px;
    }

    .rule-title {
        font-family: 'Bebas Neue', sans-serif;
        color: #F4C542;
        font-size: 26px;
        letter-spacing: 1.5px;
        margin-bottom: 10px;
    }

    .champion-banner {
        border-radius: 20px;
        padding: 28px;
        margin-top: 20px;
        background:
            linear-gradient(120deg, rgba(244,197,66,.14), rgba(244,197,66,.03)),
            #151A1E;
        border: 1px solid rgba(244,197,66,.35);
        text-align: center;
    }

    .champion-label {
        color: #F4C542;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    .champion-name {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 54px;
        letter-spacing: 2px;
        color: #FFFFFF;
        margin: 8px 0;
    }

    .admin-badge {
        display: inline-block;
        padding: 7px 11px;
        border-radius: 999px;
        background: rgba(53,184,107,.13);
        color: #65D994;
        border: 1px solid rgba(53,184,107,.30);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .public-badge {
        display: inline-block;
        padding: 7px 11px;
        border-radius: 999px;
        background: rgba(255,255,255,.06);
        color: #AEB7BE;
        border: 1px solid rgba(255,255,255,.10);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .mini-stat {
        background: #151A1E;
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 15px;
        padding: 17px;
    }

    .mini-stat-number {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 36px;
        color: #FFFFFF;
    }

    .mini-stat-label {
        color: #89939A;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }

    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,.12);
        background: #20262B;
        color: #FFFFFF;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        min-height: 42px;
        transition: all .15s ease;
    }

    .stButton > button:hover {
        border-color: #F4C542;
        color: #F4C542;
        transform: translateY(-1px);
    }

    .stTextInput input,
    .stNumberInput input,
    .stSelectbox [data-baseweb="select"] > div {
        background: #151A1E !important;
        color: #FFFFFF !important;
        border-color: rgba(255,255,255,.12) !important;
        border-radius: 10px !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 15px;
        overflow: hidden;
    }

    [data-testid="stExpander"] {
        background: #151A1E;
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 14px;
    }

    hr {
        border-color: rgba(255,255,255,.08);
    }

    @media (max-width: 800px) {
        .hero {
            padding: 30px 24px;
            min-height: 260px;
        }
        .hero-title {
            font-size: 66px;
        }
        .timeline-item {
            grid-template-columns: 85px 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# DATOS
# ==============================================================================

def generar_partidos_round_robin(equipos_nombres, grupo_label, horarios=None):
    partidos = []

    for i in range(len(equipos_nombres)):
        for j in range(i + 1, len(equipos_nombres)):
            partidos.append(
                {
                    "grupo": grupo_label,
                    "local": equipos_nombres[i],
                    "visitante": equipos_nombres[j],
                    "marcador_local": None,
                    "marcador_visitante": None,
                    "horario": "10:00",
                    "jugado": False,
                }
            )

    if horarios:
        for partido, horario in zip(partidos, horarios):
            partido["horario"] = horario

    return partidos


def crear_equipos_disciplina(disciplina):
    equipos = []
    orden_tribus = list(TRIBUS.keys())
    cantidad_por_tribu = EQUIPOS_POR_TRIBU[disciplina]
    contador_tribu = {t: 0 for t in orden_tribus}

    total_equipos = cantidad_por_tribu * len(orden_tribus)

    for n in range(total_equipos):
        tribu = orden_tribus[n % len(orden_tribus)]
        contador_tribu[tribu] += 1

        # ==============================================================
        # REEMPLAZAR CON NOMBRES REALES DE EQUIPOS
        # ==============================================================
        nombre = f"Equipo {contador_tribu[tribu]} {disciplina} ({tribu})"

        equipos.append(
            {
                "nombre": nombre,
                "tribu": tribu,
                # REEMPLAZAR CON PARTICIPANTES REALES
                "participantes": [f"Jugador/a {p + 1}" for p in range(8)],
            }
        )

    return equipos


def armar_grupos(equipos, disciplina):
    tam = TAMANO_GRUPO[disciplina]
    nombres = [e["nombre"] for e in equipos]

    if tam is None:
        return {"Único": nombres}

    grupos = {}
    for idx, inicio in enumerate(range(0, len(nombres), tam)):
        grupos[NOMBRES_GRUPOS[idx]] = nombres[inicio : inicio + tam]

    return grupos


def inicializar_disciplina(disciplina):
    equipos = crear_equipos_disciplina(disciplina)
    grupos = armar_grupos(equipos, disciplina)

    partidos = []

    # ==============================================================
    # FÚTBOL MASCULINO
    # ==============================================================
    if disciplina == "Fútbol Masculino":

        fixture = {
            "A": [
                (0, 1, "09:30"),
                (1, 2, "10:30"),
                (2, 0, "11:30"),
            ],
            "B": [
                (0, 1, "09:30"),
                (1, 2, "10:30"),
                (2, 0, "11:30"),
            ],
            "C": [
                (0, 1, "10:00"),
                (1, 2, "11:00"),
                (2, 0, "12:00"),
            ],
            "D": [
                (0, 1, "10:00"),
                (1, 2, "11:00"),
                (2, 0, "12:00"),
            ],
        }

        for grupo_label, equipos_grupo in grupos.items():
            for local_idx, visitante_idx, horario in fixture[grupo_label]:
                partidos.append(
                    {
                        "grupo": grupo_label,
                        "local": equipos_grupo[local_idx],
                        "visitante": equipos_grupo[visitante_idx],
                        "marcador_local": None,
                        "marcador_visitante": None,
                        "horario": horario,
                        "jugado": False,
                    }
                )

        # Reordenamos para mostrar el fixture exactamente
        # como fue establecido oficialmente.
        orden_oficial = [
            ("A", "09:30"),
            ("B", "09:30"),
            ("C", "10:00"),
            ("D", "10:00"),
            ("A", "10:30"),
            ("B", "10:30"),
            ("C", "11:00"),
            ("D", "11:00"),
            ("A", "11:30"),
            ("B", "11:30"),
            ("C", "12:00"),
            ("D", "12:00"),
        ]

        partidos_ordenados = []

        for grupo, horario in orden_oficial:
            for partido in partidos:
                if (
                    partido["grupo"] == grupo
                    and partido["horario"] == horario
                    and partido not in partidos_ordenados
                ):
                    partidos_ordenados.append(partido)
                    break

        partidos = partidos_ordenados

    # ==============================================================
    # FÚTBOL FEMENINO
    # ==============================================================
    elif disciplina == "Fútbol Femenino":

        fixture = {
            "A": [
                (0, 1, "12:50"),
                (1, 2, "13:40"),
                (2, 0, "14:30"),
            ],
            "B": [
                (0, 1, "12:50"),
                (1, 2, "13:40"),
                (2, 0, "14:30"),
            ],
            "C": [
                (0, 1, "12:50"),
                (1, 2, "13:40"),
                (2, 0, "14:30"),
            ],
        }

        # La disciplina femenina tiene 8 equipos.
        # Se distribuyen en dos grupos de 4.
        # Por eso usamos A y B.
        fixture = {
            "A": [
                (0, 1, "12:50"),
                (2, 3, "12:50"),
                (2, 0, "13:40"),
                (3, 1, "13:40"),
                (3, 0, "14:30"),
                (1, 2, "14:30"),
            ],
            "B": [
                (0, 1, "13:15"),
                (2, 3, "13:15"),
                (2, 0, "14:05"),
                (3, 1, "14:05"),
                (1, 2, "14:55"),
                (3, 0, "14:55"),
            ],
        }

        for grupo_label, equipos_grupo in grupos.items():
            if grupo_label not in fixture:
                continue

            for local_idx, visitante_idx, horario in fixture[grupo_label]:
                partidos.append(
                    {
                        "grupo": grupo_label,
                        "local": equipos_grupo[local_idx],
                        "visitante": equipos_grupo[visitante_idx],
                        "marcador_local": None,
                        "marcador_visitante": None,
                        "horario": horario,
                        "jugado": False,
                    }
                )

        # Orden oficial de todos los partidos femeninos
        orden_oficial = [
            ("A", "12:50"),
            ("B", "13:15"),
            ("A", "13:40"),
            ("B", "14:05"),
            ("A", "14:30"),
            ("B", "14:55"),
        ]

        partidos_ordenados = []

        for grupo, horario in orden_oficial:
            for partido in partidos:
                if (
                    partido["grupo"] == grupo
                    and partido["horario"] == horario
                    and partido not in partidos_ordenados
                ):
                    partidos_ordenados.append(partido)

        partidos = partidos_ordenados

    # ==============================================================
    # RESTO DE DISCIPLINAS
    # ==============================================================
    else:
        for grupo_label, equipos_grupo in grupos.items():
            partidos.extend(
                generar_partidos_round_robin(
                    equipos_grupo,
                    grupo_label,
                )
            )

    return {
        "equipos": equipos,
        "grupos": grupos,
        "partidos": partidos,
        "fase_grupos_cerrada": False,
        "clasificados": [],
        "eliminatorias": {},
        "campeon": None,
        "campeon_tribu": None,
        "bonus_otorgado": False,
    }


def inicializar_estado():
    if "app_inicializada" in st.session_state:
        return

    st.session_state.admin_logueado = False
    st.session_state.datos = {
        disciplina: inicializar_disciplina(disciplina)
        for disciplina in DISCIPLINAS
    }

    # REEMPLAZAR CON ANUNCIOS REALES
    st.session_state.tablon = [
        "Bienvenidos a La Copa Agro 2026.",
        "Próximamente se publicará el cronograma definitivo.",
    ]

    # REEMPLAZAR CON TORNEOS EXPRESS REALES
    st.session_state.torneos_express = [
    ]

    # REEMPLAZAR CON CRONOGRAMA REAL
    st.session_state.cronograma = [
        {"horario": "08:00", "actividad": "Apertura y bienvenida"},
        {"horario": "09:00", "actividad": "Inicio de fase de grupos"},
        {"horario": "13:00", "actividad": "Pausa - Almuerzo"},
        {"horario": "14:30", "actividad": "Reanudación de partidos"},
        {"horario": "18:00", "actividad": "Instancias finales"},
        {"horario": "19:30", "actividad": "Premiación"},
        {"horario": "21:00", "actividad": "Actividad de cierre"},
    ]

    st.session_state.app_inicializada = True


inicializar_estado()


# ==============================================================================
# CÁLCULOS
# ==============================================================================

def calcular_tabla_posiciones(equipos_grupo, partidos_grupo):
    tabla = {
        nombre: {
            "PJ": 0,
            "PG": 0,
            "PE": 0,
            "PP": 0,
            "GF": 0,
            "GC": 0,
            "Pts": 0,
        }
        for nombre in equipos_grupo
    }

    for p in partidos_grupo:
        if not p["jugado"]:
            continue

        local = p["local"]
        visitante = p["visitante"]
        gl = p["marcador_local"]
        gv = p["marcador_visitante"]

        tabla[local]["PJ"] += 1
        tabla[visitante]["PJ"] += 1
        tabla[local]["GF"] += gl
        tabla[local]["GC"] += gv
        tabla[visitante]["GF"] += gv
        tabla[visitante]["GC"] += gl

        if gl > gv:
            tabla[local]["PG"] += 1
            tabla[local]["Pts"] += 3
            tabla[visitante]["PP"] += 1
        elif gv > gl:
            tabla[visitante]["PG"] += 1
            tabla[visitante]["Pts"] += 3
            tabla[local]["PP"] += 1
        else:
            tabla[local]["PE"] += 1
            tabla[visitante]["PE"] += 1
            tabla[local]["Pts"] += 1
            tabla[visitante]["Pts"] += 1

    filas = []
    for nombre, datos in tabla.items():
        filas.append(
            {
                "Equipo": nombre,
                **datos,
                "DIF": datos["GF"] - datos["GC"],
            }
        )

    filas.sort(key=lambda x: (-x["Pts"], -x["DIF"], -x["GF"]))
    return filas


def nombre_a_tribu(disciplina, nombre_equipo):
    for equipo in st.session_state.datos[disciplina]["equipos"]:
        if equipo["nombre"] == nombre_equipo:
            return equipo["tribu"]
    return None


def calcular_tabla_global():
    puntos = {t: 0 for t in TRIBUS}
    puntos_express = {t: 0 for t in TRIBUS}

    for disciplina, datos in st.session_state.datos.items():
        for grupo_label, equipos_grupo in datos["grupos"].items():
            partidos_grupo = [
                p for p in datos["partidos"] if p["grupo"] == grupo_label
            ]

            tabla = calcular_tabla_posiciones(equipos_grupo, partidos_grupo)

            for fila in tabla:
                tribu = nombre_a_tribu(disciplina, fila["Equipo"])
                if tribu:
                    puntos[tribu] += fila["Pts"]

        if datos["campeon_tribu"]:
            puntos[datos["campeon_tribu"]] += 5

    for evento in st.session_state.torneos_express:
        puntos[evento["tribu"]] += evento["puntos"]
        puntos_express[evento["tribu"]] += evento["puntos"]

    filas = []
    for tribu in TRIBUS:
        filas.append(
            {
                "Tribu": tribu,
                "Puntos Totales": puntos[tribu],
                "Puntos Express": puntos_express[tribu],
            }
        )

    filas.sort(key=lambda x: (-x["Puntos Totales"], -x["Puntos Express"]))
    return filas


def armar_llave_eliminatoria(disciplina):
    datos = st.session_state.datos[disciplina]
    grupos = datos["grupos"]

    primeros = {}
    segundos = {}

    for grupo_label, equipos_grupo in grupos.items():
        partidos_grupo = [
            p for p in datos["partidos"] if p["grupo"] == grupo_label
        ]
        tabla = calcular_tabla_posiciones(equipos_grupo, partidos_grupo)

        if len(tabla) >= 2:
            primeros[grupo_label] = tabla[0]["Equipo"]
            segundos[grupo_label] = tabla[1]["Equipo"]

    clasificados = list(primeros.values()) + list(segundos.values())
    datos["clasificados"] = clasificados

    letras = list(grupos.keys())

    if TAMANO_GRUPO[disciplina] is None:
        datos["eliminatorias"] = {
            "Final": [
                {
                    "local": clasificados[0],
                    "visitante": clasificados[1],
                    "marcador_local": None,
                    "marcador_visitante": None,
                    "jugado": False,
                }
            ]
        }

    elif len(letras) == 2:

    if disciplina == "Fútbol Femenino":
        horario_semifinal_1 = "15:40"
        horario_semifinal_2 = "15:40"
        horario_final = "16:30"
    else:
        horario_semifinal_1 = "10:00"
        horario_semifinal_2 = "10:00"
        horario_final = "10:00"

    datos["eliminatorias"] = {
        "Semifinales": [
            {
                "local": primeros[letras[0]],
                "visitante": segundos[letras[1]],
                "marcador_local": None,
                "marcador_visitante": None,
                "horario": horario_semifinal_1,
                "jugado": False,
            },
            {
                "local": primeros[letras[1]],
                "visitante": segundos[letras[0]],
                "marcador_local": None,
                "marcador_visitante": None,
                "horario": horario_semifinal_2,
                "jugado": False,
            },
        ],

        "Final": [
            {
                "local": None,
                "visitante": None,
                "marcador_local": None,
                "marcador_visitante": None,
                "horario": horario_final,
                "jugado": False,
            }
        ],
    }

    elif len(letras) == 4:

    if disciplina == "Fútbol Masculino":
        horarios_cuartos = [
            "12:30",
            "13:00",
            "13:30",
            "14:00",
        ]

        horarios_semifinales = [
            "14:30",
            "15:00",
        ]

        horario_final = "16:00"

    else:
        horarios_cuartos = ["10:00"] * 4
        horarios_semifinales = ["10:00", "10:00"]
        horario_final = "10:00"

    datos["eliminatorias"] = {
        "Cuartos de Final": [
            {
                "local": primeros[letras[0]],
                "visitante": segundos[letras[2]],
                "marcador_local": None,
                "marcador_visitante": None,
                "horario": horarios_cuartos[0],
                "jugado": False,
            },
            {
                "local": primeros[letras[1]],
                "visitante": segundos[letras[3]],
                "marcador_local": None,
                "marcador_visitante": None,
                "horario": horarios_cuartos[1],
                "jugado": False,
            },
            {
                "local": primeros[letras[2]],
                "visitante": segundos[letras[0]],
                "marcador_local": None,
                "marcador_visitante": None,
                "horario": horarios_cuartos[2],
                "jugado": False,
            },
            {
                "local": primeros[letras[3]],
                "visitante": segundos[letras[1]],
                "marcador_local": None,
                "marcador_visitante": None,
                "horario": horarios_cuartos[3],
                "jugado": False,
            },
        ],

        "Semifinales": [
            {
                "local": None,
                "visitante": None,
                "marcador_local": None,
                "marcador_visitante": None,
                "horario": horarios_semifinales[0],
                "jugado": False,
            },
            {
                "local": None,
                "visitante": None,
                "marcador_local": None,
                "marcador_visitante": None,
                "horario": horarios_semifinales[1],
                "jugado": False,
            },
        ],

        "Final": [
            {
                "local": None,
                "visitante": None,
                "marcador_local": None,
                "marcador_visitante": None,
                "horario": horario_final,
                "jugado": False,
            }
        ],
    }

    datos["fase_grupos_cerrada"] = True


def avanzar_ganadores(disciplina):
    datos = st.session_state.datos[disciplina]
    eliminatorias = datos["eliminatorias"]
    rondas = list(eliminatorias.keys())

    for i in range(len(rondas) - 1):
        ronda_actual = eliminatorias[rondas[i]]
        ronda_siguiente = eliminatorias[rondas[i + 1]]

        ganadores = []

        for partido in ronda_actual:
            if partido["jugado"]:
                if partido["marcador_local"] > partido["marcador_visitante"]:
                    ganadores.append(partido["local"])
                else:
                    ganadores.append(partido["visitante"])
            else:
                ganadores.append(None)

        for j, partido_siguiente in enumerate(ronda_siguiente):
            if not partido_siguiente["jugado"]:
                if j * 2 < len(ganadores):
                    partido_siguiente["local"] = ganadores[j * 2]
                if j * 2 + 1 < len(ganadores):
                    partido_siguiente["visitante"] = ganadores[j * 2 + 1]

    final = eliminatorias.get("Final", [None])[0]

    if (
        final
        and final["jugado"]
        and not datos["bonus_otorgado"]
        and final["local"]
        and final["visitante"]
    ):
        if final["marcador_local"] > final["marcador_visitante"]:
            ganador = final["local"]
        else:
            ganador = final["visitante"]

        datos["campeon"] = ganador
        datos["campeon_tribu"] = nombre_a_tribu(disciplina, ganador)
        datos["bonus_otorgado"] = True


# ==============================================================================
# COMPONENTES
# ==============================================================================

def render_page_header(kicker, title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-label">{escape(kicker)}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:58px;
                    line-height:.9;letter-spacing:2px;color:#FFFFFF;">
            {escape(title)}
        </div>
        <div style="color:#929BA2;font-size:14px;margin-top:10px;margin-bottom:24px;">
            {escape(subtitle)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tribe_card(tribu, puntos):
    info = TRIBUS[tribu]
    st.markdown(
        f"""
        <div class="tribe-card" style="--tribe-color:{info['color']};">
            <div class="tribe-name">{escape(tribu)}</div>
            <div class="tribe-caption">Clasificación general</div>
            <div class="tribe-points">{puntos}</div>
            <div class="tribe-caption">puntos acumulados</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_match_card(disciplina, grupo, partido):
    if partido["jugado"]:
        marcador = (
            f"{partido['marcador_local']} - "
            f"{partido['marcador_visitante']}"
        )
    else:
        marcador = "VS"

    st.markdown(
        f"""
        <div class="match-card">
            <div class="match-top">
                <span>{escape(disciplina)}</span>
                <span>Grupo {escape(str(grupo))} | {escape(str(partido['horario']))}</span>
            </div>
            <div class="match-teams">
                <div class="team">{escape(partido['local'])}</div>
                <div class="match-score">{escape(marcador)}</div>
                <div class="team right">{escape(partido['visitante'])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_table(tabla):
    if not tabla:
        st.info("Todavía no hay datos suficientes para mostrar la tabla.")
        return

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Equipo": st.column_config.TextColumn("Equipo", width="large"),
            "PJ": st.column_config.NumberColumn("PJ", width="small"),
            "PG": st.column_config.NumberColumn("PG", width="small"),
            "PE": st.column_config.NumberColumn("PE", width="small"),
            "PP": st.column_config.NumberColumn("PP", width="small"),
            "GF": st.column_config.NumberColumn("GF", width="small"),
            "GC": st.column_config.NumberColumn("GC", width="small"),
            "DIF": st.column_config.NumberColumn("DIF", width="small"),
            "Pts": st.column_config.NumberColumn("Pts", width="small"),
        },
    )


# ==============================================================================
# VISTA INICIO
# ==============================================================================

def vista_inicio():
    tabla = calcular_tabla_global()
    lider = tabla[0] if tabla else None

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Torneo Intertribus 2026</div>
            <div class="hero-title">LA COPA<br>AGRO</div>
            <div class="hero-subtitle">
                Toda la información del torneo: resultados, posiciones,
                disciplinas, cronograma y clasificación general.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if lider:
        st.markdown('<div class="section-label">Clasificación actual</div>', unsafe_allow_html=True)
        cols = st.columns(4)

        for col, fila in zip(cols, tabla):
            with col:
                render_tribe_card(fila["Tribu"], fila["Puntos Totales"])

    st.markdown('<div class="section-label">Estado del torneo</div>', unsafe_allow_html=True)

    total_partidos = 0
    partidos_jugados = 0
    campeones = 0

    for datos in st.session_state.datos.values():
        total_partidos += len(datos["partidos"])
        partidos_jugados += sum(1 for p in datos["partidos"] if p["jugado"])
        if datos["campeon"]:
            campeones += 1

    cols = st.columns(3)

    with cols[0]:
        st.markdown(
            f"""
            <div class="mini-stat">
                <div class="mini-stat-number">{partidos_jugados}/{total_partidos}</div>
                <div class="mini-stat-label">Partidos jugados</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[1]:
        st.markdown(
            f"""
            <div class="mini-stat">
                <div class="mini-stat-number">{campeones}</div>
                <div class="mini-stat-label">Disciplinas definidas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[2]:
        st.markdown(
            f"""
            <div class="mini-stat">
                <div class="mini-stat-number">{len(DISCIPLINAS)}</div>
                <div class="mini-stat-label">Disciplinas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">Próximos partidos</div>', unsafe_allow_html=True)

    proximos = []
    for disciplina, datos in st.session_state.datos.items():
        for p in datos["partidos"]:
            if not p["jugado"]:
                proximos.append((disciplina, p))

    if proximos:
        for disciplina, partido in proximos[:6]:
            render_match_card(disciplina, partido["grupo"], partido)
    else:
        st.info("No hay partidos pendientes en la fase de grupos.")

    st.markdown('<div class="section-label">Tablón</div>', unsafe_allow_html=True)

    for aviso in st.session_state.tablon:
        st.markdown(
            f'<div class="announcement">{escape(aviso)}</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.admin_logueado:
        with st.expander("Administrar tablón"):
            nuevo = st.text_input("Nuevo anuncio", key="nuevo_aviso")
            if st.button("Agregar anuncio", key="agregar_aviso"):
                if nuevo.strip():
                    st.session_state.tablon.append(nuevo.strip())
                    st.rerun()

            if st.session_state.tablon:
                borrar = st.selectbox(
                    "Seleccionar anuncio para eliminar",
                    st.session_state.tablon,
                    key="borrar_aviso",
                )
                if st.button("Eliminar anuncio", key="eliminar_aviso"):
                    st.session_state.tablon.remove(borrar)
                    st.rerun()


# ==============================================================================
# VISTA TRIBUS
# ==============================================================================

def vista_tribus():
    render_page_header(
        "Equipos",
        "Tribus",
        "Conocé los equipos y participantes de cada tribu.",
    )

    tribu_seleccionada = st.selectbox(
        "Seleccionar tribu",
        list(TRIBUS.keys()),
    )

    info = TRIBUS[tribu_seleccionada]

    st.markdown(
        f"""
        <div style="border-radius:18px;padding:22px 26px;margin:12px 0 25px;
                    background:linear-gradient(120deg,{info['dark']},{info['color']});
                    color:{info['texto']};">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:46px;
                        letter-spacing:2px;">
                {escape(tribu_seleccionada)}
            </div>
            <div style="opacity:.85;font-size:12px;text-transform:uppercase;
                        letter-spacing:2px;">
                Equipos por disciplina
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for disciplina in DISCIPLINAS:
        equipos_tribu = [
            e
            for e in st.session_state.datos[disciplina]["equipos"]
            if e["tribu"] == tribu_seleccionada
        ]

        if not equipos_tribu:
            continue

        st.markdown(
            f'<div class="section-label">{escape(disciplina)}</div>',
            unsafe_allow_html=True,
        )

        cols = st.columns(min(3, len(equipos_tribu)))

        for idx, equipo in enumerate(equipos_tribu):
            with cols[idx % len(cols)]:
                with st.expander(equipo["nombre"]):
                    for participante in equipo["participantes"]:
                        st.markdown(
                            f'<div style="padding:5px 0;color:#B9C0C5;">'
                            f'{escape(participante)}</div>',
                            unsafe_allow_html=True,
                        )


# ==============================================================================
# VISTA DISCIPLINAS
# ==============================================================================

def vista_disciplinas():
    render_page_header(
        "Competencia",
        "Disciplinas",
        "Fixture, posiciones y fases eliminatorias.",
    )

    disciplina = st.selectbox("Seleccionar disciplina", DISCIPLINAS)
    datos = st.session_state.datos[disciplina]
    limite = LIMITES_MARCADOR[disciplina]

    st.markdown(
        f"""
        <div class="sport-card" style="margin-bottom:20px;">
            <div class="sport-name">{escape(disciplina)}</div>
            <div class="sport-meta">
                Límite de marcador: {limite} |
                Equipos: {len(datos['equipos'])} |
                Grupos: {len(datos['grupos'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_fixture, tab_posiciones, tab_eliminatorias = st.tabs(
        ["Fixture", "Tabla de posiciones", "Eliminatorias"]
    )

    with tab_fixture:
        for grupo_label, equipos_grupo in datos["grupos"].items():
            st.markdown(
                f'<div class="section-label">Grupo {escape(str(grupo_label))}</div>',
                unsafe_allow_html=True,
            )

            partidos_grupo = [
                p for p in datos["partidos"]
                if p["grupo"] == grupo_label
            ]

            for idx, p in enumerate(partidos_grupo):
                if st.session_state.admin_logueado:
                    render_match_card(disciplina, grupo_label, p)

                    cols = st.columns([2.3, 1, 1, 1])

                    nuevo_horario = cols[0].text_input(
                        "Horario",
                        value=p["horario"],
                        key=f"horario_{disciplina}_{grupo_label}_{idx}",
                    )

                    gl = cols[1].number_input(
                        "Local",
                        min_value=0,
                        max_value=limite,
                        value=p["marcador_local"] if p["marcador_local"] is not None else 0,
                        key=f"gl_{disciplina}_{grupo_label}_{idx}",
                    )

                    gv = cols[2].number_input(
                        "Visitante",
                        min_value=0,
                        max_value=limite,
                        value=p["marcador_visitante"] if p["marcador_visitante"] is not None else 0,
                        key=f"gv_{disciplina}_{grupo_label}_{idx}",
                    )

                    if cols[3].button(
                        "Guardar",
                        key=f"guardar_{disciplina}_{grupo_label}_{idx}",
                    ):
                        p["horario"] = nuevo_horario
                        p["marcador_local"] = int(gl)
                        p["marcador_visitante"] = int(gv)
                        p["jugado"] = True
                        st.rerun()
                else:
                    render_match_card(disciplina, grupo_label, p)

        if st.session_state.admin_logueado and not datos["fase_grupos_cerrada"]:
            st.markdown("---")
            st.warning(
                "Al cerrar la fase de grupos se calculan los clasificados "
                "y se genera el cuadro de eliminatorias. Esta acción no "
                "se puede deshacer."
            )

            confirm_key = f"confirmar_cierre_{disciplina}"
            if confirm_key not in st.session_state:
                st.session_state[confirm_key] = False

            if not st.session_state[confirm_key]:
                if st.button(
                    "Cerrar fase de grupos",
                    key=f"cerrar_{disciplina}",
                ):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                st.error(
                    "Confirmá que querés cerrar la fase de grupos "
                    "y generar las eliminatorias."
                )

                c1, c2 = st.columns(2)

                if c1.button(
                    "Confirmar avance",
                    key=f"confirmar_{disciplina}",
                ):
                    armar_llave_eliminatoria(disciplina)
                    st.session_state[confirm_key] = False
                    st.rerun()

                if c2.button(
                    "Cancelar",
                    key=f"cancelar_{disciplina}",
                ):
                    st.session_state[confirm_key] = False
                    st.rerun()

    with tab_posiciones:
        for grupo_label, equipos_grupo in datos["grupos"].items():
            st.markdown(
                f'<div class="section-label">Grupo {escape(str(grupo_label))}</div>',
                unsafe_allow_html=True,
            )

            partidos_grupo = [
                p for p in datos["partidos"]
                if p["grupo"] == grupo_label
            ]

            tabla = calcular_tabla_posiciones(
                equipos_grupo,
                partidos_grupo,
            )

            render_table(tabla)

    with tab_eliminatorias:
        if not datos["fase_grupos_cerrada"]:
            st.info(
                "El cuadro de eliminatorias aparecerá cuando "
                "el administrador cierre la fase de grupos."
            )
        else:
            for ronda, partidos_ronda in datos["eliminatorias"].items():
                st.markdown(
                    f'<div class="section-label">{escape(ronda)}</div>',
                    unsafe_allow_html=True,
                )

                for idx, p in enumerate(partidos_ronda):
                    if p["local"] is None or p["visitante"] is None:
                        st.markdown(
                            """
                            <div class="match-card">
                                <div style="color:#707980;text-align:center;
                                            padding:10px;">
                                    Clasificación pendiente
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        continue

                    render_match_card(disciplina, ronda, p)

                    if st.session_state.admin_logueado and not p["jugado"]:
                        cols = st.columns([1, 1, 1])

                        gl = cols[0].number_input(
                            "Local",
                            min_value=0,
                            max_value=limite,
                            value=0,
                            key=f"elim_gl_{disciplina}_{ronda}_{idx}",
                        )

                        gv = cols[1].number_input(
                            "Visitante",
                            min_value=0,
                            max_value=limite,
                            value=0,
                            key=f"elim_gv_{disciplina}_{ronda}_{idx}",
                        )

                        if cols[2].button(
                            "Guardar resultado",
                            key=f"elim_guardar_{disciplina}_{ronda}_{idx}",
                        ):
                            if gl == gv:
                                st.error(
                                    "No se permiten empates en eliminatorias. "
                                    "Cargá el resultado final."
                                )
                            else:
                                p["marcador_local"] = int(gl)
                                p["marcador_visitante"] = int(gv)
                                p["jugado"] = True
                                avanzar_ganadores(disciplina)
                                st.rerun()

            if datos["campeon"]:
                st.markdown(
                    f"""
                    <div class="champion-banner">
                        <div class="champion-label">Campeón de {escape(disciplina)}</div>
                        <div class="champion-name">{escape(datos['campeon'])}</div>
                        <div style="color:#A8B0B6;">
                            Tribu {escape(datos['campeon_tribu'])}
                            | Bonificación: +5 puntos
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ==============================================================================
# VISTA TABLA GLOBAL
# ==============================================================================

def vista_tabla_global():
    render_page_header(
        "Clasificación",
        "Tabla global",
        "La carrera por la Copa Agro.",
    )

    tabla = calcular_tabla_global()

    cols = st.columns(4)

    for col, fila in zip(cols, tabla):
        with col:
            render_tribe_card(fila["Tribu"], fila["Puntos Totales"])

    st.markdown(
        '<div class="section-label">Ranking detallado</div>',
        unsafe_allow_html=True,
    )

    for posicion, fila in enumerate(tabla, start=1):
        tribu = fila["Tribu"]
        info = TRIBUS[tribu]

        st.markdown(
            f"""
            <div style="display:grid;grid-template-columns:70px 1fr 120px;
                        align-items:center;gap:18px;padding:17px 20px;
                        margin-bottom:9px;border-radius:15px;
                        background:#151A1E;
                        border:1px solid rgba(255,255,255,.08);">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:34px;
                            color:{info['color']};">
                    {posicion:02d}
                </div>
                <div>
                    <div style="font-weight:800;color:#FFFFFF;font-size:16px;">
                        {escape(tribu)}
                    </div>
                    <div style="color:#7F8991;font-size:11px;">
                        Torneos Express: {fila['Puntos Express']} puntos
                    </div>
                </div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:34px;
                            color:#FFFFFF;text-align:right;">
                    {fila['Puntos Totales']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.admin_logueado:
        st.markdown("---")
        st.markdown(
            '<div class="section-label">Administración</div>',
            unsafe_allow_html=True,
        )

        with st.form("form_torneo_express"):
            tribu_sel = st.selectbox(
                "Tribu",
                list(TRIBUS.keys()),
            )
            concepto = st.text_input(
                "Concepto",
                placeholder="Ejemplo: Torneo de Truco",
            )
            puntos = st.number_input(
                "Puntos a sumar",
                min_value=0,
                value=1,
                step=1,
            )

            enviado = st.form_submit_button("Agregar Torneo Express")

            if enviado and concepto.strip():
                st.session_state.torneos_express.append(
                    {
                        "tribu": tribu_sel,
                        "concepto": concepto.strip(),
                        "puntos": int(puntos),
                    }
                )
                st.rerun()


# ==============================================================================
# VISTA CRONOGRAMA
# ==============================================================================

def vista_cronograma():
    render_page_header(
        "Agenda",
        "Cronograma",
        "Horarios y actividades principales del torneo.",
    )

    for idx, item in enumerate(st.session_state.cronograma):
        if st.session_state.admin_logueado:
            cols = st.columns([1, 3])

            item["horario"] = cols[0].text_input(
                "Horario",
                value=item["horario"],
                key=f"cron_h_{idx}",
            )

            item["actividad"] = cols[1].text_input(
                "Actividad",
                value=item["actividad"],
                key=f"cron_a_{idx}",
            )
        else:
            st.markdown(
                f"""
                <div class="timeline-item">
                    <div class="timeline-time">{escape(item['horario'])}</div>
                    <div class="timeline-event">{escape(item['actividad'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==============================================================================
# VISTA PREMIOS Y REGLAMENTO
# ==============================================================================

def vista_premios():
    render_page_header(
        "Información",
        "Premios y reglamento",
        "Sistema de puntuación y reglas de competencia.",
    )

    cols = st.columns(3)

    with cols[0]:
        st.markdown(
            """
            <div class="rule-card">
                <div class="rule-title">Premiación</div>
                <div style="color:#B7C0C7;line-height:1.7;">
                    La tribu campeona es la que acumule más puntos
                    totales al finalizar el torneo.
                    Cada disciplina entrega un campeón que suma
                    5 puntos adicionales a su tribu.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[1]:
        st.markdown(
            """
            <div class="rule-card">
                <div class="rule-title">Puntuación</div>
                <div style="color:#B7C0C7;line-height:1.7;">
                    Fase de grupos:<br>
                    Victoria: 3 puntos<br>
                    Empate: 1 punto<br>
                    Derrota: 0 puntos<br>
                    Campeón de disciplina: +5 puntos
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[2]:
        st.markdown(
            """
            <div class="rule-card">
                <div class="rule-title">Desempates</div>
                <div style="color:#B7C0C7;line-height:1.7;">
                    En grupos se utiliza la diferencia de tantos.
                    En la tabla global se priorizan los puntos de
                    Torneos Express en caso de igualdad.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-label">Topes de marcador</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(4)

    for col, disciplina in zip(cols, DISCIPLINAS):
        with col:
            st.markdown(
                f"""
                <div class="mini-stat">
                    <div class="mini-stat-number">{LIMITES_MARCADOR[disciplina]}</div>
                    <div class="mini-stat-label">{escape(disciplina)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==============================================================================
# LOGIN ADMIN
# ==============================================================================

def vista_login_admin():
    render_page_header(
        "Acceso",
        "Administración",
        "Panel protegido para cargar y modificar información.",
    )

    if st.session_state.admin_logueado:
        st.markdown(
            '<span class="admin-badge">Modo administrador activo</span>',
            unsafe_allow_html=True,
        )
        st.write("")

        if st.button("Cerrar sesión"):
            st.session_state.admin_logueado = False
            st.rerun()

        return

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div class="rule-card" style="text-align:center;">
                <div class="rule-title">Acceso restringido</div>
                <div style="color:#929BA2;margin-bottom:20px;">
                    Ingresá el PIN para habilitar la edición del torneo.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pin_ingresado = st.text_input(
            "PIN",
            type="password",
            key="pin_admin",
        )

        if st.button("Ingresar al panel", use_container_width=True):
            if pin_ingresado == PIN_ADMIN:
                st.session_state.admin_logueado = True
                st.rerun()
            else:
                st.error("PIN incorrecto.")


# ==============================================================================
# NAVEGACIÓN
# ==============================================================================

def main():
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:8px 0 24px;">
                <div style="font-family:'Bebas Neue',sans-serif;
                            font-size:38px;letter-spacing:2px;color:#FFFFFF;">
                    LA COPA AGRO
                </div>
                <div style="font-size:10px;letter-spacing:2px;
                            text-transform:uppercase;color:#7F8991;">
                    Torneo Intertribus 2026
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.admin_logueado:
            st.markdown(
                '<span class="admin-badge">Administrador</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="public-badge">Vista pública</span>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div style="height:18px;"></div>',
            unsafe_allow_html=True,
        )

        secciones = [
            "Inicio",
            "Tribus",
            "Disciplinas",
            "Tabla global",
            "Cronograma",
            "Premios y reglamento",
            "Administración",
        ]

        seccion = st.radio(
            "Navegación",
            secciones,
            label_visibility="collapsed",
        )

        st.markdown("---")

        st.markdown(
            """
            <div style="color:#68727A;font-size:10px;line-height:1.7;">
                LA COPA AGRO<br>
                Plataforma de información y gestión<br>
                Torneo Intertribus 2026
            </div>
            """,
            unsafe_allow_html=True,
        )

    if seccion == "Inicio":
        vista_inicio()
    elif seccion == "Tribus":
        vista_tribus()
    elif seccion == "Disciplinas":
        vista_disciplinas()
    elif seccion == "Tabla global":
        vista_tabla_global()
    elif seccion == "Cronograma":
        vista_cronograma()
    elif seccion == "Premios y reglamento":
        vista_premios()
    elif seccion == "Administración":
        vista_login_admin()


if __name__ == "__main__":
    main()
