# =============================================================================
# author:       Dhruv Raj Bangad (bangaddj@mail.uc.edu)
# purpose:      To insert the trojan into a circuit
# usage:        python3 trojaninsert.py <circuit_filepath> <trojan_filepath>
# =============================================================================



import os, sys, re, random, pandas as pd
from trojanparser import TrojanParser
from trojanprobability import getTrojanProbability

'''----------------------prereq functions----------------------'''

# FUNCTION: to choose the payloads for us
# it may or may not have any parameters
# this is a dummy version
def selectPayloads(circuit_outputs, trojan_outputs):
    num_trj_outputs = len(trojan_outputs)
    num_cir_outputs = len(circuit_outputs)

    # choosing random outputs nodes
    # https://stackoverflow.com/questions/22842289/generate-n-unique-random-numbers-within-a-range
    if num_cir_outputs >= num_trj_outputs:
        payload_indices = random.sample(range(num_cir_outputs), num_trj_outputs)

    # getting a sublist
    # https://stackoverflow.com/questions/22412509/getting-a-sublist-of-a-python-list-with-the-given-indices
    return [circuit_outputs[index] for index in payload_indices]

# FUNCTION: return trigger nodes on basis of the choosen algorithm
# def selectTriggerNodes(sensitivity_file, trojan_inputs):
#     trigger_nodes = []
#     num_nodes  = len(trojan_inputs)
#     fp = open(sensitivity_file, 'r+')
#     for line in fp.readlines():
#         trigger_nodes.append(line.replace(" ","").replace("\n","").replace("\t", ""))
#     return trigger_nodes




# FUNCTION: searched for a pattern in the given string
def checkPattern(pattern_list, str_list):
    for pattern in pattern_list:
        for str in str_list:
            if pattern in str:
                return str
    return ''

'''----------------------code to get the initial values----------------------'''

circuit_fp = sys.argv[1]
trojan_fp = sys.argv[2]
 
circuit_fp = 'inserted_trojan.v'
trojan_fp = 'test_assertion.v'
sensitivity_fp = 'sensitivity.txt'
# output_fp = 'inserted_trojan.v'
os.system('cat s298.v > inserted_trojan.v')

# getting all the trojan circuit components
trojan_parser_obj = TrojanParser(trojan_fp)
trojan_inputs = trojan_parser_obj.getTrojanInputs()
trojan_outputs = trojan_parser_obj.getTrojanOutputs()
trojan_nodes = trojan_parser_obj.getTrojanNodes()
trojan_registers = trojan_parser_obj.getTrojanRegisters()
trojan_clock = trojan_parser_obj.getTrojanClock()
trojan_reset = trojan_parser_obj.getTrojanReset()
trojan_inputs.remove(trojan_clock) # removing clock from inputs
trojan_inputs.remove(trojan_reset) # removing reset from inputs

# getting the main circuit components
circuit_parser_obj = TrojanParser(circuit_fp)
circuit_inputs = circuit_parser_obj.getCircuitInputs()
circuit_outputs = circuit_parser_obj.getCircuitOutputs()
circuit_clock = ''
circuit_reset = ''

clock_search_text = ['clk', 'CLK', 'clock', 'CLOCK', 'Clock']
reset_search_text = ['reset', 'RESET', 'Reset']
# getting circuit clock & reset from inputs
circuit_clock = checkPattern(clock_search_text, circuit_inputs)
circuit_reset = checkPattern(reset_search_text, circuit_inputs)


# getting the payloads and 
# adding a 'prev' to the payload outputs
payloads = selectPayloads(circuit_outputs, trojan_outputs)
payload_prev = []
for nodes in payloads:
    payload_prev.append(nodes+'_prev')

# getting the clock, reset, and trigger nodes additions
to_add_clock = '\n assign ' + trojan_clock + ' = ' + circuit_clock + ';'
to_add_reset = '\n assign ' + trojan_reset + ' = ' + circuit_reset + ';'
to_add_trigger = ''

trigger_nodes = selectTriggerNodes(sensitivity_fp, trojan_inputs)
trigger_logic = []
for i in range(len(trojan_inputs)):
    trigger_logic.append('assign ' + str(trojan_inputs[i]) + ' = ' + str(trigger_nodes[i]))

