# Receipt Processor

This is a Flask-based web service that processes receipts and calculates points based on predefined rules.

## Requirements

- Python 3.9+
- Docker (optional, for containerized deployment)

## Running the Application

### Using Python directly

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python run.py
   ```

The service will be available at http://localhost:5000.

### Using Docker

1. Build the Docker image:
   ```
   docker build -t receipt-processor .
   ```

2. Run the Docker container:
   ```
   docker run -p 5000:5000 receipt-processor
   ```

The service will be available at http://localhost:5000.

## API Endpoints

### Process Receipt

- **URL**: `/receipts/process`
- **Method**: `POST`
- **Request Body**: JSON receipt data
- **Response**: JSON containing a generated ID for the receipt

Example Request:
```json
{
  "retailer": "Target",
  "purchaseDate": "2022-01-01",
  "purchaseTime": "13:01",
  "items": [
    {
      "shortDescription": "Mountain Dew 12PK",
      "price": "6.49"
    },
    {
      "shortDescription": "Emils Cheese Pizza",
      "price": "12.25"
    }
  ],
  "total": "18.74"
}
```

Example Response:
```json
{
  "id": "7fb1377b-b223-49d9-a31a-5a02701dd310"
}
```

### Get Points

- **URL**: `/receipts/{id}/points`
- **Method**: `GET`
- **Response**: JSON containing the number of points awarded for the receipt

Example Response:
```json
{
  "points": 32
}
``` 