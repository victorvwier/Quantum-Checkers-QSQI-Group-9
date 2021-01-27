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
from qiskit import Aer


backendAer = Aer.get_backend('statevector_simulator')


class Quantumcircuit:

    def __init__(self, Rows, Cols, Piece_Rows, backend):
        self.numb = Rows * Cols // 2
        self.circuit = QuantumCircuit(self.numb, self.numb)
        self.color = np.zeros(self.numb)
        self.quantum_board = np.zeros(self.numb)
        self.backend = backend
        self.ent_tracker = []
        self.ent_counter = np.zeros((self.numb))
        self.full_circuit = self.circuit.copy()
        self.circuit2 = QuantumCircuit(self.numb, self.numb)
        
        for i in range(self.numb):
            self.ent_tracker.append([])

        for i in range(Cols * Piece_Rows // 2):
            self.circuit.x(i)
            self.circuit.x(-i - 1)
            self.color[i] = 1
            self.color[-i - 1] = -1
            self.ent_tracker[i].append(i)
            self.ent_tracker[-1-i].append(Cols * Rows // 2-1-i)
        print(self.ent_tracker)

        self.construct_binarray()

        self._build_SqSwapGate()
    
    
    def _build_SqSwapGate(self):
        self.SqSwap = QuantumCircuit(2, name='sqswap')
        self.SqSwap.cnot(0, 1)
        self.SqSwap.h(0)
        self.SqSwap.t(0)
        self.SqSwap.tdg(1)
        self.SqSwap.h(0)
        self.SqSwap.h(1)
        self.SqSwap.cnot(0, 1)
        self.SqSwap.h(0)
        self.SqSwap.h(1)
        self.SqSwap.tdg(0)
        self.SqSwap.h(0)
        self.SqSwap.cnot(0, 1)
        self.SqSwap.s(1)
        self.SqSwap.sdg(0)
        self.revSqSwap = self.SqSwap.reverse_ops()
        self.cSqSwap = self.SqSwap.control()

    def construct_binarray(self):
        tot_numb = int(2 ** self.numb)
        self.binary_array = np.zeros((tot_numb, self.numb))
        for i in range(tot_numb):
            temp = bin(i).replace("0b", "")
            self.binary_array[i, :] = list(temp.rjust(self.numb, '0'))
        self.binary_array.astype(np.int)

    def c_empty(self, old_pos, new_pos):
        self.circuit.swap(old_pos, new_pos)
        self.color[old_pos], self.color[new_pos] = 0, self.color[old_pos]
        self.ent_tracker[old_pos],self.ent_tracker[new_pos]= [],self.ent_tracker[old_pos]
        self.ent_counter[old_pos],self.ent_counter[new_pos]= 0,self.ent_counter[old_pos]

    def c_self_unentangled(self, old_pos, new_pos):
        self.circuit.swap(old_pos, new_pos)
        self.ent_tracker[old_pos],self.ent_tracker[new_pos]= self.ent_tracker[new_pos],self.ent_tracker[old_pos]
        self.ent_counter[old_pos],self.ent_counter[new_pos]= self.ent_counter[new_pos],self.ent_counter[old_pos]
        
    def c_self_entangled(self,old_pos,new_pos,failed_move):
        old = self.ent_tracker[old_pos]
        new = self.ent_tracker[new_pos]
        if len(old) == 1 and old == new:
            self.circuit.append(self.revSqSwap,(old_pos,new_pos))
            self.ent_tracker[old_pos] = []
            
            self.ent_counter[old_pos] -= 1
            self.ent_counter[new_pos] -= 1
        elif len(old) == 1:
            ent_with = []
            partner = []
            for i, lists in enumerate (self.ent_tracker):
                if old[0] in lists:
                    ent_with.append(i)
                if new[0] in lists:
                        partner.append(i)
            ent_with.remove(old_pos)
            partner.remove(new_pos)
            
            if len(ent_with) <=1:
                self.circuit.x(ent_with[0])
                self.circuit.cswap(ent_with[0],old_pos,new_pos)
                self.circuit.x(ent_with[0])
                    
                self.ent_counter[new_pos] += 1
                self.ent_counter[old_pos] += 1
                self.ent_counter[ent_with[0]] += 1
                self.ent_counter[partner[0]] += 1
                
            else:
                print('impossible try sth else')
                failed_move = True
        else:
            print('impossible try sth else')
            failed_move = True
        return failed_move
            
            
    def q_empty(self,old_pos,new_pos):
        self.circuit.append(self.SqSwap, (old_pos, new_pos))
        self.color[new_pos] = self.color[old_pos]
        
        deducer = self.ent_tracker[old_pos]
        while type(deducer[0]) != int:
            deducer = deducer[0]
        for numbers in deducer:    
            self.ent_tracker[new_pos].append(numbers)
        
        self.ent_counter[new_pos] = self.ent_counter[old_pos] + 1    
        self.ent_counter[old_pos] += 1
    


    def q_entangled(self, old_pos, new_pos):
        old = self.ent_tracker[old_pos]
        new = self.ent_tracker[new_pos]
        # self.circuit.swap(old_pos,new_pos1)
        # self.color[old_pos],self.color[new_pos1]=0,self.color[old_pos]
        self.color[new_pos] = self.color[old_pos]
        
        if len(old) == 1 and old == new:
            self.circuit.append(self.revSqSwap,(old_pos,new_pos))
            self.circuit.rx(-np.pi/3,new_pos)
            self.circuit.x(old_pos)
            self.circuit.cnot(new_pos,old_pos)
            
        elif len(old) == 1:
            ent_with = []
            partner = []
            for i, lists in enumerate (self.ent_tracker):
                if old[0] in lists:
                    ent_with.append(i)
                if new[0] in lists:
                        partner.append(i)
            ent_with.remove(old_pos)
            partner.remove(new_pos)
            
            if len(ent_with) <=1:
                self.circuit.x(ent_with[0])
                self.circuit.append(self.cSqSwap,(ent_with[0],old_pos,new_pos))
                self.circuit.x(ent_with[0])
                    
                self.ent_counter[new_pos] += 1
                self.ent_counter[old_pos] += 1
                self.ent_counter[ent_with[0]] += 1
                self.ent_counter[partner[0]] += 1
                
        else:
            print('ERROR!!!!!')
            
            # self.ent_counter[new_pos] += 1
            # self.ent_counter[old_pos] += 1
            # self.ent_counter[ent_with[0]] += 1
            # self.ent_counter[partner[0]] += 1
        
        

        # self.circuit.swap(old_pos,new_pos1)
        # self.color[old_pos],self.color[new_pos1]=0,self.color[old_pos]
        # self.circuit.h(new_pos2)
        # self.circuit.cnot(new_pos2,new_pos1)
        # self.color[new_pos2]=self.color[new_pos1]

    def new_initialization(self, positions):
        hulplist = []
        for i in range(self.numb):
            hulplist.append([])
        
        circuit2 = QuantumCircuit(self.numb, self.numb)
        for i, pos in enumerate(positions):
            if int(pos) == 1:
                hulplist[i].append(i)
                circuit2.x(i)
        self.circuit = circuit2.copy()
        self.ent_tracker = hulplist
        self.ent_counter = np.zeros(self.numb)
        
    def append_to_full_circuit(self, last=False):
        if self.numb < 10:
            self.full_circuit = self.full_circuit + self.circuit
            self.full_circuit.barrier()
            
        else:
            self.full_circuit = self.full_circuit + self.circuit
            if not last:
                for i in range(self.numb):
                    self.full_circuit.initialize([1,0],i)
                self.full_circuit.barrier()
        
        
    def draw_circuit(self):
        self.full_circuit.draw(output='mpl',justify='right',plot_barriers=False)

    def full_collapse(self, attacker, defender, behind):
        qi_job = execute(self.circuit, backend=self.backend, shots=1)
        qi_result = qi_job.result()

        self.append_to_full_circuit()
        string_repr = qi_result.get_memory(self.circuit)
        array_repr = np.flipud(np.array(list(string_repr[0])))

        a, b, c = int(array_repr[attacker]), int(array_repr[defender]), \
                  int(array_repr[behind])
        self.new_initialization(array_repr)
        
        
        return a, b, c

        # histogram = qi_result.get_counts(self.circuit)
        # print('\nState\tCounts')
        # [print('{0}\t\t{1}'.format(state, counts)) for state, counts in histogram.items()]
        # # Print the full state probabilities histogram
        # probabilities_histogram = qi_result.get_probabilities(self.circuit)
        # print('\nState\tProbabilities')
        # [print('{0}\t\t{1}'.format(state, val)) for state, val in probabilities_histogram.items()]

        # if histogram == True:
        #     plot_histogram(histogram)

    def part_collapse(self, attacker, defender, behind):

        self.circuit.measure(attacker, attacker)
        self.circuit.measure(defender, defender)
        self.circuit.measure(behind, behind)
        self.circuit2 = QuantumCircuit(self.numb, self.numb, name='measurement')

        result = execute(self.circuit, backendAer).result()
        out_state = result.get_statevector()
        
        self.circuit2.initialize(out_state, np.arange(self.numb))
        self.append_to_full_circuit()
        self.circuit = self.circuit2.copy()
        self.ent_counter = np.zeros(self.numb)
        
        hulplist = []
        for i in range(self.numb):
            hulplist.append([])
            
        self.ent_tracker = hulplist
            

    def get_probability_exact2(self):
        init_state = self.numb * '0'
        zero_state = Statevector.from_label(init_state)
        self.final_state = zero_state.evolve(self.circuit)
        full_prob = self.final_state.probabilities()
        probabilities = np.matmul(np.transpose(self.binary_array), full_prob)
        return np.flipud(probabilities)


    def remove_collapsed_piece(self, piece):
        self.circuit.x(piece)

    # def get_probability_comp(self,backend, shots=256):
    #     empty_list = []
    #     qi_job = execute(self.circuit, backend=backend, shots=shots)
    #     qi_result = qi_job.result()
    #     string_repr = qi_result.get_memory(self.circuit)
    #     #print(split_results,string_repr)
    #     for string in (string_repr):
    #         empty_list+= string
    #     split_results = np.array(empty_list).astype(np.int)
    #     probabilities = np.mean(np.reshape(split_results,(shots,self.numb)),axis=1)
    #     return probabilities

    # def get_probability_exact(self,i):

    #     all_tiles = list(np.arange(0,self.numb)) 
    #     all_tiles.remove(i)
    #     init_state = self.numb * '0'
    #     zero_state = Statevector.from_label(init_state)
    #     self.final_state = zero_state.evolve(self.circuit)
    #     denmat = partial_trace(self.final_state,all_tiles)
    #     exp_value = denmat.probabilities()
    #     return exp_value[1]
