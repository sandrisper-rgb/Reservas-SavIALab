import base64
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Reservas SavIA-Lab",
    page_icon="🧠",
    layout="centered",
)

ARCHIVO_RESERVAS = Path("reservas.csv")
LOGO_PATH = Path("Logo horizontal.png")

# OPCIONAL: pega aquí el enlace de un Google Form
GOOGLE_FORM_URL = ""

CAPACIDAD_MAXIMA = 3
DIAS_ANTICIPACION_MAXIMA = 60

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
    "Asesoría técnica",
    "Otro",
]

COLUMNAS = [
    "fecha_registro",
    "codigo_reserva",
    "nombre",
    "correo",
    "fecha",
    "dia_semana",
    "horario",
    "actividad",
    "actividad_otro",
    "software",
    "github",
    "datos_externos",
    "observaciones",
]


# =========================================================
# ESTILO / FONDO
# =========================================================

def imagen_a_base64(ruta: Path) -> str:
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode()


def agregar_estilo_savialab():
    if LOGO_PATH.exists():
        logo_base64 = imagen_a_base64(LOGO_PATH)

        fondo = f'''
        background-image:
            linear-gradient(rgba(255,255,255,0.93), rgba(255,255,255,0.93)),
            url("data:image/png;base64,{logo_base64}");
        background-repeat: no-repeat;
        background-position: center center;
        background-size: 52%;
        background-attachment: fixed;
        '''
    else:
        fondo = "background-color: #F7FAF9;"

    st.markdown(
        f'''
        <style>
        .stApp {{
            {fondo}
        }}

        .block-container {{
            background: rgba(255, 255, 255, 0.90);
            padding: 2rem 2rem 3rem 2rem;
            border-radius: 22px;
            box-shadow: 0 8px 28px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
        }}

        h1, h2, h3 {{
            color: #176D68;
        }}

        div.stButton > button {{
            border-radius: 12px;
            font-weight: 700;
        }}

        div[data-testid="stAlert"] {{
            border-radius: 14px;
        }}
        </style>
        ''',
        unsafe_allow_html=True,
    )


agregar_estilo_savialab()


# =========================================================
# FUNCIONES
# =========================================================

def cargar_reservas():
    if ARCHIVO_RESERVAS.exists():
        try:
            df = pd.read_csv(ARCHIVO_RESERVAS, dtype=str)

            for columna in COLUMNAS:
                if columna not in df.columns:
                    df[columna] = ""

            return df[COLUMNAS]

        except Exception:
            return pd.DataFrame(columns=COLUMNAS)

    return pd.DataFrame(columns=COLUMNAS)


def guardar_reserva(nueva_reserva):
    reservas = cargar_reservas()
    reservas = pd.concat(
        [reservas, pd.DataFrame([nueva_reserva])],
        ignore_index=True,
    )
    reservas.to_csv(ARCHIVO_RESERVAS, index=False)


def cupos_disponibles(reservas, fecha_iso, horario):
    if reservas.empty:
        return CAPACIDAD_MAXIMA

    ocupados = reservas[
        (reservas["fecha"] == fecha_iso)
        & (reservas["horario"] == horario)
    ].shape[0]

    return max(0, CAPACIDAD_MAXIMA - ocupados)


def correo_valido(correo):
    patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(patron, correo.strip()))


def github_valido(url):
    if not url.strip():
        return True

    return url.strip().startswith(
        ("https://github.com/", "http://github.com/")
    )


def ya_tiene_reserva(reservas, correo, fecha_iso, horario):
    if reservas.empty:
        return False

    correos = reservas["correo"].fillna("").astype(str).str.lower()

    coincidencias = reservas[
        (correos == correo.strip().lower())
        & (reservas["fecha"] == fecha_iso)
        & (reservas["horario"] == horario)
    ]

    return not coincidencias.empty


def generar_codigo():
    return "SAVIA-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]


def nombre_dia_espanol(fecha):
    dias = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo",
    }
    return dias[fecha.weekday()]


# =========================================================
# ENCABEZADO
# =========================================================

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=330)

st.title("Reserva de estación de trabajo")

st.write(
    "Seleccione una fecha y una franja horaria para reservar una de las "
    "estaciones de trabajo disponibles en SavIA-Lab."
)

st.info(
    "SavIA-Lab dispone de **3 estaciones de trabajo**. "
    "Cada franja horaria admite un máximo de **3 reservas**."
)

st.caption(
    "Las reservas están disponibles de lunes a viernes y pueden realizarse "
    f"hasta con {DIAS_ANTICIPACION_MAXIMA} días de anticipación."
)


# =========================================================
# FECHA Y HORARIO
# =========================================================

reservas = cargar_reservas()

st.subheader("1. Seleccione la fecha")

fecha_seleccionada = st.date_input(
    "Fecha de la reserva",
    value=date.today(),
    min_value=date.today(),
    max_value=date.today() + timedelta(days=DIAS_ANTICIPACION_MAXIMA),
    format="DD/MM/YYYY",
)

if fecha_seleccionada.weekday() >= 5:
    st.warning(
        "SavIA-Lab no habilita reservas los sábados ni domingos. "
        "Por favor seleccione un día hábil."
    )
    st.stop()

fecha_iso = fecha_seleccionada.strftime("%Y-%m-%d")
dia_semana = nombre_dia_espanol(fecha_seleccionada)

