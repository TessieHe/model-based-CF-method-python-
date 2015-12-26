import sys
#from decimal import *
import numpy as np
import time
import random
import math

def main():
    if len(sys.argv) < 6:
        print 'Usage: python Recommender_CV.py ratings.csv dimensions learning_rate regularization N_fold'
        sys.exit(1)
    trainfile = open(sys.argv[1],'r')
    n_fold = int(sys.argv[5])
    #getcontext().prec = 4
    #Decimal(1) / Decimal(7)
    data = list()
    for line in trainfile:
        line = line.split(',')
        data.append([line[0],line[1],int(line[2])])
    trainfile.close()
    np.random.shuffle(data)
    start = 0
    data0 = []
    time1 = time.time()
    for i in range(n_fold):
        stop = start + len(data)/n_fold
        data0.append(data[start:stop])
        start = stop
    metrics = 0
    for i in range(n_fold):
        traindata = []
        testdata = data0[i]
        for item in data0:
            if data0.index(item)!=i:
                traindata.extend(item)
        metrics += train(traindata,testdata)
        print "finished fold:", i
    print round(metrics/n_fold,4)
    time2 = time.time()
    print 'time:',time2 - time1
    
def train(traindata,testdata):
    dimension = int(sys.argv[2])
    rate = float(sys.argv[3])
    lamda = float(sys.argv[4])
    #iteration = 1000
    userprofile,itemprofile = dict(),dict()
    count = 1
    iteration = 0
    while True:
        iteration += 1
        for line in traindata:
            user,item,rating = line[0],line[1],line[2]
            if userprofile.get(user)==None:
                userprofile.update({user:[random.randint(1,5)]*dimension})
            if itemprofile.get(item)==None:
                itemprofile.update({item:[random.randint(1,5)]*dimension})
            predict = min(sum([x*y for x,y in zip(userprofile[user],itemprofile[item])]),5)
            error = rating - predict
            usertemp,itemtemp = list(), list()
            for s in range(dimension):
                usertemp.append(userprofile[user][s]+2*rate*(error*itemprofile[item][s]-lamda*userprofile[user][s]))
                itemtemp.append(itemprofile[item][s]+2*rate*(error*userprofile[user][s]-lamda*itemprofile[item][s]))
            userprofile.update({user:usertemp})
            itemprofile.update({item:itemtemp})
        rmse_cur = 0
        user_count, item_count = 0,0
        for line in testdata:
            user,item,rating = line[0],line[1],line[2]
#if no existed user or item profile, set score to 1 on all dimension
            if userprofile.get(user)==None:
                #print "this user didn't appear before"
                user_count+=1 
            if itemprofile.get(item)==None:
                #print "this item didn't appear before"
                item_count+=1
            predict = sum([x*y for x,y in zip(userprofile.get(user,[1]*dimension),itemprofile.get(item,[1]*dimension))])
            predict = int(min(5,max(1,round(predict))))
            rmse_cur += (rating - predict)**2
        rmse_cur = math.sqrt(float(rmse_cur)/len(testdata))
        
        if count > 0:
            count -= 1
            rmse_prev = rmse_cur
            continue
        elif abs(rmse_cur-rmse_prev) < 0.000001:
            print user_count,item_count
            print rmse_cur
            print iteration
            return rmse_cur
        else:
            iteration += 1
            rmse_prev = rmse_cur
            continue            
if __name__ == '__main__':
    main()
