from flask import Flask, jsonify, request, Response
from typing import Tuple, Dict, Any, Union
from app.receipt_processor import process_receipt, get_receipt_points


def register_routes(app: Flask) -> None:
    """
    Register routes with the Flask application.
    
    Args:
        app: The Flask application to register routes with
    """
    @app.route('/receipts/process', methods=['POST'])
    def process() -> Union[Response, Tuple[Response, int]]:
        """
        Process a receipt and return a unique ID.
        
        Returns:
            A JSON response with the receipt ID or an error message
        """
        receipt_data = request.json
        if not receipt_data:
            return jsonify({"error": "The receipt is invalid."}), 400
        
        receipt_id = process_receipt(receipt_data)
        if receipt_id is None:
            return jsonify({"error": "The receipt is invalid."}), 400
            
        return jsonify({"id": receipt_id})
    
    @app.route('/receipts/<id>/points', methods=['GET'])
    def points(id: str) -> Union[Response, Tuple[Response, int]]:
        """
        Get the points for a receipt by ID.
        
        Args:
            id: The ID of the receipt to get points for
            
        Returns:
            A JSON response with the points or an error message
        """
        points = get_receipt_points(id)
        if points is None:
            return jsonify({"error": "No receipt found for that ID."}), 404
        
        return jsonify({"points": points}) 