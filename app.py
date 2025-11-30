import streamlit as st
# import openai (Eliminado)
import google.generativeai as genai
import os
import json
from datetime import datetime
from duckduckgo_search import DDGS

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

# Configuración de la página
st.set_page_config(page_title="Travel Planner", page_icon="✈️", layout="wide")

# Título y Descripción
st.title("✈️ Travel Planner: Tu Diseñador de Viajes Personal")
st.markdown("""
Esta herramienta utiliza Tecnología Generativa Avanzada (OpenAI o Gemini) y **Búsqueda Web en Tiempo Real** para crear itinerarios.
""")

# Sidebar para Configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Detectar si hay clave en .env
    env_gemini_key = os.getenv("GEMINI_API_KEY")
    
    st.markdown("### 🤖 Motor: Google Gemini")
    
    api_key = ""
    if env_gemini_key:
        st.success("✅ API Key cargada desde .env")
        api_key = env_gemini_key
    else:
        api_key = st.text_input("Gemini API Key", type="password", help="Consíguela gratis en aistudio.google.com")
        if api_key:
            st.success("✅ Clave ingresada correctamente")
        st.caption("[Obtener clave gratis aquí](https://aistudio.google.com/app/apikey)")

    st.divider()
    st.info("✅ Cumple con: Prompt Engineering, RAG y **Tool Use (Browsing)**.")

# --- Base de Conocimiento Simulada (RAG) ---
knowledge_base = {
    "Japón": {
        "clima": "Templado, con cuatro estaciones distintas. Primavera (cerezos) y otoño (hojas rojas) son las mejores épocas.",
        "moneda": "Yen japonés (JPY).",
        "tips": "Es importante llevar efectivo. El transporte público es excelente. No se deja propina.",
        "destinos_top": ["Tokio", "Kioto", "Osaka", "Hiroshima", "Nara"],
        "coords": [
            {"lat": 35.6762, "lon": 139.6503, "name": "Tokio"},
            {"lat": 35.0116, "lon": 135.7681, "name": "Kioto"},
            {"lat": 34.6937, "lon": 135.5023, "name": "Osaka"}
        ]
    },
    "Francia": {
        "clima": "Generalmente templado. Inviernos suaves y veranos cálidos.",
        "moneda": "Euro (EUR).",
        "tips": "Aprender algunas frases básicas en francés es muy apreciado. El servicio en restaurantes incluye propina.",
        "destinos_top": ["París", "Niza", "Lyon", "Burdeos", "Marsella"],
        "coords": [
            {"lat": 48.8566, "lon": 2.3522, "name": "París"},
            {"lat": 43.7102, "lon": 7.2620, "name": "Niza"},
            {"lat": 45.7640, "lon": 4.8357, "name": "Lyon"}
        ]
    },
    "Perú": {
        "clima": "Variado. Costa árida, Andes fríos y Selva húmeda.",
        "moneda": "Sol (PEN).",
        "tips": "Para Machu Picchu, reservar con mucha antelación. Cuidado con el mal de altura en Cusco.",
        "destinos_top": ["Cusco", "Machu Picchu", "Lima", "Arequipa", "Iquitos"],
        "coords": [
            {"lat": -12.0464, "lon": -77.0428, "name": "Lima"},
            {"lat": -13.5320, "lon": -71.9675, "name": "Cusco"},
            {"lat": -13.1631, "lon": -72.5450, "name": "Machu Picchu"}
        ]
    },
    "España": {
        "clima": "Mediterráneo en la costa, continental en el interior. Veranos calurosos.",
        "moneda": "Euro (EUR).",
        "tips": "La cena suele ser tarde (21:00+). Las tapas son una forma de vida.",
        "destinos_top": ["Madrid", "Barcelona", "Sevilla", "Granada", "Valencia"],
        "coords": [
            {"lat": 40.4168, "lon": -3.7038, "name": "Madrid"},
            {"lat": 41.3851, "lon": 2.1734, "name": "Barcelona"},
            {"lat": 37.3891, "lon": -5.9845, "name": "Sevilla"}
        ]
    },
    "Italia": {
        "clima": "Mediterráneo. Inviernos suaves y veranos calurosos.",
        "moneda": "Euro (EUR).",
        "tips": "El 'coperto' es un cargo por servicio común. El café se toma de pie en la barra.",
        "destinos_top": ["Roma", "Florencia", "Venecia", "Milán", "Nápoles"],
        "coords": [
            {"lat": 41.9028, "lon": 12.4964, "name": "Roma"},
            {"lat": 43.7696, "lon": 11.2558, "name": "Florencia"},
            {"lat": 45.4408, "lon": 12.3155, "name": "Venecia"}
        ]
    },
    "Estados Unidos": {
        "clima": "Muy variado. Costa Este húmeda, Oeste seco. Inviernos fríos en el norte.",
        "moneda": "Dólar estadounidense (USD).",
        "tips": "La propina es obligatoria (15-20%). Las distancias son enormes, planea bien el transporte.",
        "destinos_top": ["Nueva York", "Los Ángeles", "Miami", "San Francisco", "Las Vegas"],
        "coords": [
            {"lat": 40.7128, "lon": -74.0060, "name": "Nueva York"},
            {"lat": 34.0522, "lon": -118.2437, "name": "Los Ángeles"},
            {"lat": 25.7617, "lon": -80.1918, "name": "Miami"}
        ]
    },
    "Reino Unido": {
        "clima": "Oceánico templado. Lluvia frecuente y días nublados.",
        "moneda": "Libra esterlina (GBP).",
        "tips": "Los museos nacionales suelen ser gratuitos. Conduce por la izquierda.",
        "destinos_top": ["Londres", "Edimburgo", "Mánchester", "Liverpool", "Bath"],
        "coords": [
            {"lat": 51.5074, "lon": -0.1278, "name": "Londres"},
            {"lat": 55.9533, "lon": -3.1883, "name": "Edimburgo"},
            {"lat": 53.4808, "lon": -2.2426, "name": "Mánchester"}
        ]
    },
    "Alemania": {
        "clima": "Templado. Inviernos fríos y veranos agradables.",
        "moneda": "Euro (EUR).",
        "tips": "El efectivo sigue siendo muy usado. La puntualidad es clave.",
        "destinos_top": ["Berlín", "Múnich", "Hamburgo", "Fráncfort", "Colonia"],
        "coords": [
            {"lat": 52.5200, "lon": 13.4050, "name": "Berlín"},
            {"lat": 48.1351, "lon": 11.5820, "name": "Múnich"},
            {"lat": 53.5511, "lon": 9.9937, "name": "Hamburgo"}
        ]
    }
}

