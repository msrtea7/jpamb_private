from parsing_utilities import extract_text, re, JAVA_LANGUAGE

def analyze_recursive_risk(body_node, source_code):
    method_name = body_node.parent.child_by_field_name("name").text.decode()
    recursive_query = JAVA_LANGUAGE.query(f"""
        (method_invocation
            name: (_) @name
            (#eq? @name "{method_name}")
        ) @recursive_call
    """)
    recursive_calls = recursive_query.captures(body_node)
    
    risk_score = 0
    if recursive_calls:
        risk_score += 20  # Base risk for having recursive calls
        
        # Check for base case
        if_query = JAVA_LANGUAGE.query("""
            (if_statement) @if
        """)
        if_statements = if_query.captures(body_node)
        
        has_base_case = False
        for if_stmt in if_statements:
            if_text = extract_text(if_stmt[1], source_code)
            if re.search(r'return', if_text):
                has_base_case = True
                break
        
        if not has_base_case:
            risk_score += 30  # Higher risk if no clear base case is found
    
    return min(risk_score, 90)  # Cap at 60%