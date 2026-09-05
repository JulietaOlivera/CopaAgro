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
from datetime import datetime, timezone

from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh


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

    # ==============================================================
    # FÚTBOL MASCULINO - EQUIPOS REALES
    # ==============================================================

    if disciplina == "Fútbol Masculino":
        equipos_reales_futbol_masculino = [
            ("La Vino", "Maíz"),
            ("La Choloneta", "Trigo"),
            ("Yo Te Vi", "Angus"),

            ("El Rancho FC", "Maíz"),
            ("Cantora de Basto", "Trigo"),
            ("Luchoneta", "Holando"),

            ("Los Fabianes", "Maíz"),
            ("Real Ganadero", "Angus"),
            ("Deportivo Litoral", "Holando"),

            ("Atlético Barbecho", "Trigo"),
            ("La Chancha Wacha", "Angus"),
            ("Real Bañil", "Holando"),
        ]

        jugadores_futbol_masculino = {
            "La Vino": [
                "Elvio Trossero",
                "Matías Becker",
                "Emiliano Schroder",
                "Rodrigo Ramallo",
                "Fabián Chaparro",
                "Enzo Olivari",
                "Brian Balbuena",
                "Juan Acevedo",
                "Ricardo Sanabria",
                "Lisandro Romero",
            ],
        
            "La Choloneta": [
                "Lucas Picculo",
                "Lucas Lell",
                "Ezequiel Bianchini",
                "Juan Martín Zaragoza",
                "Thomas Garcilazo",
                "Baltazar Michell",
                "Stefano Saavedra",
                "Julián Huck",
                "Joaquín Palacios",
                "Valentín Ojeda",
            ],
        
            "Yo Te Vi": [
                "Osiris Gonzales",
                "Nahuel Galian",
                "Alan Salas",
                "Martín Sarasola",
                "Alexis Regales",
                "Jeremías Barzola",
                "Enzo Lencina",
                "Ramiro Reyes",
                "Thiago Garay",
                "Santi Garay",
                "Mario Bracamonte",
            ],
        
            "El Rancho FC": [
                "Agustín Benítez",
                "Santino Stamatti",
                "Jerónimo Sivilla",
                "Joaquín Garay",
                "Jerónimo Rochi",
                "Ricardo Trossero",
                "Santiago Márquez",
                "Agustín Roubineau",
                "Nicolás Sirtori",
                "Renato Armocida",
            ],
        
            "Cantora de Basto": [
                "Lautaro Alvarez",
                "Alex Kispen",
                "Joaquín Sancio",
                "Iván Palavecino",
                "Tomás Cuevas",
                "Atilio Denardi",
                "Mauro Passadore",
                "Mateo Leiss",
                "Ignacio Iribarren",
                "Máximo Rojas",
            ],
        
            "Luchoneta": [
                "Nicolás Domínguez",
                "Bautista Cáceres Taffarel",
                "Joaquín Rodríguez",
                "Juan Emilio Weber Mutti",
                "Juan Ignacio De Bravandere",
                "Enedin Matías Echaniz",
                "Tobías Fabri",
                "Hahn Julián Mazzeto",
                "Juan Schwartz",
            ],
        
            "Los Fabianes": [
                "Duilio De Luca",
                "Franco Romani",
                "Salustiano Burruchaga",
                "Augusto Grane",
                "Simón Bollo",
                "Mauro Arlettaz",
                "Damián Domingorena",
                "Lautaro Silva",
                "Agustín Navarret",
                "Flavio Busco",
            ],
        
            "Real Ganadero": [
                "Agustín Alva",
                "Juan Ignacio Meroi",
                "Mateo Mendoza",
                "Juan Cruz Lozze",
                "Mateo Franco",
                "Franco Voucher",
                "Mauro Sandrigo",
                "Francisco Parisi",
                "Martín Bustos",
                "Francisco Roskopf",
            ],
        
            "Deportivo Litoral": [
                "Germán Wiesner",
                "Franco Choves",
                "Alexis Rodrigo Liturbe",
                "Máximo Liturbe",
                "Alejo Bermudes",
                "Pross",
                "Iván Peña",
                "Jere Varisco",
                "Namir Pavé",
                "Agustín Holzman",
            ],
        
            "Atlético Barbecho": [
                "Martín Gaona",
                "Nahuel Müller",
                "Sabá Flores",
                "Enzo Gigena",
                "Benicio Fontana",
                "Deian Landra",
                "Francisco Humaran",
                "Lisandro Pagnone",
                "Pedro Pérez",
                "Lisandro Silvestre",
            ],
        
            "La Chancha Wacha": [
                "Martín Gaona",
                "Nahuel Müller",
                "Sabá Flores",
                "Enzo Gigena",
                "Benicio Fontana",
                "Deian Landra",
                "Francisco Humaran",
                "Lisandro Pagnone",
                "Pedro Pérez",
                "Lisandro Silvestre",
            ],
        
            "Real Bañil": [
                "José Cisterna",
                "Max Ortega",
                "Tomás Roth",
                "Ariel Riffel",
                "Carlos Alvarez",
                "Víctor Chaliol",
                "Lautaro Rodríguez",
                "Nicolás Vallejos",
                "Esteban Ávila",
            ],
        }

        for nombre, tribu in equipos_reales_futbol_masculino:
            equipos.append(
                {
                    "nombre": nombre,
                    "tribu": tribu,
                    "participantes": jugadores_futbol_masculino.get(nombre, []),
                }
            )

        return equipos

    # ==============================================================
    # RESTO DE DISCIPLINAS
    # ==============================================================

    for n in range(total_equipos):
        tribu = orden_tribus[n % len(orden_tribus)]
        contador_tribu[tribu] += 1

        nombre = f"Equipo {contador_tribu[tribu]} {disciplina} ({tribu})"

        equipos.append(
            {
                "nombre": nombre,
                "tribu": tribu,
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


# ==============================================================================
# CONEXIÓN A LA BASE DE DATOS COMPARTIDA (Supabase / PostgreSQL)
# ==============================================================================
#
# Estas credenciales se leen desde los "Secrets" de Streamlit Community
# Cloud (Settings -> Secrets), por lo que nunca quedan expuestas al
# navegador: todo este código corre en el servidor.
#
#   SUPABASE_URL = "https://XXXXXXXX.supabase.co"
#   SUPABASE_KEY = "eyJhbGciOi....(Service Role Key)..."
#
# En Supabase solo se guardan los datos DINÁMICOS de cada partido
# (marcador, horario, cancha, si se jugó) y si la fase de grupos de cada
# disciplina ya fue cerrada. Todo lo demás (tribus, equipos,
# participantes, grupos, fixture "de fábrica", reglas, límites) sigue
# definido acá, en main.py, y es de SOLO LECTURA para el administrador.
# ==============================================================================

@st.cache_resource(show_spinner=False)
def obtener_cliente_db() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_data(ttl=5, show_spinner=False)
def leer_resultados_partidos():
    """
    Trae TODOS los resultados dinámicos guardados en Supabase en una sola
    consulta y arma un diccionario indexado por
    (disciplina, tipo, clave, slot) para cruzarlo con el fixture estático.

    Está cacheada 5 segundos y ese caché es COMPARTIDO por todas las
    sesiones de la app (no es "por usuario"): por eso alcanza con
    limpiarlo una vez cuando el admin guarda un cambio para que se
    propague a cualquiera que refresque después.
    """
    cliente = obtener_cliente_db()
    respuesta = cliente.table("resultados_partidos").select("*").execute()

    filas = {}
    for fila in respuesta.data:
        clave = (fila["disciplina"], fila["tipo"], fila["clave"], fila["slot"])
        filas[clave] = fila
    return filas


@st.cache_data(ttl=5, show_spinner=False)
def leer_estado_disciplinas():
    """Trae, para cada disciplina, si la fase de grupos ya fue cerrada."""
    cliente = obtener_cliente_db()
    respuesta = cliente.table("estado_disciplinas").select("*").execute()
    return {fila["disciplina"]: fila["fase_grupos_cerrada"] for fila in respuesta.data}


def guardar_resultado_partido(
    disciplina, tipo, clave, slot, *,
    marcador_local=None, marcador_visitante=None,
    horario=None, cancha=None, jugado=False, ganador_forzado=None,
):
    """
    Guarda (inserta o actualiza) el resultado dinámico de UN partido.
    "tipo" es 'grupo' o 'eliminatoria'; "clave" es la letra del grupo
    (ej. 'A') o el nombre de la ronda eliminatoria (ej. 'Cuartos de
    Final'); "slot" es la posición del partido dentro de ese grupo/ronda.
    """
    cliente = obtener_cliente_db()
    cliente.table("resultados_partidos").upsert(
        {
            "disciplina": disciplina,
            "tipo": tipo,
            "clave": clave,
            "slot": slot,
            "marcador_local": marcador_local,
            "marcador_visitante": marcador_visitante,
            "horario": horario,
            "cancha": cancha,
            "jugado": jugado,
            "ganador_forzado": ganador_forzado,
            "actualizado_en": datetime.now(timezone.utc).isoformat(),
        },
        on_conflict="disciplina,tipo,clave,slot",
    ).execute()

    # Invalidamos el caché compartido: así el propio admin ve el cambio
    # al instante, y cualquier otra sesión que refresque (por el
    # auto-refresco o por su propia interacción) también lo verá.
    leer_resultados_partidos.clear()


def guardar_estado_fase(disciplina, cerrada):
    """Guarda si la fase de grupos de una disciplina está cerrada o no."""
    cliente = obtener_cliente_db()
    cliente.table("estado_disciplinas").upsert(
        {
            "disciplina": disciplina,
            "fase_grupos_cerrada": cerrada,
            "actualizado_en": datetime.now(timezone.utc).isoformat(),
        },
        on_conflict="disciplina",
    ).execute()
    leer_estado_disciplinas.clear()


# ==============================================================================
# ESTRUCTURA ESTÁTICA DEL TORNEO (equipos, grupos y fixture "de fábrica")
# ==============================================================================
# Todo lo que se arma acá es SOLO LECTURA para el administrador: nombres de
# tribus, equipos, participantes, grupos y el fixture original (quién
# juega contra quién, y los horarios/canchas por defecto). El admin solo
# puede modificar, desde el panel, el horario/cancha/marcador YA CARGADO
# de un partido puntual — nunca esta estructura.
# ==============================================================================

def construir_partidos_base_grupo(disciplina, grupo_label, equipos_grupo):
    """
    Devuelve el fixture "de fábrica" (local, visitante, horario y cancha
    por defecto) de un grupo, en un orden fijo que define el "slot" de
    cada partido: la clave que se usa después para guardar sus
    resultados en Supabase.
    """
    if disciplina == "Fútbol Masculino":
        fixture_por_grupo = {
            "A": [(0, 1, "09:30", "Cancha A"), (1, 2, "10:30", "Cancha A"), (2, 0, "11:30", "Cancha A")],
            "B": [(0, 1, "09:30", "Cancha D"), (1, 2, "10:30", "Cancha D"), (2, 0, "11:30", "Cancha D")],
            "C": [(0, 1, "10:00", "Cancha A"), (1, 2, "11:00", "Cancha A"), (2, 0, "12:00", "Cancha A")],
            "D": [(0, 1, "10:00", "Cancha D"), (1, 2, "11:00", "Cancha D"), (2, 0, "12:00", "Cancha D")],
        }
        return [
            {
                "local": equipos_grupo[local_idx],
                "visitante": equipos_grupo[visitante_idx],
                "horario_default": horario,
                "cancha_default": cancha,
            }
            for local_idx, visitante_idx, horario, cancha in fixture_por_grupo[grupo_label]
        ]

    if disciplina == "Fútbol Femenino":
        fixture_por_grupo = {
            "A": [(0, 1, "12:50"), (2, 3, "12:50"), (2, 0, "13:40"), (3, 1, "13:40"), (3, 0, "14:30"), (1, 2, "14:30")],
            "B": [(0, 1, "13:15"), (2, 3, "13:15"), (2, 0, "14:05"), (3, 1, "14:05"), (1, 2, "14:55"), (3, 0, "14:55")],
        }
        return [
            {
                "local": equipos_grupo[local_idx],
                "visitante": equipos_grupo[visitante_idx],
                "horario_default": horario,
                "cancha_default": "",
            }
            for local_idx, visitante_idx, horario in fixture_por_grupo[grupo_label]
        ]

    # Básquet y Vóley Mixto: todos contra todos dentro del grupo, sin
    # horarios ni canchas predefinidos (el admin los completa).
    partidos = []
    for i in range(len(equipos_grupo)):
        for j in range(i + 1, len(equipos_grupo)):
            partidos.append({
                "local": equipos_grupo[i],
                "visitante": equipos_grupo[j],
                "horario_default": "10:00",
                "cancha_default": "",
            })
    return partidos


@st.cache_resource(show_spinner=False)
def construir_esqueletos():
    """
    Arma, UNA SOLA VEZ por proceso (y compartido por todas las sesiones,
    porque no depende de ningún dato dinámico), la estructura completa y
    estática del torneo: equipos, grupos y fixture de cada disciplina.
    """
    esqueletos = {}
    for disciplina in DISCIPLINAS:
        equipos = crear_equipos_disciplina(disciplina)
        grupos_nombres = armar_grupos(equipos, disciplina)

        partidos_base = {
            grupo_label: construir_partidos_base_grupo(disciplina, grupo_label, equipos_grupo)
            for grupo_label, equipos_grupo in grupos_nombres.items()
        }

        esqueletos[disciplina] = {
            "equipos": equipos,
            "grupos_nombres": grupos_nombres,
            "partidos_base": partidos_base,
        }

    return esqueletos


def inicializar_estado():
    """
    Inicializa el estado propio de CADA sesión de navegador. Ya no incluye
    los datos del torneo (equipos/partidos/resultados): esos ahora salen
    siempre en vivo de construir_esqueletos() (estático) + Supabase
    (dinámico), y por eso son iguales para todos los usuarios.
    """
    if "app_inicializada" in st.session_state:
        return

    st.session_state.admin_logueado = False

    # NOTA DE ALCANCE: el tablón, los Torneos Express y el cronograma NO
    # forman parte de esta sincronización (el alcance pedido fue
    # exclusivamente marcador/horario/cancha de los partidos), por lo que
    # siguen viviendo acá, en session_state: cada edición del admin sobre
    # estos 3 puntos solo se ve en su propia sesión/pestaña. Si en algún
    # momento quieren que también se compartan, se resuelve con el mismo
    # patrón (una tabla más en Supabase).

    # REEMPLAZAR CON ANUNCIOS REALES
    st.session_state.tablon = [
        "Bienvenidos a La Copa Agro 2026.",
        "Próximamente se publicará el cronograma definitivo.",
    ]

    # REEMPLAZAR CON TORNEOS EXPRESS REALES
    st.session_state.torneos_express = []

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
    for equipo in construir_esqueletos()[disciplina]["equipos"]:
        if equipo["nombre"] == nombre_equipo:
            return equipo["tribu"]
    return None


def calcular_tabla_global():
    puntos = {t: 0 for t in TRIBUS}
    puntos_express = {t: 0 for t in TRIBUS}

    for disciplina in DISCIPLINAS:
        esqueleto = construir_esqueletos()[disciplina]

        for grupo_label, nombres_grupo in esqueleto["grupos_nombres"].items():
            partidos_grupo = obtener_partidos_grupo(disciplina, grupo_label)
            tabla = calcular_tabla_posiciones(nombres_grupo, partidos_grupo)

            for fila in tabla:
                tribu = nombre_a_tribu(disciplina, fila["Equipo"])
                if tribu:
                    puntos[tribu] += fila["Pts"]

        _, _, campeon_tribu = construir_eliminatorias(disciplina)
        if campeon_tribu:
            puntos[campeon_tribu] += 5

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



def obtener_partidos_grupo(disciplina, grupo_label):
    """
    Combina el esqueleto ESTÁTICO del fixture (definido en main.py) con
    los datos DINÁMICOS guardados en Supabase (marcador, horario, cancha,
    si se jugó) para ese grupo. Se llama en cada ejecución del script, por
    lo que siempre refleja el último estado guardado en la base de datos.
    """
    base_partidos = construir_esqueletos()[disciplina]["partidos_base"][grupo_label]
    dinamicos = leer_resultados_partidos()

    partidos = []
    for slot, base in enumerate(base_partidos):
        fila = dinamicos.get((disciplina, "grupo", grupo_label, slot), {})
        partidos.append({
            "grupo": grupo_label,
            "slot": slot,
            "local": base["local"],
            "visitante": base["visitante"],
            "horario": fila.get("horario") or base["horario_default"],
            "cancha": fila.get("cancha") or base["cancha_default"],
            "marcador_local": fila.get("marcador_local"),
            "marcador_visitante": fila.get("marcador_visitante"),
            "jugado": fila.get("jugado", False),
        })
    return partidos


def resolver_ganador(partido):
    """
    Determina el ganador de un partido de eliminatorias.

    - Si el admin cargó un "ganador_forzado" (caso especial: definición
      por penales, walkover, etc., donde el marcador no alcanza para
      reflejar quién avanza), se respeta esa decisión.
    - Si no, el ganador se calcula automáticamente comparando el
      marcador.
    - Si el partido no se jugó, o el marcador está empatado y no hay
      ganador_forzado, todavía no hay ganador definido.
    """
    if partido is None:
        return None
    if partido.get("ganador_forzado"):
        return partido["ganador_forzado"]
    if not partido["jugado"]:
        return None
    if partido["marcador_local"] is None or partido["marcador_visitante"] is None:
        return None
    if partido["marcador_local"] == partido["marcador_visitante"]:
        return None
    return (
        partido["local"]
        if partido["marcador_local"] > partido["marcador_visitante"]
        else partido["visitante"]
    )


def obtener_clasificados(disciplina):
    """Calcula el 1º y 2º de cada grupo a partir de los resultados actuales."""
    esqueleto = construir_esqueletos()[disciplina]
    primeros, segundos = {}, {}

    for grupo_label, nombres_grupo in esqueleto["grupos_nombres"].items():
        partidos_grupo = obtener_partidos_grupo(disciplina, grupo_label)
        tabla = calcular_tabla_posiciones(nombres_grupo, partidos_grupo)
        if len(tabla) >= 2:
            primeros[grupo_label] = tabla[0]["Equipo"]
            segundos[grupo_label] = tabla[1]["Equipo"]

    return primeros, segundos


def construir_eliminatorias(disciplina):
    """
    Arma el cuadro de eliminatorias completo EN VIVO, a partir de:
      - el estado "fase_grupos_cerrada" guardado en Supabase (decisión
        manual del admin),
      - los clasificados, calculados a partir de los resultados de
        grupos ya cargados,
      - los resultados de cada cruce eliminatorio guardados en Supabase.

    No se guarda ningún cruce ni ganador calculado: todo se recalcula acá
    cada vez que se llama a esta función, así siempre queda sincronizado
    con los resultados cargados hasta el momento.

    Devuelve: (eliminatorias, campeon, campeon_tribu)
    """
    if not leer_estado_disciplinas().get(disciplina, False):
        return {}, None, None

    primeros, segundos = obtener_clasificados(disciplina)
    letras = list(construir_esqueletos()[disciplina]["grupos_nombres"].keys())
    dinamicos = leer_resultados_partidos()

    def construir_partido(ronda, slot, local, visitante, horario_default):
        fila = dinamicos.get((disciplina, "eliminatoria", ronda, slot), {})
        return {
            "local": local,
            "visitante": visitante,
            "slot": slot,
            "horario": fila.get("horario") or horario_default,
            "cancha": fila.get("cancha") or "",
            "marcador_local": fila.get("marcador_local"),
            "marcador_visitante": fila.get("marcador_visitante"),
            "jugado": fila.get("jugado", False),
            "ganador_forzado": fila.get("ganador_forzado"),
        }

    eliminatorias = {}

    if TAMANO_GRUPO[disciplina] is None:
        # Vóley Mixto: un único grupo, todos contra todos.
        # Los 2 mejores de la tabla pasan directo a la Final.
        clasificados = [primeros[letras[0]], segundos[letras[0]]]
        eliminatorias["Final"] = [
            construir_partido("Final", 0, clasificados[0], clasificados[1], "10:00")
        ]

    elif len(letras) == 2:
        # Fútbol Femenino / Básquet: 2 grupos -> Semifinales -> Final
        horario_semis = "15:40" if disciplina == "Fútbol Femenino" else "10:00"
        horario_final = "16:30" if disciplina == "Fútbol Femenino" else "10:00"

        eliminatorias["Semifinales"] = [
            construir_partido("Semifinales", 0, primeros[letras[0]], segundos[letras[1]], horario_semis),
            construir_partido("Semifinales", 1, primeros[letras[1]], segundos[letras[0]], horario_semis),
        ]

        ganador_sf1 = resolver_ganador(eliminatorias["Semifinales"][0])
        ganador_sf2 = resolver_ganador(eliminatorias["Semifinales"][1])

        eliminatorias["Final"] = [
            construir_partido("Final", 0, ganador_sf1, ganador_sf2, horario_final)
        ]

    elif len(letras) == 4:
        # Fútbol Masculino: 4 grupos -> Cuartos -> Semifinales -> Final
        eliminatorias["Cuartos de Final"] = [
            construir_partido("Cuartos de Final", 0, primeros[letras[0]], segundos[letras[2]], "12:30"),
            construir_partido("Cuartos de Final", 1, primeros[letras[1]], segundos[letras[3]], "13:00"),
            construir_partido("Cuartos de Final", 2, primeros[letras[2]], segundos[letras[0]], "13:30"),
            construir_partido("Cuartos de Final", 3, primeros[letras[3]], segundos[letras[1]], "14:00"),
        ]

        ganadores_cuartos = [resolver_ganador(p) for p in eliminatorias["Cuartos de Final"]]

        eliminatorias["Semifinales"] = [
            construir_partido("Semifinales", 0, ganadores_cuartos[0], ganadores_cuartos[1], "14:30"),
            construir_partido("Semifinales", 1, ganadores_cuartos[2], ganadores_cuartos[3], "15:00"),
        ]

        ganador_sf1 = resolver_ganador(eliminatorias["Semifinales"][0])
        ganador_sf2 = resolver_ganador(eliminatorias["Semifinales"][1])

        eliminatorias["Final"] = [
            construir_partido("Final", 0, ganador_sf1, ganador_sf2, "16:00")
        ]

    final = eliminatorias.get("Final", [None])[0]
    campeon = resolver_ganador(final) if final else None
    campeon_tribu = nombre_a_tribu(disciplina, campeon) if campeon else None

    return eliminatorias, campeon, campeon_tribu



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
                <span>Grupo {escape(str(grupo))} | {escape(str(partido['horario']))} | {escape(str(partido.get('cancha', '')))}</span>
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

    for disciplina in DISCIPLINAS:
        for grupo_label in construir_esqueletos()[disciplina]["grupos_nombres"]:
            partidos_grupo = obtener_partidos_grupo(disciplina, grupo_label)
            total_partidos += len(partidos_grupo)
            partidos_jugados += sum(1 for p in partidos_grupo if p["jugado"])

        _, campeon, _ = construir_eliminatorias(disciplina)
        if campeon:
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
    for disciplina in DISCIPLINAS:
        for grupo_label in construir_esqueletos()[disciplina]["grupos_nombres"]:
            for p in obtener_partidos_grupo(disciplina, grupo_label):
                if not p["jugado"]:
                    proximos.append((disciplina, p))

    proximos.sort(key=lambda item: item[1]["horario"])

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
            st.caption(
                "El tablón, los Torneos Express y el cronograma quedaron "
                "fuera del alcance de la sincronización con base de datos "
                "definida para este cambio, así que cada edición solo se "
                "ve en tu propia sesión/pestaña."
            )
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
            for e in construir_esqueletos()[disciplina]["equipos"]
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
    esqueleto = construir_esqueletos()[disciplina]
    limite = LIMITES_MARCADOR[disciplina]
    fase_cerrada = leer_estado_disciplinas().get(disciplina, False)

    st.markdown(
        f"""
        <div class="sport-card" style="margin-bottom:20px;">
            <div class="sport-name">{escape(disciplina)}</div>
            <div class="sport-meta">
                Límite de marcador: {limite} |
                Equipos: {len(esqueleto['equipos'])} |
                Grupos: {len(esqueleto['grupos_nombres'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_fixture, tab_posiciones, tab_eliminatorias = st.tabs(
        ["Fixture", "Tabla de posiciones", "Eliminatorias"]
    )

    with tab_fixture:
        for grupo_label in esqueleto["grupos_nombres"]:
            st.markdown(
                f'<div class="section-label">Grupo {escape(str(grupo_label))}</div>',
                unsafe_allow_html=True,
            )

            partidos_grupo = obtener_partidos_grupo(disciplina, grupo_label)

            for p in partidos_grupo:
                slot = p["slot"]

                if st.session_state.admin_logueado:
                    render_match_card(disciplina, grupo_label, p)

                    cols = st.columns([1.8, 1.2, 1, 1, 1])

                    nuevo_horario = cols[0].text_input(
                        "Horario",
                        value=p["horario"],
                        key=f"horario_{disciplina}_{grupo_label}_{slot}",
                    )

                    cancha = cols[1].text_input(
                        "Cancha",
                        value=p.get("cancha", ""),
                        key=f"cancha_{disciplina}_{grupo_label}_{slot}",
                    )

                    gl = cols[2].number_input(
                        "Local",
                        min_value=0,
                        max_value=limite,
                        value=p["marcador_local"] if p["marcador_local"] is not None else 0,
                        key=f"gl_{disciplina}_{grupo_label}_{slot}",
                    )

                    gv = cols[3].number_input(
                        "Visitante",
                        min_value=0,
                        max_value=limite,
                        value=p["marcador_visitante"] if p["marcador_visitante"] is not None else 0,
                        key=f"gv_{disciplina}_{grupo_label}_{slot}",
                    )

                    if cols[4].button(
                        "Guardar",
                        key=f"guardar_{disciplina}_{grupo_label}_{slot}",
                    ):
                        guardar_resultado_partido(
                            disciplina, "grupo", grupo_label, slot,
                            marcador_local=int(gl),
                            marcador_visitante=int(gv),
                            horario=nuevo_horario,
                            cancha=cancha,
                            jugado=True,
                        )
                        st.rerun()
                else:
                    render_match_card(disciplina, grupo_label, p)

        if st.session_state.admin_logueado and not fase_cerrada:
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
                    guardar_estado_fase(disciplina, True)
                    st.session_state[confirm_key] = False
                    st.rerun()

                if c2.button(
                    "Cancelar",
                    key=f"cancelar_{disciplina}",
                ):
                    st.session_state[confirm_key] = False
                    st.rerun()

    with tab_posiciones:
        for grupo_label, nombres_grupo in esqueleto["grupos_nombres"].items():
            st.markdown(
                f'<div class="section-label">Grupo {escape(str(grupo_label))}</div>',
                unsafe_allow_html=True,
            )

            partidos_grupo = obtener_partidos_grupo(disciplina, grupo_label)
            tabla = calcular_tabla_posiciones(nombres_grupo, partidos_grupo)
            render_table(tabla)

    with tab_eliminatorias:
        if not fase_cerrada:
            st.info(
                "El cuadro de eliminatorias aparecerá cuando "
                "el administrador cierre la fase de grupos."
            )
        else:
            eliminatorias, campeon, campeon_tribu = construir_eliminatorias(disciplina)

            for ronda, partidos_ronda in eliminatorias.items():
                st.markdown(
                    f'<div class="section-label">{escape(ronda)}</div>',
                    unsafe_allow_html=True,
                )

                for p in partidos_ronda:
                    slot = p["slot"]

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
                        cols = st.columns([1, 1, 2])

                        gl = cols[0].number_input(
                            "Local",
                            min_value=0,
                            max_value=limite,
                            value=0,
                            key=f"elim_gl_{disciplina}_{ronda}_{slot}",
                        )

                        gv = cols[1].number_input(
                            "Visitante",
                            min_value=0,
                            max_value=limite,
                            value=0,
                            key=f"elim_gv_{disciplina}_{ronda}_{slot}",
                        )

                        ganador_manual = cols[2].selectbox(
                            "¿Definido por penales / caso especial?",
                            ["Automático (según marcador)", p["local"], p["visitante"]],
                            key=f"elim_ganador_{disciplina}_{ronda}_{slot}",
                            help=(
                                "Usá esta opción solo cuando el marcador no "
                                "alcanza para determinar quién avanza (por "
                                "ejemplo, una definición por penales). En "
                                "ese caso, elegí directamente al equipo "
                                "ganador en vez de cargar un marcador."
                            ),
                        )

                        if st.button(
                            "Guardar resultado",
                            key=f"elim_guardar_{disciplina}_{ronda}_{slot}",
                        ):
                            gano_forzado = (
                                None if ganador_manual == "Automático (según marcador)"
                                else ganador_manual
                            )

                            if gano_forzado is None and gl == gv:
                                st.error(
                                    "No se permiten empates en eliminatorias. "
                                    "Cargá el resultado final o indicá el "
                                    "ganador manualmente (por ejemplo, por "
                                    "penales)."
                                )
                            else:
                                guardar_resultado_partido(
                                    disciplina, "eliminatoria", ronda, slot,
                                    marcador_local=int(gl),
                                    marcador_visitante=int(gv),
                                    jugado=True,
                                    ganador_forzado=gano_forzado,
                                )
                                st.rerun()

            if campeon:
                st.markdown(
                    f"""
                    <div class="champion-banner">
                        <div class="champion-label">Campeón de {escape(disciplina)}</div>
                        <div class="champion-name">{escape(campeon)}</div>
                        <div style="color:#A8B0B6;">
                            Tribu {escape(campeon_tribu)}
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

        # --->BOTÓN <---
        # ---> REEMPLAZÁ EL CÓDIGO DEL BOTÓN POR ESTE <---
        st.markdown("---")
        st.write("🛠️ **Herramientas de Desarrollo (Modo Prueba)**")
        if st.button("🚨 Resetear todos los resultados a 0"):
            try:
                from supabase import create_client
                url = st.secrets["SUPABASE_URL"]
                key = st.secrets["SUPABASE_KEY"]
                cliente_db = create_client(url, key)
                
                # Usamos los nombres exactos de tu tabla
                cliente_db.table("resultados_partidos").update({
                    "jugado": False,
                    "marcador_local": 0,
                    "marcador_visitante": 0
                }).eq("jugado", True).execute()
                
                st.success("¡Resultados limpios! Recargá la página para ver todo en cero.")
            except Exception as e:
                st.error(f"Error al resetear: {e}")
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
    # Refresco automático: cada 15 segundos se vuelve a ejecutar el script,
    # lo que fuerza una nueva lectura de Supabase (sujeta al caché de 5s).
    # Así, un usuario que dejó la página abierta también ve los resultados
    # nuevos sin tener que tocar nada.
    st_autorefresh(interval=15_000, key="auto_refresco")

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

        if st.button("🔄 Actualizar ahora", use_container_width=True):
            leer_resultados_partidos.clear()
            leer_estado_disciplinas.clear()
            st.rerun()

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
