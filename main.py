# ==============================================================================
# LA COPA AGRO - Aplicación de gestión de torneo deportivo
# ==============================================================================
# Desarrollado en Streamlit. Pensado para ser modificado fácilmente por
# Julieta (administradora del proyecto) desde Replit.
#
# CÓMO CORRERLO EN REPLIT:
#   1. Asegurate de tener un archivo requirements.txt con la línea: streamlit
#   2. Comando de ejecución: streamlit run main.py
#
# PIN de administrador: JBJ2026 (ver función "vista_login_admin")
# ==============================================================================

import streamlit as st
from datetime import datetime

# ------------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="La Copa Agro",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Inyección de CSS para forzar la tipografía moderna
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)
PIN_ADMIN = "JBJ2026"

# Colores representativos de cada tribu (interfaz)
TRIBUS = {
    "Maíz": {"color": "#2E7D32", "texto": "#FFFFFF"},
    "Trigo": {"color": "#F9A825", "texto": "#000000"},
    "Angus": {"color": "#C62828", "texto": "#FFFFFF"},
    "Holando": {"color": "#212121", "texto": "#FFFFFF"},
}

# Cantidad de equipos por tribu, según disciplina
EQUIPOS_POR_TRIBU = {
    "Fútbol Masculino": 3,
    "Fútbol Femenino": 2,
    "Básquet": 2,
    "Vóley Mixto": 1,
}

# Tamaño de cada grupo por disciplina (None = todos contra todos, sin grupos)
TAMANO_GRUPO = {
    "Fútbol Masculino": 3,   # 12 equipos -> 4 grupos de 3
    "Fútbol Femenino": 4,    # 8 equipos -> 2 grupos de 4
    "Básquet": 4,            # 8 equipos -> 2 grupos de 4
    "Vóley Mixto": None,     # 4 equipos -> todos contra todos, sin grupos
}

# Tope de marcador por disciplina (evita errores de tipeo del admin)
LIMITES_MARCADOR = {
    "Fútbol Masculino": 30,
    "Fútbol Femenino": 30,
    "Básquet": 150,
    "Vóley Mixto": 50,
}

# Cuántos equipos pasan de cada grupo a la siguiente ronda
CLASIFICADOS_POR_GRUPO = 2

DISCIPLINAS = list(EQUIPOS_POR_TRIBU.keys())
NOMBRES_GRUPOS = ["A", "B", "C", "D", "E", "F"]


# ==============================================================================
# INICIALIZACIÓN DE DATOS (simula una base de datos usando st.session_state)
# ==============================================================================

def generar_partidos_round_robin(equipos_nombres, grupo_label):
    """Genera los partidos de 'todos contra todos' para una lista de equipos."""
    partidos = []
    for i in range(len(equipos_nombres)):
        for j in range(i + 1, len(equipos_nombres)):
            partidos.append({
                "grupo": grupo_label,
                "local": equipos_nombres[i],
                "visitante": equipos_nombres[j],
                "marcador_local": None,
                "marcador_visitante": None,
                # ### REEMPLAZAR CON HORARIOS REALES ACÁ ### (dato de relleno)
                "horario": "10:00 AM",
                "jugado": False,
            })
    return partidos


def crear_equipos_disciplina(disciplina):
    """Crea los equipos de relleno para una disciplina, repartidos entre tribus."""
    equipos = []
    orden_tribus = list(TRIBUS.keys())
    cantidad_por_tribu = EQUIPOS_POR_TRIBU[disciplina]
    contador_tribu = {t: 0 for t in orden_tribus}

    total_equipos = cantidad_por_tribu * len(orden_tribus)
    for n in range(total_equipos):
        tribu = orden_tribus[n % len(orden_tribus)]
        contador_tribu[tribu] += 1
        # ############################################################
        # ### REEMPLAZAR CON NOMBRES DE EQUIPOS ACÁ ###
        # Este es el dato de relleno que Julieta debe reemplazar por
        # los nombres reales de los equipos cuando estén confirmados.
        # ############################################################
        nombre = f"Equipo {contador_tribu[tribu]} {disciplina} ({tribu})"
        equipos.append({
            "nombre": nombre,
            "tribu": tribu,
            # ### REEMPLAZAR CON NOMBRES DE PARTICIPANTES ACÁ ###
            "participantes": [f"Jugador/a {p+1}" for p in range(8)],
        })
    return equipos


