#!/usr/bin/env python3

import os
import sys
import logging
import re
from parsing_utilities import *
from assertions import *
from infinite_loop import *
from null_pointer import *
from out_bounds import *
from zero_div import *
from recursion import *

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
l = logging.getLogger(__name__)

# Analyze the complexity and risks of the method body
def analyze_method_body(body_node, source_code):
    body_text = extract_text(body_node, source_code)
    
    # Initialize probabilities
    probs = {
        "assertion error": 5,
        "ok": 70,
        "*": 5,
        "divide by zero": 5,
        "out of bounds": 5,
        "null pointer": 10
    }
    
    # Analyze assertions
    assert_query = JAVA_LANGUAGE.query("""(assert_statement) @assert""")
    assert_nodes = assert_query.captures(body_node)
    if assert_nodes:
        assertion_risk = analyze_assertion_risk(assert_nodes, source_code)
        probs["assertion error"] += assertion_risk
        probs["ok"] -= assertion_risk
    
    # Analyze array operations
    array_query = JAVA_LANGUAGE.query("""
        (array_access) @array_access
        (array_creation_expression) @array_creation
    """)
    array_nodes = array_query.captures(body_node)
    if array_nodes:
        array_risk = analyze_array_risk(array_nodes, source_code)
        probs["out of bounds"] += array_risk
        probs["ok"] -= array_risk
    
    # Analyze null checks
    null_query = JAVA_LANGUAGE.query("""
        (null_literal) @null
    """)
    null_nodes = null_query.captures(body_node)
    if null_nodes:
        null_risk = analyze_null_risk(null_nodes, source_code)
        probs["null pointer"] += null_risk
        probs["ok"] -= null_risk

    # Analyze divisions by zero
    division_query = JAVA_LANGUAGE.query("""
    (
    (binary_expression 
        left: (_) 
        operator: "/" 
        right: (_)
    )@expr
    )
    """)
    division_nodes = division_query.captures(body_node)
    if division_nodes:
        division_risk = analyse_zero_div_risk(division_nodes)
        probs["divide by zero"] += division_risk
        probs["ok"] -= division_risk

    # Analyze infinite loops
    infinite_loop_risk = analyze_infinite_loop_risk(body_node, source_code)
    probs["*"] += infinite_loop_risk
    probs["ok"] -= infinite_loop_risk
    
    # Analyze recursive calls
    recursive_risk = analyze_recursive_risk(body_node, source_code)
    probs["*"] += recursive_risk
    probs["ok"] -= recursive_risk
    
    # Ensure all probabilities are within [0, 100] and sum to 100
    probs = {k: max(0, min(v, 100)) for k, v in probs.items()}
    total = sum(probs.values())
    probs = {k: round(v / total * 100, 2) for k, v in probs.items()}
    
    return probs

# Main logic for handling the method and analysis
def main(method_name):
    i = parse_method_name(method_name)
    tree, srcfile = parse_source_file(i["class_name"])

    class_node = find_class(tree, i["class_name"])
    method_node = find_method(class_node, i["method_name"], i["params"])

    body = method_node.child_by_field_name("body")
    if not body or not body.text:
        l.debug(f"No body found for method {i['method_name']}")
        print("ok;100%")
        sys.exit(0)

    # Read the source code for text extraction
    with open(srcfile, "rb") as f:
        source_code = f.read()

    # Analyze the method body
    probabilities = analyze_method_body(body, source_code)

    # Print the results
    for outcome, probability in probabilities.items():
        print(f"{outcome};{probability}%")

# Entry point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        l.error("Please provide a method name.")
        sys.exit(-1)
    main(sys.argv[1])