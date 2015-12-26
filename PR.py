import sys
import numpy as np 


#to decide whether current row is all zero element
def all_of_zeros(row):
    for element in row:
        if element != 0:
            return False
    return True

#initialization to caculate steady-state probability
#start point doesn't impact algorithm convergence
def initialization(n_nodes):
    x = np.zeros(n_nodes)
    x[0] = 1
    return x

def main():
    if len(sys.argv) < 1:
        print 'usage: python PR.py input_filename output_filename'
        sys.exit(1)
    else:
        inputfilename = sys.argv[1]
        outputfilename = sys.argv[2]
        
    #read in nodes and edges
    with open(inputfilename) as f:
        n_nodes,n_edges = map(int,tuple(f.readline().split()))
        lines = f.readlines()
    f.close()
    
    #store edges information into a list of lists
    edges = []
    for line in lines:
        edge = [map(int,line.split())]
        edges.extend(edge)
        
    #create adjacency matrix, if there is an edge from i to j, matrix[i][j]=1
    #duplicate edges will be counted 
    matrix = np.zeros((n_nodes,n_nodes),dtype = np.float)
    for i in range(n_edges):
        matrix[edges[i][0]-1][edges[i][1]-1] += 1
        
    alpha = 0.85
    
    #compute transition probability matrix
    for i in range(matrix.shape[0]):
        #if there is no edge from i to any other nodes, set all elements in this row to 1/n_nodes
        if all_of_zeros(matrix[i]):
            matrix[i] = np.add(matrix[i],1.0/matrix.shape[1])
        else:
            temp = np.sum(matrix[i])
            matrix[i] = np.divide(matrix[i],temp)
            #transition matrix with teleporting
            matrix[i] = matrix[i].dot(alpha)
            matrix[i] = np.add(matrix[i],float(1-alpha)/matrix.shape[1])

    #compute pagerank with power method
    cur_step = initialization(n_nodes)
    while(True):
        next = np.dot(cur_step,matrix)
        #default setting: rtol=1e-05, atol=1e-08; if current stemp is approximately equal to previous step, stop computing and get result
        if np.allclose(next,cur_step):
            break
        else:
            cur_step = next
            
    #record the result for steady rate in the output file
    output = open(outputfilename,'w')
    for element in next:
        output.write(str(element)+'\n')
    output.close()
    print 'Done'
if __name__ == '__main__':
    main() 