def armar_grupos(equipos, disciplina):
    """Divide la lista de equipos en grupos según TAMANO_GRUPO."""
    tam = TAMANO_GRUPO[disciplina]
    nombres = [e["nombre"] for e in equipos]

    if tam is None:
        # Sin grupos: un único grupo "Único" con todos los equipos
        grupos = {"Único": nombres}
    else:
        grupos = {}
        for idx, inicio in enumerate(range(0, len(nombres), tam)):
            letra = NOMBRES_GRUPOS[idx]
            grupos[letra] = nombres[inicio:inicio + tam]
    return grupos


def inicializar_disciplina(disciplina):
    equipos = crear_equipos_disciplina(disciplina)
    grupos = armar_grupos(equipos, disciplina)

    partidos = []
    for grupo_label, equipos_grupo in grupos.items():
        partidos.extend(generar_partidos_round_robin(equipos_grupo, grupo_label))

    return {
        "equipos": equipos,
        "grupos": grupos,
        "partidos": partidos,
        "fase_grupos_cerrada": False,
        "clasificados": [],          # lista de nombres de equipos clasificados
        "eliminatorias": {},         # dict con las llaves de eliminatorias
        "campeon": None,             # nombre del equipo campeón
        "campeon_tribu": None,
        "bonus_otorgado": False,     # evita sumar el +5 dos veces
    }


def inicializar_estado():
    """Crea todo el estado inicial de la app la primera vez que se ejecuta."""
    if "app_inicializada" in st.session_state:
        return

    st.session_state.admin_logueado = False

    st.session_state.datos = {
        disciplina: inicializar_disciplina(disciplina) for disciplina in DISCIPLINAS
    }

    # Tablón de anuncios (dato de relleno)
    st.session_state.tablon = [
        "🏆 ¡Bienvenidos a La Copa Agro 2026!",
        "📢 Recordá inscribir tu equipo antes del inicio del torneo.",
    ]

    # Torneos Express: lista de eventos que suman +1 a la tribu
    st.session_state.torneos_express = [
        # Ejemplo de dato de relleno, el admin puede agregar/eliminar
        {"tribu": "Trigo", "concepto": "Torneo de Truco", "puntos": 1},
    ]

    # Cronograma general (dato de relleno)
    st.session_state.cronograma = [
        {"horario": "08:00 AM", "actividad": "Apertura y bienvenida"},
        {"horario": "09:00 AM", "actividad": "Inicio Fase de Grupos - Todas las disciplinas"},
        {"horario": "01:00 PM", "actividad": "Pausa - Almuerzo"},
        {"horario": "02:30 PM", "actividad": "Reanudación de partidos"},
        {"horario": "06:00 PM", "actividad": "Instancias finales"},
        {"horario": "07:30 PM", "actividad": "Premiación"},
        {"horario": "09:00 PM", "actividad": "La peña de Agro (al día siguiente)"},
        # ### REEMPLAZAR CON HORARIOS REALES ACÁ ###
    ]

    st.session_state.app_inicializada = True


inicializar_estado()


# ==============================================================================
# FUNCIONES DE CÁLCULO (posiciones, desempates, tabla global)
# ==============================================================================

def calcular_tabla_posiciones(equipos_grupo, partidos_grupo):
    """Calcula la tabla de posiciones de un grupo (PJ, PG, PE, PP, GF, GC, DIF, Pts)."""
    tabla = {
        nombre: {"PJ": 0, "PG": 0, "PE": 0, "PP": 0, "GF": 0, "GC": 0, "Pts": 0}
        for nombre in equipos_grupo
    }

    for p in partidos_grupo:
        if not p["jugado"]:
            continue
        local, visitante = p["local"], p["visitante"]
        gl, gv = p["marcador_local"], p["marcador_visitante"]

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
        dif = datos["GF"] - datos["GC"]
        filas.append({"Equipo": nombre, **datos, "DIF": dif})

    # Desempate en grupos: por diferencia de tantos (a favor menos en contra)
    filas.sort(key=lambda x: (-x["Pts"], -x["DIF"], -x["GF"]))
    return filas


def nombre_a_tribu(disciplina, nombre_equipo):
    for e in st.session_state.datos[disciplina]["equipos"]:
        if e["nombre"] == nombre_equipo:
            return e["tribu"]
    return None


