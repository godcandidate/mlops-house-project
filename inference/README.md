# House Price Inference Service

Serverless inference endpoints for house price predictions and feedback collection.

## Lambda Functions

### 1. Prediction Lambda (Container)

- **Location**: `prediction/`
- **Type**: Container image deployment
- **Purpose**: House price predictions

### 2. Feedback Lambda (Zip)

- **Location**: `feedback/`
- **Type**: Zip file deployment
- **Purpose**: Collect prediction feedback

## Deployment

### Prediction Lambda (Container)

```bash
cd prediction-image/
docker build -t house-price-prediction .
# Push to ECR and deploy
```

### Feedback Lambda (Zip)

```bash
cd feedback/
zip -r feedback-lambda.zip .
aws lambda update-function-code --function-name feedback-handler --zip-file fileb://feedback-lambda.zip
```

## 📡 Usage

### Make Prediction

```bash
curl -X POST "https://prediction-lambda-url/" \
-H "Content-Type: application/json" \
-d '{
  "sqft": 1500,
  "bedrooms": 3,
  "bathrooms": 2,
  "location": "suburban",
  "year_built": 2000,
  "condition": "fair"
}'
```

### Submit Feedback

```bash
curl -X POST "https://feedback-lambda-url/" \
-H "Content-Type: application/json" \
-d '{
  "prediction_id": "abc123",
  "actual_price": 290000,
  "feedback": "accurate"
}'
```
