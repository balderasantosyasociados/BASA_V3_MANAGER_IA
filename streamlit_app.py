# ==============================================================================
# 🤖 BASA MANAGER IA V3 - FUSIONADO EN ESPAÑOL - BASA MANAGER IA + GDP DASHBOARD
# Baldera Santos & Asociados SRL | RNC 133378711
# Fusion: Tu app GDP Dashboard (Banco Mundial) traducida + BASA Manager IA V2.1 probado
# Todo en español, 1 solo Streamlit, funciona en celular + PC
# Si no existe data/gdp_data.csv, genera datos de ejemplo y NO se cae
# ==============================================================================

import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import math
import random
from datetime import date, datetime, timedelta
from pathlib import Path

st.set_page_config(page_title="BASA Manager IA - PIB Mundial", layout="wide", page_icon="🤖")

# --- BASE BASA MANAGER IA ---
BASE = Path("BASA_MANAGER_IA")
BASE.mkdir(exist_ok=True)
DB = BASE / "basa_manager.db"

def get_conn():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = get_conn()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_usuario VARCHAR(20) UNIQUE,
        nombre_completo VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        rol VARCHAR(20) CHECK(rol IN ('Desarrollador', 'Cliente', 'Administrador')),
        cuenta_bancaria VARCHAR(50),
        banco VARCHAR(50),
        pais VARCHAR(50),
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        clave_hash TEXT,
        telefono TEXT,
        bio TEXT,
        nombre_cuenta TEXT,
        tipo_cuenta TEXT,
        paypal TEXT,
        codigo_dev TEXT,
        comision_pct REAL DEFAULT 15.0,
        balance REAL DEFAULT 0,
        estado TEXT DEFAULT 'PENDIENTE',
        verificado INT DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS proyectos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_proyecto VARCHAR(30) UNIQUE,
        titulo VARCHAR(150) NOT NULL,
        categoria VARCHAR(50),
        descripcion TEXT,
        objetivo TEXT,
        tiempo_entrega_dias INT,
        monto_ofrecido DECIMAL(10,2),
        modalidad VARCHAR(20) CHECK(modalidad IN ('Donación', 'Gratuito', 'Pago Fijo', 'Comisión')),
        estado VARCHAR(20) DEFAULT 'Abierto',
        cliente_id INT,
        proposito TEXT,
        moneda TEXT DEFAULT 'USD',
        cliente_nombre TEXT,
        destacado INT DEFAULT 0,
        vistas INT DEFAULT 0,
        fecha TEXT,
        FOREIGN KEY(cliente_id) REFERENCES usuarios(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS entregas_repositorio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proyecto_id INT,
        desarrollador_id INT,
        codigo_entrega VARCHAR(50) UNIQUE,
        url_repositorio_script TEXT,
        api_endpoint TEXT,
        acuerdo_derechos_aceptado BOOLEAN DEFAULT 1,
        fecha_entrega DATETIME DEFAULT CURRENT_TIMESTAMP,
        titulo_sistema TEXT,
        descripcion TEXT,
        precio_venta REAL,
        moneda TEXT DEFAULT 'USD',
        estado TEXT DEFAULT 'En revision',
        codigo_repositorio TEXT,
        FOREIGN KEY(proyecto_id) REFERENCES proyectos(id),
        FOREIGN KEY(desarrollador_id) REFERENCES usuarios(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ventas_comisiones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proyecto_id INT,
        comprador_id INT,
        desarrollador_id INT,
        monto_venta DECIMAL(10,2),
        porcentaje_comision DECIMAL(5,2),
        monto_comision DECIMAL(10,2),
        estado_pago VARCHAR(20) DEFAULT 'Pendiente',
        fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
        codigo_proyecto TEXT,
        comprador_nombre TEXT,
        comprador_correo TEXT,
        FOREIGN KEY(proyecto_id) REFERENCES proyectos(id),
        FOREIGN KEY(comprador_id) REFERENCES usuarios(id),
        FOREIGN KEY(desarrollador_id) REFERENCES usuarios(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS propuestas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, codigo_proyecto TEXT, dev_codigo TEXT, dev_nombre TEXT,
        mensaje TEXT, tiempo_propuesto INT, monto_propuesto REAL, estado TEXT DEFAULT 'Pendiente', fecha TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS pagos_semanales (
        id INTEGER PRIMARY KEY AUTOINCREMENT, dev_codigo TEXT, dev_nombre TEXT, semana TEXT,
        total_ventas REAL, total_comision REAL, metodo TEXT, referencia TEXT, estado TEXT DEFAULT 'Pendiente', fecha TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS publicidad (
        id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, tipo TEXT, monto REAL, moneda TEXT,
        cliente TEXT, fecha_inicio TEXT, fecha_fin TEXT, estado TEXT DEFAULT 'Activa')""")
    c.execute("""CREATE TABLE IF NOT EXISTS donaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT, codigo_proyecto TEXT, donante TEXT, monto REAL,
        moneda TEXT, mensaje TEXT, fecha TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS soporte_ia (
        id INTEGER PRIMARY KEY AUTOINCREMENT, codigo_proyecto TEXT, cliente TEXT, mensaje TEXT, respuesta TEXT, estado TEXT DEFAULT 'Abierto', fecha TEXT)""")
    if not c.execute("SELECT * FROM usuarios WHERE email='basa@basa.do'").fetchone():
        c.execute("INSERT INTO usuarios (codigo_usuario,nombre_completo,email,rol,cuenta_bancaria,banco,pais,clave_hash,codigo_dev,comision_pct,estado,verificado) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                  ("USR-001", "Pedro Baldera", "basa@basa.do", "Administrador", "****0021", "BHD", "Republica Dominicana", hashlib.sha256("Basa2026*".encode()).hexdigest(), "BASA-01-PB", 0, "APROBADO", 1))
    if not c.execute("SELECT * FROM proyectos WHERE codigo_proyecto='BASA-01-PB'").fetchone():
        c.execute("INSERT INTO proyectos (codigo_proyecto,titulo,categoria,descripcion,objetivo,proposito,tiempo_entrega_dias,monto_ofrecido,modalidad,estado,cliente_nombre,moneda,fecha,destacado) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  ("BASA-01-PB", "Software Auditar Nominas - Auditoria Forense Mundial", "Auditoría Forense y Nóminas", "Auditar nominas de cualquier pais", "Buscar en portal institucional, organo rector, Contraloria, Seguridad Social y generar informe real de auditoria forense. Detectar fantasmas, duplicados, pagos irregulares.", "Auditar nomina y generar informe forense real", 21, 1500, "Comisión", "Abierto", "Pedro Baldera", "USD", str(date.today()), 1))
    c.commit()
    c.close()

init_db()

def hash_clave(x):
    return hashlib.sha256(str(x).encode()).hexdigest()

def generar_codigo(consecutivo, nombre):
    partes = nombre.strip().split()
    iniciales = "".join([p[0].upper() for p in partes if p])[:2]
    if len(iniciales) < 2:
        iniciales = (iniciales + "X")[:2]
    base = f"BASA-{consecutivo:02d}-{iniciales}"
    c = get_conn()
    existe = c.execute("SELECT COUNT(*) FROM proyectos WHERE codigo_proyecto=?", (base,)).fetchone()[0]
    c.close()
    if existe == 0:
        return base
    return f"{base}-{existe+1}"

def gen_codigo_dev(nombre):
    partes = nombre.strip().split()
    ini = "".join([p[0].upper() for p in partes if p])[:2]
    if len(ini) < 2:
        ini = (ini + "X")[:2]
    base = f"BASA-01-{ini}"
    c = get_conn()
    existe = c.execute("SELECT COUNT(*) FROM usuarios WHERE codigo_dev=?", (base,)).fetchone()[0]
    c.close()
    if existe == 0:
        return base
    return f"{base}-{existe+1}"

# --- TU FUNCION GDP - TRADUCIDA Y CON RESPALDO SI NO HAY CSV ---
@st.cache_data
def get_gdp_data():
    """Obtiene datos PIB del Banco Mundial. Si no hay CSV, genera datos de ejemplo para no caerse."""
    DATA_FILENAME = Path(__file__).parent / 'data' / 'gdp_data.csv'
    MIN_YEAR = 1960
    MAX_YEAR = 2022
    if DATA_FILENAME.exists():
        try:
            raw_gdp_df = pd.read_csv(DATA_FILENAME)
            gdp_df = raw_gdp_df.melt(
                ['Country Code'],
                [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
                'Year',
                'GDP',
            )
            gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
            # Traducir columnas para BASA
            gdp_df = gdp_df.rename(columns={'Country Code': 'Codigo Pais', 'Year': 'Año', 'GDP': 'PIB'})
            return gdp_df
        except Exception:
            pass
    # Respaldo: datos de ejemplo si no hay CSV - Para que la app nunca se caiga
    paises_ejemplo = {
        'DEU': 3800000000000, 'FRA': 2700000000000, 'GBR': 3100000000000,
        'BRA': 1900000000000, 'MEX': 1300000000000, 'JPN': 4900000000000,
        'DOM': 110000000000, 'USA': 23000000000000, 'COL': 340000000000, 'ESP': 1400000000000
    }
    filas = []
    for codigo, base in paises_ejemplo.items():
        for anio in range(MIN_YEAR, MAX_YEAR + 1):
            # Crecimiento simulado 2.5% anual + variacion
            factor = (1.025 ** (anio - MIN_YEAR)) * (0.9 + 0.2 * ((anio % 7) / 7))
            # Para que en 1960 sea mas bajo, normalizamos
            valor = base * (0.15 + 0.85 * ((anio - MIN_YEAR) / (MAX_YEAR - MIN_YEAR))) * factor / 3.5
            filas.append({'Codigo Pais': codigo, 'Año': anio, 'PIB': valor})
    df = pd.DataFrame(filas)
    return df

if "user_ia" not in st.session_state:
    st.session_state.user_ia = None

# --- LOGIN / REGISTRO BASA ---
if st.session_state.user_ia is None:
    st.title("🤖 BASA Manager IA - Fusionado con PIB Mundial")
    st.caption("Crea tu sistema, API, app, juego, cancion, video, finanzas - Gana por desarrollo + comision + donaciones | + Datos PIB Banco Mundial para auditar por pais")
    t1, t2 = st.tabs(["🔐 Entrar", "📝 Registro de Usuario"])
    with t1:
        with st.form("login_ia"):
            correo = st.text_input("Correo")
            clave = st.text_input("Clave", type="password")
            if st.form_submit_button("Entrar"):
                c = get_conn()
                row = c.execute("SELECT * FROM usuarios WHERE email=?", (correo,)).fetchone()
                c.close()
                if row and row["clave_hash"] == hash_clave(clave):
                    if row["estado"] == "PENDIENTE":
                        st.warning("PENDIENTE. BASA debe aprobarte.")
                    else:
                        st.session_state.user_ia = dict(row)
                        st.rerun()
                else:
                    st.error("Correo o clave incorrectos.")
    with t2:
        with st.form("form_registro"):
            nombre = st.text_input("Nombre Completo * - Ej: Pedro Baldera")
            email = st.text_input("Correo Electronico *")
            rol = st.selectbox("Rol Principal", ["Desarrollador", "Cliente", "Administrador"])
            pais = st.text_input("Pais", value="Republica Dominicana")
            telefono = st.text_input("Telefono / WhatsApp")
            bio = st.text_area("Que sabes hacer? Ej: Python, API, Apps, Juegos, Finanzas")
            st.markdown("### 💳 Datos Bancarios para Pagos / Comisiones")
            banco = st.text_input("Banco u Operador de Pago")
            cuenta = st.text_input("Numero de Cuenta / IBAN / PayPal / Swift *")
            nombre_cuenta = st.text_input("Nombre en la cuenta *")
            tipo_cuenta = st.selectbox("Tipo Cuenta", ["Ahorro", "Corriente", "PayPal"])
            paypal = st.text_input("PayPal / Correo PayPal")
            clave2 = st.text_input("Crear Clave *", type="password")
            acepto = st.checkbox("Acepto contrato: Al entregar, cedo derechos a BASA para venta / uso bajo precio recibido. BASA me paga semanalmente.")
            submitted = st.form_submit_button("Registrar Usuario")
            if submitted:
                if not nombre or not email or not clave2:
                    st.error("Nombre, Correo y Clave obligatorios.")
                elif not acepto:
                    st.error("Debes aceptar contrato.")
                elif not cuenta and not paypal:
                    st.error("Pon cuenta o PayPal para cobrar.")
                else:
                    try:
                        c = get_conn()
                        count = c.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] + 1
                        cod_user = f"USR-{count:03d}"
                        cod_dev = gen_codigo_dev(nombre)
                        c.execute("INSERT INTO usuarios (codigo_usuario,nombre_completo,email,rol,cuenta_bancaria,banco,pais,clave_hash,telefono,bio,nombre_cuenta,tipo_cuenta,paypal,codigo_dev,estado) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                  (cod_user, nombre, email, rol, cuenta, banco, pais, hash_clave(clave2), telefono, bio, nombre_cuenta, tipo_cuenta, paypal, cod_dev, "PENDIENTE"))
                        c.commit()
                        c.close()
                        st.success(f"Registrado! Codigo usuario: {cod_user} | Codigo Dev: {cod_dev}")
                    except Exception:
                        st.error("Ese correo ya esta registrado.")
    st.stop()

user = st.session_state.user_ia
es_admin = user["rol"] == "Administrador" or user["email"] == "basa@basa.do"

st.title("🤖 BASA Manager IA")
st.caption(f"Bienvenido {user['nombre_completo']} | Codigo: {user['codigo_dev']} | Rol: {user['rol']} | Balance: ${float(user['balance'] or 0):,.2f} | Comision: {user['comision_pct']}%")
if st.button("Cerrar Sesion"):
    st.session_state.user_ia = None
    st.rerun()

# Menu fusionado: BASA + GDP
st.sidebar.title("BASA Manager IA 🤖")
opcion = st.sidebar.radio("Navegación", ["Dashboard General", "🌎 PIB Mundial - Banco Mundial", "Registro de Usuario", "Publicar Requerimiento", "Explorar Requerimientos - Aceptar Tarea", "Repositorio Maestro", "Comprar Sistema + Configurar Credenciales", "Liquidación de Comisiones", "Donar / Aportar", "Publicidad", "Soporte al Comprador", "BASA Admin - Aprobar Usuarios"])
st.sidebar.success(f"Codigo: {user['codigo_dev']}")
st.sidebar.info("Fusion: BASA Manager IA + PIB Banco Mundial para auditar por pais")

# Cargar datos PIB una sola vez
gdp_df = get_gdp_data()

if opcion == "Dashboard General":
    st.title("📊 Panel General de Control - BASA Manager IA")
    conn = get_conn()
    df_proj = pd.read_sql_query("SELECT * FROM proyectos", conn)
    df_users = pd.read_sql_query("SELECT * FROM usuarios", conn)
    df_com = pd.read_sql_query("SELECT * FROM ventas_comisiones", conn)
    conn.close()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Proyectos Publicados", len(df_proj))
    col2.metric("Desarrolladores / Usuarios", len(df_users))
    col3.metric("Monto Total Proyectos ($)", f"{df_proj['monto_ofrecido'].sum():,.2f}" if not df_proj.empty else "0.00")
    col4.metric("Comisiones Pendientes ($)", f"{df_com[df_com['estado_pago'] == 'Pendiente']['monto_comision'].sum():,.2f}" if not df_com.empty else "0.00")
    st.markdown("---")
    st.subheader("📌 Proyectos Recientes")
    if not df_proj.empty:
        st.dataframe(df_proj[['codigo_proyecto', 'titulo', 'categoria', 'monto_ofrecido', 'modalidad', 'estado']], use_container_width=True)
    else:
        st.info("No hay proyectos registrados aún.")
    st.info("Ejemplo destacado: BASA-01-PB - Auditar Nominas Mundial - $1,500 USD - 21 dias - Comision 15% - Usa PIB Mundial para comparar paises.")
    # Mini PIB en Dashboard
    st.subheader("🌎 PIB Mundial - Vista rapida (Banco Mundial)")
    st.caption("Explora datos PIB de [Banco Mundial Open Data](https://data.worldbank.org/). Los datos llegan hasta 2022 y algunos años pueden faltar.")
    paises_mini = ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN']
    df_mini = gdp_df[gdp_df['Codigo Pais'].isin(paises_mini) & (gdp_df['Año'] >= 2000)]
    st.line_chart(df_mini, x='Año', y='PIB', color='Codigo Pais')
    if not df_proj.empty:
        for _, row in df_proj.iterrows():
            with st.expander(f"🟢 [{row['codigo_proyecto']}] - {row['titulo']}"):
                st.write(f"**Categoria:** {row['categoria']} | **Modalidad:** {row['modalidad']} | **Monto:** ${float(row['monto_ofrecido'] or 0):,.2f}")
                st.write(f"**Proposito:** {row['proposito']}")
                st.write(f"**Objetivo:** {row['objetivo']}")

elif opcion == "🌎 PIB Mundial - Banco Mundial":
    # --- TU GDP DASHBOARD TRADUCIDO AL ESPAÑOL Y FUSIONADO ---
    st.title("🌎 Panel PIB Mundial - Banco Mundial")
    st.write("Explora datos PIB de [Banco Mundial Open Data](https://data.worldbank.org/). Como verás, los datos solo llegan hasta 2022 por ahora, y los datos de ciertos años a menudo faltan. Pero es una fuente genial (y gratis) para auditar nóminas y finanzas por país.")
    st.write("")
    st.write("")
    min_value = int(gdp_df['Año'].min())
    max_value = int(gdp_df['Año'].max())
    from_year, to_year = st.slider(
        '¿Qué años te interesan?',
        min_value=min_value,
        max_value=max_value,
        value=[min_value, max_value])
    countries = sorted(gdp_df['Codigo Pais'].unique())
    if not len(countries):
        st.warning("Selecciona al menos un país")
    selected_countries = st.multiselect(
        '¿Qué países quieres ver?',
        countries,
        ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])
    st.write("")
    st.write("")
    # Filtrar datos - Tu logica, traducida
    filtered_gdp_df = gdp_df[
        (gdp_df['Codigo Pais'].isin(selected_countries))
        & (gdp_df['Año'] <= to_year)
        & (from_year <= gdp_df['Año'])
    ]
    st.header('PIB en el tiempo', divider='gray')
    st.write("")
    st.line_chart(
        filtered_gdp_df,
        x='Año',
        y='PIB',
        color='Codigo Pais',
    )
    st.write("")
    st.write("")
    first_year = gdp_df[gdp_df['Año'] == from_year]
    last_year = gdp_df[gdp_df['Año'] == to_year]
    st.header(f'PIB en {to_year}', divider='gray')
    st.write("")
    cols = st.columns(4)
    for i, country in enumerate(selected_countries):
        col = cols[i % len(cols)]
        with col:
            try:
                first_gdp = first_year[first_year['Codigo Pais'] == country]['PIB'].iat[0] / 1000000000
                last_gdp = last_year[last_year['Codigo Pais'] == country]['PIB'].iat[0] / 1000000000
            except Exception:
                first_gdp = float('nan')
                last_gdp = float('nan')
            if math.isnan(first_gdp) or math.isnan(last_gdp):
                growth = 'n/a'
                delta_color = 'off'
                last_val = 'n/a'
            else:
                growth = f'{last_gdp / first_gdp:,.2f}x'
                delta_color = 'normal'
                last_val = f'{last_gdp:,.0f}B'
            st.metric(
                label=f'{country} PIB',
                value=last_val,
                delta=growth,
                delta_color=delta_color
            )
    st.markdown("---")
    st.subheader("📌 ¿Para qué sirve esto en BASA Manager IA?")
    st.write("**1. Auditoría de nóminas por país:** Si un país tiene PIB de $110B (DOM) y su nómina pública reporta $50B, algo no cuadra. El sistema BASA-01-PB usa este PIB como referencia.")
    st.write("**2. Para desarrolladores:** Puedes crear un módulo que compare PIB vs nómina vs Contraloría y genere informe forense.")
    st.write("**3. Para clientes:** Si publicas un requerimiento de auditoría, pon el país y el año, y el dev ya sabe qué PIB buscar.")
    st.write("**Dato:** Si subes tu propio `data/gdp_data.csv` del Banco Mundial, este panel usa tus datos reales. Si no lo subes, usa datos de ejemplo y no se cae.")

elif opcion == "Registro de Usuario":
    st.title("👤 Registro de Desarrollador / Cliente")
    conn = get_conn()
    df = pd.read_sql_query("SELECT codigo_usuario, nombre_completo, email, rol, banco, cuenta_bancaria, pais, codigo_dev, balance, estado FROM usuarios ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)
    st.write(f"**Tu ficha para cobrar:** Banco {user['banco']} | Cuenta {user['cuenta_bancaria']} | A nombre de {user['nombre_cuenta']} | PayPal {user['paypal']}")

elif opcion == "Publicar Requerimiento":
    st.title("📝 Publicar Requerimiento / Solicitud de Sistema")
    with st.form("form_proyecto"):
        titulo = st.text_input("Título del Requerimiento / Sistema *")
        categoria = st.selectbox("Área / Categoría", ["Auditoría Forense y Nóminas", "Finanzas y Contabilidad", "API / Microservicios", "Aplicación Móvil / Web", "IA / Machine Learning", "Publicidad y Multimedia", "Juegos / Entretenimiento", "Negocios", "Uber / Servicio", "PIB / Datos Banco Mundial"])
        descripcion = st.text_area("Descripción detallada *")
        proposito = st.text_area("Propósito * - Para que sirve")
        objetivo = st.text_area("Objetivo * - Que debe lograr")
        tiempo_dias = st.number_input("Tiempo estimado de entrega (Días)", min_value=1, value=15)
        modalidad = st.selectbox("Modalidad de Pago", ["Pago Fijo", "Donación", "Gratuito", "Comisión"])
        monto = st.number_input("Monto ofrecido / Precio ($)", min_value=0.0, value=500.0)
        moneda = st.selectbox("Moneda", ["USD", "DOP", "MXN", "COP", "EUR"])
        desarrollador_asignado = st.text_input("Nombre / Iniciales del Creador", value=user['nombre_completo'])
        acepta_contrato = st.checkbox("Acepto términos de cesión de derechos para repositorio maestro BASA.")
        submitted = st.form_submit_button("Publicar Proyecto")
        if submitted:
            if not acepta_contrato:
                st.error("Debe aceptar términos contractuales.")
            elif titulo and desarrollador_asignado and proposito and objetivo:
                conn = get_conn()
                count = conn.execute("SELECT COUNT(*) FROM proyectos").fetchone()[0] + 1
                cod_proj = generar_codigo(count, desarrollador_asignado)
                c = conn.execute("SELECT id FROM usuarios WHERE email=?", (user['email'],)).fetchone()
                cliente_id = c[0] if c else None
                conn.execute("INSERT INTO proyectos (codigo_proyecto,titulo,categoria,descripcion,objetivo,proposito,tiempo_entrega_dias,monto_ofrecido,modalidad,estado,cliente_id,cliente_nombre,moneda,fecha) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             (cod_proj, titulo, categoria, descripcion, objetivo, proposito, tiempo_dias, monto, modalidad, "Abierto", cliente_id, user['nombre_completo'], moneda, str(date.today())))
                conn.commit()
                conn.close()
                st.success(f"Proyecto publicado con Código Maestro: **{cod_proj}**")
            else:
                st.error("Titulo, Proposito, Objetivo y Creador obligatorios.")

elif opcion == "Explorar Requerimientos - Aceptar Tarea":
    st.title("🔍 Requerimientos Abiertos")
    conn = get_conn()
    df = pd.read_sql_query("SELECT codigo_proyecto AS Codigo, titulo AS Titulo, categoria AS Categoria, tiempo_entrega_dias AS Dias, monto_ofrecido AS Monto, modalidad AS Modalidad, estado AS Estado, cliente_nombre AS Cliente FROM proyectos WHERE estado='Abierto' ORDER BY destacado DESC, id DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)
    if len(df) > 0:
        sel = st.selectbox("Elige requerimiento", df["Codigo"].tolist())
        conn = get_conn()
        det = conn.execute("SELECT * FROM proyectos WHERE codigo_proyecto=?", (sel,)).fetchone()
        conn.close()
        if det:
            st.write(f"**{det['titulo']}**")
            st.write(f"**Proposito:** {det['proposito']}")
            st.write(f"**Objetivo:** {det['objetivo']}")
        mensaje = st.text_area("Mensaje para el cliente")
        tiempo_prop = st.number_input("Tiempo que propones dias", value=14)
        monto_prop = st.number_input("Monto que propones", value=float(det['monto_ofrecido']) if det else 0.0)
        if st.button("✅ Aceptar Tarea"):
            conn = get_conn()
            conn.execute("INSERT INTO propuestas (codigo_proyecto,dev_codigo,dev_nombre,mensaje,tiempo_propuesto,monto_propuesto,estado,fecha) VALUES (?,?,?,?,?,?,?,?)",
                         (sel, user['codigo_dev'], user['nombre_completo'], mensaje, tiempo_prop, monto_prop, "Pendiente", str(date.today())))
            conn.commit()
            conn.close()
            st.success(f"Propuesta enviada para {sel}.")

elif opcion == "Repositorio Maestro":
    st.title("📦 Repositorio Maestro de Módulos y APIs")
    conn = get_conn()
    df_proj = pd.read_sql_query("SELECT * FROM proyectos", conn)
    conn.close()
    if not df_proj.empty:
        for index, row in df_proj.iterrows():
            with st.expander(f"🟢 [{row['codigo_proyecto']}] - {row['titulo']} ({row['categoria']})"):
                st.write(f"**Modalidad:** {row['modalidad']} | **Monto:** ${float(row['monto_ofrecido'] or 0):,.2f} | **Estado:** {row['estado']}")
                st.write(f"**Descripcion:** {row['descripcion']}")
                repo_url = st.text_input("URL Repositorio (GitHub / GitLab)", key=f"url_{row['id']}")
                api_url = st.text_input("Endpoint API", key=f"api_{row['id']}")
                precio_v = st.number_input("Precio venta al publico", value=float(row['monto_ofrecido'] or 500), key=f"prec_{row['id']}")
                if st.button("Guardar Entrega en Repositorio Maestro", key=f"btn_{row['id']}"):
                    conn = get_conn()
                    codigo_entrega = f"{row['codigo_proyecto']}-ENT-001"
                    conn.execute("INSERT INTO entregas_repositorio (proyecto_id,desarrollador_id,codigo_entrega,url_repositorio_script,api_endpoint,acuerdo_derechos_aceptado,titulo_sistema,descripcion,precio_venta,estado,codigo_repositorio) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                                 (int(row['id']), int(user['id']), codigo_entrega, repo_url, api_url, 1, row['titulo'], row['descripcion'], precio_v, "En revision", row['codigo_proyecto']))
                    conn.execute("UPDATE proyectos SET estado='En Desarrollo' WHERE id=?", (int(row['id']),))
                    conn.commit()
                    conn.close()
                    st.success(f"Código {row['codigo_proyecto']} vinculado. Entrega: {codigo_entrega}")
    else:
        st.info("Repositorio vacío.")

elif opcion == "Comprar Sistema + Configurar Credenciales":
    st.title("💳 Comprar Sistema - Configura credenciales y opera")
    conn = get_conn()
    repos = pd.read_sql_query("SELECT codigo_proyecto, titulo, monto_ofrecido FROM proyectos WHERE estado IN ('Abierto','En Desarrollo','Completado')", conn)
    conn.close()
    if len(repos) == 0:
        st.info("Aun no hay sistemas.")
    else:
        sel_repo = st.selectbox("Elige sistema a comprar", repos["codigo_proyecto"].tolist())
        row_repo = repos[repos["codigo_proyecto"] == sel_repo].iloc[0]
        st.write(f"**{row_repo['titulo']}** - Precio: {float(row_repo['monto_ofrecido']):,.2f}")
        with st.form("comprar"):
            comprador_nombre = st.text_input("Tu Nombre", value=user['nombre_completo'])
            comprador_correo = st.text_input("Tu Correo", value=user['email'])
            metodo = st.selectbox("Metodo Pago", ["Tarjeta", "Transferencia BHD ****0021", "PayPal", "Donacion"])
            referencia = st.text_input("Referencia Pago")
            api_key_prop = st.text_input("Tu API Key / Usuario")
            rnc_prop = st.text_input("Tu RNC / ID Fiscal")
            clave_prop = st.text_input("Tu Clave", type="password")
            pct = st.slider("Porcentaje Comision Dev %", min_value=5, max_value=50, value=int(user['comision_pct'] or 15))
            if st.form_submit_button("💳 Comprar Ahora y Activar"):
                if not referencia:
                    st.error("Pon referencia de pago.")
                else:
                    conn = get_conn()
                    proj = conn.execute("SELECT * FROM proyectos WHERE codigo_proyecto=?", (sel_repo,)).fetchone()
                    proj_id = proj["id"] if proj else None
                    dev_row = conn.execute("SELECT * FROM entregas_repositorio WHERE proyecto_id=? ORDER BY id DESC LIMIT 1", (proj_id,)).fetchone()
                    dev_id = dev_row["desarrollador_id"] if dev_row else proj["cliente_id"]
                    monto_v = float(row_repo["monto_ofrecido"])
                    com_dev = round(monto_v * pct / 100, 2)
                    conn.execute("INSERT INTO ventas_comisiones (proyecto_id,comprador_id,desarrollador_id,monto_venta,porcentaje_comision,monto_comision,estado_pago,codigo_proyecto,comprador_nombre,comprador_correo) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                 (proj_id, int(user['id']), dev_id, monto_v, pct, com_dev, "Pendiente", sel_repo, comprador_nombre, comprador_correo))
                    if dev_id:
                        conn.execute("UPDATE usuarios SET balance=balance+? WHERE id=?", (com_dev, int(dev_id)))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Comprado {sel_repo} por {monto_v:,.2f}. RNC {rnc_prop} configurado. Dev recibe ${com_dev:,.2f} ({pct}%) en pago semanal.")
        conn = get_conn()
        mis_compras = pd.read_sql_query("SELECT * FROM ventas_comisiones WHERE comprador_id=? ORDER BY id DESC", conn, params=(int(user['id']),))
        conn.close()
        st.subheader("Mis Compras")
        st.dataframe(mis_compras, use_container_width=True)

elif opcion == "Liquidación de Comisiones":
    st.title("💸 Pagos y Comisiones Semanales")
    conn = get_conn()
    df_proj = pd.read_sql_query("SELECT codigo_proyecto, titulo FROM proyectos", conn)
    with st.form("form_comision"):
        if not df_proj.empty:
            proj_sel = st.selectbox("Seleccionar Proyecto Vendido", df_proj['codigo_proyecto'] + " - " + df_proj['titulo'])
            cod_proj = proj_sel.split(" - ")[0]
            monto_vta = st.number_input("Monto de la Venta ($)", min_value=1.0, value=100.0)
            pct_comision = st.slider("Porcentaje Comisión Dev (%)", min_value=5, max_value=50, value=20)
            submitted = st.form_submit_button("Registrar Venta y Generar Comisión")
            if submitted:
                proj = conn.execute("SELECT * FROM proyectos WHERE codigo_proyecto=?", (cod_proj,)).fetchone()
                monto_ganado = (monto_vta * pct_comision) / 100.0
                conn.execute("INSERT INTO ventas_comisiones (proyecto_id,comprador_id,desarrollador_id,monto_venta,porcentaje_comision,monto_comision,estado_pago,codigo_proyecto,comprador_nombre) VALUES (?,?,?,?,?,?,?,?,?)",
                             (proj["id"] if proj else None, int(user['id']), proj["cliente_id"] if proj else None, monto_vta, pct_comision, monto_ganado, "Pendiente", cod_proj, user['nombre_completo']))
                if proj and proj["cliente_id"]:
                    conn.execute("UPDATE usuarios SET balance=balance+? WHERE id=?", (monto_ganado, int(proj["cliente_id"])))
                conn.commit()
                st.success(f"Comisión de ${monto_ganado:,.2f} registrada. Estado: Pendiente - BASA paga semanal.")
    st.markdown("---")
    st.subheader("📋 Liquidaciones")
    df_com = pd.read_sql_query("SELECT codigo_proyecto AS Codigo, monto_venta AS Venta, porcentaje_comision AS Porc, monto_comision AS Comision, estado_pago AS Estado, fecha_venta AS Fecha FROM ventas_comisiones ORDER BY id DESC", conn)
    conn.close()
    if not df_com.empty:
        st.dataframe(df_com, use_container_width=True)
    if es_admin:
        st.subheader("BASA Admin - Pagar Comision Semanal")
        dev_codigo_p = st.text_input("Codigo Dev a pagar - Ej: BASA-01-PB")
        semana = st.text_input("Semana - Ej: 2026-11-02 al 2026-11-08")
        monto_pagar = st.number_input("Monto comision a pagar", value=0.0)
        metodo_p = st.selectbox("Metodo", ["Transferencia BHD", "PayPal", "Efectivo"])
        ref_p = st.text_input("Referencia Pago Semanal")
        if st.button("💰 Pagar Comision Semanal"):
            conn = get_conn()
            dev_u = conn.execute("SELECT * FROM usuarios WHERE codigo_dev=?", (dev_codigo_p,)).fetchone()
            nom_dev = dev_u["nombre_completo"] if dev_u else dev_codigo_p
            conn.execute("INSERT INTO pagos_semanales (dev_codigo,dev_nombre,semana,total_ventas,total_comision,metodo,referencia,estado,fecha) VALUES (?,?,?,?,?,?,?,?,?)",
                         (dev_codigo_p, nom_dev, semana, monto_pagar, monto_pagar, metodo_p, ref_p, "Pagado", str(date.today())))
            if dev_u:
                conn.execute("UPDATE usuarios SET balance=0 WHERE codigo_dev=?", (dev_codigo_p,))
            conn.commit()
            conn.close()
            st.success(f"✅ Pago semanal {monto_pagar:,.2f} pagado a {nom_dev} via {metodo_p}. Balance en 0.")

elif opcion == "Donar / Aportar":
    st.title("💝 Donar / Aportar")
    conn = get_conn()
    reqs = pd.read_sql_query("SELECT codigo_proyecto, titulo, monto_ofrecido FROM proyectos WHERE estado='Abierto'", conn)
    conn.close()
    if len(reqs) > 0:
        sel_don = st.selectbox("Elige requerimiento", reqs["codigo_proyecto"].tolist())
        monto_don = st.number_input("Monto Donacion", value=50.0)
        moneda_don = st.selectbox("Moneda", ["USD", "DOP"])
        mensaje_don = st.text_input("Mensaje")
        if st.button("💝 Donar Ahora"):
            conn = get_conn()
            conn.execute("INSERT INTO donaciones (codigo_proyecto,donante,monto,moneda,mensaje,fecha) VALUES (?,?,?,?,?,?)",
                         (sel_don, user['nombre_completo'], monto_don, moneda_don, mensaje_don, str(date.today())))
            conn.commit()
            conn.close()
            st.success(f"✅ Donacion {monto_don} {moneda_don} para {sel_don}.")
    conn = get_conn()
    dons = pd.read_sql_query("SELECT * FROM donaciones ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(dons, use_container_width=True)

elif opcion == "Publicidad":
    st.title("📢 Publicidad")
    with st.form("pub"):
        titulo_pub = st.text_input("Titulo Publicidad *")
        tipo_pub = st.selectbox("Tipo", ["Destacar Sistema", "Destacar Requerimiento", "Banner", "Video"])
        monto_pub = st.number_input("Monto Publicidad", value=50.0)
        moneda_pub = st.selectbox("Moneda", ["USD", "DOP"])
        dias_pub = st.number_input("Dias", value=7)
        if st.form_submit_button("📢 Pagar Publicidad y Activar"):
            conn = get_conn()
            conn.execute("INSERT INTO publicidad (titulo,tipo,monto,moneda,cliente,fecha_inicio,fecha_fin,estado) VALUES (?,?,?,?,?,?,?,?)",
                         (titulo_pub, tipo_pub, monto_pub, moneda_pub, user['nombre_completo'], str(date.today()), str(date.today() + timedelta(days=int(dias_pub))), "Activa"))
            conn.commit()
            conn.close()
            st.success(f"✅ Publicidad activada: {titulo_pub} por {dias_pub} dias.")
    conn = get_conn()
    pubs = pd.read_sql_query("SELECT * FROM publicidad ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(pubs, use_container_width=True)

elif opcion == "Soporte al Comprador":
    st.title("🛠️ Soporte")
    conn = get_conn()
    repos = pd.read_sql_query("SELECT codigo_proyecto FROM proyectos", conn)
    conn.close()
    sel_sop = st.selectbox("Sistema con problema", repos["codigo_proyecto"].tolist() if len(repos) > 0 else ["BASA-01-PB"])
    mensaje_sop = st.text_area("Describe tu problema")
    if st.button("📩 Enviar Soporte"):
        conn = get_conn()
        conn.execute("INSERT INTO soporte_ia (codigo_proyecto,cliente,mensaje,estado,fecha) VALUES (?,?,?,?,?)",
                     (sel_sop, user['nombre_completo'], mensaje_sop, "Abierto", str(date.today())))
        conn.commit()
        conn.close()
        st.success("Soporte enviado.")
    conn = get_conn()
    sops = pd.read_sql_query("SELECT * FROM soporte_ia ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(sops, use_container_width=True)

elif opcion == "BASA Admin - Aprobar Usuarios":
    if not es_admin:
        st.error("Solo BASA Admin.")
    else:
        st.title("✅ BASA Admin - Aprobar Usuarios")
        conn = get_conn()
        users = pd.read_sql_query("SELECT id, nombre_completo, email, rol, pais, codigo_dev, balance, estado FROM usuarios ORDER BY id DESC", conn)
        conn.close()
        st.dataframe(users, use_container_width=True)
        sel_u = st.text_input("Correo a aprobar")
        if st.button("✅ Aprobar Usuario"):
            conn = get_conn()
            conn.execute("UPDATE usuarios SET estado='APROBADO', verificado=1 WHERE email=?", (sel_u,))
            conn.commit()
            conn.close()
            st.success(f"{sel_u} aprobado.")
            st.rerun()