def calcular_tabla_global():
    """Suma los puntos de fase de grupos + bonus de campeón + torneos express."""
    puntos = {t: 0 for t in TRIBUS}
    puntos_express = {t: 0 for t in TRIBUS}

    # Puntos de fase de grupos (3/1/0) de todas las disciplinas
    for disciplina, datos in st.session_state.datos.items():
        for grupo_label, equipos_grupo in datos["grupos"].items():
            partidos_grupo = [p for p in datos["partidos"] if p["grupo"] == grupo_label]
            tabla = calcular_tabla_posiciones(equipos_grupo, partidos_grupo)
            for fila in tabla:
                tribu = nombre_a_tribu(disciplina, fila["Equipo"])
                if tribu:
                    puntos[tribu] += fila["Pts"]

        # Bonus de campeón de disciplina (+5 puntos)
        if datos["campeon_tribu"]:
            puntos[datos["campeon_tribu"]] += 5

    # Torneos Express
    for evento in st.session_state.torneos_express:
        puntos[evento["tribu"]] += evento["puntos"]
        puntos_express[evento["tribu"]] += evento["puntos"]

    filas = []
    for tribu in TRIBUS:
        filas.append({
            "Tribu": tribu,
            "Puntos Totales": puntos[tribu],
            "Puntos Express": puntos_express[tribu],
        })

    # Desempate Global (Copa Agro): gana quien tenga más puntos de Torneos Express
    filas.sort(key=lambda x: (-x["Puntos Totales"], -x["Puntos Express"]))
    return filas


def armar_llave_eliminatoria(disciplina):
    """Arma el cuadro de eliminatorias según los clasificados de cada grupo."""
    datos = st.session_state.datos[disciplina]
    grupos = datos["grupos"]

    primeros = {}
    segundos = {}
    for grupo_label, equipos_grupo in grupos.items():
        partidos_grupo = [p for p in datos["partidos"] if p["grupo"] == grupo_label]
        tabla = calcular_tabla_posiciones(equipos_grupo, partidos_grupo)
        primeros[grupo_label] = tabla[0]["Equipo"]
        segundos[grupo_label] = tabla[1]["Equipo"]

    clasificados = list(primeros.values()) + list(segundos.values())
    datos["clasificados"] = clasificados

    letras = list(grupos.keys())

    if TAMANO_GRUPO[disciplina] is None:
        # Vóley Mixto: sin grupos, los 2 mejores pasan directo a la Final
        datos["eliminatorias"] = {
            "Final": [{
                "local": clasificados[0], "visitante": clasificados[1],
                "marcador_local": None, "marcador_visitante": None, "jugado": False,
            }]
        }
    elif len(letras) == 2:
        # Fútbol Femenino / Básquet: 2 grupos -> Semifinales -> Final
        datos["eliminatorias"] = {
            "Semifinales": [
                {"local": primeros[letras[0]], "visitante": segundos[letras[1]],
                 "marcador_local": None, "marcador_visitante": None, "jugado": False},
                {"local": primeros[letras[1]], "visitante": segundos[letras[0]],
                 "marcador_local": None, "marcador_visitante": None, "jugado": False},
            ],
            "Final": [
                {"local": None, "visitante": None,
                 "marcador_local": None, "marcador_visitante": None, "jugado": False},
            ],
        }
    elif len(letras) == 4:
        # Fútbol Masculino: 4 grupos -> Cuartos -> Semis -> Final
        datos["eliminatorias"] = {
            "Cuartos de Final": [
                {"local": primeros[letras[0]], "visitante": segundos[letras[1]],
                 "marcador_local": None, "marcador_visitante": None, "jugado": False},
                {"local": primeros[letras[1]], "visitante": segundos[letras[0]],
                 "marcador_local": None, "marcador_visitante": None, "jugado": False},
                {"local": primeros[letras[2]], "visitante": segundos[letras[3]],
                 "marcador_local": None, "marcador_visitante": None, "jugado": False},
                {"local": primeros[letras[3]], "visitante": segundos[letras[2]],
                 "marcador_local": None, "marcador_visitante": None, "jugado": False},
            ],
            "Semifinales": [
                {"local": None, "visitante": None,
                 "marcador_local": None, "marcador_visitante": None, "jugado": False},
                {"local": None, "visitante": None,
                 "marcador_local": None, "marcador_visitante": None, "jugado": False},
            ],
            "Final": [
                {"local": None, "visitante": None,
                 "marcador_local": None, "marcador_visitante": None, "jugado": False},
            ],
        }

    datos["fase_grupos_cerrada"] = True


