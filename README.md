# Asistente Personal con IA

Un chatbot basado en Gradio que actúa como tu representante personal en tu sitio web, respondiendo preguntas sobre tu experiencia profesional usando información de tu CV y resumen profesional.

## Características

- **Representación Profesional**: Actúa como tú para responder preguntas relacionadas con tu carrera
- **Respuestas Basadas en Documentos**: Solo usa información de tu CV (PDF) y archivo de resumen
- **Generación de Leads**: Captura automáticamente información de contacto de visitantes interesados
- **Seguimiento de Preguntas**: Registra preguntas que no pudo responder para mejoras futuras
- **Razonamiento Chain of Thought**: Usa pensamiento estructurado para proporcionar respuestas precisas y relevantes

## Cómo Funciona

El asistente de IA sigue un proceso estricto de Chain of Thought:

1. **Verificación de Información**: Confirma si la respuesta existe en tus documentos
2. **Evaluación de Relevancia**: Determina si la pregunta es profesionalmente relevante
3. **Estrategia de Respuesta**: Decide cómo responder basado en la disponibilidad de información
4. **Oportunidad de Engagement**: Evalúa si es momento de solicitar información de contacto

## Estructura del Proyecto

```
.
├── app.py                 # Aplicación principal
├── .env                   # Variables de entorno (no incluido en git)
├── me/
│   ├── cv.pdf            # Tu CV en formato PDF
│   └── summary.txt       # Resumen profesional en texto
└── requirements.txt      # Dependencias de Python
```

## Instalación

1. **Clona el repositorio**:
```bash
git clone <tu-repositorio>
cd personal-ai-assistant
```

2. **Crea un entorno virtual**:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. **Instala las dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configura las variables de entorno**:
Crea un archivo `.env` en la raíz del proyecto:
```env
# API Keys
GROQ_API_KEY=tu_clave_groq_aqui

# Pushover (para notificaciones)
PUSHOVER_TOKEN=tu_token_pushover
PUSHOVER_USER=tu_usuario_pushover
```

5. **Prepara tus documentos**:
   - Coloca tu CV en formato PDF en `me/cv.pdf`
   - Crea tu resumen profesional en `me/summary.txt`

## Uso

```bash
python app.py
```

La aplicación se ejecutará en `http://localhost:7860`

## Configuración

### Variables de Entorno Requeridas

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `GROQ_API_KEY` | Clave API de Groq para el modelo LLM | ✅ |
| `PUSHOVER_TOKEN` | Token de Pushover para notificaciones | ✅ |
| `PUSHOVER_USER` | Usuario de Pushover para notificaciones | ✅ |

### Documentos Requeridos

- **`me/cv.pdf`**: Tu CV en formato PDF. El sistema extraerá automáticamente el texto.
- **`me/summary.txt`**: Un resumen profesional en texto plano con información clave sobre tu experiencia.

## Herramientas del AI

El asistente tiene acceso a dos herramientas:

### 1. `record_user_details`
- **Propósito**: Registra información de contacto de visitantes interesados
- **Parámetros**: `email` (requerido), `name` (opcional), `notes` (opcional)
- **Uso**: Se activa automáticamente cuando alguien muestra interés en contactarte

### 2. `record_unknown_question`
- **Propósito**: Registra preguntas que no se pudieron responder
- **Parámetros**: `question` (requerido)
- **Uso**: Se activa cuando la información no está disponible en tus documentos

## Personalización

### Modificar el Prompt del Sistema

Edita la función `system_prompt()` en `app.py` para ajustar:
- El tono de comunicación
- Las instrucciones específicas
- El enfoque de engagement

### Agregar Nuevas Herramientas

1. Define la función de la herramienta:
```python
def nueva_herramienta(parametro):
    # Tu lógica aquí
    return {"resultado": "valor"}
```

2. Crea el esquema JSON:
```python
nueva_herramienta_json = {
    "name": "nueva_herramienta",
    "description": "Descripción de la herramienta",
    "parameters": {
        # Esquema de parámetros
    }
}
```

3. Agrégala al array `tools`:
```python
tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
    {"type": "function", "function": nueva_herramienta_json}
]
```

## Tecnologías Utilizadas

- **[Gradio](https://gradio.app/)**: Framework para la interfaz web
- **[OpenAI Python Client](https://github.com/openai/openai-python)**: Cliente para APIs compatibles con OpenAI
- **[Groq](https://groq.com/)**: Proveedor de LLM (usando Llama 3)
- **[PyPDF](https://pypdf.readthedocs.io/)**: Extracción de texto de PDFs
- **[Pushover](https://pushover.net/)**: Servicio de notificaciones
- **[python-dotenv](https://pypi.org/project/python-dotenv/)**: Gestión de variables de entorno

## Modelo de IA

- **Modelo**: `llama3-8b-8192` (vía Groq)
- **Capacidades**: Function calling, conversación natural, razonamiento
- **Limitaciones**: Contexto de 8192 tokens

## Notificaciones

El sistema envía notificaciones via Pushover cuando:
- Un visitante proporciona su información de contacto
- Se registra una pregunta que no se pudo responder

## Consideraciones de Seguridad

- Las claves API se manejan via variables de entorno
- No se almacena información persistente en el navegador
- Los datos de contacto se envían inmediatamente via Pushover

## Resolución de Problemas

### Error: "metadata is unsupported"
- **Causa**: Conflicto entre formatos de mensaje de Gradio y Groq
- **Solución**: El código ya incluye limpieza automática de mensajes

### Error: "OpenAI.__init__() takes 1 positional argument"
- **Causa**: API key no se pasa como parámetro nombrado
- **Solución**: Usar `api_key=` en el constructor

### Error: Archivo no encontrado
- **Causa**: Falta el CV o el archivo de resumen
- **Solución**: Verificar que `me/cv.pdf` y `me/summary.txt` existan

## Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Contacto

Para preguntas sobre este proyecto, puedes:
- Abrir un issue en GitHub
- Contactar directamente a través del chatbot en funcionamiento

---

**Nota**: Este README asume que tienes conocimientos básicos de Python y desarrollo web. Si necesitas ayuda adicional, consulta la documentación de las tecnologías utilizadas.
