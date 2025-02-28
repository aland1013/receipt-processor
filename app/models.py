from pydantic import BaseModel, Field, field_validator
from typing import List
import re

class Item(BaseModel):
    shortDescription: str = Field(..., pattern=r"^[\w\s\-]+$")
    price: str = Field(..., pattern=r"^\d+\.\d{2}$")

class Receipt(BaseModel):
    retailer: str = Field(..., pattern=r"^[\w\s\-&]+$")
    purchaseDate: str
    purchaseTime: str
    items: List[Item] = Field(..., min_items=1)
    total: str = Field(..., pattern=r"^\d+\.\d{2}$")
    
    @field_validator('purchaseDate')
    def validate_date(cls, v: str) -> str:
        """
        Validate that the purchase date is in YYYY-MM-DD format.
        
        Args:
            v: The purchase date to validate
            
        Returns:
            The validated purchase date
            
        Raises:
            ValueError: If the purchase date is not in YYYY-MM-DD format
        """
        # Ensure date is in YYYY-MM-DD format
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Invalid date format, expected YYYY-MM-DD")
        return v
    
    @field_validator('purchaseTime')
    def validate_time(cls, v: str) -> str:
        """
        Validate that the purchase time is in HH:MM format.
        
        Args:
            v: The purchase time to validate
            
        Returns:
            The validated purchase time
            
        Raises:
            ValueError: If the purchase time is not in HH:MM format
        """
        # Ensure time is in HH:MM format
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError("Invalid time format, expected HH:MM")
        return v 