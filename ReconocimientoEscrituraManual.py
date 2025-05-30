import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Streamlit 
st.set_page_config(page_title='Tablero Inteligente')
st.title('Tablero Inteligente')
with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")
   
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)
    drawing_mode = st.selectbox(
        "Selecciona el modo de dibujo:",
        ("freedraw", "line", "circle", "rect")
    )
    stroke_color = st.color_picker("Selecciona el color del trazo ", "#000000")
    fill_color = st.color_picker("Selecciona el color de relleno (círculo/rectángulo)", "#FFFFFF")

st.subheader("Dibuja en el lienzo y presiona el botón para analizarla")

# Parámetros para el lienzo
bg_color = '#FFFFFF'

page_bg_color = """
<style>
/* Fondo principal */
[data-testid="stAppViewContainer"] {
    background-color: #d3f8e3; /* Cambia el color de la página principal */
}

/* Fondo del sidebar */
[data-testid="stSidebar"] {
    background-image: url("https://img.freepik.com/free-vector/simple-pattern-background_1319-147.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

[data-testid="stMarkdownContainer"] {
    color: #0e0f15;
}
</style>
"""

st.markdown(page_bg_color, unsafe_allow_html=True)


# Crear el lienzo
canvas_result = st_canvas(
    fill_color=fill_color,  # Color de relleno personalizable
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=700,
    drawing_mode=drawing_mode,  # El modo seleccionado por el usuario
    key="canvas",
)

ke = st.text_input('Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke

# Recuperar la clave API
api_key = os.environ['OPENAI_API_KEY']

# Inicializar el cliente OpenAI con la clave API
client = OpenAI(api_key=api_key)

analyze_button = st.button("Analiza el dibujo", type="secondary")

# Verificar si se dibujó algo y si la API Key es válida
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Codificar la imagen
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        # Codificar la imagen en base64
        base64_image = encode_image_to_base64("img.png")
            
        prompt_text = (f"Describe en español brevemente la imagen")
    
        # Realizar la solicitud a la API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )
            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")
            # Actualización final después de la respuesta
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
else:
    # Mensajes de advertencia
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