import time

def search_web_realtime(query):
    """Realiza una búsqueda real en DuckDuckGo (Backend HTML para evitar Rate Limits)."""
    try:
        time.sleep(1) # Throttling para ser amigable con el servidor
        with DDGS() as ddgs:
            # Usamos backend='html' que es más robusto contra bloqueos
            results = list(ddgs.text(query, region='es-es', max_results=3, backend='html'))
            if results:
                return f"Información web sobre '{query}':\n" + "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return f"Error en búsqueda web: {str(e)}"
    return "No se encontraron resultados web recientes."

def generate_with_gemini(prompt, api_key):
    """Genera texto usando Google Gemini."""
    try:
        genai.configure(api_key=api_key)
        # Usamos gemini-flash-latest que es el alias estable para la versión Flash más reciente
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Configuración de seguridad permisiva para evitar bloqueos falsos positivos
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        response = model.generate_content(prompt, safety_settings=safety_settings)
        return response.text
    except Exception as e:
        return f"Error con Gemini: {str(e)}"

# OpenAI eliminado por solicitud del usuario

def generate_itinerary(destination, duration, budget, interests, constraints, api_key):
    """Controlador principal de generación."""
    
    # 1. TOOL USE: Búsqueda Web (RAG Real)
    with st.status(f"🔎 Investigando sobre {destination}...", expanded=True) as status:
        st.write("Consultando DuckDuckGo...")
        # Queries simplificadas para asegurar resultados con backend HTML
        web_context = search_web_realtime(f"agenda cultural {destination} 2025")
        weather_context = search_web_realtime(f"clima {destination} pronostico")
        news_context = search_web_realtime(f"turismo {destination} noticias")
        status.update(label="¡Investigación completada!", state="complete", expanded=False)
    
    # 2. RAG Simulado (Base de Conocimiento Local)
    local_context = ""
    if destination in knowledge_base:
        data = knowledge_base[destination]
        local_context = f"""
        - Clima Típico: {data['clima']}
        - Moneda: {data['moneda']}
        - Tips Expertos: {data['tips']}
        - Destinos Top: {", ".join(data['destinos_top'])}
        """

    full_context = f"{web_context}\n\n{weather_context}\n\n{news_context}"

    # 3. Prompt Engineering
    prompt = f"""
    Actúa como un agente de viajes experto y carismático. Crea un itinerario detallado para el siguiente viaje:
    
    DATOS DEL VIAJE:
    - Destino: {destination}
    - Duración: {duration} días
    - Presupuesto: {budget}
    - Intereses: {interests}
    - Notas: {constraints}
    
    CONTEXTO EXPERTO LOCAL (Base de Conocimiento):
    {local_context}

    CONTEXTO EN TIEMPO REAL (De la Web):
    {full_context}
    
    INSTRUCCIONES:
    1. **CRUCIAL**: Comienza con una sección destacada llamada "📡 Reporte de Inteligencia en Vivo". Aquí DEBES mencionar 2-3 datos concretos y recientes que encontraste en la búsqueda web (ej. "He detectado que hay lluvias esta semana", "Encontré una noticia sobre un festival en...", "El pronóstico actual indica..."). Demuestra que estás conectado a internet.
    2. Crea un itinerario día por día con actividades lógicas.
    3. Usa el CONTEXTO EXPERTO LOCAL para dar consejos sobre moneda y tips culturales.
    4. Usa el CONTEXTO EN TIEMPO REAL para personalizar (si llueve, sugiere museos).
    5. Formato Markdown limpio y atractivo.
    """
    
    if not api_key:
        return "⚠️ Por favor ingresa una API Key válida para generar el itinerario."

    return generate_with_gemini(prompt, api_key)

