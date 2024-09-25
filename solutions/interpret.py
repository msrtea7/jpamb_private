#!/usr/bin/env python3
""" The skeleton for writing an interpreter given the bytecode.
"""

from dataclasses import dataclass
import sys, logging, random, string
from typing import Optional

from jpamb_utils import InputParser, IntValue, MethodId, CharValue, BoolValue, IntListValue, CharListValue

l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s")


@dataclass
class SimpleInterpreter:
    bytecode: list
    locals: list
    stack: list
    pc: int = 0
    done: Optional[str] = None

    def interpet(self, limit=10):
        for i in range(limit):
            next = self.bytecode[self.pc]
            l.debug(f"STEP {i}:")
            l.debug(f"  PC: {self.pc} {next}")
            l.debug(f"  LOCALS: {self.locals}")
            l.debug(f"  STACK: {self.stack}")

            if fn := getattr(self, "step_" + next["opr"], None):
                fn(next)
            else:
                return f"can't handle {next['opr']!r}"

            if self.done:
                break
        else:
            self.done = "out of time"

        l.debug(f"DONE {self.done}")
        l.debug(f"  LOCALS: {self.locals}")
        l.debug(f"  STACK: {self.stack}")

        return self.done

    def step_push(self, bc):
        val = bc["value"]["value"]
        if val is not None:
            if bc["value"]["type"] == "integer" or bc["type"] == "int" or bc["type"] == "integer":
                self.stack.insert(0, val)
                self.pc += 1
                return IntValue(bc["value"]["value"])
            raise ValueError(f"Currently unknown value {bc}")

       # self.stack.insert(0, val)
        self.pc += 1

    def step_return(self, bc):
        if bc["type"] is not None:
            self.stack.pop(0)
        self.done = "ok"

    def step_dup(self):
        if self.stack:
            self.stack.insert(0, self.stack[0])
        self.pc += 1

    def step_get(self, bc):
        field = bc.get('field', {})
        field_name = field.get('name')
        value = False if field_name == "$assertionsDisabled" else None
        self.stack.insert(0, value)
        self.pc += 1

    def step_ifz(self, bc):
        val = self.stack.pop(0)
        if val is not None:
            if val != 0:
                self.pc = bc["target"]
            else:
                self.pc += 1
        else: 
            self.pc += 1


    def step_new(self, bc):
        class_name = bc.get("class", {}).get("name")

        if class_name == "java/lang/AssertionError":
            new_object = {"class": "AssertionError"} 
            self.stack.insert(0, new_object)
        self.pc += 1

    def step_invoke(self, bc):
        method = bc["method"]
        if method["name"] == "<init>" and method["ref"]["name"] == "java/lang/AssertionError":
            self.stack.pop(0)
        self.pc += 1



    def step_throw(self, bc):
        thrown_exception = self.stack.pop(0)
        if thrown_exception["class"] == "AssertionError":
            self.done = "AssertionError thrown"


        self.pc += 1



##################################### RANDOM TESTER ####################################


def generate_random_input():
    JVM_TYPES = ["int", "boolean", "char","int[]", "char[]"]
    jvm_type = random.choice(JVM_TYPES)

    if jvm_type == "int":
        return IntValue(random.randint(0, 100000000000)) 
    

    if jvm_type ==  "char":
       return CharValue(random.choice(string.ascii_letters))
    
    if jvm_type == "boolean":
         return BoolValue(random.choice([True, False]))
    
    if jvm_type == "int[]":
        array_size = random.randint(1, 10)
        return IntListValue(tuple(random.randint(-100, 100) for _ in range(array_size))) 
 

    if jvm_type == "char[]":
        array_size = random.randint(1, 10)
        return CharListValue(tuple(random.choice(string.ascii_letters) for _ in range(array_size)))
   
    raise ValueError(f"Unsupported JVM type: {jvm_type}")

def run_random_tests(method_id_str, num_tests=10, depth_limit=10):
    methodid = MethodId.parse(method_id_str)
    m = methodid.load()

    for i in range(num_tests):
        random_input = generate_random_input()  # Example for int type input
        inputs = [random_input]

        interpreter = SimpleInterpreter(m["code"]["bytecode"], [input.tolocal() for input in inputs], [])

        print(f"Test {i + 1}: Input={inputs}")
        result = interpreter.interpet(limit=depth_limit)
        print(f"Result: {result}")

        if interpreter.done == "out of time":
            print("Test timed out.")
        elif "Exception" in result:
            print(f"Exception thrown: {result}")
        else:
            print(f"Execution finished normally: {result}")




if __name__ == "__main__":

    if len(sys.argv) > 2:
            methodid = MethodId.parse(sys.argv[1])
            inputs = InputParser.parse(sys.argv[2])
            m = methodid.load()
            i = SimpleInterpreter(m["code"]["bytecode"], [i.tolocal() for i in inputs], [])
            print(i.interpet())

    else:
        run_random_tests("jpamb.cases.Simple.justReturn:()I", num_tests=10, depth_limit=10)