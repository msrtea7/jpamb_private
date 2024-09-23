file_path = './stats/cases.txt'

### Acticity 1 start

# read the content
try:
    with open(file_path, 'r') as file:
        content = file.read() # Read whole content
        content = content.replace(' ','')
        lines = content.split("\n") # line str array
except FileNotFoundError:
    content = "File not found."
except Exception as e:
    content = f"An error occurred: {str(e)}"

import re
RE = r"(.+)\.(.+):\((.*)\)(.)\((.*)\)->(.*)"

# matches(typ e-> list): a (Cmethod path, method name, param type, return type, possi_param, possi_reeor)
# example:
# ('jpamb.cases.Simple', 'assertPositive', 'I', 'V', '-1', 'assertionerror')
# ('jpamb.cases.Simple', 'assertPositive', 'I', 'V', '1', 'ok')
matches = re.findall(RE, content, re.MULTILINE) # read all of cases.txt
# m = re.match(RE,content) # read one line's info only
# print(m["class_name"])

### activity 1 end

### activity 2 start
from pathlib import Path

def raw_text_regex(line:list):
    srcfile = (Path("src/main/java") / line[0].replace(".", "/")).with_suffix(".java")
    # open .java file, read the raw content
    try:
        with open(srcfile, 'r') as file:
            file_content = file.read() # Read whole content
    except FileNotFoundError:
        file_content = "File not found."
    except Exception as e:
        file_content = f"An error occurred: {str(e)}"
    print(file_content)

raw_text_regex(matches[0])

# failed regexs
# /public\W+static\W+(?P<retype>void)\W+(?P<mname>\w*)\((?P<param>.*)\)\W*/gm
# public\s+static\s+(?:\w+\s+)?\w+\s*\([\w\s,]*\)\s*\{([\s\S]*?)\}
# public\s+static\s+(?:\w+\s+)?\w+\s*\([^\)]*\)\s*\{([\s\S]*?)\}
# \s*\{([\s\S]*?)\}

## activity 2 ends

# # A fucking bug with ndarray
# import numpy as np
# matches_array = np.array(matches) # make it a array, in convenience of following operations
# scrfile_array = matches_array.copy()
# scrfile_array.astype(str)
# # coule be optimized by lambda expression
# for i, classpath in enumerate(scrfile_array[:, [0]]):
#     st = classpath[0].replace(".", "/")
#     str = "src/main/java" + st + ".java"
#     scrfile_array[i, [0]] = str
#     print(scrfile_array[i,[0]])
# # end bug



