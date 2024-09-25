#!/usr/bin/env python3
"""The skeleton for writing an interpreter given the bytecode."""

from dataclasses import dataclass
from pathlib import Path
import sys, logging
from types import new_class
from typing import Literal, TypeAlias, Optional

l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s")

JvmType: TypeAlias = Literal["boolean"] | Literal["int"]


@dataclass(frozen=True)
class MethodId:
    class_name: str
    method_name: str
    params: list[JvmType]
    return_type: Optional[JvmType]

    @classmethod
    def parse(cls, name):
        import re

        TYPE_LOOKUP: dict[str, JvmType] = {
            "Z": "boolean",
            "I": "int",
        }

        RE = (
            r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)"
        )
        if not (i := re.match(RE, name)):
            l.error("invalid method name: %r", name)
            sys.exit(-1)
        return cls(
            class_name=i["class_name"],
            method_name=i["method_name"],
            params=[TYPE_LOOKUP[p] for p in i["params"]],
            return_type=None if i["return"] == "V" else TYPE_LOOKUP[i["return"]],
        )

    # read the json file
    def classfile(self):
        return Path("decompiled", *self.class_name.split(".")).with_suffix(".json")

    def load(self):
        import json

        classfile = self.classfile()
        with open(classfile) as f:
            l.debug(f"read decompiled classfile {classfile}")
            classfile = json.load(f)
        for m in classfile["methods"]:
            if (
                m["name"] == self.method_name
                and len(self.params) == len(m["params"])
                and all(
                    p == t["type"]["base"] for p, t in zip(self.params, m["params"])
                )
            ):
                return m
        else:
            print("Could not find method")
            sys.exit(-1)

    def create_interpreter(self, inputs):
        method = self.load()
        return SimpleInterpreter(
            bytecode=method["code"]["bytecode"],
            locals=inputs,
            stack=[],
            pc=0,
        )


@dataclass
class SimpleInterpreter:
    bytecode: list
    locals: list
    stack: list
    pc: int
    done: Optional[str] = None

    def interpet(self, limit=10):
        for i in range(limit):
            next = self.bytecode[self.pc]
            l.debug(f"STEP {i}:")
            l.debug(f"  PC: {self.pc} {next}")
            l.debug(f"  LOCALS: {self.locals}")
            l.debug(f"  STACK: {self.stack}")

            # getattr(object, attribute, default), default: Optional. The value to return if the attribute does not exist
            # 也就是在这里调用了方法/属性  attribute
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

    # read through the code
    def step_get(self, bc):
        print("--- step_get content: ", bc, "---")
        # type -field- dict, field这里应该是nested dict
        field = bc.get("field", {})
        field_name = field.get("name")

        # like getting the $assertionsDisabled static field. You can assume that is always be false.
        if field_name == "$assertionsDisabled":
            value = False
        else:
            value = None

        self.stack.insert(0, value)
        self.pc += 1

    # 是否要在所有方法前检查 if not self.stack: raise RuntimeError("Stack underflow: No elements in the stack to throw.")
    def step_push(self, bc):
        print("--- step_push content: ", bc, "---")
        print("push value: ", bc["value"]["value"])
        self.stack.insert(0, bc["value"]["value"])
        self.pc += 1

    def step_return(self, bc):
        if bc["type"] is not None:
            self.stack.pop(0)
        self.done = "ok"

    def step_ifz(self, bc):
        value_to_compare = self.stack.pop(0)
        if value_to_compare != 0 or value_to_compare:
            self.pc = bc.get(
                "target"
            )  # go to the NOT(i-th), the field "target" is just the index of the PC target value in the bc
        else:
            # self.pc += bc.get("offset")
            self.pc += 1

    def step_load(self, bc):
        # here I assume get the last parameter
        data_to_be_load = self.locals[-1]
        if type(data_to_be_load).__name__ == bc.get("type"):
            self.stack.insert(0, data_to_be_load)
        else:
            print("!!!ERORRR, wrong type!!!")

        self.pc += 1

    def step_new(self, bc):
        # Object_name = bc.get("class").split("/")[-1]
        # new_object = {"class", Object_name}

        self.stack.insert(0, bc.get("class"))
        self.pc += 1

    def step_dup(self, bc):
        if self.stack:
            self.stack.insert(0, self.stack[0])

        self.pc += 1

    def step_throw(self, bc):
        # Pop the reference (exception object) from the stack
        # exception_ref = self.stack.pop()
        # 我这里只直接print这个error而不终止程序，因为这时候md没有error对象离谱
        print("!ERRRRRRRRRRRRRRRRRROR! This fraction of code bug is not fixed")
        self.pc += bc.get("offset")


if __name__ == "__main__":
    methodid = MethodId.parse(sys.argv[1])  # 在这里读了bytecode bc
    inputs = []
    result = sys.argv[2][
        1:-1
    ]  # 第二个参数，(balabala) 里面的部分,也就是传给方法的params
    if result != "":
        for i in result.split(","):
            if i == "true" or i == "false":
                inputs.append(i == "true")
            else:
                inputs.append(int(i))
    # print("inputes", inputs)
    print(methodid.create_interpreter(inputs).interpet())

    # python solutions/interpreter_Junrui.py "jpamb.cases.Simple.assertBoolean:(Z)V" "(false)"
