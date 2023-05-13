# SVC Parser - Synthesized Verilog Circuit
import re

# FUNCTION: searched for a pattern in the given string
def checkPattern(pattern_list, str_list):
    for pattern in pattern_list:
        for str in str_list:
            if pattern in str:
                return str
    return None

class CircuitParser:
    def __init__(self, filename):
        self.module_name = ''
        self.module_line = ''
        self.inputs = []
        self.outputs = []
        self.wires = []
        self.registers = []
        self.clock = ''
        self.reset = ''

        # Define regular expressions to match module name, inputs, outputs, wires, and registers
        # for explaination: https://regex101.com/r/0CXHON/1
        module_re = r"(^([^\/\/].*)?^\s*module\s+(\w+)\s*\(((\s*.*\w+,*\s*)+\s*)\);)"
        input_re = r"^([^\/\/].*)?^\s*(input\s*((\s*.*\w+,*\s*)+\s*);)"
        output_re = r"^([^\/\/].*)?^\s*(output\s*((\s*.*\w+,*\s*)+\s*);)"
        wire_re = r"^([^\/\/].*)?^\s*(wire\s*((\s*.*\w+,*\s*)+\s*);)"
        register_re = r"^([^\/\/].*)?^\s*((\w+)\s+(.+)\s*(\((\s*.\w+\s*\(\s*.+\s*\),*\s*)+\s*\)));"
     
        file = open(filename, 'r').read()

        # Find the module name
        matches = re.finditer(module_re, file, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            self.module_name = match.group(3)
            self.module_line = match.group(1)
            print("Module name:", self.module_name)
            print(self.module_line)

        # Find the inputs
        matches = re.finditer(input_re, file, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            self.inputs.append((re.sub(r'\s+', '', match.group(3)).split(",")))
        print("Inputs:", self.inputs)

        # Finding clock and reset in inputs
        clock_search_text = ['clk', 'CLK', 'clock', 'CLOCK', 'Clock']
        reset_search_text = ['reset', 'RESET', 'Reset']

        # checking for clock & reset in inputs
        for input_list in self.inputs:
            self.clock = checkPattern(clock_search_text, input_list)
            self.reset = checkPattern(reset_search_text, input_list)
            if self.clock and self.reset:
                print(f'CLOCK: {self.clock} \nRESET: {self.reset}')                
                break        

        # Find the outputs
        matches = re.finditer(output_re, file, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            self.outputs.append((re.sub(r'\s+', '', match.group(3)).split(",")))
        print("outputs:", self.outputs)

        # Find the wires
        matches = re.finditer(wire_re, file, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            self.wires.append((re.sub(r'\s+', '', match.group(3)).split(",")))
        print("wires:", self.wires)

        # Find the registers
        matches = re.finditer(register_re, file, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            register_type = match.group(3)
            register_name = match.group(4)
            register_args = re.sub(r'\s+', '', match.group(5))
            self.registers.append((register_type, register_name, register_args))
        print("Registers:", self.registers)

    def getModuleName(self):
        return self.module_name

    def getModuleLine(self):
        return self.module_line

    def getInputs(self):
        return self.inputs

    def getOutputs(self):
        return self.outputs
    
    def getWires(self):
        return self.wires

    def getRegisters(self):
        return self.registers

    def getClockAndReset(self):
        return self.clock, self.reset

    def setModuleName(self, module_name):
        self.module_name = module_name

    def setModuleLine(self, module_line):
        self.module_line = module_line

    def setInputs(self, inputs):
        self.inputs = inputs

    def setOutputs(self, outputs):
        self.outputs = outputs

    def setWires(self, wires):
        self.wires = wires

    def setRegisters(self, registers):
        self.registers = registers

    def setClockAndReset(self, clock, reset):
        self.clock = clock
        self.reset = reset

    # TODO: implement this function
    def makeCircuit(self):
        data = ''
        # add module name
        #data += 'module {name}({inouts});\n'.format(name = self.module_name, inouts = ', '.join(self.inputs+self.outputs))
        print(self.module_line)
        data += self.module_line + '\n'

        # add inputs
        for input_list in self.inputs:
            data += '\tinput {inp};\n'.format(inp = ', '.join(input_list))

        # add outputs
        for output_list in self.outputs:
            data += '\toutput {outp};\n'.format(outp = ', '.join(output_list))

        # add wires
        for wire_list in self.wires:
            data += '\twire {wi};\n'.format(wi = ', '.join(wire_list))

        # add registers
        for i,reg in enumerate(self.registers):
#            if reg[1] in self.wires:
#                new_name = reg[1]           
            if re.match(r'U\d+', reg[1]):
                new_name = f'U{i}'
            elif reg[1] == '':
                new_name = ''
            else:
                new_name = reg[1]
            data += f'\t{reg[0]} {new_name} {reg[2]};\n'

        # add endmodule
        data += '\nendmodule'

        result_filename = f'trjIN{self.module_name}.v'
        with open(result_filename, "w") as file:
            file.write(data)