def avanzar_ganadores(disciplina):
    """Completa automáticamente la siguiente ronda con los ganadores ya cargados."""
    eliminatorias = st.session_state.datos[disciplina]["eliminatorias"]
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

    # Si la Final ya se jugó, definir campeón (una sola vez)
    datos = st.session_state.datos[disciplina]
    final = eliminatorias.get("Final", [None])[0]
    if final and final["jugado"] and not datos["bonus_otorgado"]:
        ganador = (final["local"] if final["marcador_local"] > final["marcador_visitante"]
                   else final["visitante"])
        datos["campeon"] = ganador
        datos["campeon_tribu"] = nombre_a_tribu(disciplina, ganador)
        datos["bonus_otorgado"] = True


# ==============================================================================
# COMPONENTES VISUALES REUTILIZABLES
# ==============================================================================

def encabezado_tribu(tribu):
    info = TRIBUS[tribu]
    st.markdown(
        f"""<div style="background-color:{info['color']}; color:{info['texto']};
        padding:10px 16px; border-radius:8px; font-weight:bold; font-size:1.1em;
        margin-bottom:8px;">Tribu {tribu}</div>""",
        unsafe_allow_html=True,
    )


def mostrar_tabla_posiciones(disciplina, grupo_label, equipos_grupo):
    partidos_grupo = [p for p in st.session_state.datos[disciplina]["partidos"]
                       if p["grupo"] == grupo_label]
    tabla = calcular_tabla_posiciones(equipos_grupo, partidos_grupo)
    st.dataframe(tabla, use_container_width=True, hide_index=True)


# ==============================================================================
# VISTA: INICIO
# ==============================================================================

def vista_inicio():
    st.title("🏆 La Copa Agro")
    st.caption("Torneo deportivo entre tribus")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fotos pendientes")
        # ### INSERTAR LINK DE IMAGEN ACÁ ###
        st.image("https://via.placeholder.com/400x300.png?text=Foto+de+Kuani",
                  use_container_width=True)
    with col2:
        st.subheader("Fotos pendientes")
        # ### INSERTAR LINK DE IMAGEN ACÁ ###
        st.image("https://via.placeholder.com/400x300.png?text=Foto+de+Walterms",
                  use_container_width=True)

    st.divider()

    st.subheader("⚡ Jugando ahora / Próximos partidos")
    proximos = []
    for disciplina, datos in st.session_state.datos.items():
        for p in datos["partidos"]:
            if not p["jugado"]:
                proximos.append({
                    "Disciplina": disciplina,
                    "Grupo": p["grupo"],
                    "Partido": f"{p['local']} vs {p['visitante']}",
                    "Horario": p["horario"],
                })
    if proximos:
        st.dataframe(proximos[:8], use_container_width=True, hide_index=True)
    else:
        st.info("No hay partidos pendientes en fase de grupos por el momento.")

    st.divider()

    st.subheader("📢 Tablón de anuncios")
    for aviso in st.session_state.tablon:
        st.markdown(f"- {aviso}")

    if st.session_state.admin_logueado:
        with st.expander("➕ Administrar tablón de anuncios"):
            nuevo_aviso = st.text_input("Nuevo anuncio", key="nuevo_aviso_input")
            if st.button("Agregar anuncio"):
                if nuevo_aviso.strip():
                    st.session_state.tablon.append(nuevo_aviso.strip())
                    st.rerun()
            if st.session_state.tablon:
                aviso_a_borrar = st.selectbox("Eliminar anuncio", st.session_state.tablon)
                if st.button("Eliminar anuncio seleccionado"):
                    st.session_state.tablon.remove(aviso_a_borrar)
                    st.rerun()

    st.divider()

    st.subheader("🤝 Sponsors")
    # ### INSERTAR LINK DE IMAGEN ACÁ ### (grilla de sponsors, dato de relleno)
    sponsors = ["Sponsor A", "Sponsor B", "Sponsor C", "Sponsor D"]
    cols = st.columns(len(sponsors))
    for col, sponsor in zip(cols, sponsors):
        with col:
            st.image(f"https://via.placeholder.com/200x100.png?text={sponsor.replace(' ', '+')}",
                      use_container_width=True)


