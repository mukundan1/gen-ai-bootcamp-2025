from flask import Blueprint, jsonify
from pykakasi import kakasi

bp = Blueprint('japanese_utils', __name__)
kakasi = kakasi()

@bp.route('/api/romaji/<text>', methods=['GET'])
def get_romaji(text):
    """Convert Japanese text to romaji."""
    result = kakasi.convert(text)
    romaji = ''.join([item['hepburn'] for item in result])
    return jsonify({'romaji': romaji})

@bp.route('/api/reading/<text>', methods=['GET'])
def get_reading(text):
    """Get the reading (hiragana) for Japanese text."""
    result = kakasi.convert(text)
    reading = ''.join([item['hira'] for item in result])
    return jsonify({'reading': reading})
