from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
import os
from werkzeug.utils import secure_filename
from converter import PDFConverter
import json
from datetime import datetime
import subprocess
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static/flipbooks'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file uploaded'}), 400
    
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a PDF'}), 400
    
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pdf_path)
    
    flipbook_name = os.path.splitext(filename)[0]
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], flipbook_name)
    os.makedirs(output_dir, exist_ok=True)
    
    converter = PDFConverter(pdf_path, output_dir)
    pages = converter.convert_to_images(dpi=150)
    
    if not pages:
        return jsonify({'error': 'Failed to convert PDF'}), 500
    
    page_data = []
    for i, page_path in enumerate(pages, start=1):
        rel_path = os.path.relpath(page_path, 'static')
        page_data.append({
            'page': i,
            'image': rel_path.replace('\\', '/')
        })
    
    metadata = {
        'filename': filename,
        'total_pages': len(pages),
        'created_at': datetime.now().isoformat(),
        'pages': page_data
    }
    
    metadata_path = os.path.join(output_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return jsonify({
        'success': True,
        'flipbook_id': flipbook_name,
        'total_pages': len(pages),
        'metadata': metadata
    })

@app.route('/flipbook/<flipbook_id>')
def view_flipbook(flipbook_id):
    metadata_path = os.path.join(app.config['OUTPUT_FOLDER'], flipbook_id, 'metadata.json')
    if not os.path.exists(metadata_path):
        return "Flipbook not found", 404
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    return render_template('flipbook.html', metadata=metadata, flipbook_id=flipbook_id)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/export/<flipbook_id>', methods=['POST'])
def export_exe(flipbook_id):
    flipbook_dir = os.path.join(app.config['OUTPUT_FOLDER'], flipbook_id)
    if not os.path.exists(flipbook_dir):
        return jsonify({'error': 'Flipbook not found'}), 404
    
    def build_in_background():
        try:
            result = subprocess.run(
                ['python', 'export_flipbook.py', flipbook_id],
                capture_output=True,
                text=True,
                timeout=300
            )
            print(f"Export output: {result.stdout}")
            if result.stderr:
                print(f"Export errors: {result.stderr}")
        except Exception as e:
            print(f"Export error: {e}")
    
    thread = threading.Thread(target=build_in_background, daemon=True)
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Export started. This may take a few minutes...'
    })

@app.route('/download/<flipbook_id>')
def download_exe(flipbook_id):
    exe_path = os.path.join('output_exe', f'{flipbook_id}.exe')
    if os.path.exists(exe_path):
        return send_file(exe_path, as_attachment=True, download_name=f'{flipbook_id}.exe')
    else:
        return jsonify({'error': 'Executable not ready yet. Please wait and try again.'}), 404

@app.route('/check-export/<flipbook_id>')
def check_export(flipbook_id):
    exe_path = os.path.join('output_exe', f'{flipbook_id}.exe')
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)
        return jsonify({
            'ready': True,
            'size_mb': round(file_size, 2)
        })
    else:
        return jsonify({'ready': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
