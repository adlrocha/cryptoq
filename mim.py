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

# Noise matrix
x = np.identity(16)
theta = 0.01
x[0][0] = math.cos(theta)
x[1][0] = math.sin(theta)
x[0][1] = -math.sin(theta)
x[1][1] = math.cos(theta)

def rotationMatrix(theta):
    x = np.identity(2)
    x[0][0] = math.cos(theta)
    x[1][0] = math.sin(theta)
    x[0][1] = -math.sin(theta)
    x[1][1] = math.cos(theta)
    return x

#theta1 and theta2 eavsdroppter error
def generateQK(num_bits, theta1=0, theta2=0, securityThresh=1000, withHist=False):

    # Create the circuit
    cx_circ = parityCircuit(theta1, theta2)

    # Execute the circuit
    job = execute(cx_circ, backend = Aer.get_backend('qasm_simulator'), shots=256*num_bits, memory=True)
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
    memory = memory[len(memory)-num_bits: len(memory)]

    # print(memory[len(memory)-1][4])
    res = {'A': '', 'B': '', 'errorCounter':0, 'valid': True}
    counter = 0
    i = len(memory)-1
    while len(res["A"]) != num_bits:
        print('Memory', memory[i])
        # Check if error in parity bit
        if memory[i][4] == '0':
            print("Enters here")
            counter+=1
        else:
            res["A"] = res["A"] + memory[i][1]
            res["B"] = res["B"] + memory[i][2]
        
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