import sys
import random

def main():
    if len(sys.argv) < 6:
        print 'Usage: python Recommender.py ratings.csv toBeRated.csv dimensions learning_rate regularization'
        sys.exit(1)
    trainfile = open(sys.argv[1],'r')
    dimension = int(sys.argv[3])
    rate = float(sys.argv[4])
    lamda = float(sys.argv[5])
    iteration = 1000
    userprofile,itemprofile = dict(),dict()
    for i in range(iteration):
        for line in trainfile:
            line = line.split(',')
            user,item,rating = line[0],line[1],int(line[2])
            if userprofile.get(user)==None:
                userprofile.update({user:[random.randint(1,5)]*dimension})
            if itemprofile.get(item)==None:
                itemprofile.update({item:[random.randint(1,5)]*dimension})
            predict = min(sum([x*y for x,y in zip(userprofile[user],itemprofile[item])]),5)
            error = rating - predict
            usertemp,itemtemp = list(),list()
            for s in range(dimension):
                usertemp.append(userprofile[user][s]+2*rate*(error*itemprofile[item][s]-lamda*userprofile[user][s]))
                itemtemp.append(itemprofile[item][s]+2*rate*(error*userprofile[user][s]-lamda*itemprofile[item][s]))
            userprofile.update({user:usertemp})
            itemprofile.update({item:itemtemp})
        print i
    testfile = open(sys.argv[2],'r')
    output = open('result.csv','w')
    for line in testfile:
        line = line.split(',')
        predict = sum([x*y for x,y in zip(userprofile[line[0]],itemprofile[line[1][:-1]])])
        predict = int(min(5,max(1,round(predict))))
        output.write(repr(predict)+'\n')
    trainfile.close()
    testfile.close()
    output.close()
if __name__ == '__main__':
    main()

                                
