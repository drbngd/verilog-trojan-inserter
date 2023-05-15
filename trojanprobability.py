# =============================================================================
# author:       Dhruv Raj Bangad (bangaddj@mail.uc.edu)
# purpose:      To parse the trojan porbability info into a pandas dataframe
# usage:        from trojanprobability import getTrojanProbability 
#               after importing, use it as function
# return value: pandas dataframe
# =============================================================================

import os, sys, re, math, pandas as pd


def getTrojanProbability(trojan_file):

    # generating the probability file
    x = trojan_file.strip('.v')
    prob_fp = f'temp_prob.txt'
    cmd = f'./prob junk.txt {trojan_file} > {prob_fp}'
    os.system(cmd)

    # initializing the pandas dataframe
    df = pd.DataFrame(columns=['node_name', 'p_low', 'p_high', 'cc0', 'cc1', 'c0', 'scope_testability'], index=[])

    # parsing the probability file to get the pandas dataframe
    fp = open(prob_fp, 'r')
    lines = fp.readlines()
    
    # prob_pattern = r'(\w+)\s+\[(\d+(\.\d+)?)\s+(\d+(\.\d+)?)\]'
    '''prob pattern made by me'''
    prob_pattern = r'Probabaility\s:=\s\s(\S*)\s\[(\S*)\s(\S*)\]'

    scoap_pattern = r'Gate\s*:\s*(\w+)\s*CC0\s*:\s*(\d+)\s*CC1\s*:\s*(\d+)\s*CO\s*:\s*(\d+)'
    scoap_pattern = r'Gate\s:\s\s(\S+)\s\sCC0\s:\s\s(\S+)\s\sCC1\s:\s\s(\S+)\s\sCO\s:\s\s(\S+)'

    for line in lines:

        # since Probability is displayed in the beginning of the generated file
        # hence, we first find probability values and add them to the data frame
        if 'Probabaility :=' in line:
            match = re.search(prob_pattern, line)
            if match:
                node = match.group(1)                    # gets node name through regex
                probs_0 = float(match.group(2))                                # gets probability through regex
                probs_1 = float(match.group(3))
                new_row = {'node_name': node, 'p_low': probs_0, 'p_high': probs_1} # new row to add to dataframe
                df.loc[len(df.index)] = new_row                                         # appends new row to dataframe end
        
        # scope values are displayed after the probability values,
        # so we update the particular node row with the scope values
        elif 'Gate :' in line:
            match = re.search(scoap_pattern, line)
            if match:
                node = match.group(1)
                scope = [int(match.group(2)), int(match.group(3)), int(match.group(4))]
                
                '''prev version'''
                # node = re.findall(r'Gate :  (.*?)  CC', line)[0]                               # gets node name through regex              
                # scope = re.findall(r'\s(\d+)', line)                                           # gets CC0, CC1, C0 values 
            
            
            #scope_test = math.dist((int(scope[0]), int(scope[1]), int(scope[2])), (0,0,0)) # computes the scope testability
            scope_test = math.sqrt(int(scope[0])**2 + int(scope[1])**2 + int(scope[2])**2) # computes the scope for python 3.6 and less
            scope.append(scope_test)                                                       # append it to the scope list
            
            #insert_loc = df.index[df['node_name']== node].tolist()[0]                      # finds insert location
            
            '''trying to catch error'''
            insert_locs = df.index[df['node_name'] == node].tolist()
            if insert_locs:
                insert_loc = insert_locs[0]
                # Proceed with further operations using `insert_loc`
            else:
                # Handle the case when no matching rows are found
                print(f'{trojan_file} had error with finding following node: {node}')

            
            
            df.loc[insert_loc, ['cc0', 'cc1', 'c0', 'scope_testability']] = scope          # updates df with new values for the node
    
    fp.close()
#    os.system(f'rm -rf {prob_fp}')     
    return df

# for testing
d = getTrojanProbability(str(sys.argv[1]))
print(d)
