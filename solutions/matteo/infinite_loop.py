from parsing_utilities import extract_text, re, JAVA_LANGUAGE

def analyze_infinite_loop_risk(body_node, source_code):
    loop_query = JAVA_LANGUAGE.query("""
        (while_statement) @while
        (for_statement) @for
        (do_statement) @do
    """)
    loop_nodes = loop_query.captures(body_node)
    
    risk_score = 0
    
    for key, capture in loop_nodes.items():
        loop_text = extract_text(capture[0], source_code)
        
        # Check for loops without clear exit conditions
        if key == "while":
            if re.search(r'while\s*\(\s*true\s*\)', loop_text):
                risk_score += 30
            elif not re.search(r'break', loop_text) and not re.search(r'return', loop_text):
                risk_score += 15
        
        elif key == "for":
            if not re.search(r'break', loop_text) and not re.search(r'return', loop_text):
                if not re.search(r'<|>|<=|>=', loop_text):  # No clear termination condition
                    risk_score += 20
                else:
                    risk_score += 10
        
        elif key == "do":
            if not re.search(r'break', loop_text) and not re.search(r'return', loop_text):
                risk_score += 15
        
        # Check for loops with suspicious increment/decrement patterns
        if re.search(r'(i\+\+|i\-\-|i\s*=\s*i\s*[\+\-]\s*1)', loop_text):
            if not re.search(r'i\s*[<>]=?\s*\w+', loop_text):  # No comparison with a variable
                risk_score += 10
    
    return min(risk_score, 50)  # Cap at 50%