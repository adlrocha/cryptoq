from qiskit import execute, QuantumCircuit, QuantumRegister, ClassicalRegister, Aer
from qiskit.quantum_info.operators import Operator
from qiskit.quantum_info import process_fidelity
from qiskit.providers.aer import QasmSimulator
from qiskit.providers.aer.noise import NoiseModel, errors
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
    x = np.identity(4)
    x[0][0] = math.cos(theta)
    x[1][0] = math.sin(theta)
    x[0][1] = -math.sin(theta)
    x[1][1] = math.cos(theta)
    print("rotation", x)
    return x

rotationMatrix(0.5)
# print(x)



def generateQK(num_bits, withHist=False, withError=False, ):
    # Unitary function if not error.
    if not withError:
        x = np.identity(16)

    # Noise operator
    id_op = Operator(x)

    # Define the Quantum and Classical Registers
    qr = QuantumRegister(4)
    cr = ClassicalRegister(4)

    cx_circ = QuantumCircuit(qr, cr)
    cx_circ.h(qr[1])
    cx_circ.h(qr[3])
    cx_circ.cx(qr[1], qr[0])
    cx_circ.cx(qr[3], qr[2])

    # Noise addition
    cx_circ.unitary(id_op, qr[0:4], label='idop')
    cx_circ.measure(qr[0:4], cr[0:4])


    # Execute the circuit
    job = execute(cx_circ, backend = Aer.get_backend('qasm_simulator'), shots=256*num_bits, memory=True)
    result = job.result()

    # Print circuit.
    print(cx_circ)

    # Print the result
    if withHist:
        counts = result.get_counts(cx_circ)
        plot.bar(counts.keys(), counts.values(), 1.0, color='g')
        plot.show()
    
    memory = result.get_memory()
    num_bits = int(num_bits/4)
    return memory[len(memory)-num_bits: len(memory)]
