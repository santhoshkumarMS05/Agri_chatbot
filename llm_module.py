import os
import requests
import logging
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

def truncate_context(context, max_chars=3000):
    """Truncate context to prevent payload size issues"""
    if len(context) <= max_chars:
        return context
    
    # Try to truncate at sentence boundaries
    truncated = context[:max_chars]
    last_period = truncated.rfind('.')
    if last_period > max_chars * 0.7:
        return truncated[:last_period + 1]
    
    return truncated + "..."

def extract_location_from_query(query):
    """Extract location information from user query only if explicitly mentioned"""
    if not query:
        return None
        
    query_lower = query.lower()
    
    # Look for explicit location mentions with keywords
    location_patterns = [
        r'\bin\s+([a-zA-Z\s]+?)(?:\s|$|,|\?)',
        r'\bfrom\s+([a-zA-Z\s]+?)(?:\s|$|,|\?)',
        r'\bat\s+([a-zA-Z\s]+?)(?:\s|$|,|\?)',
        r'\bnear\s+([a-zA-Z\s]+?)(?:\s|$|,|\?)',
        r'\baround\s+([a-zA-Z\s]+?)(?:\s|$|,|\?)',
        r'\bfor\s+([a-zA-Z\s]+?)(?:\s|$|,|\?)'
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, query_lower)
        for match in matches:
            location = match.strip()
            # Remove common non-location words
            location = re.sub(r'\b(my|area|region|place|farm|field|growing|crops|agriculture)\b', '', location, flags=re.IGNORECASE).strip()
            # Clean up and check if it looks like a real location
            location = re.sub(r'[^\w\s]', '', location).strip().title()
            if location and len(location) > 2 and not location.lower() in ['summer', 'winter', 'monsoon', 'season']:
                return location
    
    return None

def check_location_in_context(context, user_location):
    """Check if location exists in context and determine match type"""
    if not user_location or not context:
        return "general"
    
    context_lower = context.lower()
    user_location_lower = user_location.lower()
    
    # Check for exact match
    if user_location_lower in context_lower:
        return "exact"
    
    # Check for partial match (individual words)
    location_words = user_location_lower.split()
    matches = 0
    for word in location_words:
        if len(word) > 3 and word in context_lower:
            matches += 1
    
    if matches > 0:
        return "partial"
    
    return "fallback"

def prepare_context_for_query(context, user_location, match_type):
    """Prepare context based on whether location was mentioned"""
    if not user_location:
        # No location mentioned - use all available data
        prefix = "Agricultural data from multiple regions and locations:\n\n"
        suffix = "\n\nNote: This data covers various agricultural regions and growing conditions."
        return prefix + context + suffix
    
    # Location mentioned - handle accordingly
    if match_type == "exact":
        return f"Agricultural data for {user_location}:\n\n" + context
    elif match_type == "partial":
        prefix = f"Regional agricultural data for {user_location} and similar areas:\n\n"
        suffix = f"\n\nNote: This data covers the broader region including {user_location}."
        return prefix + context + suffix
    else:
        # Fallback when location mentioned but not found
        prefix = f"General agricultural guidelines applicable to {user_location}:\n\n"
        suffix = f"\n\nNote: These are general recommendations that can be adapted for {user_location} based on local conditions."
        return prefix + context + suffix

def extract_crop_count_from_query(query):
    """Extract number of crops requested from user query"""
    if not query:
        return 4
        
    query_lower = query.lower()
    
    # Look for numbers
    numbers = re.findall(r'\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b', query_lower)
    
    number_map = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }
    
    for num in numbers:
        if num.isdigit():
            return min(int(num), 8)
        elif num in number_map:
            return number_map[num]
    
    # Default based on context
    if any(word in query_lower for word in ['few', 'some', 'several']):
        return 3
    elif any(word in query_lower for word in ['many', 'multiple', 'various']):
        return 5
    
    return 4

def format_response_for_html(response):
    """Convert markdown-style formatting to HTML for proper display"""
    if not response:
        return response
        
    # Convert **text** to <strong>text</strong>
    response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)
    
    # Convert bullet points
    lines = response.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip().startswith('* '):
            line = line.replace('* ', '• ')
        elif line.strip().startswith('- '):
            line = line.replace('- ', '• ')
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def create_engagement_footer():
    """Create an engaging footer for responses"""
    footers = [
        "\n\n💬 Would you like more suggestions or have questions about growing these crops?",
        "\n\n🌱 Need more details about any of these crops? Just ask!",
        "\n\n📞 Want to know more about planting times or care tips? I'm here to help!",
        "\n\n🤔 Have specific questions about your soil or climate? Feel free to ask!"
    ]
    
    import random
    return random.choice(footers)

def create_response_note(user_location, match_type):
    """Create appropriate note based on query type"""
    if not user_location:
        # No location mentioned - general response
        return ""
    
    # Location mentioned
    if match_type == "exact":
        return ""
    elif match_type == "partial":
        return f"\n\n📍 <em>Using regional data for {user_location} area.</em>"
    else:
        return f"\n\n📍 <em>General recommendations for {user_location}. Consult local experts for specific varieties.</em>"

