"""
Analizador de Fórmula 1 🏎️
Módulo 1: Comparador de telemetría entre pilotos
Construido con Streamlit + FastF1

Ejecutar con: streamlit run app.py
"""

import os

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import fastf1
import fastf1.plotting

# ----------------------------------------------------------------------------
# Configuración de página y caché de FastF1
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Analizador de F1", page_icon="🏎️", layout="wide")

CACHE_DIR = "f1_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)
fastf1.plotting.setup_mpl(misc_mpl_mods=False)

SESSION_LABELS = {
    "Prácticas 1": "FP1",
    "Prácticas 2": "FP2",
    "Prácticas 3": "FP3",
    "Clasificación": "Q",
    "Clasificación Sprint": "SQ",
    "Sprint": "S",
    "Carrera": "R",
}


# ----------------------------------------------------------------------------
# Funciones con caché (evitan volver a descargar/recalcular en cada rerun)
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_schedule(year: int) -> pd.DataFrame:
    return fastf1.get_event_schedule(year, include_testing=False)


@st.cache_resource(show_spinner="Descargando datos de la sesión (primera vez puede tardar)…")
def load_session(year: int, gp: str, session_code: str):
    session = fastf1.get_session(year, gp, session_code)
    session.load(telemetry=True, weather=False, messages=False)
    return session


def driver_options(session):
    """Devuelve lista de (código, etiqueta) para los selectores de piloto."""
    options = []
    for code in sorted(session.laps["Driver"].unique()):
        try:
            info = session.get_driver(code)
            label = f"{code} — {info['FullName']} ({info['TeamName']})"
        except Exception:
            label = code
        options.append((code, label))
    return options


def get_lap(session, driver_code, mode, lap_number=None):
    driver_laps = session.laps.pick_drivers(driver_code)
    if mode == "fastest":
        return driver_laps.pick_fastest()
    matching = driver_laps.pick_laps(int(lap_number))
    return matching.iloc[0] if len(matching) else None


def compute_delta(reference_lap, compare_lap):
    """Diferencia de tiempo acumulada a lo largo de la distancia.
    Valor positivo = el piloto de referencia va por delante en ese punto."""
    ref = reference_lap.get_car_data().add_distance()
    comp = compare_lap.get_car_data().add_distance()

    ref_time = ref["Time"].dt.total_seconds().to_numpy()
    ref_dist = ref["Distance"].to_numpy()
    comp_time = comp["Time"].dt.total_seconds().to_numpy()
    comp_dist = comp["Distance"].to_numpy()

    comp_time_interp = np.interp(ref_dist, comp_dist, comp_time)
    delta = comp_time_interp - ref_time
    return ref_dist, delta


def style_for(session, driver_code):
    return fastf1.plotting.get_driver_style(
        identifier=driver_code, style=["color", "linestyle"], session=session
    )


def plotly_dash(linestyle):
    return "solid" if linestyle in ("solid", "-") else "dash"


def fmt_time(value):
    if pd.isna(value):
        return "—"
    return str(value).split(" ")[-1][:-3]


# ----------------------------------------------------------------------------
# Barra lateral: selección de sesión
# ----------------------------------------------------------------------------
st.sidebar.title("🏎️ Analizador de F1")
st.sidebar.caption("Módulo 1 · Comparador de telemetría entre pilotos")

year = st.sidebar.selectbox("Temporada", list(range(2026, 2017, -1)))
st.sidebar.caption("La telemetría solo está disponible desde 2018 en adelante.")

schedule = get_schedule(year)
gp = st.sidebar.selectbox("Gran Premio", schedule["EventName"].tolist())

session_label = st.sidebar.selectbox("Sesión", list(SESSION_LABELS.keys()), index=6)
session_code = SESSION_LABELS[session_label]

load_clicked = st.sidebar.button("Cargar sesión", type="primary", use_container_width=True)
st.sidebar.caption("Si cambias Temporada/GP/Sesión, vuelve a pulsar este botón para aplicarlo.")

