from flask import Flask, request, render_template, session, redirect, url_for
import os
import pdfplumber
import openai
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'un_valor_predeterminado_para_desarrollo')
openai.api_key = os.getenv('OPENAI_API_KEY')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extraer_texto_de_pdf_con_pdfplumber(ruta_pdf):
    texto_completo = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + "\n"
    return texto_completo

@app.route('/', methods=['GET', 'POST'])
def index():
    respuesta = None
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                filename = file.filename  # Solo el nombre del archivo
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                # Guardar solo el nombre del archivo y el texto extraído en la sesión
                session['file_name'] = filename  # Cambiado de 'file_path' a 'file_name'
                session['texto_pdf'] = extraer_texto_de_pdf_con_pdfplumber(file_path)
        pregunta = request.form.get('pregunta')
        if pregunta and 'texto_pdf' in session:
            texto_contexto = session['texto_pdf']
            respuesta = hacer_pregunta_a_gpt(texto_contexto, pregunta)
    else:
        # En caso de GET, opcionalmente limpiar la sesión para empezar de nuevo
        session.pop('file_name', None)  # Asegúrate de limpiar 'file_name'
        session.pop('texto_pdf', None)

    file_name = session.get('file_name', None)  # Usa 'file_name' en lugar de 'file_path'
    return render_template('index.html', respuesta=respuesta, file_name=file_name)

def hacer_pregunta_a_gpt(texto_contexto, pregunta):
    MAX_TOKENS_FOR_PROMPT = 4096 - 150  # Reserva tokens para la pregunta y respuesta
    if len(texto_contexto) > MAX_TOKENS_FOR_PROMPT:
        texto_contexto = texto_contexto[:MAX_TOKENS_FOR_PROMPT]
    
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=f"{texto_contexto}\n\nPregunta: {pregunta}\nRespuesta:",
            temperature=0.5,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["\n"],
            
        )
        return response['choices'][0]['text'].strip()
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

#if __name__ == '__main__':
#   app.run(debug=True)
