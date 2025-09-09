#!/usr/bin/env python3
"""
Security utilities for StilBAR-Converter
Provides secure error handling and input validation
"""
import re
import logging
from typing import Optional, Tuple
import streamlit as st

# Set up secure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app_security.log'
)
logger = logging.getLogger(__name__)

def sanitize_error_message(error: Exception, user_message: str = "An error occurred") -> str:
    """
    Sanitize error messages to prevent information disclosure
    Log full error details securely while showing safe message to user
    """
    # Log the full error for debugging
    logger.error(f"Application error: {str(error)}", exc_info=True)
    
    # Return a safe, generic message to the user
    error_str = str(error).lower()
    
    # Check for database-related errors
    if any(keyword in error_str for keyword in ['connection', 'database', 'sql', 'supabase']):
        return "Database service temporarily unavailable. Please try again later."
    
    # Check for authentication errors
    if any(keyword in error_str for keyword in ['auth', 'credential', 'permission', 'unauthorized']):
        return "Authentication error. Please check your configuration."
    
    # Check for file-related errors
    if any(keyword in error_str for keyword in ['file', 'path', 'directory']):
        return "File operation failed. Please check your input."
    
    # Default safe message
    return user_message

def validate_stilbar_code(code: str) -> Tuple[bool, str]:
    """
    Validate StilBAR code input for security and format
    """
    if not code:
        return False, "StilBAR code cannot be empty"
    
    # Length validation
    if len(code) > 500:  # Reasonable upper limit
        return False, "StilBAR code too long"
    
    # Character validation - allow alphanumeric, dashes, pipes, dots, and a few special chars
    allowed_pattern = re.compile(r'^[A-Za-z0-9\-–|.\[\]()_+=]+$')
    if not allowed_pattern.match(code):
        return False, "StilBAR code contains invalid characters"
    
    return True, ""

def validate_smiles_input(smiles: str) -> Tuple[bool, str]:
    """
    Validate SMILES string input for security
    """
    if not smiles:
        return False, "SMILES string cannot be empty"
    
    # Length validation
    if len(smiles) > 10000:  # Very long SMILES could be malicious
        return False, "SMILES string too long"
    
    # Basic character validation for SMILES
    # SMILES typically contain: letters, numbers, parentheses, brackets, special chars
    allowed_pattern = re.compile(r'^[A-Za-z0-9\[\]()@+=\-#\\/.%\s]+$')
    if not allowed_pattern.match(smiles):
        return False, "SMILES string contains invalid characters"
    
    return True, ""

def validate_compound_name(name: str) -> Tuple[bool, str]:
    """
    Validate compound name input
    """
    if not name:
        return False, "Compound name cannot be empty"
    
    # Length validation
    if len(name) > 200:
        return False, "Compound name too long"
    
    # Character validation - allow reasonable characters for compound names
    allowed_pattern = re.compile(r'^[A-Za-z0-9\s\-_().,]+$')
    if not allowed_pattern.match(name):
        return False, "Compound name contains invalid characters"
    
    return True, ""

def validate_csv_file_size(file_size: int, max_size_mb: int = 10) -> Tuple[bool, str]:
    """
    Validate uploaded file size
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        return False, f"File size exceeds {max_size_mb}MB limit"
    
    return True, ""

def secure_display_error(error: Exception, context: str = ""):
    """
    Display error message securely using Streamlit
    """
    safe_message = sanitize_error_message(error, f"Operation failed: {context}")
    st.error(safe_message)

def log_security_event(event_type: str, details: str, severity: str = "INFO"):
    """
    Log security-related events
    """
    log_message = f"SECURITY [{event_type}]: {details}"
    
    if severity == "ERROR":
        logger.error(log_message)
    elif severity == "WARNING":
        logger.warning(log_message)
    else:
        logger.info(log_message)