# --- Interfaz Principal ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Tus Preferencias")
    
    # Destino con desplegable fijo para asegurar 100% de éxito en el mapa
    dest_options = sorted(list(knowledge_base.keys()))
    destination = st.selectbox("¿A dónde quieres ir?", dest_options)

    duration = st.slider("Duración (días)", min_value=1, max_value=30, value=5)
    budget = st.select_slider("Presupuesto", options=["Económico", "Moderado", "Lujo"], value="Moderado")
    interests = st.multiselect("Intereses", ["Cultura", "Gastronomía", "Naturaleza", "Aventura", "Relax", "Vida Nocturna"], default=["Cultura", "Gastronomía"])
    
    # Preferencias adicionales ahora es un multiselect para agilizar
    constraints_options = ["Viajo con niños", "Vegetariano", "Sin gluten", "Movilidad reducida", "Evitar multitudes", "Mochilero", "Luna de miel"]
    constraints_list = st.multiselect("Preferencias Adicionales", constraints_options)
    constraints = ", ".join(constraints_list)
    
    generate_btn = st.button("✨ Generar Itinerario Real", type="primary")
    
    if generate_btn:
        st.toast("✨ ¡Manos a la obra! Diseñando tu viaje...", icon="✈️")
        st.info("⏳ Tu Agente Personal está trabajando en tu itinerario. Por favor, **desliza hacia abajo** para ver el resultado 👇")

with col2:
    st.subheader("�️ Mapa del Destino")
    
    # Mostrar mapa si el destino está en la base de conocimiento
    import pandas as pd
    import numpy as np
    import unicodedata

    def normalize_text(text):
        """Elimina acentos y convierte a minúsculas."""
        return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn").lower()
    
    map_data = None
    if destination:
        for key, data in knowledge_base.items():
            # Comparación robusta (ignora mayúsculas y tildes: japon == Japón)
            if normalize_text(key) in normalize_text(destination):
                if "coords" in data:
                    map_data = pd.DataFrame(data["coords"])
                    st.map(map_data, zoom=4)
                    st.caption(f"📍 Destinos principales en {key}")
                break

# --- Generación y Visualización de Resultados (Full Width) ---
if generate_btn:
    st.divider()
    st.subheader("📝 Tu Itinerario Personalizado")
    
    if not destination:
        st.warning("Por favor, ingresa un destino.")
    elif not api_key:
        st.error("❌ Necesitas una API Key para activar el Agente. Selecciona 'Google Gemini' y obtén una gratis.")
    else:
        with st.spinner("✨ Consultando fuentes globales y diseñando tu experiencia exclusiva..."):
            interests_str = ", ".join(interests)
            result = generate_itinerary(destination, duration, budget, interests_str, constraints, api_key)
            st.markdown(result)
            
            st.download_button(
                label="📥 Descargar Itinerario",
                data=result,
                file_name=f"itinerario_{destination}.md",
                mime="text/markdown"
            )

# Footer
st.markdown("---")
st.caption("Caso Práctico Unidad 1 - Generative AI")

# Sección de Documentación Integrada
with st.expander("📚 Ver Manual de Ingeniería de Prompts (Lógica Interna)"):
    try:
        with open("manual_prompts.md", "r", encoding="utf-8") as f:
            manual_content = f.read()
        st.markdown(manual_content)
    except FileNotFoundError:
        st.warning("El archivo manual_prompts.md no se encuentra en el directorio.")
