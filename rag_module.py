import json
import os
import logging
import re
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

SIMPLE_DB_DIR = "simple_db"

def load_database():
    """Load the simple keyword-based database"""
    try:
        database_path = os.path.join(SIMPLE_DB_DIR, "database.json")
        keywords_path = os.path.join(SIMPLE_DB_DIR, "keywords.json")
        
        if not os.path.exists(database_path) or not os.path.exists(keywords_path):
            raise FileNotFoundError("Database files not found. Please run prepare_data.py first.")
        
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
            
        with open(keywords_path, 'r', encoding='utf-8') as f:
            keywords_index = json.load(f)
        
        return database, keywords_index
        
    except Exception as e:
        logger.error(f"Error loading database: {str(e)}")
        return None, None

def get_context_from_query(query, k=2):  # Reduced from 3 to 2 documents
    """Retrieve relevant context using simple keyword matching with size limits"""
    try:
        if not query or not query.strip():
            return ""
        
        database, keywords_index = load_database()
        if not database or not keywords_index:
            return ""
        
        # Extract keywords from query
        query_words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        
        if not query_words:
            return ""
        
        # Score documents based on keyword matches
        doc_scores = Counter()
        
        for word in query_words:
            if word in keywords_index:
                for doc_id in keywords_index[word]:
                    doc_scores[doc_id] += 1
        
        # Get top k documents
        top_docs = doc_scores.most_common(k)
        
        if not top_docs:
            # Fallback: partial matching
            for word in query_words:
                for keyword in keywords_index:
                    if word in keyword or keyword in word:
                        for doc_id in keywords_index[keyword]:
                            doc_scores[doc_id] += 0.5
            
            top_docs = doc_scores.most_common(k)
        
        # Get document content with size limits
        context_parts = []
        total_length = 0
        max_context_length = 2000  # Limit total context size
        
        for doc_id, score in top_docs:
            if doc_id < len(database):
                doc_content = database[doc_id]['full_text']
                
                # Check if adding this document would exceed limit
                if total_length + len(doc_content) > max_context_length:
                    # Truncate the document to fit
                    remaining_space = max_context_length - total_length
                    if remaining_space > 100:  # Only add if we have meaningful space
                        truncated_content = doc_content[:remaining_space-3] + "..."
                        context_parts.append(truncated_content)
                    break
                
                context_parts.append(doc_content)
                total_length += len(doc_content)
        
        context = "\n\n".join(context_parts)
        
        logger.info(f"Retrieved {len(context_parts)} documents ({len(context)} chars) for query: {query}")
        return context
        
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        return ""