from flask import Flask, request, render_template, send_file, url_for
from PIL import Image
from rembg import remove
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Garantir que a pasta de uploads exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def convert_to_sticker(input_path, output_path):
    img = Image.open(input_path)
    img_no_bg = remove(img)  # Remover fundo
    img_no_bg = img_no_bg.resize((512, 512), Image.Resampling.LANCZOS)
    img_no_bg.save(output_path, 'WEBP', quality=85)

@app.route('/', methods=['GET', 'POST'])
def index():
    sticker_url = None
    whatsapp_link = None
    
    if request.method == 'POST':
        # Verificar se o arquivo e o número foram enviados
        if 'file' not in request.files or 'phone_number' not in request.form:
            return "Imagem ou número de telefone não fornecido", 400
        
        file = request.files['file']
        phone_number = request.form['phone_number'].strip()  # Número fornecido pelo usuário
        
        if file.filename == '':
            return "Nenhum arquivo selecionado", 400
        
        # Salvar o arquivo temporariamente
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_image.jpg')
        file.save(input_path)
        
        # Converter para sticker
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'sticker.webp')
        convert_to_sticker(input_path, output_path)
        
        # Gerar URLs
        sticker_url = url_for('static', filename='uploads/sticker.webp', _external=True)  # URL absoluta
        # Formatar o número (remover caracteres indesejados e adicionar código do país, se necessário)
        phone_number = ''.join(filter(str.isdigit, phone_number))  # Apenas dígitos
        if not phone_number.startswith('55'):  # Exemplo: adicionar código do Brasil se não estiver presente
            phone_number = '55' + phone_number
        whatsapp_link = f"https://wa.me/{phone_number}?text={sticker_url}"
        
        # Remover arquivo temporário
        os.remove(input_path)
    
    return render_template('index.html', sticker_url=sticker_url, whatsapp_link=whatsapp_link)

if __name__ == '__main__':
    app.run(debug=True)