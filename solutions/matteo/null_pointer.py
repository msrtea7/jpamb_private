from parsing_utilities import extract_text, re

# Analyze the risk of null pointer exceptions
def analyze_null_risk(null_nodes, source_code):
    risk_score = 0
    for capture in null_nodes:
        null_text = extract_text(capture[1], source_code)
        if re.search(r'=\s*null', null_text):
            risk_score += 20
        if re.search(r'if\s*\(.*==\s*null\)', null_text):
            risk_score += 10
    return min(risk_score, 90)  # Cap at 60%