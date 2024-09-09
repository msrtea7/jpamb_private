from logging import DEBUG, debug, basicConfig

basicConfig(level=DEBUG)
debug("We now debug this shit")

import sys

method_id = sys.argv[1]

debug("method is %s", method_id)

print("devide by zero; 100%")
print("ok; 100%")
print("*; 20%")
print("assertion error; 50%")

# with open('src/main/java/' + class_.replace(".", "/") + '.java') as f:
#   txt = f.read()
#
# debug("file is %s", txt)
#
#
