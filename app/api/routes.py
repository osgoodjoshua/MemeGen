from flask import jsonify, request
from app import db
from app.models import Image, Caption
from app.api import api_bp

@api_bp.route('/images', methods=['GET'])
def get_images():
    images = Image.query.all()
    return jsonify([{'id': image.id, 'url': image.url} for image in images])

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
