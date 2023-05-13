# =============================================================================
# author:       Dhruv Raj Bangad (bangaddj@mail.uc.edu)
# purpose:      To insert the trojan into a circuit
# usage:        
# =============================================================================

import os, sys, re, random, pandas as pd
from svcparser import CircuitParser as cp
from trojanprobability import getTrojanProbability

'''----------------------prereq functions----------------------'''

# FUNCTION: to choose the trigger nodes
def getTrigNodes(filename, num_input_nodes):
    prob_df = getTrojanProbability(filename)
    trigger_nodes = []

    # asking user what he wants
    print('Choose the parameter on which you want to select the trigger nodes:')
    print('[1] P(low)')
    print('[2] P(high)')
    print('[3] Scope Value - \u221a(cc0^2 + cc1^2 + c0^2)')
    
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
    
    num_rndm = int(num_rndm * num_input_nodes / 100)
    num_not_rndm = num_input_nodes - num_rndm

    # getting list of nodes sorted by choosen parameter
    sorted_node_names = prob_df.sort_values(by=[sort_param])['node_name'].tolist()
    # TODO: ask nikhil bh. about this step
    nodes_to_avoid = clock_search_text + reset_search_text + circuit_outputs
    for node in sorted_node_names:
        if node not in nodes_to_avoid and len(trigger_nodes) <= num_not_rndm:
            trigger_nodes.append(node)
    print(nodes_to_avoid)
    # adding the random nodes
    nodes_to_avoid += trigger_nodes
    random.shuffle(sorted_node_names) # shuffling the node names
    for node in sorted_node_names:
        if node not in nodes_to_avoid and len(trigger_nodes) <= num_input_nodes:
            trigger_nodes.append(node)

    return trigger_nodes

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

# FUNCTION: searched for a pattern in the given string
def checkPattern(pattern_list, str_list):
    for pattern in pattern_list:
        for str in str_list:
            if pattern in str:
                return str
    return ''

'''----------------------start: parsing files----------------------'''

circuit_fp = sys.argv[1]
print(circuit_fp)
trojan_fp = sys.argv[2]
# os.system(f'cat {circuit_fp} > inserted_trojan.v')
os.system('touch inserted_trojan.v')
result_fp = f'inserted_trojan.v'
print(circuit_fp)

circuit_obj = cp(circuit_fp)
trojan_obj = cp(trojan_fp)
result_obj = cp(result_fp)   # empty parser obj

# declaring components for result file
result_module_name = result_obj.getModuleName()
result_inputs = result_obj.getInputs()
result_outputs = result_obj.getOutputs()
result_wires = result_obj.getWires()
result_registers = result_obj.getRegisters()
result_clock, result_reset = result_obj.getClockAndReset()

# getting trojan data
trojan_inputs = trojan_obj.getInputs()
trojan_outputs = trojan_obj.getOutputs()
trojan_wires = trojan_obj.getWires()
trojan_registers = trojan_obj.getRegisters()
trojan_clock, trojan_reset = trojan_obj.getClockAndReset()

# getting circuit data
circuit_module_name = circuit_obj.getModuleName()
circuit_inputs = circuit_obj.getInputs()
circuit_outputs = circuit_obj.getOutputs()
circuit_wires = circuit_obj.getWires()
circuit_registers = circuit_obj.getRegisters()
circuit_clock, circuit_reset = circuit_obj.getClockAndReset()

print('trojaninsert.py: All circuit files have been parsed.')
'''----------------------end: parsing trojan & circuit files----------------------'''


'''----------------------start: getting trigger nodes & payloads----------------------'''
# getting trigger nodes
trigger_nodes = getTrigNodes(circuit_fp, len(trojan_inputs-2))

print('trojaninsert.py: All trigger nodes have been fetched.')

# assigning payload to output
payloads = selectPayloads(circuit_outputs, trojan_outputs)

print('trojaninsert.py: All payloads have been chosen.')
'''----------------------end: getting trigger nodes & payloads----------------------'''



'''----------------------start: changing trojan node names----------------------'''
trojan_nodes_before = trojan_inputs + trojan_outputs + trojan_wires
# add suffix to trojan-related lists
trojan_inputs = [input + '_trj' for input in trojan_inputs]
trojan_outputs = [output + '_trj' for output in trojan_outputs]
trojan_wires = [twire + '_trj' for twire in trojan_wires]

trojan_clock += '_trj'
trojan_reset += '_trj'

trojan_nodes_after = trojan_inputs + trojan_outputs + trojan_wires

for i in range(len(trojan_registers)):
    element = trojan_registers[i]
    temp = element[2]
    for j in range(len(payloads)):
        if trojan_nodes_before[j] in temp:
            element = (element[0], element[1], temp.replace(trojan_nodes_before[j], trojan_nodes_after[j]))
    circuit_registers[i] = element
'''----------------------end: changing trojan node names----------------------'''


'''----------------------start: payload node manipulation----------------------'''
# adding a previous node to 
payload_connection_fanIN = [payload + '_prev' for payload in payloads]

# replace payload node with payload_prev in circuit wires
for i, payload in enumerate(payloads):
    payload_index = circuit_wires.index(payload)
    circuit_wires[payload_index] = payload_connection_fanIN[i]

# replace payload node with payload_prev in circuit registers
for i in range(len(circuit_registers)):
    element = circuit_registers[i]
    original_payload = element[2]
    for j in range(len(payloads)):
        if payloads[j] in original_payload:
            element = (element[0], element[1], original_payload.replace(payloads[j], payload_connection_fanIN[j]))
    circuit_registers[i] = element
'''----------------------end: payload node manipulation----------------------'''


'''----------------------start:inserting the trojan----------------------'''

# initializing the result obj with values
result_module_name = circuit_module_name
result_inputs = circuit_inputs
result_outputs = circuit_outputs

# storing circuit wires, and trojan inputs, outputs, and wires in result_wires
result_wires = circuit_wires + trojan_inputs + trojan_outputs + trojan_wires

# assigning trojan clock and resest to circuit's
result_registers.append((f"assign {trojan_clock} = {circuit_clock};", "", ""))
result_registers.append((f"assign {trojan_reset} = {circuit_reset};", "", ""))

# adding trigger nodes in the result_registers
trojan_inputs = [i for i in trojan_inputs if i not in (trojan_clock, trojan_reset)]
for i in range(len(trigger_nodes)):
    assign_str = f"assign {trojan_inputs[i]} = {trigger_nodes[i]};"
    result_registers.append((assign_str), "", "")

# add trojan registers to result_registers
result_registers.extend(trojan_registers)

# add circuit registers to result_registers
result_registers.extend(circuit_registers)

# add payload
for i, payload in enumerate(payloads):
    payload_logic = ('XOR2X1', f'rtj_maruti{i}', f'(.IN1({trojan_outputs[i]}), .IN2({payload_connection_fanIN[i]}), .Q({payloads[i]}))')
    result_registers.append(payload_logic)

result_obj.setModuleName(result_module_name)
result_obj.setInputs(result_inputs)
result_obj.setOutputs(result_outputs)
result_obj.setWires(result_wires)
result_obj.setRegisters(result_registers)


result_obj.makeCircuit()


















# parse trojan
    # change the input, output, regnames

# parse circuit
    # find a payload
    # change regnames
    # get trigger nodes
    # assign payload
