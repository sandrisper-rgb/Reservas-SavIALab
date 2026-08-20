from pathlib import Path
import base64
import re

app_path = Path("/mnt/data/app.py")
logo_path = Path("/mnt/data/Logo horizontal.png")

code = app_path.read_text(encoding="utf-8")
logo_b64 = base64.b64encode(logo_path.read_bytes()).decode("ascii")

# Replace file-based logo configuration with embedded logo.
code = code.replace(
    'LOGO_PATH = Path("Logo horizontal.png")\n\n# OPCIONAL: pega aquí el enlace de un Google Form\n',
    f'LOGO_BASE64 = """{logo_b64}"""\n\n# OPCIONAL: pega aquí el enlace de un Google Form\n'
)

# Replace style helpers section.
pattern = re.compile(
    r'def imagen_a_base64\(ruta: Path\) -> str:.*?agregar_estilo_savialab\(\)\n',
    re.S
)

replacement = r'''def agregar_estilo_savialab():
    st.markdown(
        f"""
        <style>
        /* Fondo general con el logo de SavIA-Lab como marca de agua */
        .stApp {{
            background-color: #F7FAF9;
            background-image:
                linear-gradient(
                    rgba(255,255,255,0.88),
                    rgba(255,255,255,0.88)
                ),
                url("data:image/png;base64,{LOGO_BASE64}");
            background-repeat: no-repeat;
            background-position: center 55%;
            background-size: 68%;
            background-attachment: fixed;
        }}

        /* Caja principal del formulario ligeramente translúcida */
        .block-container {{
            background: rgba(255, 255, 255, 0.82);
            padding: 2rem 2rem 3rem 2rem;
            border-radius: 24px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.09);
            border: 1px solid rgba(0,0,0,0.05);
            backdrop-filter: blur(2px);
            -webkit-backdrop-filter: blur(2px);
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
        """,
        unsafe_allow_html=True,
    )


agregar_estilo_savialab()
'''

code, n = pattern.subn(replacement, code, count=1)
if n != 1:
    raise RuntimeError("No se pudo reemplazar la sección de estilo.")

# Remove the top st.image block since the logo is now used as background.
code = re.sub(
    r'\nif LOGO_PATH\.exists\(\):\n\s+st\.image\(str\(LOGO_PATH\), width=330\)\n',
    '\n',
    code,
    count=1,
)

out = Path("/mnt/data/app_savialab_fondo_integrado.py")
out.write_text(code, encoding="utf-8")

print(f"Archivo creado: {out}")
print(f"Tamaño: {out.stat().st_size/1024:.1f} KB")
