# =============================================================================
# author:       Dhruv Raj Bangad (bangaddj@mail.uc.edu)
# purpose:      To parse any synthesized verilog file to get 
#               outputs, inputs, nodes, etc.
# usage:        from trojanparser import TrojanParser
# =============================================================================

# import networkx as nx
# import matplotlib.pyplot as plt
import os
import sys
import re
# from readbench import ReadBench

# FUNCTION: searched for a pattern in the given string
def checkPattern(pattern_list, str_list):
    for pattern in pattern_list:
        for str in str_list:
            if pattern in str:
                return str
    return ''

class TrojanParser:
    def __init__(self, file_name):
        self.trojan_inputs = []
        self.trojan_outputs = []
        self.trojan_wires = []
        self.trojan_nodes = []
        self.trojan_register = []
        self.temp_inputs = []
        self.temp_outputs = []
        self.temp_wires = []
        self.temp_nodes = []
        self.trojan_clock = ''
        self.trojan_reset = ''
        self.clock_search_text = ['clk', 'CLK', 'clock', 'CLOCK', 'Clock']
        self.reset_search_text = ['reset', 'RESET', 'Reset']
        if not os.path.isfile(file_name):
            print("Error: {} doesn't exist".format(file_name))
            sys.exit() 

        # editing names and getting trojan's circuit components
        fp = open(file_name, "r+")
        data = fp.read()   

        self.trojan_nodes = []
        data_replace = []
        
        # getting all the inputs        
        input_start_index = data.find("input ", data.find("module "))
        input_end_index = data.find(";", input_start_index)
        self.temp_inputs = data[input_start_index+6: input_end_index].replace(" ","").replace("\n","").replace("\t", "").split(',')
        # adding '_trojan' to each node's name
        for node_name in self.temp_inputs:
            self.trojan_inputs.append(node_name+'_trj')

        
        # checking for clock in inputs
        self.trojan_clock = checkPattern(self.clock_search_text, self.trojan_inputs)
        self.trojan_reset = checkPattern(self.reset_search_text, self.trojan_inputs)

        

        # getting all the outputs
        output_start_index = data.find("output ", data.find("module "))
        output_end_index = data.find(";", output_start_index)
        self.temp_outputs = data[output_start_index+7: output_end_index].replace(" ", "").replace("\n", "").replace("\t", "").split(',')
        # adding '_trojan' to each node's name
        for node_name in self.temp_outputs:
            self.trojan_outputs.append(node_name+'_trj')

        # getting all the wires
        wire_start_index = data.find("wire ", data.find("module "))
        wire_end_index = data.find(";", wire_start_index)
        self.temp_wires = data[wire_start_index+5: wire_end_index].replace(" ", "").replace("\n", "").replace("\t", "").split(',')
        # adding '_trojan' to each node's name
        for node_name in self.temp_wires:
            self.trojan_wires.append(node_name+'_trj')

        # keep in mind the order of storing the inputs, outputs, and wires
        # should be same for for the lists
        # new names                
        self.trojan_nodes = self.trojan_inputs + self.trojan_outputs + self.trojan_wires
        # old names        
        data_replace = self.temp_inputs + self.temp_outputs + self.temp_wires
        self.temp_nodes = data_replace
        
        # now searching for these elements and replacing them with 
        # the values in data_replace 
        for i in range(len(data_replace)):
            data = data.replace(data_replace[i], self.trojan_nodes[i])

        semi_index = data.find(";", data.find(self.trojan_nodes[len(self.trojan_nodes)-1], data.find("module ")))
        endmod_index = data.find("endmodule", semi_index)
        self.trojan_register = data[semi_index+1:endmod_index-1].replace(" ", "").replace("\n", "").replace("\t", "").split(';')
        self.trojan_register.pop()

        # writing to the file
        # gets cursor to start of file        
        # fp.seek(0)
        # fp.write(data)
        # fp.truncate()
        # fp.close()

        semi_index = data.find(";", data.find(self.trojan_nodes[len(self.trojan_nodes)-1], data.find("module ")))
        endmod_index = data.find("endmodule", semi_index)
        self.trojan_register = data[semi_index+1:endmod_index-1].replace(" ", "").replace("\n", "").replace("\t", "").split(';')
        self.trojan_register.pop()



      
    def getTrojanRegisters(self):
        return self.trojan_register
    
    def getTrojanInputs(self):
        return self.trojan_inputs
            
    def getTrojanOutputs(self):
        return self.trojan_outputs
    
    def getTrojanWires(self):
        return self.trojan_wires
    
    def getTrojanNodes(self):
        return self.trojan_nodes  

    def getTrojanClock(self):
        return self.trojan_clock

    def getTrojanReset(self):
        return self.trojan_reset
    
    def getCircuitInputs(self):
        return self.temp_inputs
    
    def getCircuitOutputs(self):
        return self.temp_outputs
    
    def getCircuitWires(self):
        return self.temp_wires
    
    def getCircuitNodes(self):
        return self.temp_nodes
        
