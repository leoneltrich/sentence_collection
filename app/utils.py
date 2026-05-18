import string

def normalize_sentence(text):
    """
    Normalizes a sentence:
    - Lowercase all characters
    - Remove all punctuation including commas
    """
    if not text:
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    
    # Remove line breaks and extra whitespace
    # .split() handles all whitespace including \n, \r, \t
    text = " ".join(text.split())
    
    return text.strip()
