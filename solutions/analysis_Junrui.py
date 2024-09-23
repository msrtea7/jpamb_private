#!/usr/bin/env python3
"""A very stupid syntatic analysis, that only checks for assertion errors."""

import os
import sys, logging

l = logging
l.basicConfig(level=logging.DEBUG)

(name,) = sys.argv[1:]

import re
from pathlib import Path

# Read the method_name
RE = r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)"
if not (i := re.match(RE, name)):
    l.error("invalid method name: %r", name)
    sys.exit(-1)

TYPE_LOOKUP = {
    "Z": "boolean",
    "I": "int",
}


srcfile = (Path("src/main/java") / i["class_name"].replace(".", "/")).with_suffix(
    ".java"
)

import tree_sitter
import tree_sitter_java

JAVA_LANGUAGE = tree_sitter.Language(tree_sitter_java.language())
parser = tree_sitter.Parser(JAVA_LANGUAGE)

# run
with open(srcfile, "rb") as f:
    l.debug("parse sourcefile %s", srcfile)
    tree = parser.parse(f.read())

simple_classname = i["class_name"].split(".")[-1]

# To figure out how to write these you can consult the
# https://tree-sitter.github.io/tree-sitter/playground
class_q = JAVA_LANGUAGE.query(
    f"""
    (class_declaration 
        name: ((identifier) @class-name 
               (#eq? @class-name "{simple_classname}"))) @class
"""
)

for node in class_q.captures(tree.root_node)["class"]:
    break
else:
    l.error(f"could not find a class of name {simple_classname} in {srcfile}")
    sys.exit(-1)

l.debug("Found class %s", node.range)

method_name = i["method_name"]

method_q = JAVA_LANGUAGE.query(
    f"""
    (method_declaration name: 
      ((identifier) @method-name (#eq? @method-name "{method_name}"))
    ) @method
"""
)

for node in method_q.captures(node)["method"]:
    if not (p := node.child_by_field_name("parameters")):
        l.debug(f"Could not find parameteres of {method_name}")
        continue

    params = [c for c in p.children if c.type == "formal_parameter"]

    if len(params) == len(i["params"]) and all(
        (tp := t.child_by_field_name("type")) is not None
        and tp.text is not None
        and TYPE_LOOKUP[tn] == tp.text.decode()
        for tn, t in zip(i["params"], params)
    ):
        break
else:
    l.warning(f"could not find a method of name {method_name} in {simple_classname}")
    sys.exit(-1)

l.debug("Found method %s %s", method_name, node.range)

body = node.child_by_field_name("body")
assert body and body.text
for t in body.text.splitlines():
    l.debug("line: %s", t.decode())


## My query start

print("My query start")
divide_0 = JAVA_LANGUAGE.query(f"""(
  (
    (binary_expression
        operator: "/"
    )
)
)@divide_0
""")

# This works in https://tree-sitter.github.io/tree-sitter/playground,  but I don't know how to extract it from the body

# (
#     (binary_expression
#         operator: "/"
#         left: ([(identifier) (decimal_integer_literal)])
#         right: ([(identifier) (decimal_integer_literal)])
#     )q
# )

print(type(divide_0))

# print(assert_divide_0.captures(body).items())
captures = divide_0.captures(tree.root_node)['divide_0']

for capture in captures:
    print(capture)


print("My query ends")

sys.exit(0)

## My query end


assert_q = JAVA_LANGUAGE.query(f"""(assert_statement) @assert""")


for node, t in assert_q.captures(body).items():
    if t == "assert":
        break
else:
    l.debug("Did not find any assertions")
    print("assertion error;20%")
    sys.exit(0)

l.debug("Found assertion")
print("assertion error;80%")
sys.exit(0)
