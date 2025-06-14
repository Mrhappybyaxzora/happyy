def queryModifier(query: str) -> str:

    new_query = query.lower().strip()
    query_words = new_query.split()
    
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom","can you","what's","where's","how's"]
    
    if any(word + " " in new_query for word in question_words):

        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"

        else:
            new_query += "?"

    else:

        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."

        else:
            new_query += "."

    return new_query.capitalize()