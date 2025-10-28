import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json
from gtts import gTTS
from deep_translator import GoogleTranslator  # ✅ reemplazo moderno compatible

# --- Estilo general con tonos fríos ---
st.markdown("""
    <style>
        /* Fondo general con degradado frío */
        .stApp {
            background: linear-gradient(135deg, #e3f2fd 0%, #e8eaf6 50%, #ede7f6 100%);
            font-family: 'Poppins', sans-serif;
            color: #263238;
        }

        /* Títulos principales */
        h1, h2, h3 {
            background: linear-gradient(90deg, #4b6cb7, #6a85b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            font-weight: 700;
        }

        /* Header superior */
        header[data-testid="stHeader"] {
            background: linear-gradient(90deg, #6a85b6 0%, #bac8e0 50%, #c5cae9 100%);
            color: white !important;
        }

        /* Texto general oscuro */
        .stMarkdown, .stMarkdown p, label, div[data-testid="stWidgetLabel"] {
            color: #263238 !important;
        }

        /* Botones de Streamlit */
        .stButton > button {
            background: linear-gradient(90deg, #7e57c2, #9575cd);
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0px 4px 12px rgba(123, 97, 255, 0.25);
            transition: 0.3s;
        }

        .stButton > button:hover {
            background: linear-gradient(90deg, #6a5ac7, #7b68ee);
            transform: scale(1.03);
        }

        /* Imagen centrada */
        [data-testid="stImage"] img {
            display: block;
            margin-left: auto;
            margin-right: auto;
            border-radius: 12px;
            box-shadow: 0px 4px 12px rgba(100, 130, 200, 0.3);
        }

        /* Cuadro de mensajes */
        .msg-box {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            background: linear-gradient(180deg, #e3f2fd 0%, #f3e5f5 100%);
            box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
            color: #37474f;
            text-align: center;
        }

        /* Texto de ayuda */
        .hint {
            text-align: center;
            color: #37474f;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# --- Configuración MQTT ---
def on_publish(client, userdata, result):
    print("El dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message

# --- Interfaz principal ---
st.title("INTERFACES MULTIMODALES")
st.subheader("Control por Voz")

image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

st.markdown("<p class='hint'>Toca el botón y habla</p>", unsafe_allow_html=True)

# --- Botón de voz (Bokeh) ---
stt_button = Button(label="Iniciar reconocimiento", width=220)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

# --- Captura de resultados del evento ---
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# --- Procesamiento de la voz capturada ---
if result:
    if "GET_TEXT" in result:
        # Texto detectado
        texto_detectado = result.get("GET_TEXT")
        st.markdown(f"<div class='msg-box'>Comando detectado: <b>{texto_detectado}</b></div>", unsafe_allow_html=True)
        
        # ✅ Traducción automática con deep-translator
        try:
            texto_traducido = GoogleTranslator(source='auto', target='es').translate(texto_detectado)
            st.markdown(f"<div class='msg-box'>Traducción al español: <b>{texto_traducido}</b></div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error al traducir el texto: {e}")

        # MQTT publicación
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": texto_detectado.strip()})
        ret = client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except:
        pass
