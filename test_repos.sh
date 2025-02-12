#!/bin/bash

# Get the CSRF token from the login page
echo "Getting CSRF token..."
CSRF_TOKEN=$(curl -s http://localhost:5000/login | grep "csrf-token" | sed -n 's/.*content="\([^"]*\)".*/\1/p')

echo "Using CSRF token: $CSRF_TOKEN"

# Login using proper form data and CSRF token
echo "Logging in..."
COOKIE=$(curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -d "csrf_token=$CSRF_TOKEN&email=test@example.com&password=test123" \
  -c - | grep session | cut -f7)

echo "Using session cookie: $COOKIE"

# Query repositories with the session cookie
echo "Querying repositories..."
curl -X GET http://localhost:5000/api/repositories \
  -H "Accept: application/json" \
  -H "Cookie: session=$COOKIE" \
  -H "X-CSRF-Token: $CSRF_TOKEN"