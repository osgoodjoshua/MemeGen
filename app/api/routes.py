from flask import jsonify, request, current_app
from app import db
from werkzeug.utils import secure_filename
from app.models import Image, Caption
from app.api import api_bp
import os

@api_bp.route('/images', methods=['GET'])
def get_images():
    images = Image.query.all()
    return jsonify([{'id': image.id, 'url': image.url, 'is_core': image.is_core} for image in images])

@api_bp.route('/captions', methods=['GET'])
def get_captions():
    captions = Caption.query.all()
    return jsonify([{
        'id': caption.id,
        'text': caption.text,
        'image_id': caption.image_id,
        'url': f"{request.url_root[:-1]}{caption.image.url}" if not caption.image.url.startswith('http') else caption.image.url
    } for caption in captions])

@api_bp.route('/captions', methods=['POST'])
def create_caption():
    data = request.json
    text = data.get('text')
    image_id = data.get('image_id')

    if not text or not image_id:
        return jsonify({'error': 'Invalid input'}), 400

    caption = Caption(text=text, image_id=image_id)
    db.session.add(caption)
    db.session.commit()

    return jsonify({'id': caption.id, 'text': caption.text, 'image_id': caption.image_id}), 201

@api_bp.route('/captions/<int:caption_id>', methods=['GET'])
def get_caption(caption_id):
    caption = Caption.query.get_or_404(caption_id)
    return jsonify({
        'id': caption.id,
        'text': caption.text,
        'image_id': caption.image_id,
        'url': caption.image.url if caption.image.url.startswith('http') else f"{request.url_root[:-1]}{caption.image.url}"
    })

@api_bp.route('/captions/<int:caption_id>', methods=['PUT'])
def update_caption(caption_id):
    caption = Caption.query.get_or_404(caption_id)
    data = request.json

    text = data.get('text')
    if not text:
        return jsonify({'error': 'Invalid input'}), 400

    caption.text = text
    db.session.commit()

    return jsonify({'id': caption.id, 'text': caption.text, 'image_id': caption.image_id})

@api_bp.route('/captions/<int:caption_id>', methods=['DELETE'])
def delete_caption(caption_id):
    caption = Caption.query.get_or_404(caption_id)
    db.session.delete(caption)
    db.session.commit()
    return '', 204

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Ensure the upload folder exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Create the image record in the database
        image = Image(url=f'/static/uploads/{filename}', is_core=False)
        db.session.add(image)
        db.session.commit()
        
        return jsonify({'message': 'File uploaded successfully', 'image_id': image.id, 'image_url': image.url}), 201
    return jsonify({'error': 'File upload failed'}), 500
