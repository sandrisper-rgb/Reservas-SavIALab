import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Reservas SavIA-Lab",
    page_icon="🧠",
    layout="centered"
)

ARCHIVO_RESERVAS = Path("reservas.csv")
CAPACIDAD_MAXIMA = 6

DIAS_DISPONIBLES = {
    "Miércoles 15 de julio de 2026": "2026-07-15",
    "Jueves 16 de julio de 2026": "2026-07-16",
    "Viernes 17 de julio de 2026": "2026-07-17",
}

HORARIOS = [
    "9:00 a. m. - 10:00 a. m.",
    "10:00 a. m. - 11:00 a. m.",
    "11:00 a. m. - 12:00 m.",
    "2:00 p. m. - 3:00 p. m.",
    "3:00 p. m. - 4:00 p. m.",
    "4:00 p. m. - 5:00 p. m.",
]

ACTIVIDADES = [
    "Uso de estación de trabajo",
    "Acceso al servidor",
    "Instalación de software o paquetes",
    "Cargue de datos desde disco externo",
    "Configuración de repositorio GitHub",
    "Otro",
]

def cargar_reservas():
    if ARCHIVO_RESERVAS.exists():
        return pd.read_csv(ARCHIVO_RESERVAS)

    return pd.DataFrame(columns=[
        "fecha_registro",
        "nombre",
        "correo",
        "dia",
        "fecha",
        "horario",
        "actividad",
        "software",
        "github",
        "datos_externos",
        "observaciones"
    ])

def guardar_reserva(nueva_reserva):
    reservas = cargar_reservas()
    reservas = pd.concat([reservas, pd.DataFrame([nueva_reserva])], ignore_index=True)
    reservas.to_csv(ARCHIVO_RESERVAS, index=False)

def cupos_disponibles(reservas, dia, horario):
    if reservas.empty:
        return CAPACIDAD_MAXIMA

    ocupados = reservas[
        (reservas["dia"] == dia) &
        (reservas["horario"] == horario)
    ].shape[0]

    return CAPACIDAD_MAXIMA - ocupados

st.title("Reservas de horario en SavIA-Lab")
st.write(
    "Sistema de registro para organizar el uso de estaciones de trabajo, "
    "acceso al servidor, instalación de software, configuración de repositorios "
    "y cargue de datos."
)

st.info(
    "SavIA-Lab cuenta con 6 estaciones de trabajo. "
    "Cada franja horaria permite máximo 6 personas registradas."
)

reservas = cargar_reservas()

st.subheader("Seleccione día y horario")

dia = st.selectbox("Día disponible", list(DIAS_DISPONIBLES.keys()))

horarios_con_cupo = []

for horario in HORARIOS:
    cupos = cupos_disponibles(reservas, dia, horario)
    if cupos > 0:
        horarios_con_cupo.append(f"{horario} | Cupos disponibles: {cupos}")

if not horarios_con_cupo:
    st.error("No hay cupos disponibles para este día.")
    st.stop()

horario_seleccionado = st.selectbox("Horario disponible", horarios_con_cupo)
horario_limpio = horario_seleccionado.split(" | ")[0]

st.subheader("Datos de la persona")

nombre = st.text_input("Nombre completo")
correo = st.text_input("Correo institucional")
actividad = st.selectbox("Actividad principal", ACTIVIDADES)

software = st.text_area(
    "Software, paquetes o librerías requeridas",
    placeholder="Ejemplo: Python, R, TensorFlow, PyTorch, Cellpose, QuPath, etc."
)

github = st.text_input(
    "Repositorio de GitHub, si aplica",
    placeholder="https://github.com/usuario/repositorio"
)

datos_externos = st.radio(
    "¿Entregará datos en disco externo para cargue al servidor?",
    ["No", "Sí"]
)

observaciones = st.text_area("Observaciones adicionales")

if st.button("Registrar reserva"):
    if not nombre or not correo:
        st.warning("Por favor complete nombre y correo institucional.")
    else:
        cupos = cupos_disponibles(reservas, dia, horario_limpio)

        if cupos <= 0:
            st.error("Esta franja ya no tiene cupos disponibles.")
        else:
            nueva_reserva = {
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nombre": nombre,
                "correo": correo,
                "dia": dia,
                "fecha": DIAS_DISPONIBLES[dia],
                "horario": horario_limpio,
                "actividad": actividad,
                "software": software,
                "github": github,
                "datos_externos": datos_externos,
                "observaciones": observaciones,
            }

            guardar_reserva(nueva_reserva)

            st.success("Reserva registrada correctamente.")
            st.write(f"**Día:** {dia}")
            st.write(f"**Horario:** {horario_limpio}")
            st.write(f"**Actividad:** {actividad}")

st.divider()

with st.expander("Ver resumen de reservas"):
    reservas_actualizadas = cargar_reservas()
    if reservas_actualizadas.empty:
        st.write("Aún no hay reservas registradas.")
    else:
        st.dataframe(reservas_actualizadas, use_container_width=True)