if "session" not in st.session_state:
    st.session_state.session = None

if load_clicked:
    try:
        st.session_state.session = load_session(year, gp, session_code)
    except Exception as e:
        st.session_state.session = None
        st.sidebar.error(f"No se pudo cargar la sesión: {e}")

st.sidebar.divider()
st.sidebar.info(
    "Próximas secciones: Temporada, Clasificación, Neumáticos, "
    "Pit stops, Sectores y Posiciones."
)

session = st.session_state.session

# ----------------------------------------------------------------------------
# Cuerpo principal
# ----------------------------------------------------------------------------
st.title("🏎️ Analizador de Fórmula 1")

if session is None:
    st.info(
        "Elige temporada, Gran Premio y sesión en la barra lateral, "
        "y pulsa **Cargar sesión** para empezar."
    )
    st.stop()

st.subheader(f"{session.event['EventName']} {year} — {session_label}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Circuito", session.event["Location"])
c2.metric("País", session.event["Country"])
c3.metric("Vueltas registradas", int(session.laps["LapNumber"].max()) if len(session.laps) else 0)
c4.metric("Pilotos", session.laps["Driver"].nunique())

st.divider()

options = driver_options(session)
codes = [o[0] for o in options]
labels = {o[0]: o[1] for o in options}

col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    driver1 = st.selectbox("Piloto 1", codes, format_func=lambda c: labels[c], index=0)
with col2:
    idx2 = 1 if len(codes) > 1 else 0
    driver2 = st.selectbox("Piloto 2", codes, format_func=lambda c: labels[c], index=idx2)
with col3:
    lap_mode_label = st.radio(
        "Vuelta a comparar", ["Vuelta más rápida", "Vuelta específica"], horizontal=True
    )
    lap_mode = "fastest" if lap_mode_label == "Vuelta más rápida" else "specific"

lap_number1 = lap_number2 = None
if lap_mode == "specific":
    max_lap = int(session.laps["LapNumber"].max())
    n1, n2 = st.columns(2)
    with n1:
        lap_number1 = st.number_input(f"Vuelta de {driver1}", min_value=1, max_value=max_lap, value=1, step=1)
    with n2:
        lap_number2 = st.number_input(f"Vuelta de {driver2}", min_value=1, max_value=max_lap, value=1, step=1)

lap1 = get_lap(session, driver1, lap_mode, lap_number1)
lap2 = get_lap(session, driver2, lap_mode, lap_number2)

if lap1 is None or lap2 is None or pd.isna(lap1.get("LapTime")) or pd.isna(lap2.get("LapTime")):
    st.warning("No se encontraron datos válidos para la vuelta seleccionada de alguno de los pilotos.")
    st.stop()

try:
    tel1 = lap1.get_telemetry()
    tel2 = lap2.get_telemetry()
except Exception as e:
    st.error(f"No se pudo obtener la telemetría de la vuelta seleccionada: {e}")
    st.stop()

style1, style2 = style_for(session, driver1), style_for(session, driver2)
color1, dash1 = style1["color"], plotly_dash(style1["linestyle"])
color2, dash2 = style2["color"], plotly_dash(style2["linestyle"])

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Velocidad y pedales", "RPM y marchas", "Delta de tiempo", "Mapa del circuito", "Resumen de vuelta"]
)

# ---- TAB 1: velocidad, acelerador, freno ----
with tab1:
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
        subplot_titles=("Velocidad (km/h)", "Acelerador (%)", "Freno (activado)"),
    )
    for tel, code, color, dash in [(tel1, driver1, color1, dash1), (tel2, driver2, color2, dash2)]:
        fig.add_trace(go.Scatter(x=tel["Distance"], y=tel["Speed"], name=code,
                                  line=dict(color=color, dash=dash)), row=1, col=1)
        fig.add_trace(go.Scatter(x=tel["Distance"], y=tel["Throttle"], name=code,
                                  line=dict(color=color, dash=dash), showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=tel["Distance"], y=tel["Brake"].astype(int), name=code,
                                  line=dict(color=color, dash=dash, shape="hv"), showlegend=False), row=3, col=1)
    fig.update_xaxes(title_text="Distancia (m)", row=3, col=1)
    fig.update_layout(height=700, legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, use_container_width=True)

