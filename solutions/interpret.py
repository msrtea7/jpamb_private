#!/usr/bin/env python3
""" The skeleton for writing an interpreter given the bytecode.
"""

from dataclasses import dataclass
import sys, logging
from typing import Optional

from jpamb_utils import InputParser, IntValue, MethodId

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




if __name__ == "__main__":
    methodid = MethodId.parse(sys.argv[1])
    inputs = InputParser.parse(sys.argv[2])
    m = methodid.load()
    i = SimpleInterpreter(m["code"]["bytecode"], [i.tolocal() for i in inputs], [])
    print(i.interpet())
