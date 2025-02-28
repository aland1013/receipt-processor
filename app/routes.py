from flask import jsonify, request
from app.receipt_processor import process_receipt, get_receipt_points

def register_routes(app):
    @app.route('/receipts/process', methods=['POST'])
    def process():
        receipt_data = request.json
        if not receipt_data:
            return jsonify({"error": "The receipt is invalid."}), 400
        
        receipt_id = process_receipt(receipt_data)
        if receipt_id is None:
            return jsonify({"error": "The receipt is invalid."}), 400
            
        return jsonify({"id": receipt_id})
    
    @app.route('/receipts/<id>/points', methods=['GET'])
    def points(id):
        points = get_receipt_points(id)
        if points is None:
            return jsonify({"error": "No receipt found for that ID."}), 404
        
        return jsonify({"points": points}) 