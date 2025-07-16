"""Privacy and data protection utilities."""

import hashlib
import re
import html
from typing import Any, Dict, List, Optional, Set


def anonymize_data(
    data: Dict[str, Any], fields_to_anonymize: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """Anonymize sensitive data fields.
    
    Args:
        data: Data dictionary to anonymize
        fields_to_anonymize: Optional set of field names to anonymize. If ``None``,
            a default set of common sensitive fields is used.
        
    Returns:
        Anonymized data dictionary
    """
    if fields_to_anonymize is None:
        fields_to_anonymize = {
            "username", "name", "email", "phone_number",
            "full_name", "bio", "website", "external_url"
        }
    
    anonymized = data.copy()
    
    for key, value in data.items():
        if key.lower() in fields_to_anonymize:
            if isinstance(value, str) and value:
                anonymized[key] = _hash_string(value)
            else:
                anonymized[key] = "***ANONYMIZED***"
        elif isinstance(value, dict):
            anonymized[key] = anonymize_data(value, fields_to_anonymize)
        elif isinstance(value, list):
            anonymized[key] = [
                anonymize_data(item, fields_to_anonymize) if isinstance(item, dict) else item
                for item in value
            ]
    
    return anonymized


def _hash_string(text: str) -> str:
    """Create a consistent hash of a string for anonymization.
    
    Args:
        text: Text to hash
        
    Returns:
        Hashed representation
    """
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def detect_sensitive_info(text: str) -> List[str]:
    """Detect potentially sensitive information in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of detected sensitive information types
    """
    if not text:
        return []
    
    sensitive_patterns = []
    
    # Email addresses
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        sensitive_patterns.append("email")
    
    # Phone numbers (basic pattern)
    if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
        sensitive_patterns.append("phone")
    
    # URLs
    if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
        sensitive_patterns.append("url")
    
    # Credit card numbers (basic pattern)
    if re.search(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', text):
        sensitive_patterns.append("credit_card")
    
    # Social Security Numbers (US format)
    if re.search(r'\b\d{3}-?\d{2}-?\d{4}\b', text):
        sensitive_patterns.append("ssn")
    
    return sensitive_patterns


def remove_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove metadata that could be identifying.
    
    Args:
        data: Data dictionary
        
    Returns:
        Data with metadata removed
    """
    metadata_fields = {
        "device_id", "session_id", "ip_address", "user_agent",
        "location", "geo_coordinates", "device_info",
        "raw_data", "internal_id"
    }
    
    cleaned = {}
    for key, value in data.items():
        if key.lower() not in metadata_fields:
            if isinstance(value, dict):
                cleaned[key] = remove_metadata(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    remove_metadata(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                cleaned[key] = value
    
    return cleaned


def generate_privacy_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a privacy report for the data.
    
    Args:
        data: Data to analyze
        
    Returns:
        Privacy report with findings and recommendations
    """
    report = {
        "total_entries": 0,
        "sensitive_data_found": [],
        "recommendations": [],
        "risk_level": "low"
    }
    
    def analyze_recursive(obj, path=""):
        if isinstance(obj, dict):
            report["total_entries"] += 1
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check for sensitive field names
                if key.lower() in {"email", "phone", "address", "location"}:
                    report["sensitive_data_found"].append({
                        "type": "sensitive_field",
                        "field": current_path,
                        "value_type": type(value).__name__
                    })
                
                # Check text content for sensitive patterns
                if isinstance(value, str):
                    sensitive_types = detect_sensitive_info(value)
                    for sens_type in sensitive_types:
                        report["sensitive_data_found"].append({
                            "type": sens_type,
                            "field": current_path,
                            "pattern_detected": True
                        })
                
                analyze_recursive(value, current_path)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                analyze_recursive(item, f"{path}[{i}]")
    
    analyze_recursive(data)
    
    # Generate recommendations
    if report["sensitive_data_found"]:
        report["recommendations"].append("Consider anonymizing sensitive data before sharing")
        report["risk_level"] = "medium"
        
        if len(report["sensitive_data_found"]) > 10:
            report["risk_level"] = "high"
            report["recommendations"].append("High amount of sensitive data detected - strongly recommend anonymization")
    
    if any(item["type"] in {"email", "phone", "credit_card", "ssn"} 
           for item in report["sensitive_data_found"]):
        report["risk_level"] = "high"
        report["recommendations"].append("Personal identifying information detected - anonymization required")
    
    return report


def safe_filename(filename: str) -> str:
    """Convert filename to safe version by removing/replacing problematic characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove or replace problematic characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    safe_name = ''.join(char for char in safe_name if ord(char) >= 32)
    
    # Limit length
    if len(safe_name) > 255:
        name, ext = safe_name.rsplit('.', 1) if '.' in safe_name else (safe_name, '')
        safe_name = name[:255-len(ext)-1] + ('.' + ext if ext else '')
    
    return safe_name.strip()


def anonymize_conversation_data(conversation):
    """Anonymize sensitive data in a conversation object.
    
    Args:
        conversation: Conversation object to anonymize
        
    Returns:
        Anonymized conversation object
    """
    try:
        # Create a deep copy to avoid modifying the original
        import copy
        anonymized_conv = copy.deepcopy(conversation)
        
        # Generate anonymous participant mapping
        participant_mapping = {}
        for i, participant in enumerate(anonymized_conv.participants):
            if not participant.is_self:
                original_name = participant.name
                anonymous_name = f"Contact_{i+1}"
                participant_mapping[original_name] = anonymous_name
                participant.name = anonymous_name
                if participant.username:
                    participant.username = f"user_{i+1}"
        
        # Anonymize conversation title
        for original, anonymous in participant_mapping.items():
            anonymized_conv.title = anonymized_conv.title.replace(original, anonymous)
        
        # Anonymize messages
        for message in anonymized_conv.messages:
            if message.sender_name in participant_mapping:
                message.sender_name = participant_mapping[message.sender_name]
            
            # Optionally anonymize message content (remove @mentions of participants)
            if message.content:
                for original, anonymous in participant_mapping.items():
                    message.content = message.content.replace(f"@{original.lower()}", f"@{anonymous.lower()}")
        
        # Clear raw data to remove any identifying information
        anonymized_conv.raw_data = {}
        
        # Mark as anonymized
        anonymized_conv.anonymization_applied = True
        
        return anonymized_conv
        
    except Exception as e:
        # If anonymization fails, return the original conversation
        print(f"Warning: Failed to anonymize conversation: {e}")
        return conversation


def safe_html_escape(text: str) -> str:
    """Safely escape HTML characters in text.
    
    Args:
        text: Text to escape
        
    Returns:
        HTML-safe escaped text
    """
    if not text:
        return ""
    return html.escape(str(text))