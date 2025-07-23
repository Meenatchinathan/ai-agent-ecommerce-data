#!/bin/bash

API_URL="http://localhost:8000/query"

echo "Starting E-commerce AI Agent Demo"
echo "================================="

# Question 1
echo -e "\n1. Getting total sales..."
curl -X POST "$API_URL" \
-H "Content-Type: application/json" \
-d '{"question":"What is my total sales?"}'

# Question 2 
echo -e "\n\n2. Calculating RoAS..."
curl -X POST "$API_URL" \
-H "Content-Type: application/json" \
-d '{"question":"Calculate the RoAS (Return on Ad Spend)"}'

# Question 3
echo -e "\n\n3. Finding highest CPC product..."
curl -X POST "$API_URL" \
-H "Content-Type: application/json" \
-d '{"question":"Which product had the highest CPC (Cost Per Click)?"}'

echo -e "\n\nDemo complete!"