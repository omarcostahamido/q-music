#import qiskit
from qiskit.tools.visualization import circuit_drawer

from qiskit import ClassicalRegister, QuantumRegister #, QuantumProgram
from qiskit import QuantumCircuit,execute

from qiskit import Aer, IBMQ


import struct
import numpy as np
import math
from scipy import signal as sg
from scipy.io import wavfile
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

def genWave(f=440,T=1, phase = 0,type='sine'):

    Fs = 44100                    ## Sampling Rate
                          ## Frequency (in Hz)
    sample = 44100*T                ## Number of samples 
    x = np.arange(sample)

    if type == 'sine':
        ####### sine wave ###########
        y = np.sin((2 * np.pi * f * x +phase)/ Fs)
    elif type == 'square':
        ####### square wave ##########
        y = sg.square((2 *np.pi * f *x+phase) / Fs )
    elif type == 'duty':
        ####### square wave with Duty Cycle ##########
        y = sg.square((2 *np.pi * f *x +phase)/ Fs , duty = 0.8)
    elif type == 'saw':
        ####### Sawtooth wave ########
        y = sg.sawtooth((2 *np.pi * f *x+phase) / Fs )
    
    return y

def sineadd(s1,s2,a1,a2):
    l1 = len(s1)
    l2 = len(s2)
    s1 = s1[0:min(l1,l2)]
    s2 = s2[0:min(l1,l2)]
    
    added = (np.add(a1*s1,a2*s2))
    return added   #/np.max(added)

def bloch_sonify(phi_theta,filename):
    phase_weight = 20
    F0 = 262
    F1 = 330
    stotal = np.array([])
    for angles in phi_theta:
       #print(angles)
       s1 = genWave(F0-angles[0]*phase_weight,0.05,0,'sine')
       #s2 = genWave(F1+angles[0],0.25,angles[0],'saw')
       s2 = genWave(F1+angles[0]*phase_weight,0.05,0,'saw')
       s3 = sineadd(s1,s2,math.pi-angles[1],angles[1])
       stotal = np.concatenate((stotal,s3))
    #stotal = savgol_filter(stotal, 51, 3)
    stotal = savgol_filter(stotal, 251, 3)
    stotal /= np.max(np.abs(stotal),axis=0)
    wavfile.write(filename,44100,stotal)

#assumes 3 qubits
def results_sonify(results, T=2, octave = 2, wavetype='sine', repeat = 0):
    #results is a list of lists
    #c3,e3,g3, b3,d4,f4,a4,c5
    Fmap = [130.81,164.81,196,246.94,293.67,349.23,440,523.25]
    N = len(results)

    stotal = np.array([])   
    #each r will be 3 qubits - i.e. 8 counts
    #each of the 8 counts is then mapped onto the amplitude of Fmap sines
    for r in results:
        sines = r[0]*genWave(octave*Fmap[0],T,0,wavetype)
        #r /= np.max(np.abs(r),axis=0)
        for count_index in range(1,len(r)-1):
            sines+=r[count_index]*genWave(octave*Fmap[count_index],T,0,wavetype)
        #normalise
        sines /= np.max(np.abs(sines),axis=0)
        #so now we have a chord for one set of results
        stotal = np.concatenate((stotal,sines))
    for i in range(0,repeat):
        stotal = np.concatenate((stotal,stotal))
    stotal = savgol_filter(stotal, 251, 3)
    return stotal
    
#results = [[100,150,50,36,85,27,85,98],[29,48,238,48,29,59,48,290],[38,57,30,28,568,38,38,49,30]]
#x = results_sonify(results,wavetype="saw")
#wavfile.write("results_son.wav",44100,x)


#qasm_root = 'C:\\Users\\ajkirke\\Dropbox\\Work\\python\\IBMMusic\\QISKitTests\\'
#qasm_root = 'C:/Users/ajkirke/Dropbox/Work/python/
backend = Aer.get_backend('qasm_simulator')     # this is the backend that will be used

q = QuantumRegister(3)
c = ClassicalRegister(3)    
qc = QuantumCircuit(q, c)     

#qasm_file= "alexis_qasm.qasm"
#qasm_file =qasm_root + qasm_file
qasm_file= "alexis_Grover.qasm"

def run_qasm(qasm_list):
    with open('temp_qasm_file.qasm', 'w') as f:
        for item in qasm_list:
            f.write("%s\n" % item)
    qCircuit = QuantumCircuit.from_qasm_file('temp_qasm_file.qasm') #(qasm_file) 
    job_sim = execute(qCircuit, backend, shots=1024)
    count_dict = job_sim.result().get_counts(qCircuit) 
    print(count_dict)
    result_items = ['000','001','010','011','100','101','110','111']
    #shows which of result_items is in count_dict
    in_results = list(count_dict)

    #This will turn it into results with 0s inserted for those not returned
    full_results = []
    for ri in result_items:
        if ri in in_results:
            full_results.append(count_dict[ri])
        else:
            full_results.append(0)
    return full_results

with open(qasm_file) as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content] 

print(content)

header = []
group = []
groups = []
footer = []
for line in content:
    if line!='':
        group.append(line)
        #print('appending ', line)
    else:
        if 'include' in group[0]:
            header = group
            group =[]
            #print('reset after header')
        elif 'measure' in group[0]:
            footer = group
            group = []
            #print('reset after footer')
        else:
            groups.append(group)
            group = []
            #print('reset after group')
if footer == []:
    footer = group

#print('header ', header)
#print('groups ', groups)
#print('footer ', footer)

independent = False
results = []
prepper = []
g_cum = []
groups = ['']+groups
for g in groups:

    if independent:
        code = header + g + footer
        #print(code)
        results.append(run_qasm(code))
    else:
        g_cum+=g
        code = header + g_cum + footer
        print("cum_code ", code)
        results.append(run_qasm(code))

        
        
print(results)
    
x = results_sonify(results,wavetype="sine", T=0.25, repeat = 3)
wavfile.write("results_son.wav",44100,x)




        

#print(full_results)
#the system takes as input a qasm file
#there must be a line gap between the header and the rest of the qasm code
#Then it goes through each line doing independent or dependent
#will do indep first
#an elemnent is a set of commands seperated by a blank line
#Indep basically inputs all 0s into the qasm element
#then measures the count
#
#Independent Version:
#So first: break qasm file down into elements: header, element1, element 2, ..., footer (measurement)
#Then run header + element1+footer, header+element2+footer
#then sonify
#
#dependent:
#So first: break qasm file down into elements: header, element1, element 2, ..., footer (measurement)
#Run header+element1+footer
#from result estimate INPUT2 = a|0>+ b|1> estimate a and b - for each qubit - based on result of 1
#Then create prepper2 = U3 funcions to recreate a and b as inputs
#Then run header+prepper2+element2+footer
#and then redo that process with the output of footer to create prepper3 etc

#Would be good to convert counts to 
