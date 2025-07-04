import json
import os
import logging
import re
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_simple_database():
    """Create a simple keyword-based database without embeddings"""
    try:
        # Check if the data file exists
        data_file = "crop_recommendation_rag_text.txt"
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file '{data_file}' not found.")
        
        logger.info(f"Loading data from {data_file}")
        
        # Read the text file
        with open(data_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into sections
        sections = [section.strip() for section in content.split('\n\n') if section.strip()]
        
        logger.info(f"Found {len(sections)} sections")
        
        # Create database structure
        database = []
        keywords_index = defaultdict(list)
        
        for i, section in enumerate(sections):
            lines = section.split('\n')
            title = lines[0] if lines else f"Section {i+1}"
            content_text = '\n'.join(lines[1:]) if len(lines) > 1 else section
            
            doc = {
                'id': i,
                'title': title,
                'content': content_text,
                'full_text': section
            }
            database.append(doc)
            
            # Create keyword index
            text_for_keywords = (title + ' ' + content_text).lower()
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text_for_keywords)
            
            for word in set(words):
                keywords_index[word].append(i)
        
        # Save the database
        os.makedirs("simple_db", exist_ok=True)
        
        with open("simple_db/database.json", "w", encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        with open("simple_db/keywords.json", "w", encoding='utf-8') as f:
            json.dump(dict(keywords_index), f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Simple database created successfully")
        return True

    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return False

if __name__ == "__main__":
    print("🌾 Creating simple crop recommendation database...")
    
    success = create_simple_database()
    
    if success:
        print("✅ Setup completed successfully!")
        print("📁 Database saved in 'simple_db' directory")
        print("🚀 You can now run: python app.py")
    else:
        print("❌ Failed to create database")