# ==============================================================================
# VISTA: TRIBUS
# ==============================================================================

def vista_tribus():
    st.title("👥 Tribus")

    tribu_seleccionada = st.selectbox("Elegí una tribu", list(TRIBUS.keys()))
    encabezado_tribu(tribu_seleccionada)

    for disciplina in DISCIPLINAS:
        equipos_tribu = [
            e for e in st.session_state.datos[disciplina]["equipos"]
            if e["tribu"] == tribu_seleccionada
        ]
        if not equipos_tribu:
            continue

        st.markdown(f"#### {disciplina}")
        for equipo in equipos_tribu:
            with st.expander(equipo["nombre"]):
                st.write("**Participantes:**")
                for participante in equipo["participantes"]:
                    st.markdown(f"- {participante}")


# ==============================================================================
# VISTA: DISCIPLINAS
# ==============================================================================

def vista_disciplinas():
    st.title("⚽ Disciplinas")

    disciplina = st.selectbox("Elegí una disciplina", DISCIPLINAS)
    datos = st.session_state.datos[disciplina]
    limite = LIMITES_MARCADOR[disciplina]

    tab_fixture, tab_posiciones, tab_eliminatorias = st.tabs(
        ["📅 Fixture / Horarios", "📊 Tabla de Posiciones", "🏅 Cuadro de Eliminatorias"]
    )

    # --- FIXTURE / HORARIOS ---------------------------------------------------
    with tab_fixture:
        for grupo_label, equipos_grupo in datos["grupos"].items():
            st.markdown(f"**Grupo {grupo_label}**")
            partidos_grupo = [p for p in datos["partidos"] if p["grupo"] == grupo_label]

            for idx, p in enumerate(partidos_grupo):
                cols = st.columns([3, 1, 1, 2])
                cols[0].write(f"{p['local']} vs {p['visitante']}")

                if st.session_state.admin_logueado:
                    nuevo_horario = cols[3].text_input(
                        "Horario", value=p["horario"],
                        key=f"horario_{disciplina}_{grupo_label}_{idx}",
                        label_visibility="collapsed",
                    )
                    p["horario"] = nuevo_horario

                    gl = cols[1].number_input(
                        "Local", min_value=0, max_value=limite,
                        value=p["marcador_local"] if p["marcador_local"] is not None else 0,
                        key=f"gl_{disciplina}_{grupo_label}_{idx}",
                        label_visibility="collapsed",
                    )
                    gv = cols[2].number_input(
                        "Visitante", min_value=0, max_value=limite,
                        value=p["marcador_visitante"] if p["marcador_visitante"] is not None else 0,
                        key=f"gv_{disciplina}_{grupo_label}_{idx}",
                        label_visibility="collapsed",
                    )
                    if st.button("Guardar resultado", key=f"guardar_{disciplina}_{grupo_label}_{idx}"):
                        p["marcador_local"] = gl
                        p["marcador_visitante"] = gv
                        p["jugado"] = True
                        st.rerun()
                else:
                    marcador = (f"{p['marcador_local']} - {p['marcador_visitante']}"
                                if p["jugado"] else "vs")
                    cols[1].write(marcador)
                    cols[3].write(p["horario"])
            st.markdown("---")

        if st.session_state.admin_logueado and not datos["fase_grupos_cerrada"]:
            st.warning(
                "Al cerrar la fase de grupos se calculan los clasificados "
                "(por puntos y diferencia de gol) y se arma el cuadro de eliminatorias. "
                "Esta acción no se puede deshacer."
            )
            confirmar_key = f"confirmar_cierre_{disciplina}"
            if confirmar_key not in st.session_state:
                st.session_state[confirmar_key] = False

            if not st.session_state[confirmar_key]:
                if st.button(f"Cerrar Fase de Grupos y Calcular ({disciplina})"):
                    st.session_state[confirmar_key] = True
                    st.rerun()
            else:
                st.error("¿Confirmás el cierre de la fase de grupos y el avance de equipos?")
                c1, c2 = st.columns(2)
                if c1.button("✅ Confirmar avance", key=f"si_{disciplina}"):
                    armar_llave_eliminatoria(disciplina)
                    st.session_state[confirmar_key] = False
                    st.success("¡Fase de grupos cerrada! Cuadro de eliminatorias generado.")
                    st.rerun()
                if c2.button("❌ Cancelar", key=f"no_{disciplina}"):
                    st.session_state[confirmar_key] = False
                    st.rerun()

    # --- TABLA DE POSICIONES ---------------------------------------------------
    with tab_posiciones:
        for grupo_label, equipos_grupo in datos["grupos"].items():
            st.markdown(f"**Grupo {grupo_label}**")
            mostrar_tabla_posiciones(disciplina, grupo_label, equipos_grupo)

    # --- CUADRO DE ELIMINATORIAS ------------------------------------------------
    with tab_eliminatorias:
        if not datos["fase_grupos_cerrada"]:
            st.info("El cuadro de eliminatorias se generará cuando el admin cierre la fase de grupos.")
        else:
            for ronda, partidos_ronda in datos["eliminatorias"].items():
                st.markdown(f"**{ronda}**")
                for idx, p in enumerate(partidos_ronda):
                    if p["local"] is None or p["visitante"] is None:
                        st.write("Por definir")
                        continue

                    cols = st.columns([3, 1, 1, 2])
                    cols[0].write(f"{p['local']} vs {p['visitante']}")

                    if st.session_state.admin_logueado and not p["jugado"]:
                        gl = cols[1].number_input(
                            "Local", min_value=0, max_value=limite, value=0,
                            key=f"elim_gl_{disciplina}_{ronda}_{idx}",
                            label_visibility="collapsed",
                        )
                        gv = cols[2].number_input(
                            "Visitante", min_value=0, max_value=limite, value=0,
                            key=f"elim_gv_{disciplina}_{ronda}_{idx}",
                            label_visibility="collapsed",
                        )
                        if cols[3].button("Guardar", key=f"elim_guardar_{disciplina}_{ronda}_{idx}"):
                            if gl == gv:
                                st.error("No se permiten empates en fases eliminatorias. "
                                         "Cargá el resultado final (con penales / alargue incluidos).")
                            else:
                                p["marcador_local"] = gl
                                p["marcador_visitante"] = gv
                                p["jugado"] = True
                                avanzar_ganadores(disciplina)
                                st.rerun()
                    else:
                        marcador = (f"{p['marcador_local']} - {p['marcador_visitante']}"
                                    if p["jugado"] else "vs")
                        cols[1].write(marcador)
                st.markdown("---")

            if datos["campeon"]:
                st.success(f"🏆 Campeón de {disciplina}: **{datos['campeon']}** "
                           f"(Tribu {datos['campeon_tribu']}) — +5 puntos a la tabla global")


