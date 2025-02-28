import requests
import unittest
import json

BASE_URL = "http://localhost:5000"

class ReceiptProcessorTests(unittest.TestCase):
    
    def test_target_receipt_example(self):
        # Target receipt from README example
        receipt = {
            "retailer": "Target",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {
                    "shortDescription": "Mountain Dew 12PK",
                    "price": "6.49"
                },{
                    "shortDescription": "Emils Cheese Pizza",
                    "price": "12.25"
                },{
                    "shortDescription": "Knorr Creamy Chicken",
                    "price": "1.26"
                },{
                    "shortDescription": "Doritos Nacho Cheese",
                    "price": "3.35"
                },{
                    "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
                    "price": "12.00"
                }
            ],
            "total": "35.35"
        }
        
        response = requests.post(f"{BASE_URL}/receipts/process", json=receipt)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertTrue(data["id"])
        
        receipt_id = data["id"]
        response = requests.get(f"{BASE_URL}/receipts/{receipt_id}/points")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("points", data)
        self.assertEqual(data["points"], 28)
    
    def test_mm_receipt_example(self):
        # M&M Corner Market receipt from README example
        receipt = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-03-20",
            "purchaseTime": "14:33",
            "items": [
                {
                    "shortDescription": "Gatorade",
                    "price": "2.25"
                },{
                    "shortDescription": "Gatorade",
                    "price": "2.25"
                },{
                    "shortDescription": "Gatorade",
                    "price": "2.25"
                },{
                    "shortDescription": "Gatorade",
                    "price": "2.25"
                }
            ],
            "total": "9.00"
        }
        
        response = requests.post(f"{BASE_URL}/receipts/process", json=receipt)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        receipt_id = data["id"]
        
        response = requests.get(f"{BASE_URL}/receipts/{receipt_id}/points")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["points"], 109)
    
    def test_invalid_receipt(self):
        # Missing required field
        invalid_receipt = {
            "retailer": "Target",
            # Missing purchaseDate
            "purchaseTime": "13:01",
            "items": [
                {
                    "shortDescription": "Mountain Dew 12PK",
                    "price": "6.49"
                }
            ],
            "total": "6.49"
        }
        
        response = requests.post(f"{BASE_URL}/receipts/process", json=invalid_receipt)
        self.assertEqual(response.status_code, 400)
        
    def test_nonexistent_receipt(self):
        # Try to get points for a non-existent receipt ID
        response = requests.get(f"{BASE_URL}/receipts/nonexistent-id/points")
        self.assertEqual(response.status_code, 404)
    
    def test_retailer_name_points(self):
        # Test that retailer name points are calculated correctly
        receipts = [
            {
                "name": "Simple",
                "retailer": "Target",
                "expected_points_from_name": 6
            },
            {
                "name": "With special chars",
                "retailer": "M&M Corner Market",
                "expected_points_from_name": 14  # & is not alphanumeric
            }
        ]
        
        for test_case in receipts:
            receipt = {
                "retailer": test_case["retailer"],
                "purchaseDate": "2022-01-01",
                "purchaseTime": "13:01",
                "items": [{"shortDescription": "Item", "price": "5.00"}],
                "total": "5.00"
            }
            
            response = requests.post(f"{BASE_URL}/receipts/process", json=receipt)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            receipt_id = data["id"]
            
            response = requests.get(f"{BASE_URL}/receipts/{receipt_id}/points")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            

            self.assertGreaterEqual(data["points"], test_case["expected_points_from_name"])
    
    def test_round_dollar_points(self):
        # Test that 50 points are awarded for round dollar amounts
        receipts = [
            {
                "name": "Round dollar",
                "total": "10.00",
                "expected_bonus": 50
            },
            {
                "name": "Not round dollar",
                "total": "10.01",
                "expected_bonus": 0
            }
        ]
        
        for test_case in receipts:
            receipt = {
                "retailer": "X",  # Minimizing points from retailer name
                "purchaseDate": "2022-01-02",  # Even day to avoid odd day points
                "purchaseTime": "12:00",  # Outside 2-4 PM window
                "items": [{"shortDescription": "Item", "price": test_case["total"]}],
                "total": test_case["total"]
            }
            
            response = requests.post(f"{BASE_URL}/receipts/process", json=receipt)
            receipt_id = response.json()["id"]
            
            response = requests.get(f"{BASE_URL}/receipts/{receipt_id}/points")
            points = response.json()["points"]
            
            if test_case["expected_bonus"] > 0:
                self.assertGreaterEqual(points, test_case["expected_bonus"])
            else:
                # Should only have points from the retailer name (1)
                self.assertEqual(points, 1)  # 'X' has 1 alphanumeric character

    def test_comprehensive_validation(self):
        """Test various validation scenarios to ensure proper input validation."""
        
        # Base valid receipt to modify for each test case
        valid_receipt = {
            "retailer": "Target",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {
                    "shortDescription": "Mountain Dew 12PK",
                    "price": "6.49"
                }
            ],
            "total": "6.49"
        }
        
        # Test cases with expected error status
        validation_test_cases = [
            # Test all required fields are actually required
            {
                "name": "Missing retailer",
                "receipt_mod": {"retailer": None},  # Will be removed below
                "expected_status": 400
            },
            {
                "name": "Missing purchaseDate",
                "receipt_mod": {"purchaseDate": None},  # Will be removed below
                "expected_status": 400
            },
            {
                "name": "Missing purchaseTime",
                "receipt_mod": {"purchaseTime": None},  # Will be removed below
                "expected_status": 400
            },
            {
                "name": "Missing items array entirely",
                "receipt_mod": {"items": None},  # Will be removed below
                "expected_status": 400
            },
            {
                "name": "Missing total",
                "receipt_mod": {"total": None},  # Will be removed below
                "expected_status": 400
            },
            {
                "name": "Missing shortDescription in item",
                "receipt_mod": {"items": [{"price": "6.49"}]},  # Missing shortDescription
                "expected_status": 400
            },
            {
                "name": "Missing price in item",
                "receipt_mod": {"items": [{"shortDescription": "Mountain Dew 12PK"}]},  # Missing price
                "expected_status": 400
            },
            
            # Test validation of field formats
            {
                "name": "Empty retailer name",
                "receipt_mod": {"retailer": ""},
                "expected_status": 400
            },
            {
                "name": "Invalid date format",
                "receipt_mod": {"purchaseDate": "01/01/2022"},  # Wrong format
                "expected_status": 400
            },
            {
                "name": "Invalid time format",
                "receipt_mod": {"purchaseTime": "1:01 PM"},  # Wrong format
                "expected_status": 400
            },
            {
                "name": "Empty items array",
                "receipt_mod": {"items": []},
                "expected_status": 400
            },
            {
                "name": "Invalid price format",
                "receipt_mod": {"items": [{"shortDescription": "Item", "price": "6.5"}]},  # Missing second decimal
                "expected_status": 400
            },
            {
                "name": "Invalid total format",
                "receipt_mod": {"total": "6"},  # Missing decimal part
                "expected_status": 400
            },
            {
                "name": "Invalid shortDescription with special chars",
                "receipt_mod": {"items": [{"shortDescription": "Item with $ symbol", "price": "6.49"}]},
                "expected_status": 400
            }
        ]
        
        for test_case in validation_test_cases:
            # Create a deep copy of the valid receipt to avoid modifying the original
            test_receipt = json.loads(json.dumps(valid_receipt))
            
            # Apply the modifications for this test case
            for key, value in test_case["receipt_mod"].items():
                if value is None:
                    # Remove the key if value is None
                    test_receipt.pop(key, None)
                else:
                    test_receipt[key] = value
            
            # Send the request
            response = requests.post(f"{BASE_URL}/receipts/process", json=test_receipt)
            
            # Check the status code
            self.assertEqual(
                response.status_code, 
                test_case["expected_status"], 
                f"Test case '{test_case['name']}' failed: expected status {test_case['expected_status']}, got {response.status_code}"
            )

    
if __name__ == "__main__":
    unittest.main() 