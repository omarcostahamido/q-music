include "qelib1.inc";
qreg q[3];
creg c[3];

h q[0];
h q[1];
h q[2];

//compute XOR of q1 and q2
cx q[2],q[1];

x q[0];
x q[1];
x q[2];

//ccZ gate
cx q[1],q[0];
tdg q[0];
cx q[2],q[0];
t q[0];
cx q[1],q[0];
tdg q[0];
cx q[2],q[0];
t q[0];
tdg q[1];
h q[0];
cx q[2],q[1];
tdg q[1];
cx q[2],q[1];
s q[1];
t q[2];
h q[0];

//Registers restored to original value, for the rest of Grover's
x q[0]; x q[1];
x q[2];

cx q[2],q[1];

//The part of Grover's algorithm that doesn't depend on Oracle
h q[0];
h q[1];
h q[2];

x q[0];
x q[1];
x q[2];

cx q[1],q[0];
tdg q[0];
cx q[2],q[0];
t q[0];
cx q[1],q[0];
tdg q[0];
cx q[2],q[0];
t q[0];tdg q[1];
h q[0];
cx q[2],q[1];
tdg q[1];
cx q[2],q[1];
s q[1];
t q[2];
h q[0];

x q[0];
x q[1];
x q[2];

h q[0];
h q[1];
h q[2];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];