# trojaninsertion_pub

## About
This repo contains the necessary files to insert a trojan file into any circuit file (verilog only).

## Usage
Make sure that you have all of these files in the same directory:

- trojaninsert.py
- trojanparser.py
- trojanprobability.py
- prob

Once you have all of these files, you can type the following command to insert a trojan into a circuit file
```
python3 trojaninsert.py path/to/circuit.v path/to/trojan.py
```
The resulting file will be found in the same directory, with this name: **inserted_trojan.v**