def is_agriculture_related_query(query):
    """Check if the query is related to agriculture/farming"""
    if not query:
        return False
    
    query_lower = query.lower()
    
    # Agriculture-related keywords
    agriculture_keywords = [
        'crop', 'crops', 'farming', 'farm', 'agriculture', 'agricultural', 'plant', 'planting',
        'grow', 'growing', 'harvest', 'field', 'soil', 'seed', 'seeds', 'fertilizer',
        'irrigation', 'cultivation', 'cultivate', 'yield', 'production', 'farmer',
        'wheat', 'rice', 'corn', 'maize', 'sugarcane', 'cotton', 'vegetable', 'fruit',
        'season', 'monsoon', 'kharif', 'rabi', 'zaid', 'sowing', 'reaping',
        'pesticide', 'herbicide', 'organic', 'profit', 'income', 'market', 'price',
        'climate', 'weather', 'rain', 'drought', 'water', 'land', 'acre', 'hectare'
    ]
    
    # Check if query contains agriculture keywords
    for keyword in agriculture_keywords:
        if keyword in query_lower:
            return True
    
    # Check for agriculture-related phrases
    agriculture_phrases = [
        'what to grow', 'which crop', 'best for farming', 'agricultural advice',
        'farming tips', 'crop recommendation', 'suitable for cultivation',
        'high yield', 'profitable crops', 'cash crops', 'food crops'
    ]
    
    for phrase in agriculture_phrases:
        if phrase in query_lower:
            return True
    
    return False

def get_llm_response(query, context):
    """Get crop recommendation response from Groq LLM with smart location handling"""
    try:
        # Validate inputs
        if not GROQ_API_KEY:
            return "❌ <strong>API configuration error.</strong> Please contact support."
        
        if not query or not context:
            return "❓ <strong>Please provide a valid question about crops.</strong>"
        
        # Check if query is agriculture-related
        if not is_agriculture_related_query(query):
            return "🌾 <strong>I'm a farming advisor and can only help with agriculture-related questions.</strong><br><br>Please ask me about:<br>• Crop recommendations<br>• Farming advice<br>• Agricultural practices<br>• Growing conditions<br>• Soil and climate information"
        
        # Extract location only if explicitly mentioned
        user_location = extract_location_from_query(query)
        
        # Determine how to handle the context
        if user_location:
            match_type = check_location_in_context(context, user_location)
            prepared_context = prepare_context_for_query(context, user_location, match_type)
            location_instruction = f"Focus on recommendations for {user_location} based on available data."
            farm_location = user_location
        else:
            match_type = "general"
            prepared_context = prepare_context_for_query(context, None, None)
            location_instruction = "Provide general recommendations based on all available agricultural data from various regions."
            farm_location = "General (multiple regions)"
        
        # Truncate context
        truncated_context = truncate_context(prepared_context, max_chars=2500)
        
        # Get crop count
        requested_crops = extract_crop_count_from_query(query)
        
        # Build location-aware prompt
        prompt = f"""You are a helpful farming advisor. Give practical crop recommendations.

Available Data: {truncated_context}

Question: {query}

Instructions:
1. Recommend exactly {requested_crops} crops
2. {location_instruction}
3. Use simple, farmer-friendly language
4. Focus on practical growing benefits
5. Always provide helpful suggestions (never say "no data available")
6. If no specific location mentioned, give general recommendations suitable for various regions

Format your response as:
🌾 Farm Information:
Location: {farm_location}
[Include relevant details from available data]

✅ Top {requested_crops} Crop Recommendations:

1. [CROP NAME] - [Why it's suitable for the conditions]
   Benefit: [Specific advantage]

2. [CROP NAME] - [Why it's suitable for the conditions]
   Benefit: [Specific advantage]

[Continue for all {requested_crops} crops]

🌟 Growing Tips:
- [Practical tip 1]
- [Practical tip 2]

Keep it encouraging and actionable."""

        # API request
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a friendly farming advisor. Always provide helpful crop recommendations based on the available data. Use simple language and be encouraging."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.9
        }

        logger.info(f"Making API request for {requested_crops} crops (Location: {user_location if user_location else 'General'})")
        
        response = requests.post(
            GROQ_BASE_URL,
            headers=headers,
            json=data,
            timeout=45
        )
        
        if response.status_code != 200:
            logger.error(f"API error: {response.status_code}")
            return "🔧 <strong>Service temporarily unavailable.</strong> Please try again in a moment."
        
        result = response.json()
        
        if not result.get('choices') or not result['choices']:
            logger.error("Invalid API response structure")
            return "⚠️ <strong>Invalid response received.</strong> Please try again."
        
        llm_response = result['choices'][0]['message']['content'].strip()
        
        if not llm_response:
            return "❓ <strong>Empty response received.</strong> Please rephrase your question."
        
        # Format response
        formatted_response = format_response_for_html(llm_response)
        response_note = create_response_note(user_location, match_type)
        engagement_footer = create_engagement_footer()
        
        final_response = formatted_response + response_note + engagement_footer
        
        logger.info("Successfully processed request")
        return final_response

    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return "🕐 <strong>Request timed out.</strong> Please try a shorter question."
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 0
        logger.error(f"HTTP error: {status_code}")
        
        if status_code == 413:
            return "📝 <strong>Question too long.</strong> Please ask something shorter."
        elif status_code == 429:
            return "⏰ <strong>Too many requests.</strong> Please wait a minute and try again."
        else:
            return "🔧 <strong>Service error.</strong> Please try again later."
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return "📡 <strong>Connection error.</strong> Please check your internet connection."
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return "⚠️ <strong>Something went wrong.</strong> Please try again or contact support."