# ==============================================================================
# VISTA: TABLA GLOBAL DE TRIBUS
# ==============================================================================

def vista_tabla_global():
    st.title("📈 Tabla Global de Tribus")

    tabla = calcular_tabla_global()

    for fila in tabla:
        tribu = fila["Tribu"]
        info = TRIBUS[tribu]
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(
                f"""<div style="background-color:{info['color']}; color:{info['texto']};
                padding:12px 16px; border-radius:8px; font-weight:bold; font-size:1.1em;">
                {tribu} — {fila['Puntos Totales']} puntos
                </div>""",
                unsafe_allow_html=True,
            )
        with col2:
            st.write("")

        if fila["Puntos Express"] > 0:
            with st.expander(f"Ver origen de los puntos Express de {tribu}"):
                eventos_tribu = [e for e in st.session_state.torneos_express if e["tribu"] == tribu]
                for evento in eventos_tribu:
                    st.markdown(f"- Tribu {tribu} sumó +{evento['puntos']}pto en: {evento['concepto']}")
        st.write("")

    if st.session_state.admin_logueado:
        st.divider()
        st.subheader("➕ Cargar Torneo Express")
        with st.form("form_torneo_express"):
            tribu_sel = st.selectbox("Tribu", list(TRIBUS.keys()))
            concepto = st.text_input("Concepto (ej: Torneo de Truco)")
            puntos = st.number_input("Puntos a sumar", min_value=0, value=1, step=1)
            enviado = st.form_submit_button("Agregar Torneo Express")
            if enviado and concepto.strip():
                st.session_state.torneos_express.append({
                    "tribu": tribu_sel, "concepto": concepto.strip(), "puntos": int(puntos)
                })
                st.success("Torneo Express agregado.")
                st.rerun()


