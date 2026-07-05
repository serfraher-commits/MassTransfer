import streamlit as st
import numpy as np
import pandas as pd
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="El Desafío de Hagen-Poiseuille", page_icon="💧", layout="wide")

# --- BASE DE DATOS SIMULADA (Session State) ---
if 'db_alumnos' not in st.session_state:
    st.session_state.db_alumnos = {
        "Alonso Pérez": {"fluido": "Glicerina", "mu": 1.49, "rho": 1260, "R": 0.02, "L": 5.0, "dP": 10000, "tokens": 0, "logros": []},
        "María Gómez": {"fluido": "Aceite de Motor", "mu": 0.29, "rho": 880, "R": 0.015, "L": 3.0, "dP": 8000, "tokens": 0, "logros": []},
        "Carlos Ruiz": {"fluido": "Solución Azucarada", "mu": 0.05, "rho": 1100, "R": 0.01, "L": 2.5, "dP": 5000, "tokens": 0, "logros": []}
    }

db = st.session_state.db_alumnos

# --- TÍTULO Y CONTEXTO ---
st.title("💧 Simulador de Transferencia de Momentum")
st.markdown("### *Materia: Balances de Momentum, Calor y Masa (5to Semestre)*")
st.write("Bienvenido al módulo de validación hidrodinámica. Resuelve tu problema analítico, introduce tus resultados y compáralos con el modelo numérico.")



# --- INTERFAZ LATERAL: LOG-IN DE ALUMNO ---
st.sidebar.header("🔑 Acceso de Estudiante")
alumno_activo = st.sidebar.selectbox("Selecciona tu nombre:", list(db.keys()))

# Cargar datos del alumno desde la "Base de Datos"
datos = db[alumno_activo]

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Tus Datos Asignados")
st.sidebar.text(f"Fluido: {datos['fluido']}")
st.sidebar.text(f"Viscosidad (μ): {datos['mu']} Pa·s")
st.sidebar.text(f"Radio tubería (R): {datos['R']} m")
st.sidebar.text(f"Longitud (L): {datos['L']} m")
st.sidebar.text(f"Caída de Presión (ΔP): {datos['dP']} Pa")

st.sidebar.markdown("---")
st.sidebar.subheader("🏆 Tu Perfil de Recompensas")
st.sidebar.metric(label="Tokens de Momentum (TM)", value=f"{datos['tokens']} TM")
if datos['logros']:
    st.sidebar.write("🏅 Logros unlocked:")
    for logro in datos['logros']:
        st.sidebar.caption(f"- {logro}")
else:
    st.sidebar.caption("Aún no has desbloqueado logros.")

# --- CUERPO PRINCIPAL: INTERACCIÓN ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 1. Introduce tu Solución Analítica")
    st.write("Calcula la velocidad máxima teórica ($v_{max} = \\frac{\\Delta P \\cdot R^2}{4 \\mu L}$)")
    
    # Input del alumno
    v_max_alumno = st.number_input("Tu v_max calculada (m/s):", min_value=0.0, format="%.4f")
    
    st.markdown("---")
    st.subheader("⏱️ 2. Simulación y Envío")
    horas_transcurridas = st.slider("Horas transcurridas desde el lanzamiento de la actividad:", 1, 72, 24)
    
    boton_enviar = st.button("🚀 Validar y Enviar al Servidor")

# Cálculo de la solución real (Ecuación de Hagen-Poiseuille)
dP, R, mu, L = datos['dP'], datos['R'], datos['mu'], datos['L']
v_max_real = (dP * (R**2)) / (4 * mu * L)

# --- LÓGICA DE VALIDACIÓN Y GAMIFICACIÓN ---
with col2:
    st.subheader("📊 Gráfica del Perfil de Velocidades ($v_z$ vs $r$)")
    
    # Generar puntos para el perfil de velocidad (Parábola de Poiseuille)
    r_vals = np.linspace(-R, R, 100)
    v_vals_real = v_max_real * (1 - (r_vals / R)**2)
    
    # Dataframe para graficar
    df_grafica = pd.DataFrame({"Radio (m)": r_vals, "Velocidad Real (m/s)": v_vals_real})
    st.line_chart(df_grafica.set_index("Radio (m)"))

    if boton_enviar:
        st.markdown("### 🏁 Resultado de la Evaluación")
        
        # Calcular error
        error = abs((v_max_alumno - v_max_real) / v_max_real) * 100
        st.write(f"**Tu v_max:** {v_max_alumno:.4f} m/s")
        st.write(f"**v_max de la App:** {v_max_real:.4f} m/s")
        st.write(f"**Error Relativo:** {error:.2f}%")
        
        # Evaluar condiciones de competencia
        tokens_ganados = 0
        logros_nuevos = []
        
        if error <= 1.0 and horas_transcurridas <= 48:
            st.success("🥇 ¡LOGRO DESBLOQUEADO: INGENIERO SENIOR (ORO)!")
            tokens_ganados = 100
            logros_nuevos.append("Rango Oro: Ingeniero Senior")
            st.balloons()
        elif error <= 5.0:
            st.info("🥈 ¡LOGRO DESBLOQUEADO: CONSULTOR JUNIOR (PLATA)!")
            tokens_ganados = 75
            logros_nuevos.append("Rango Plata: Consultor Junior")
        elif error <= 10.0:
            st.warning("🥉 ¡LOGRO DESBLOQUEADO: VALIDADOR TÉCNICO (BRONCE)!")
            tokens_ganados = 50
            logros_nuevos.append("Rango Bronce: Validador Técnico")
        else:
            st.error("❌ El error supera el 10%. Revisa tus balances de momentum y condiciones de frontera.")
            
        # Actualizar "Base de Datos" en vivo
        if tokens_ganados > 0:
            db[alumno_activo]["tokens"] = tokens_ganados
            db[alumno_activo]["logros"] = logros_nuevos
            st.experimental_rerun()
