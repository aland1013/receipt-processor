import uuid
import math
from datetime import datetime
from typing import Dict, Optional, Any, Union
from app.models import Receipt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for receipts
receipts_store: Dict[str, Dict[str, Any]] = {}


def process_receipt(receipt_data: Dict[str, Any]) -> Optional[str]:
    """
    Process a receipt and calculate points.
    
    Args:
        receipt_data: The receipt data to process
        
    Returns:
        A unique ID for the receipt, or None if processing failed
    """
    try:
        # Validate the receipt using Pydantic model
        receipt = Receipt(**receipt_data)
        
        # Generate a unique ID
        receipt_id = str(uuid.uuid4())
        
        # Calculate points
        points = calculate_points(receipt)
        
        # Store the receipt and points
        receipts_store[receipt_id] = {
            "receipt": receipt.model_dump(),
            "points": points
        }
        
        return receipt_id
    except Exception as e:
        # Log the error
        logger.error(f"Error processing receipt: {e}")
        # Return None instead of raising the exception
        return None


def get_receipt_points(receipt_id: str) -> Optional[int]:
    """
    Get the points for a receipt by ID.
    
    Args:
        receipt_id: The ID of the receipt to get points for
        
    Returns:
        The points for the receipt, or None if the receipt ID is not found
    """
    receipt_data = receipts_store.get(receipt_id)
    if receipt_data:
        return receipt_data["points"]
    return None


def calculate_points(receipt: Receipt) -> int:
    """
    Calculate points for a receipt based on the rules.
    
    Args:
        receipt: The receipt to calculate points for
        
    Returns:
        The calculated points for the receipt
    """
    points = 0
    
    # One point for every alphanumeric character in the retailer name
    retailer_alphanumeric = sum(1 for char in receipt.retailer if char.isalnum())
    points += retailer_alphanumeric
    
    # 50 points if the total is a round dollar amount with no cents
    total_float = float(receipt.total)
    if total_float.is_integer():
        points += 50
    
    # 25 points if the total is a multiple of 0.25
    if total_float % 0.25 == 0:
        points += 25
    
    # 5 points for every two items on the receipt
    points += (len(receipt.items) // 2) * 5
    
    # If the trimmed length of the item description is a multiple of 3,
    # multiply the price by 0.2 and round up to the nearest integer
    for item in receipt.items:
        trimmed_desc = item.shortDescription.strip()
        if len(trimmed_desc) % 3 == 0:
            price = float(item.price)
            points += math.ceil(price * 0.2)
    
    # 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt.purchaseDate, "%Y-%m-%d")
    if purchase_date.day % 2 == 1:  # Odd day
        points += 6
    
    # 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = datetime.strptime(receipt.purchaseTime, "%H:%M").time()
    if datetime.strptime("14:00", "%H:%M").time() < purchase_time < datetime.strptime("16:00", "%H:%M").time():
        points += 10
    
    return points 