# ---- TAB 2: rpm y marchas ----
with tab2:
    fig2 = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
        subplot_titles=("RPM", "Marcha"),
    )
    for tel, code, color, dash in [(tel1, driver1, color1, dash1), (tel2, driver2, color2, dash2)]:
        fig2.add_trace(go.Scatter(x=tel["Distance"], y=tel["RPM"], name=code,
                                   line=dict(color=color, dash=dash)), row=1, col=1)
        fig2.add_trace(go.Scatter(x=tel["Distance"], y=tel["nGear"], name=code,
                                   line=dict(color=color, dash=dash, shape="hv"), showlegend=False), row=2, col=1)
    fig2.update_xaxes(title_text="Distancia (m)", row=2, col=1)
    fig2.update_layout(height=550, legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig2, use_container_width=True)

# ---- TAB 3: delta de tiempo ----
with tab3:
    ref_dist, delta = compute_delta(lap1, lap2)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=ref_dist, y=delta, fill="tozeroy",
                               line=dict(color=color1), name=f"{driver1} vs {driver2}"))
    fig3.add_hline(y=0, line_dash="dot", line_color="gray")
    fig3.update_layout(
        height=450,
        xaxis_title="Distancia (m)",
        yaxis_title=f"◀ {driver2} por delante   |   {driver1} por delante ▶",
    )
    st.plotly_chart(fig3, use_container_width=True)

    lap_delta = (lap2["LapTime"] - lap1["LapTime"]).total_seconds()
    st.metric(f"Diferencia de vuelta ({driver2} − {driver1})", f"{lap_delta:+.3f} s")

# ---- TAB 4: mapa del circuito ----
with tab4:
    driver_for_map = st.radio("Colorear el mapa según la velocidad de:", [driver1, driver2], horizontal=True)
    tel_map = tel1 if driver_for_map == driver1 else tel2

    x = tel_map["X"].to_numpy()
    y = tel_map["Y"].to_numpy()
    speed = tel_map["Speed"].to_numpy()

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    fig4, ax4 = plt.subplots(figsize=(8, 8))
    ax4.axis("off")
    ax4.set_aspect("equal")
    lc = LineCollection(segments, cmap="plasma")
    lc.set_array(speed)
    lc.set_linewidth(4)
    line = ax4.add_collection(lc)
    ax4.set_xlim(x.min() - 300, x.max() + 300)
    ax4.set_ylim(y.min() - 300, y.max() + 300)

    try:
        circuit_info = session.get_circuit_info()
        for _, corner in circuit_info.corners.iterrows():
            ax4.text(
                corner["X"], corner["Y"], str(int(corner["Number"])),
                fontsize=8, color="white", ha="center", va="center",
                bbox=dict(boxstyle="circle", facecolor="black", alpha=0.6),
            )
    except Exception:
        pass

    fig4.colorbar(line, ax=ax4, label="Velocidad (km/h)", shrink=0.7)
    st.pyplot(fig4)

# ---- TAB 5: resumen de vuelta ----
with tab5:
    def lap_summary(lap, code):
        return {
            "Piloto": code,
            "Tiempo de vuelta": fmt_time(lap.get("LapTime")),
            "Sector 1": fmt_time(lap.get("Sector1Time")),
            "Sector 2": fmt_time(lap.get("Sector2Time")),
            "Sector 3": fmt_time(lap.get("Sector3Time")),
            "Compuesto": lap.get("Compound", "—"),
            "Vida del neumático": lap.get("TyreLife", "—"),
            "Vel. punta (trampa)": lap.get("SpeedST", "—"),
        }

    summary_df = pd.DataFrame([lap_summary(lap1, driver1), lap_summary(lap2, driver2)])
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
