# ✈️ AI Travel Planner (Agente de Viajes Inteligente)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Gemini](https://img.shields.io/badge/AI-Gemini%20Flash-orange)

Este proyecto es una solución práctica para la Unidad 1 del curso de **Generative AI**. Implementa un Agente de Viajes capaz de diseñar itinerarios personalizados utilizando un enfoque de **RAG Híbrido** (Retrieval-Augmented Generation) que combina inteligencia artificial generativa con datos en tiempo real.

## 🚀 Características Principales

- **Cerebro IA:** Utiliza **Google Gemini Flash (Latest)** para razonamiento rápido y lógico.
- **Ojos en la Web:** Integración con **DuckDuckGo** para obtener clima, noticias y eventos en tiempo real (evitando alucinaciones).
- **Conocimiento Experto:** Base de datos local con tips culturales, moneda y coordenadas geográficas.
- **Interfaz Interactiva:** Mapa dinámico y UI limpia construida con Streamlit.
- **Documentación Integrada:** El manual de ingeniería de prompts está embebido en la aplicación.

## 🛠️ Instalación y Ejecución

Este proyecto está diseñado para correr en cualquier sistema (Windows, Mac, Linux) que tenga Python instalado.

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Carlos-Bernal-AI/IEP-GIA.git
cd solucion_caso_practico
```

### 2. Crear un Entorno Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar API Key

Crea un archivo `.env` en la raíz del proyecto y añade tu clave de Google Gemini (es gratis):

```text
GEMINI_API_KEY=tu_clave_aqui
```

_Si no tienes una, la aplicación te permitirá ingresarla manualmente en la interfaz._

### 5. Ejecutar la Aplicación

```bash
streamlit run app.py
```

O si estás en Linux/Mac, puedes usar el script facilitador:

```bash
./run.sh
```

## 📂 Estructura del Proyecto

- `app.py`: Código principal de la aplicación.
- `manual_prompts.md`: Documentación técnica de la ingeniería de prompts (Lógica Interna).
- `reflexion.md`: Ensayo reflexivo sobre los desafíos y aprendizajes del proyecto.
- `requirements.txt`: Lista de librerías necesarias.

## 🎓 Autor

Carlos Bernal
