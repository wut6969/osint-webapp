from flask import Blueprint, request, jsonify
from app.osint import investigate_email

bp = Blueprint('main', __name__)

@bp.route('/api/investigate', methods=['POST'])
def investigate():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    results = investigate_email(email)
    return jsonify(results)

@bp.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'})
