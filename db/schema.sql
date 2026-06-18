-- Create customers table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    gender VARCHAR(10),
    senior_citizen BOOLEAN,
    partner BOOLEAN,
    dependents BOOLEAN,
    tenure INTEGER,
    phone_service BOOLEAN,
    multiple_lines VARCHAR(20),
    internet_service VARCHAR(20),
    online_security VARCHAR(20),
    online_backup VARCHAR(20),
    device_protection VARCHAR(20),
    tech_support VARCHAR(20),
    streaming_tv VARCHAR(20),
    streaming_movies VARCHAR(20),
    contract_type VARCHAR(20),
    paperless_billing BOOLEAN,
    payment_method VARCHAR(30),
    monthly_charges DECIMAL(10,2),
    total_charges DECIMAL(10,2),
    churn_label BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Create predictions table
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id) ON DELETE SET NULL,
    churn_probability  FLOAT,
    churn_prediction BOOLEAN,
    model_version VARCHAR(20),
    threshold_used  FLOAT,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
);
-- Create index for faster lookups
CREATE INDEX idx_predictions_customer_id ON predictions(customer_id);
CREATE INDEX idx_predictions_predicted_at ON predictions(predicted_at);