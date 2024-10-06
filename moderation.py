import re

# Список запрещенных слов (можно расширить)
BAD_WORDS = ['плохое_слово1', 'плохое_слово2', '...']

def moderate_text(text):
    pattern = re.compile('|'.join(BAD_WORDS), re.IGNORECASE)
    return bool(pattern.search(text))
