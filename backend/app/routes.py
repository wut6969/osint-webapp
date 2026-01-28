from flask import Blueprint, request, jsonify
from app.osint import investigate_email
from app.name_osint import investigate_name

bp = Blueprint('main', __name__)

@bp.route('/api/investigate', methods=['POST'])
def investigate():
    data = request.get_json()
    email = data.get('email', '').strip()
    first_name = data.get('firstName', '').strip()
    last_name = data.get('lastName', '').strip()
    
    # Validate that at least one search parameter is provided
    if not email and not (first_name and last_name):
        return jsonify({'error': 'Please provide either an email address or both first and last name'}), 400
    
    results = {}
    
    # Run email investigation if email provided
    if email:
        results['email_results'] = investigate_email(email)
    
    # Run name investigation if name provided
    if first_name and last_name:
        results['name_results'] = investigate_name(first_name, last_name, email if email else None)
    
    return jsonify(results)

@bp.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'})