st.write(
    f"**Día seleccionado:** {dia_semana}, "
    f"{fecha_seleccionada.strftime('%d/%m/%Y')}"
)

st.subheader("2. Seleccione el horario")

horarios_con_cupo = []

for horario in HORARIOS:
    cupos = cupos_disponibles(reservas, fecha_iso, horario)

    if cupos > 0:
        horarios_con_cupo.append(
            f"{horario} | Cupos disponibles: {cupos} de {CAPACIDAD_MAXIMA}"
        )

if not horarios_con_cupo:
    st.error("No hay cupos disponibles para la fecha seleccionada.")
    st.stop()

horario_seleccionado = st.selectbox(
    "Horario disponible",
    horarios_con_cupo,
)

horario_limpio = horario_seleccionado.split(" | ")[0]


# =========================================================
# DATOS DE LA PERSONA
# =========================================================

st.subheader("3. Datos de la persona")

nombre = st.text_input("Nombre completo *")

correo = st.text_input(
    "Correo institucional *",
    placeholder="nombre@universidad.edu.co",
)

actividad = st.selectbox(
    "Actividad principal *",
    ACTIVIDADES,
)

actividad_otro = ""

if actividad == "Otro":
    actividad_otro = st.text_input(
        "Indique la actividad *",
        placeholder="Describa brevemente la actividad que realizará",
    )

software = st.text_area(
    "Software, paquetes o librerías requeridas",
    placeholder=(
        "Ejemplo: Python, R, TensorFlow, PyTorch, "
        "Cellpose, QuPath, etc."
    ),
)

github = st.text_input(
    "Repositorio de GitHub, si aplica",
    placeholder="https://github.com/usuario/repositorio",
)

datos_externos = st.radio(
    "¿Entregará datos en disco externo para cargue al servidor?",
    ["No", "Sí"],
    horizontal=True,
)

observaciones = st.text_area(
    "Observaciones adicionales",
    placeholder="Información que SavIA-Lab deba conocer antes de su reserva.",
)

acepta = st.checkbox(
    "Confirmo que la información registrada es correcta y que utilizaré "
    "el espacio únicamente durante la franja reservada."
)


# =========================================================
# REGISTRO
# =========================================================

if st.button(
    "Registrar reserva",
    type="primary",
    use_container_width=True,
):
    errores = []

    if not nombre.strip():
        errores.append("Debe ingresar su nombre completo.")

    if not correo.strip():
        errores.append("Debe ingresar su correo institucional.")
    elif not correo_valido(correo):
        errores.append("El formato del correo electrónico no es válido.")

    if actividad == "Otro" and not actividad_otro.strip():
        errores.append("Debe especificar la actividad.")

    if not github_valido(github):
        errores.append(
            "El repositorio debe ser una dirección válida de GitHub."
        )

    if not acepta:
        errores.append("Debe aceptar las condiciones de la reserva.")

    reservas_actuales = cargar_reservas()

    cupos = cupos_disponibles(
        reservas_actuales,
        fecha_iso,
        horario_limpio,
    )

    if cupos <= 0:
        errores.append(
            "La franja seleccionada acaba de completar su capacidad. "
            "Seleccione otro horario."
        )

    if correo.strip() and ya_tiene_reserva(
        reservas_actuales,
        correo,
        fecha_iso,
        horario_limpio,
    ):
        errores.append(
            "Ya existe una reserva con este correo para la misma fecha y horario."
        )

    if errores:
        for error in errores:
            st.error(error)

    else:
        codigo = generar_codigo()

        nueva_reserva = {
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "codigo_reserva": codigo,
            "nombre": nombre.strip(),
            "correo": correo.strip().lower(),
            "fecha": fecha_iso,
            "dia_semana": dia_semana,
            "horario": horario_limpio,
            "actividad": actividad,
            "actividad_otro": actividad_otro.strip(),
            "software": software.strip(),
            "github": github.strip(),
            "datos_externos": datos_externos,
            "observaciones": observaciones.strip(),
        }

        guardar_reserva(nueva_reserva)

        st.success("✅ Reserva registrada correctamente.")

        actividad_mostrar = (
            actividad_otro if actividad == "Otro" else actividad
        )

        st.markdown(
            f'''
            ### Confirmación de reserva

            **Código:** `{codigo}`  
            **Fecha:** {dia_semana}, {fecha_seleccionada.strftime('%d/%m/%Y')}  
            **Horario:** {horario_limpio}  
            **Actividad:** {actividad_mostrar}  
            **Nombre:** {nombre.strip()}
            '''
        )

        st.info(
            "Conserve el código de reserva. "
            "Si necesita modificar o cancelar la reserva, "
            "comuníquese con SavIA-Lab."
        )


# =========================================================
# GOOGLE FORM OPCIONAL
# =========================================================

if GOOGLE_FORM_URL.strip():
    st.divider()
    st.subheader("Información complementaria")

    st.write(
        "Si SavIA-Lab requiere información adicional para su actividad, "
        "puede completar el formulario complementario."
    )

    st.link_button(
        "Abrir formulario de SavIA-Lab",
        GOOGLE_FORM_URL,
        use_container_width=True,
    )


# =========================================================
# PIE DE PÁGINA
# =========================================================

st.divider()

st.caption(
    "SavIA-Lab · Universidad El Bosque · Sistema de reservas"
)
