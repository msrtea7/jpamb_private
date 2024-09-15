#!/usr/bin/env python3

import os
import sys
import logging
import re
from pathlib import Path
import tree_sitter
import tree_sitter_java

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
l = logging.getLogger(__name__)

# Global constants
TYPE_LOOKUP = {
    "Z": "boolean",
    "I": "int",
    "J": "long",
    "F": "float",
    "D": "double",
    "B": "byte",
    "C": "char",
    "S": "short",
}

# Initialize Tree-sitter parser
JAVA_LANGUAGE = tree_sitter.Language(tree_sitter_java.language())
parser = tree_sitter.Parser(JAVA_LANGUAGE)

# Function to parse the method name
def parse_method_name(method_name):
    RE = r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)"
    match = re.match(RE, method_name)
    if not match:
        l.error("Invalid method name: %r", method_name)
        sys.exit(-1)
    return match.groupdict()

# Load and parse the source file
def parse_source_file(class_name):
    srcfile = (Path("src/main/java") / class_name.replace(".", "/")).with_suffix(".java")
    with open(srcfile, "rb") as f:
        l.debug("Parsing sourcefile %s", srcfile)
        return parser.parse(f.read()), srcfile

# Find the class in the source file
def find_class(tree, class_name):
    simple_classname = class_name.split(".")[-1]
    class_query = JAVA_LANGUAGE.query(f"""
        (class_declaration 
            name: ((identifier) @class-name 
                   (#eq? @class-name "{simple_classname}"))) @class
    """)
    class_nodes = class_query.captures(tree.root_node)
    if not class_nodes:
        l.error(f"Could not find class {simple_classname}")
        sys.exit(-1)
    for capture in class_nodes.items():
        if capture[0] == "class":
            l.debug("Found class %s", capture[0])
            return capture
    l.error(f"Could not find class {simple_classname}")
    sys.exit(-1)

# Find the method in the class
def find_method(class_node, method_name, params):
    method_query = JAVA_LANGUAGE.query(f"""
        (method_declaration name: 
          ((identifier) @method-name (#eq? @method-name "{method_name}"))) @method
    """)
    method_nodes = method_query.captures(class_node[1][0])
    for capture in method_nodes.items():
        if capture[0] == "method":
            node = capture[1][0]
            if check_method_parameters(node, params):
                l.debug("Found method %s %s", method_name, node.range)
                return node
    l.warning(f"Could not find method {method_name}")
    sys.exit(-1)

# Check if the method parameters match
def check_method_parameters(method_node, param_types):
    params_node = method_node.child_by_field_name("parameters")
    params = [c for c in params_node.children if c.type == "formal_parameter"] if params_node else []
    return len(params) == len(param_types) and all(
        (tp := t.child_by_field_name("type")) is not None
        and tp.text is not None
        and TYPE_LOOKUP.get(tn, tn) == tp.text.decode()
        for tn, t in zip(param_types, params)
    )

# Extract text from a node or return the text if it's already a string
def extract_text(node_or_text, source_code):
    if isinstance(node_or_text, str):
        return node_or_text
    elif isinstance(node_or_text, tree_sitter.Node):
        return source_code[node_or_text.start_byte:node_or_text.end_byte].decode().strip()
    else:
        l.warning(f"Unexpected type for node_or_text: {type(node_or_text)}")
        return str(node_or_text)