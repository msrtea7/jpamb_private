from parsing_utilities import *

# Analyze the risk of dividing by zero
def analyse_zero_div_risk(divide_nodes):
    risk_score = 10
    explicit_div_query = JAVA_LANGUAGE.query("""
(
  (binary_expression 
    left: (_) 
    operator: "/" 
    right: (decimal_integer_literal) @zero
  )
  (#eq? @zero "0")
)
""")

    for capture in divide_nodes.items():
        explicit_div_nodes = explicit_div_query.captures(capture[1][0])
        if explicit_div_nodes:
            risk_score = 70
            return risk_score
    return risk_score