#!/usr/bin/env python3
"""
WhatsApp MCP Server using FastAPI

This server implements a webhook for receiving WhatsApp messages and a test endpoint for sending messages
using the Meta WhatsApp Cloud API.
"""

import os
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="WhatsApp MCP Server", description="Meta WhatsApp Cloud API Server")

# Retrieve environment variables
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_PHONE_NUMBER = os.getenv("WHATSAPP_PHONE_NUMBER", "")  # Optional: for reference
WHATSAPP_WEBHOOK_CALLBACK_URL = os.getenv("WHATSAPP_WEBHOOK_CALLBACK_URL", "")  # Optional: for reference

# Validate required environment variables
if not WHATSAPP_ACCESS_TOKEN:
    raise ValueError("Missing WHATSAPP_ACCESS_TOKEN in environment variables")
if not WHATSAPP_PHONE_NUMBER_ID:
    raise ValueError("Missing WHATSAPP_PHONE_NUMBER_ID in environment variables")
if not WHATSAPP_VERIFY_TOKEN:
    raise ValueError("Missing WHATSAPP_VERIFY_TOKEN in environment variables")

# WhatsApp API base URL
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Verify the webhook with Meta's verification process.
    
    This endpoint handles GET requests sent by Meta during webhook verification.
    It checks the 'hub.verify_token' against the stored WHATSAPP_VERIFY_TOKEN
    and returns the 'hub.challenge' if verification is successful.
    """
    # Get query parameters from the request
    params = request.query_params
    
    # Extract verification parameters
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    # Verify that the mode is subscribe and the token matches
    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return PlainTextResponse(content=challenge)
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Forbidden: Verification failed")


@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle incoming webhook payloads from WhatsApp Cloud API.
    
    This endpoint receives POST requests from Meta's WhatsApp Cloud API
    containing message updates, delivery receipts, etc.
    """
    # Get the JSON payload from the request
    payload = await request.json()
    
    # Log the incoming payload
    logger.info(f"Incoming webhook payload: {json.dumps(payload, indent=2)}")
    
    # Process the payload (in a real application, you would parse and handle different message types)
    # For now, we just log the payload
    
    # Return a success response
    return {"status": "received", "message": "Webhook received successfully"}


@app.post("/send-test")
async def send_test_message(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Send a test WhatsApp message using the WhatsApp Cloud API.
    
    This endpoint accepts a JSON payload with 'phone_number' and 'message' fields,
    then sends the message using the configured WhatsApp credentials.
    
    Expected JSON format:
    {
        "phone_number": "1234567890",
        "message": "Hello from WhatsApp MCP Server!"
    }
    """
    # Extract phone number and message from the request body
    phone_number = data.get("phone_number")
    message = data.get("message")
    
    # Validate required fields
    if not phone_number:
        raise HTTPException(status_code=400, detail="Phone number is required")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Prepare the message payload for WhatsApp Cloud API
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    # Log the outgoing message
    logger.info(f"Sending message to {phone_number}: {message}")
    
    try:
        # Validate phone number format (basic validation)
        if not phone_number or len(phone_number.replace("+", "").replace("-", "").replace(" ", "")) < 10:
            raise HTTPException(status_code=400, detail="Invalid phone number format. Please provide a valid phone number.")
        
        # Send the message to WhatsApp Cloud API
        response = requests.post(
            f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
            headers=headers,
            json=payload
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"Message sent successfully: {response_data}")
            return {
                "status": "success",
                "message_id": response_data.get("messages", [{}])[0].get("id"),
                "details": "Message sent successfully"
            }
        else:
            logger.error(f"Failed to send message: {response.text}")
            # Return the error from WhatsApp API instead of raising an exception
            try:
                error_response = response.json()
                error_message = error_response.get("error", {}).get("message", f"API Error: {response.text}")
            except:
                error_message = f"API Error: {response.text}"
            
            raise HTTPException(
                status_code=response.status_code,
                detail=error_message
            )
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/")
async def root():
    """
    Root endpoint to check if the server is running.
    """
    return {
        "message": "Welcome to Uzma's Collection",
        "whatsapp_phone_number_id": WHATSAPP_PHONE_NUMBER_ID,
        "whatsapp_phone_number": WHATSAPP_PHONE_NUMBER,
        "webhook_callback_url": WHATSAPP_WEBHOOK_CALLBACK_URL,
        "webhook_url": "/webhook",
        "test_endpoint": "/send-test"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify server status.
    """
    return {
        "status": "healthy",
        "service": "WhatsApp MCP Server",
        "environment_vars_loaded": bool(WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_VERIFY_TOKEN)
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the server using uvicorn
    # The server will be available at http://localhost:8083
    uvicorn.run(
        "whatsapp_mcp_server:app",  # Reference to the FastAPI app
        host="0.0.0.0",             # Listen on all interfaces
        port=8083,                  # Port 8083 as specified
        reload=True                 # Enable auto-reload for development
    )