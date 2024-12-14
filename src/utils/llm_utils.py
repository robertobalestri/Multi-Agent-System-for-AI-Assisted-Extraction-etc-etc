from typing import List, Dict
import re
import json
from src.utils.logger_utils import setup_logging

logger = setup_logging(__name__)

def clean_llm_json_response(response: str) -> List[Dict]:
    """
    Clean and extract a valid JSON array from the LLM response.
    
    Args:
        response (str): The raw response from the LLM, expected to contain JSON.
    
    Returns:
        List[Dict]: A cleaned list of dictionaries containing the entities.
    
    Raises:
        ValueError: If no valid JSON object or array found in the response.
    """
    
    # Remove from the string ```json, ```plaintext, ```markdown and ```
    response_cleaned = re.sub(r"```(json|plaintext|markdown)?", "", response)
    
    # Remove any comments
    response_cleaned = re.sub(r'//.*?$|/\*.*?\*/', '', response_cleaned, flags=re.MULTILINE | re.DOTALL)
    
    # Try to extract a JSON object or array from the cleaned response
    json_match = re.search(r'(\{|\[)[\s\S]*(\}|\])', response_cleaned)
    
    #if the first and last characters are ' or " then remove them in 2 calls
    if response_cleaned[0] in ['"', "'"]:
        response_cleaned = response_cleaned[1:]
    if response_cleaned[-1] in ['"', "'"]:
        response_cleaned = response_cleaned[:-1]
    
    if json_match:
        json_str = json_match.group(0)
        
        # Replace all curly apostrophes with regular apostrophes
        json_str = json_str.replace("'", "'")
        
        # Wrap the response in an array if it contains a single object
        if json_str.startswith('{'):
            json_str = f'[{json_str}]'  # Wrap single object in an array
        
        # Try to parse the JSON
        try:
            parsed_json = json.loads(json_str)
            
            # If the parsed JSON is a dictionary, convert it to a list
            if isinstance(parsed_json, dict):
                return [parsed_json]  # Wrap the single entity in a list
            elif isinstance(parsed_json, list):
                return parsed_json  # Return the parsed list of dictionaries
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cleaned JSON: {e}")
            logger.error(f"Cleaned JSON string: {json_str}")
            logger.error(f"Full response: {response}")
            raise ValueError(f"Failed to parse cleaned JSON: {e}")
    
    # If no valid JSON is found, raise an error
    raise ValueError("No valid JSON object or array found in the response")

def clean_llm_text_response(response: str) -> str:
    """
    Clean and extract meaningful text from a markdown or plaintext LLM response.
    
    Args:
        response (str): The raw response from the LLM, expected to be plaintext or markdown.
    
    Returns:
        str: A cleaned version of the text.
    """
    
    # Remove any formatting indicators like ```plaintext, ```markdown, and ```
    response_cleaned = re.sub(r"```(plaintext|markdown|html)?", "", response)
    response_cleaned = re.sub(r"```", "", response_cleaned)  # Remove all triple backticks
    response_cleaned = re.sub(r"’", "'", response_cleaned)  # Replace all curly apostrophies with regular apostrophes
    # Strip extra whitespace
    response_cleaned = response_cleaned.strip()
    
    return response_cleaned