from parsing_utilities import extract_text, re

# Analyze the risk of array out of bounds and null pointer exceptions
def analyze_array_risk(array_nodes, source_code):
    risk_score = 0
    for capture in array_nodes.items():
        array_text = extract_text(capture[1][0], source_code)
        if capture[0] == "array_access":
            if not re.search(r'if.*<.*length', array_text):
                risk_score += 15
        elif capture[0] == "array_creation_expression":
            if "null" in array_text:
                risk_score += 20
    return min(risk_score, 90)  # Cap at 60%