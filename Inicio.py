import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Streamlit 
st.set_page_config(page_title='Tablero Inteligente', layout="wide")

# Título y subtítulo
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Tablero Inteligente</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555555;'>Dibuja un boceto en el panel y presiona 'Analizar'</h4>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.subheader("Acerca de")
    st.write("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto.")
    st.markdown("---")
    stroke_width = st.slider('Ancho de línea', 1, 30, 5)

# Canvas
stroke_color = "#000000"
bg_color = '#FFFFFF'
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

# API Key input
ke = st.text_input('Ingresa tu Clave', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ.get('OPENAI_API_KEY', None)

# Inicializar cliente OpenAI
if api_key:
    client = OpenAI(api_key=api_key)

# Botón de análisis
analyze_button = st.button("Analiza la imagen")

# Lógica de análisis
if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("Analizando..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")
        st.session_state.base64_image = base64_image

        prompt_text = "Describe in spanish briefly the image"

        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ],
                }],
                max_tokens=500,
            )

            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response)

            # Guardar en session_state
            st.session_state.full_response = full_response
            st.session_state.analysis_done = True

            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

# Sección de creación de historia
if st.session_state.analysis_done:
    st.markdown("---")
    st.subheader("¿Quieres crear una historia?")

    if st.button("Crear historia infantil"):
        with st.spinner("Creando historia..."):
            story_prompt = f"Basándote en esta descripción: '{st.session_state.full_response}', crea una historia infantil breve y entretenida. La historia debe ser creativa y apropiada para niños."

            story_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_prompt}],
                max_tokens=500,
            )

            st.markdown("**Tu historia:**")
            st.write(story_response.choices[0].message.content)

# Advertencia si no hay API Key
if not api_key:
    st.warning("Por favor ingresa tu API key.")