# ==============================================================================
# VISTA: CRONOGRAMA GENERAL
# ==============================================================================

def vista_cronograma():
    st.title("🗓️ Cronograma General")

    if st.session_state.admin_logueado:
        st.info("Como administrador podés editar los horarios del cronograma abajo.")
        for idx, item in enumerate(st.session_state.cronograma):
            cols = st.columns([1, 3])
            item["horario"] = cols[0].text_input(
                "Horario", value=item["horario"], key=f"cron_h_{idx}", label_visibility="collapsed"
            )
            item["actividad"] = cols[1].text_input(
                "Actividad", value=item["actividad"], key=f"cron_a_{idx}", label_visibility="collapsed"
            )
    else:
        st.dataframe(st.session_state.cronograma, use_container_width=True, hide_index=True)


# ==============================================================================
# VISTA: PREMIOS Y REGLAMENTO
# ==============================================================================

def vista_premios():
    st.title("📜 Premios y Reglamento")

    st.markdown("""
### 🏆 Premiación
- La tribu campeona de **La Copa Agro** es la que acumule más puntos totales al finalizar el torneo.
- Cada disciplina entrega también su propio campeón, que otorga **+5 puntos** directos a la tabla global.

### 📋 Sistema de puntuación
- **Fase de grupos:** Victoria = 3 pts · Empate = 1 pt · Derrota = 0 pts
- **Campeón de disciplina:** +5 puntos directos a la tribu
- **Torneos Express:** +1 punto a la tabla global por cada torneo ganado

### ⚖️ Reglas de desempate
- **En un grupo:** se define por diferencia de tantos (goles/puntos a favor menos en contra).
- **En la tabla global:** si dos tribus empatan en puntos totales, gana la que tenga más puntos
  acumulados exclusivamente de Torneos Express.
- **En fases eliminatorias:** no existen los empates. El resultado final que carga el admin ya
  incluye penales, alargue, o la diferencia de dos puntos correspondiente en vóley.

### 🔒 Topes de marcador
- Fútbol Masculino y Femenino: máximo 30 goles por equipo
- Básquet: máximo 150 puntos por equipo
- Vóley Mixto: máximo 50 puntos por equipo

*(Sección de texto estático — Julieta puede editar este contenido libremente)*
    """)


# ==============================================================================
# VISTA: LOGIN ADMIN
# ==============================================================================

def vista_login_admin():
    st.title("🔐 Login Admin")

    if st.session_state.admin_logueado:
        st.success("Sesión de administrador activa.")
        if st.button("Cerrar sesión"):
            st.session_state.admin_logueado = False
            st.rerun()
        return

    pin_ingresado = st.text_input("Ingresá el PIN de administrador", type="password")
    if st.button("Ingresar"):
        if pin_ingresado == PIN_ADMIN:
            st.session_state.admin_logueado = True
            st.success("¡Acceso concedido! Ya podés editar el torneo desde las distintas secciones.")
            st.rerun()
        else:
            st.error("PIN incorrecto.")


# ==============================================================================
# NAVEGACIÓN LATERAL (MENÚ PRINCIPAL)
# ==============================================================================

def main():
    st.sidebar.title("🏆 La Copa Agro")

    if st.session_state.admin_logueado:
        st.sidebar.success("Modo Administrador activo")
    else:
        st.sidebar.info("Vista Pública (solo lectura)")

    secciones = [
        "Inicio",
        "Tribus",
        "Disciplinas",
        "Tabla Global Tribus",
        "Cronograma General",
        "Premios y Reglamento",
        "Login Admin",
    ]
    seccion = st.sidebar.radio("Navegación", secciones)

    if seccion == "Inicio":
        vista_inicio()
    elif seccion == "Tribus":
        vista_tribus()
    elif seccion == "Disciplinas":
        vista_disciplinas()
    elif seccion == "Tabla Global Tribus":
        vista_tabla_global()
    elif seccion == "Cronograma General":
        vista_cronograma()
    elif seccion == "Premios y Reglamento":
        vista_premios()
    elif seccion == "Login Admin":
        vista_login_admin()


if __name__ == "__main__":
    main()
