from qiskit import execute, QuantumCircuit, QuantumRegister, ClassicalRegister, Aer
from qiskit.quantum_info.operators import Operator
from qiskit.quantum_info import process_fidelity
from qiskit.providers.aer import QasmSimulator
from qiskit.providers.aer.noise import NoiseModel, errors
from qiskit.aqua.components.oracles import LogicalExpressionOracle, TruthTableOracle

import math

from qiskit.tools.visualization import plot_histogram

import numpy as np
import matplotlib.pyplot as plot
import string

from qiskit import IBMQ
IBMQ.load_accounts()

# Noise matrix
x = np.identity(16)
theta = 0.01
x[0][0] = math.cos(theta)
x[1][0] = math.sin(theta)
x[0][1] = -math.sin(theta)
x[1][1] = math.cos(theta)

def cheatingMatrices():
    c1 = np.identity(2)
    f = 1/math.sqrt(2)

    c1[0][0] = f
    c1[1][0] = -f
    c1[0][1] = f
    c1[1][1] = f

    c2 = np.identity(2)
    c2[0][0] = f
    c2[1][0] = f
    c2[0][1] = f
    c2[1][1] = -f
    return c1, c2

def rotationMatrix(theta):
    x = np.identity(2)
    x[0][0] = math.cos(theta)
    x[1][0] = math.sin(theta)
    x[0][1] = -math.sin(theta)
    x[1][1] = math.cos(theta)
    return x
#theta1 and theta2 eavsdroppter error
def generateQK(num_bits, theta1=0, theta2=0, securityThresh=1000, simulation=True, withHist=False):

    # Create the circuit
    cx_circ = parityCircuit(theta1, theta2)

    if simulation:
        # Execute the circuit
        print("Running on simulation...")
        job = execute(cx_circ, backend = Aer.get_backend('qasm_simulator'), shots=256*num_bits, memory=True)
        result = job.result()
    else:
        # Execute the circuit
        print("Running on real quantum computer...")
        job = execute(cx_circ, backend = IBMQ.get_backend('ibmqx2'), shots=256*num_bits, memory=True)
        result = job.result()

    # Print circuit.
    # print(cx_circ)

  
    # Print the result
    if withHist:
        counts = result.get_counts(cx_circ)
        plot.bar(counts.keys(), counts.values(), 1.0, color='g')
        plot.show()
    
    memory = result.get_memory()
    num_bits = int(num_bits)
    # memory = memory[len(memory)-num_bits: len(memory)]

    res = {'A': '', 'B': '', 'errorCounter':0, 'valid': True}
    counter = 0
    i = len(memory)-1
    while len(res["A"]) != num_bits:
        # print('Memory', memory[i], i)
        # Check if error in parity bit and discard if there is
        if memory[i][4] == '0':
            counter+=1
        else:
            res["A"] = res["A"] + memory[i][1]
            res["B"] = res["B"] + memory[i][2]
        
        # SecurityThreshold from which we discard the key
        if counter >= securityThresh:
            res['valid'] = False
            res["errorCounter"] = counter
            return res
        i-=1
        


    res["errorCounter"] = counter
    return res



# ParityCircuit for random bit generator and parity bit
def parityCircuit(theta1=0, theta2=0):

    # Noise rotation matrix.
    n1 = rotationMatrix(theta1)
    n2 = rotationMatrix(theta2)
    n = np.kron(n1, n2)



    # Noise operator
    id_op = Operator(n)

    truthtable = "10011001"
    oracle = TruthTableOracle(truthtable)
    or_cx = oracle.construct_circuit()
    # print(oracle.output_register)
    v = oracle.variable_register
    o = oracle.output_register

    cr1 = ClassicalRegister(3)
    cr2 = ClassicalRegister(1)

    cx_circ = QuantumCircuit(v, cr2)

    or_cx.add_register(cr1)
    cx_circ.h(v[1])
    cx_circ.cx(v[1], v[0])

    cx_circ.unitary(id_op, v[1:3], label='idop')


    total_cx = cx_circ + or_cx
    total_cx.measure(v, cr1)
    total_cx.measure(o, cr2)

    return total_cx

# ParityCircuit for random bit generator and parity bit
def parityCircuitCheating(cheating=False, cheatingType=0):

    if cheating:
        # Cheating operator
        c1 = cheatingMatrices()[cheatingType]
    else:
        c1 = np.identity(2)

    id_op = Operator(c1)

    truthtable = "10011001"
    oracle = TruthTableOracle(truthtable)
    or_cx = oracle.construct_circuit()
    # print(oracle.output_register)
    v = oracle.variable_register
    o = oracle.output_register

    cr1 = ClassicalRegister(3)
    cr2 = ClassicalRegister(1)

    cx_circ = QuantumCircuit(v, cr2)

    or_cx.add_register(cr1)
    cx_circ.h(v[1])
    cx_circ.cx(v[1], v[0])

    cx_circ.unitary(id_op, v[cheatingType+1:cheatingType+2], label='idop')


    total_cx = cx_circ + or_cx
    total_cx.measure(v, cr1)
    total_cx.measure(o, cr2)

    return total_cx

def quantumConsensus(nodes=3, cheating=False, cheatingType=[0,0,0]):

    # Placeholder for the nodes results
    res = dict(zip(string.ascii_uppercase, range(1, nodes+1)))
    toSend = dict(zip(string.ascii_uppercase, range(1, nodes+1)))

    

    # While two nodes with the same value
    while sum(res.values()) != 1:
        # Placeholder for all measurements
        pkts = ''
        for i in range(nodes):
            cx_circ = parityCircuitCheating(cheating, cheatingType[i])
            job = execute(cx_circ, backend = Aer.get_backend('qasm_simulator'), shots=1, memory=True)
            result = job.result()
            memory = result.get_memory()
            res[list(res.keys())[i]] = int(memory[0][1])

            #Adding measurements
            pkts += memory[0][2]
            pkts += memory[0][1]
            print(res)
    
    print(res)
    tmp = res.copy()
    for value in tmp:
        if res[value] == 1:
            res['winner'] = value 

    # Corner case
    print(pkts)
    toSend[list(toSend.keys())[0]] = pkts[0] + pkts[len(pkts)-1]
    #Adding proper nodes
    for i in range(0, nodes):
        # Preparing the packets
        toSend[list(toSend.keys())[i]] = pkts[2*i] + pkts[2*i-1]

    return res, toSend

def network3nodes(cheating, cheatingType):
    res = quantumConsensus(3, cheating, cheatingType)
    toSend = res[1]

    #TODO: Check the mistake here in the validation.
    # Cheat check
    if toSend['A'][1] == toSend['C'][0]:
        print('As validation correct')
    else:
        print('As validation failed. Someone cheating')

    if toSend['B'][1] == toSend['A'][0]:
        print('Bs validation correct')
    else:
        print('Bs validation failed. Someone cheating')

    if toSend['C'][1] == toSend['B'][0]:
        print('Cs validation correct')
    else:
        print('Cs validation failed. Someone cheating')
    
    return res[0]


# print(generateQK(8, 1, 0.5, 100, False))
# print(quantumConsensus())
# print(network3nodes(False, [0,0,0]))
# print(cheatingMatrices())
# print(parityCircuit())