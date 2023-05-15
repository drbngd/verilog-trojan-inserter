# trojaninsertion_pub

## About
This repo contains the necessary files to insert a trojan file into any circuit file (verilog only).

## Pre-req Python Library
The pandas is required to run this code. Install it using pip as follows:
```
pip install pandas
```

## Setup
```
git clone https://github.com/drbngd/trojaninsertion_pub.git
cd trojaninsertion_pub
chmod +x prob

```

## Usage
Make sure that you have all of these files in the same directory:

- trojaninsert.py
- svcparser.py
- trojanprobability.py
- prob

Once you have all of these files, you can type the following command to insert a trojan into a circuit file
```
python3 trojaninsert.py path/to/circuit.v path/to/trojan.py
```
The resulting file will be found in the same directory, with this name: **inserted_trojan.v**
