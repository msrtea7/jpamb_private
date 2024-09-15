from parsing_utilities import extract_text, re
# Analyze the risk of assertion errors
def analyze_assertion_risk(assert_nodes, source_code):
    risk_score = 0
    for capture in assert_nodes:
        assert_text = extract_text(capture[1], source_code)
        if "array.length" in assert_text:
            risk_score += 10
        elif re.search(r'assert\s+false', assert_text):
            risk_score += 20
        elif re.search(r'assert.*==', assert_text):  # Check for equality assertions
            risk_score += 25
        elif re.search(r'assert.*>', assert_text):  # Check for inequality assertions
            risk_score += 15
        else:
            risk_score += 15
    return min(risk_score, 70)  # Cap at 70%