# =============================================================================
# author:       Dhruv Raj Bangad (bangaddj@mail.uc.edu)
# purpose:      To parse the trojan porbability info into a pandas dataframe
# usage:        from trojanprobability import getTrojanProbability 
#               after importing, use it as function
# return value: pandas dataframe
# =============================================================================

import os, sys, re, math, pandas as pd
from trojanparser import TrojanParser



def getTrojanProbability(trojan_file):

    # generating the probability file
    cmd = f'./prob junk.txt {trojan_file} > {trojan_file}_prob.txt'
    os.system(cmd)

    # initializing the pandas dataframe
    df = pd.DataFrame(columns=['node_name', 'p_low', 'p_high', 'cc0', 'cc1', 'c0', 'scope_testability'], index=[])

    # parsing the probability file to get the pandas dataframe
    prob_fp = f'{trojan_file}_prob.txt'
    fp = open(prob_fp, 'r')
    lines = fp.readlines()

    for line in lines:

        # since Probability is displayed in the beginning of the generated file
        # hence, we first find probability values and add them to the data frame
        if 'Probabaility :=' in line:
            node = re.findall(r'Probabaility :=  (.*?) ', line)                     # gets node name through regex
            probs = re.findall(r'(\d.[0-9]+)', line)                                # gets probability through regex
            new_row = {'node_name': node[0], 'p_low': probs[0], 'p_high': probs[1]} # new row to add to dataframe
            df.loc[len(df.index)] = new_row                                         # appends new row to dataframe end
        
        # scope values are displayed after the probability values,
        # so we update the particular node row with the scope values
        elif 'Gate :' in line:
            node = re.findall(r'Gate :  (.*?)  CC', line)[0]                               # gets node name through regex              
            scope = re.findall(r'\s(\d+)', line)                                           # gets CC0, CC1, C0 values 
            scope_test = math.dist((int(scope[0]), int(scope[1]), int(scope[2])), (0,0,0)) # computes the scope testability
            scope.append(scope_test)                                                       # append it to the scope list
            insert_loc = df.index[df['node_name']== node].tolist()[0]                      # finds insert location
            df.loc[insert_loc, ['cc0', 'cc1', 'c0', 'scope_testability']] = scope          # updates df with new values for the node

    fp.close()
    return df   