to_add_trigger = '\n' + ';\n'.join(trigger_logic) + ';\n'




'''----------------------code to insert the trojan----------------------'''

# inserting trojan nodes & modified prev nodes as wire in circuit
fp = open(circuit_fp, "r+")
data = fp.read()
if data.count("endmodule") > 1:
    index = data.find('wire', data.find('endmodule'))
else:
    # to make sure that the wire word chosen is part of the code and not just a comment
    index = data.find('wire', data.find('module'))

to_add_nodes = '\nwire ' + ', '.join(trojan_nodes) + ';'
to_add_prev = '\nwire ' + ', '.join(payload_prev) + ';\n'
    
data = data[:index] + to_add_nodes + to_add_prev + data[index:]
fp.seek(0)
fp.write(data)
fp.truncate()
fp.close()

# replacing the payloads with the prev nodes, payload XOR additions, &
# inserting trojan registers with circuit registers
fp = open(circuit_fp, "r+")
data = fp.read()

temp = data.find('wire', data.find('module'))
wire_index = temp
while True:
    wire_index = temp
    temp = data.find('wire ', wire_index+1)
    if temp == -1:
        break

# now we have the last wire
# finding the last semicolon
semi_index = data.find(';', wire_index)

# replacing with prev nodes
temp = data[semi_index+1:]
for i in range(len(payload_prev)):
    temp = temp.replace(payloads[i], payload_prev[i])

# adding xor for payloads in the end
payload_insertion_logic = []
for i in range(len(payloads)):
    payload_insertion_logic.append("XOR2X1 trojan_payload"+str(i)+" (.A (" + str(trojan_outputs[i])+"), .B("+str(payload_prev[i])+"), .Y("+str(payloads[i])+"))")

to_add_payload = '\n' + ';\n'.join(payload_insertion_logic) + ';\n'

# registers to be added
to_add_reg = '\n' + ';\n'.join(trojan_registers) + ';\n'
data = data[:semi_index+1]+ to_add_clock + to_add_reset + to_add_trigger + to_add_reg + to_add_payload + temp

fp.seek(0)
fp.write(data)
fp.truncate()
fp.close()




# identifying clk and reset



# function to choose the trigger nodes
def getTrigNodes(filename, num_nodes):
    prob_df = getTrojanProbability(filename)
    trigger_nodes_list = []

    # asking user what he wants
    print('Choose the parameter on which you want to select the trigger nodes:')
    print('[1] P(low)')
    print('[2] P(high)')
    print('[3] Scope Value - √(cc0^2 + cc1^2 + c0^2)')
    
    choice = 0
    while True:
        choice = int(input('Choose an option:'))
        if choice == 1:
            sort_param = 'p_low'
            break
        elif choice == 2:
            sort_param = 'p_high'
            break
        elif choice == 3:
            sort_param = 'scope_testability'
            break
        else:
            print('Invalid choice. Try again.')


    rndm = input('Do you want some % nodes to be selected randomly? (y/n):')
    num_rndm = 0
    if rndm == 'y' or rndm == 'Y':
        num_rndm = int(input('Enter the percentage (without the % sign): '))
    
    num_rndm = int(num_rndm * num_nodes / 100)
    num_not_rndm = num_nodes - num_rndm

    # getting list of nodes sorted by choosen parameter
    sorted_node_names = prob_df.sort_values(by=[sort_param])['node_name'].tolist()
    # TODO: ask nikhil bh. about this step
    nodes_to_avoid = clock_search_text + reset_search_text + circuit_outputs
    for node in sorted_node_names:
        if node not in nodes_to_avoid and len(trigger_nodes) <= num_not_rndm:
            trigger_nodes.append(node)

    # adding the random nodes
    nodes_to_avoid += trigger_nodes
    random.shuffle(sorted_node_names) # shuffling the node names
    for node in sorted_node_names:
        if node not in nodes_to_avoid and len(trigger_nodes) <= num_nodes:
            trigger_nodes.append(node)

    return trigger_nodes


    











