# Documentación de Ingeniería de Prompts: Arquitectura del "Travel Planner"

**Proyecto:** Solución Caso Práctico Unidad 1 (Enfoque E1 - Con Código)
**Componente:** Lógica de Generación (Backend)

---

## 1. Introducción: Más allá del Chatbot

Este documento detalla la arquitectura lógica de la aplicación `app.py`. No estamos ante un simple chatbot que responde preguntas, sino ante un **Agente Cognitivo Orquestado**.

El sistema utiliza un enfoque de **Ingeniería de Sistemas Compuestos** (Compound AI Systems), donde el LLM (Gemini) es solo una pieza de un engranaje mayor controlado por código Python.

---

## 2. Flujo de Ejecución (The Execution Pipeline)

Cuando el usuario hace clic en "Generar Itinerario", el sistema ejecuta la siguiente secuencia lógica:

1.  **Captura de Intención:** Recoge los inputs estructurados (Destino, Intereses, Presupuesto) desde la interfaz Streamlit.
2.  **Fase de Investigación (Browsing):**
    - El código activa la librería `duckduckgo_search`.
    - Ejecuta 3 búsquedas paralelas: "Agenda Cultural", "Pronóstico del Clima", "Noticias de Turismo".
    - _Optimización:_ Se aplica un retraso (throttling) y un backend HTML para evitar bloqueos de seguridad (Rate Limits).
3.  **Fase de Recuperación (Retrieval):**
    - Consulta la `knowledge_base` local (diccionario Python) para obtener datos estáticos verificados (moneda, coordenadas).
4.  **Fase de Ensamblaje del Prompt:**
    - El sistema construye un "Mega-Prompt" que fusiona: Rol + Datos del Usuario + Investigación Web + Conocimiento Local.
5.  **Fase de Inferencia:**
    - Se envía el prompt al modelo `gemini-flash-latest`.
    - Se aplican filtros de seguridad permisivos para evitar falsos positivos.
6.  **Renderizado:**
    - La respuesta se transmite a la interfaz y se procesa el mapa interactivo con las coordenadas locales.

---

## 3. Arquitectura del Prompt (The Prompt Stack)

El prompt final es una construcción dinámica de tres capas:

### Capa 1: Definición de Rol (System Instruction)

Se establece la "persona" del agente para asegurar un tono consistente.

```python
prompt = f"""
Actúa como un agente de viajes experto y carismático. Crea un itinerario detallado...
"""
```

### Capa 2: Inyección de Contexto Híbrido (RAG)

Aquí reside la inteligencia del sistema. Inyectamos información que el modelo NO tiene en su entrenamiento.

#### A. Contexto de Inteligencia en Tiempo Real (Web RAG)

Datos vivos recuperados al instante.

**Template de Inyección:**

```text
CONTEXTO EN TIEMPO REAL (De la Web):
{full_context}
# Contiene: Clima (pronóstico), Noticias recientes, Agenda cultural
```

#### B. Contexto de Conocimiento Experto (Local RAG)

Datos curados manualmente para garantizar precisión cultural.

**Template de Inyección:**

```text
CONTEXTO EXPERTO LOCAL (Base de Conocimiento):
{local_context}
# Contiene: Tips de propinas, Moneda oficial, Lugares imperdibles
```

### Capa 3: Instrucciones de Tarea (Chain of Thought)

Instrucciones paso a paso para guiar el razonamiento del modelo.

1.  **Reporte de Inteligencia:** "CRUCIAL: Inicia con un reporte basado en los datos web recuperados."
2.  **Fusión de Datos:** "Usa el contexto local para tips y el contexto web para eventos."
3.  **Formato:** "Salida obligatoria en Markdown."

---

## 4. Ejemplo de Prompt en Tiempo de Ejecución

Así luce lo que realmente "lee" Gemini:

```text
[ROL]
Actúa como un agente de viajes experto...

[DATOS USUARIO]
Destino: Alemania | Intereses: Cultura

[CONTEXTO LOCAL]
- Moneda: Euro
- Tip: Puntualidad es clave.

[CONTEXTO WEB (Inyectado por Python)]
- Clima: "Lluvias ligeras en Berlín..."
- Noticias: "Festival de Cine comienza mañana..."

[INSTRUCCIONES]
1. Analiza el clima y sugiere actividades bajo techo si llueve.
2. Crea el itinerario día a día.
```

## 5. Desafíos de Ingeniería y Soluciones

Durante el desarrollo de este Agente, se identificaron y abordaron tres obstáculos técnicos críticos:

### A. Gestión de Rate Limits (Bloqueos de Búsqueda)

- **Problema:** La ejecución secuencial rápida de búsquedas en DuckDuckGo generaba errores `202 Ratelimit`, bloqueando la obtención de datos.
- **Solución:** Se implementó una estrategia de "Humanización de Peticiones":
  1.  Se migró al backend `html` (más robusto que la API JSON).
  2.  Se inyectó latencia artificial (`time.sleep(1)`) entre consultas para mitigar el bloqueo.

### B. Estabilidad del Modelo (Quota Exceeded)

- **Problema:** El uso de modelos experimentales (`gemini-2.0-flash-exp`) resultó en errores `429 Quota Exceeded` debido a límites estrictos en la capa gratuita.
- **Solución:** Se realizó una migración de arquitectura al alias de producción `gemini-flash-latest`, garantizando alta disponibilidad y velocidad sin errores de cuota.

### C. Ambigüedad Semántica (Prompt Refinement)

- **Problema:** La query "tiempo" era interpretada por el buscador como "tiempo de ejecución de software" o "gestión del tiempo", introduciendo ruido al contexto.
- **Solución:** Se refinó la ingeniería del prompt de búsqueda utilizando palabras clave inequívocas: `clima {destino} pronostico`.

---

## 6. Conclusión

Esta arquitectura demuestra cómo el código (Python) amplifica las capacidades de la IA, permitiéndole "ver" el mundo real y actuar con precisión experta.
