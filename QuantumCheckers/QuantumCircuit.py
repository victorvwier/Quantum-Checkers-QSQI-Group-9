# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 10:28:58 2021

@author: pimve
"""

import numpy as np
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute
from qiskit.visualization import plot_histogram
from qiskit.quantum_info.states import Statevector, partial_trace
from qiskit import execute

class Quantumcircuit:
    
    def __init__(self,Rows,Cols,Piece_Rows):
        self.numb = Rows*Cols // 2
        self.circuit = QuantumCircuit(self.numb, self.numb)
        self.color = np.zeros(self.numb)
        self.Qboard = np.zeros(self.numb)
        
        for i in range (Cols*Piece_Rows // 2):
            self.circuit.x(i)
            self.circuit.x(-i-1)
            self.color[i]= 1
            self.color[-i-1] = -1
            
        self.construct_binarray()
            
        #self._build_SqSwapGate()
        
    # def _build_SqSwapGate(self):
    #     self.SqSwap = QuantumCircuit(2,name='sqswap')
    #     self.SqSwap.cnot(0,1)
    #     self.SqSwap.h(0)
    #     self.SqSwap.t(0)
    #     self.SqSwap.tdg(1)
    #     self.SqSwap.h(0)
    #     self.SqSwap.h(1)
    #     self.SqSwap.cnot(0,1)
    #     self.SqSwap.h(0)
    #     self.SqSwap.h(1)
    #     self.SqSwap.tdg(0)
    #     self.SqSwap.h(0)
    #     self.SqSwap.cnot(0,1)
    #     self.SqSwap.s(1)
    #     self.SqSwap.sdg(0)
    
    def construct_binarray(self):
        
        
        tot_numb = int(2**self.numb)
        self.binary_array = np.zeros((tot_numb,self.numb))
        for i in range (tot_numb):
            temp = bin(i).replace("0b","")
            self.binary_array[i,:] = list(temp.rjust(self.numb,'0'))
        self.binary_array.astype(np.int)   
        
        
    def c_empty (self, old_pos, new_pos):
        self.circuit.swap(old_pos,new_pos)
        self.color[old_pos],self.color[new_pos]=0,self.color[old_pos]
    
    def c_own_color(self,old_pos, new_pos):
        self.circuit.swap(old_pos,new_pos)
        
    # def sqrtswap(self, old_pos, new_pos1,new_pos2):
    #     self.circuit.append(self.SqSwap,(old_pos,new_pos1))
    #     self.swap(old_pos,new_pos2)
    #     self.color[new_pos1]=self.color[new_pos2]
        
    def q_empty(self,old_pos,new_pos1,new_pos2):
        self.circuit.swap(old_pos,new_pos1)
        self.color[old_pos],self.color[new_pos1]=0,self.color[old_pos]
        self.circuit.h(new_pos2)
        self.circuit.cnot(new_pos2,new_pos1)
        self.color[new_pos2]=self.color[new_pos1]
        
        
    
    def new_initialization(self,positions):
        self.circuit = QuantumCircuit(self.numb)
        for i, pos in enumerate (positions):
            if pos == 1:
                self.circuit.x(i)
                
    def draw_circuit(self):
        self.circuit.draw(output='mpl')
        
    def perform_measurement(self,backend,shots,histogram=False):
        qi_job = execute(self.circuit, backend=backend, shots=shots)
        qi_result = qi_job.result()
        
        histogram = qi_result.get_counts(self.circuit)
        print('\nState\tCounts')
        [print('{0}\t\t{1}'.format(state, counts)) for state, counts in histogram.items()]
        # Print the full state probabilities histogram
        probabilities_histogram = qi_result.get_probabilities(self.circuit)
        print('\nState\tProbabilities')
        [print('{0}\t\t{1}'.format(state, val)) for state, val in probabilities_histogram.items()]
        
        if histogram == True:
            plot_histogram(histogram)
        
    def get_probability_comp(self,backend, shots=256):
        empty_list = []
        qi_job = execute(self.circuit, backend=backend, shots=shots)
        qi_result = qi_job.result()
        string_repr = qi_result.get_memory(self.circuit)
        #print(split_results,string_repr)
        for string in (string_repr):
            empty_list+= string
        split_results = np.array(empty_list).astype(np.int)
        probabilities = np.mean(np.reshape(split_results,(shots,self.numb)),axis=1)
        return probabilities
        
        
    def get_probability_exact(self,i):
        
        all_tiles = list(np.arange(0,self.numb)) 
        all_tiles.remove(i)
        init_state = self.numb * '0'
        zero_state = Statevector.from_label(init_state)
        self.final_state = zero_state.evolve(self.circuit)
        denmat = partial_trace(self.final_state,all_tiles)
        exp_value = denmat.probabilities()
        return exp_value[1]
        
    def get_probability_exact2(self):
        init_state = self.numb * '0'
        zero_state = Statevector.from_label(init_state)
        self.final_state = zero_state.evolve(self.circuit)
        full_prob = self.final_state.probabilities()
        probabilities = np.matmul(np.transpose(self.binary_array),full_prob)
        return np.flipud(probabilities)
        
        
        
        
        
        
        
        
        
    