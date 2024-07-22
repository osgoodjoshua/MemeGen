from flask import jsonify, request
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Image, Caption
from app.api import api_bp

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/images', methods=['GET'])
def get_images():
    images = Image.query.all()
    return jsonify([{'id': image.id, 'url': image.url} for image in images])

@api_bp.route('/captions', methods=['GET'])
def get_captions():
    captions = Caption.query.all()
    return jsonify([{'id': caption.id, 'text': caption.text, 'image_id': caption.image_id, 'url': caption.image.url} for caption in captions])

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
    return jsonify({'id': caption.id, 'text': caption.text, 'image_id': caption.image_id})

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

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        image_url = f'/static/uploads/{filename}'  # Adjust this URL based on your static files setup

        # Save image record in the database
        image = Image(url=image_url)
        db.session.add(image)
        db.session.commit()

        return jsonify({'id': image.id, 'url': image_url}), 200

    return jsonify({'error': 'File type not allowed'}), 400
