# DVR-project
An implementation of DVR protocol.

Instructions for running:
DVR.py file simulates a router and will accept the following command line arguments:
  DVR.py <router-id> <port-no> <router-config-file>
For example:
  DVR.py A 5000 ConfigA.txt
  
The router configuration file, for example ConfigA.txt, is the configuration file for Router A that has the following details:
2
B 6.5 5001
F 2.2 5005

The first line of this file indicates the number of neighbors for Router A. Note that it is not the
total number of routers in the network. Following this, there is one line dedicated to each
neighbor. It starts with the neighbor ID, followed by the cost to reach this neighbor and finally
the port number that this neighbor is using for listening. For example, the second line in the
configA.txt above indicates that the cost to neighbor B is 6.5 and this neighbor is using port
number 5001 for receiving distance-vector packets. These three fields should be separated by a single white
space between two successive fields in each line of the configuration file. Further, the link
costs should be consistent in both directions, i.e., if the cost from A to B is 6.5, then the link from
B to A will also have a cost of 6.5
