import sys
import numpy as np
import math
import time
from prediction import toberate

def main():
    if len(sys.argv) < 4:
        print 'Usage1: python recommender.py U J/P/C ratings.csv'
        print 'Usage2: python recommender.py I J/P/C ratings.csv'
        print 'Usage3: python recommender.py user.csv movies.csv ratings.csv'
        print 'Usage4: python recommender.py 1/2/3 toBeRated.csv ratings.csv'  
        sys.exit(1)
    else:
        time1 = time.time()
        inputfile = open(sys.argv[3],'r')
        data0 = list()
###read file into a list in order to operate cross-validation latter
        for line in inputfile:
            row = line.split(',')
            data0.append(row[:2]+[int(row[2])])
        inputfile.close()
        if sys.argv[1]=='1' or sys.argv[1]=='2' or sys.argv[1]=='3':
            toberate(data0)
        else:
            #similarity = sys.argv[2]
            np.random.shuffle(data0)   
###K fold cross-validation
            kfold = 10
###split data into kfold equal sublist
            start = 0
            data1 = []
            for i in range(kfold):
                stop = start + len(data0)/kfold
                data1.append(data0[start:stop])
                start = stop
            metrics = 0
            for i in range(kfold):
                traindata = []
                testdata = data1[i]
                for item in data1:
                    if data1.index(item)!= i:
                        traindata.extend(item)
###data processing according to different scheme(user/item)
                traindict = dict()
                mean = dict()
                if sys.argv[1]=='U':
                    for item in traindata:
                        if traindict.get(item[0],None)== None: #no record for this user
                            traindict.update({item[0]:{item[1]:item[2]}})
                            mean.update({item[0]:item[2]})
                        else:
                            traindict[item[0]].update({item[1]:item[2]})
                            mean.update({item[0]:mean[item[0]]+item[2]})
###when traindata is fixed, mean value for each user is fixed
                    for key in mean:
                        mean.update({key:float(mean[key])/len(traindict[key])})
                    metrics += train(traindict,testdata,mean)
                elif sys.argv[1]=='I':
                    for item in traindata:
                        if traindict.get(item[1],None)==None:
                            traindict.update({item[1]:{item[0]:item[2]}})
                            mean.update({item[1]:item[2]})
                        else:
                            traindict[item[1]].update({item[0]:item[2]})
                            mean.update({item[1]:mean[item[1]]+item[2]})
                    for key in mean:
                        mean.update({key:float(mean[key])/len(traindict[key])})
                    metrics += train_item(traindict,testdata,mean)
                else:
                    user_data,movie_data = readin()
                    u_mean,i_mean = dict(),dict()
                    user_dict,movie_dict = dict(),dict()
                    for line in traindata:
                        if user_dict.get(line[0],None)==None:
                            user_dict.update({line[0]:{line[1]:line[2]}})
                            u_mean.update({line[0]:line[2]})
                        else:
                            user_dict[line[0]].update({line[1]:line[2]})
                            u_mean.update({line[0]:u_mean[line[0]]+line[2]})
                        if movie_dict.get(line[1],None)==None:
                            movie_dict.update({line[1]:{line[0]:line[2]}})
                            i_mean.update({line[1]:line[2]})
                        else:
                            movie_dict[line[1]].update({line[0]:line[2]})
                            i_mean.update({line[1]:i_mean[line[1]]+line[2]})
                    for key in u_mean:
                        u_mean.update({key:float(u_mean[key])/len(user_dict)})
                    for key in i_mean:
                        i_mean.update({key:float(i_mean[key])/len(movie_dict)})
                    metrics += train_combine(user_dict,movie_dict,u_mean,i_mean,user_data,movie_data,testdata)                 
                print 'finished fold:',i
            print metrics/kfold
        time2 = time.time() 
        print 'time:',time2-time1   
def train(traindata,testdata,mean):
    users = traindata.keys()
    weight = dict()
    rmse = 0
    count = 0
    for active_user,pred_movie,rating in testdata:
        temp_weight = list()
        for user in users:
            if user != active_user and traindata[user].has_key(pred_movie):
                if weight.get((active_user,user))==None and weight.get((user,active_user))==None: #if no record for their weight, continue calculation                
                    commonpool = set(traindata[active_user].keys()).intersection(traindata[user].keys())
###if two users have no common movie to rate the weight will be zero and not continue calculate 
                    if len(commonpool) != 0:
                        if sys.argv[2] == 'J':
###in order to deal with memory issue for this large data, each time just compute one weight between two users
                            weight.update({(active_user,user):Jaccard(active_user,user,commonpool,traindata)})
                        elif sys.argv[2] == 'P':
                            weight.update({(active_user,user):Pearson(active_user,user,mean,commonpool,traindata)})
                        elif sys.argv[2] == 'C':
                            weight.update({(active_user,user):Cosine(active_user,user,commonpool,traindata)})
                        if weight[(active_user,user)]!=0:
                            temp_weight.append([weight.get((active_user,user)),user])
###store a temp_weight list in order to get the knn users with higher similarity
                elif weight.get((active_user,user),weight.get(user,active_user))!= 0:
                    temp_weight.append([weight.get((active_user,user),weight.get((user,active_user))),user])
        prediction = 0
        weight_sum = 0
        if len(temp_weight)!=0:
            temp_weight.sort(reverse=True)
### to speed up just compute top 100 nearest neighboor/this configuration can be re-set
            if len(temp_weight)>=100:
                temp_weight = temp_weight[:100]
            for item in temp_weight:
                weight_sum += abs(item[0])
                prediction += item[0]*(traindata[item[1]][pred_movie]-mean[item[1]])
        if weight_sum!=0:
            prediction /= weight_sum
            prediction += mean[active_user]
        else:
            prediction = mean[active_user]
        prediction = min(max(prediction,1.0),5.0)
        prediction = int(round(prediction))
        rmse += (rating-prediction)**2
        count += 1
        print count
    rmse = math.sqrt(rmse/len(testdata))
    return rmse

###item_based method
def train_item(traindata,testdata,mean):        
    movies = traindata.keys()
    weight = dict()
    rmse = 0
    count = 0
    for active_user,pred_movie,rating in testdata:
        temp_weight = list()
        for movie in movies:
            if movie!=pred_movie and traindata[movie].has_key(active_user):
                if weight.get((pred_movie,movie))==None and weight.get((movie,pred_movie))==None:
                    commonusers = set(traindata.get(pred_movie,dict()).keys()).intersection(traindata[movie].keys())
###if two movies have no common user to rate the weight will be zero and not continue calculate 
                    if len(commonusers)!= 0:
                        if sys.argv[2] =='J':
                            weight.update({(pred_movie,movie):Jaccard1(pred_movie,movie,commonusers,traindata)})
                        elif sys.argv[2] == 'P':                            
                            weight.update({(pred_movie,movie):Pearson1(pred_movie,movie,mean,commonusers,traindata)})
                        elif sys.argv[2] == 'C':
                            weight.update({(pred_movie,movie):Cosine1(pred_movie,movie,commonusers,traindata)})
                        if weight[(pred_movie,movie)]!=0:
                            temp_weight.append([weight[(pred_movie,movie)],movie])
                elif weight.get((pred_movie,movie),weight.get((movie,pred_movie)))!=0:
                    temp_weight.append([weight.get((pred_movie,movie),weight.get((movie,pred_movie))),movie])
        prediction = 0
        weight_sum = 0
        if len(temp_weight)!=0:
            temp_weight.sort(reverse=True)
### to speed up just compute top 100  nearest neighboor/this configuration can be re-set
            if len(temp_weight) >= 100:
                temp_weight = temp_weight[:100]
            for item in temp_weight:
                weight_sum += abs(item[0])
                prediction += item[0]*traindata[item[1]][active_user]
        if weight_sum != 0:
            prediction = float(prediction)/weight_sum
        prediction = min(max(prediction,1.0),5.0)
        prediction = int(round(prediction))
        rmse += (rating-prediction)**2
        count += 1
        print count
    rmse = math.sqrt(float(rmse)/len(testdata))
    return rmse
###combine information from users and movies 
def train_combine(user_dict,movie_dict,u_mean,i_mean,user_data,movie_data,testdata):  
    rmse = 0
    count = 0
    weight = dict()
    for active_user,pred_movie,rating in testdata:
        temp_weight = list()
        for movie in movie_dict.keys():
            if movie!= pred_movie and movie_dict[movie].has_key(active_user):
                if weight.get((pred_movie,movie),None)==None and weight.get((movie,pred_movie),None)==None:
                    commonusers = set(movie_dict.get(pred_movie,dict()).keys()).intersection(movie_dict[movie].keys())
                    if len(commonusers)!= 0:
                        ###combine the genre information from movie data
                        alpha = 1+len(set(movie_data[movie][1].split('|')).intersection(movie_data[pred_movie][1].split('|')))
                        weight.update({(pred_movie,movie):Jaccard2(pred_movie,movie,commonusers,user_data,user_dict,movie_dict,active_user)*alpha})
                        if weight[(pred_movie,movie)]!=0:
                            temp_weight.append([weight[(pred_movie,movie)],movie])
                elif weight.get((pred_movie,movie),weight.get((movie,pred_movie)))!= 0:
                    temp_weight.append([weight.get((pred_movie,movie),weight.get((movie,pred_movie))),movie])
        prediction = 0
        weight_sum = 0
        if len(temp_weight)!=0:
            temp_weight.sort(reverse=True)
            if len(temp_weight) >= 100:
                temp_weight = temp_weight[:100]### to speed up just compute top 100  nearest neighboor/this configuration can be re-set
                
            for item in temp_weight:
                weight_sum += abs(item[0])
                prediction += item[0]*movie_dict[item[1]][active_user]
        if weight_sum != 0:
            prediction = float(prediction)/weight_sum
        else:
            predition = 1.0
        prediction = min(max(prediction,1.0),5.0)
        prediction = int(round(prediction))
        rmse += (rating-prediction)**2
        count += 1
        print count
    rmse = math.sqrt(float(rmse)/len(testdata))
    return rmse
###calculate Jaccard Similarity
def Jaccard(active_user,user,commonpool,data):
    x = len(commonpool)
    y = len(data[active_user])
    z = len(data[user])
    weight = float(x)/(y+z-x)
    return weight

def Jaccard1(pred_movie,movie,commonusers,data):
    x = len(commonusers)
    y = len(data[pred_movie])
    z = len(data[movie])
    weight = float(x)/(y+z-x)
    return weight

def Jaccard2(pred_movie,movie,commonusers,user_data,user_dict,movie_dict,active_user):###Jaccard similarity with length vector
    info = user_data[active_user]
    x,y,z= 0,0,0
    for user in commonusers:
        beta = 1 + len(set(user_data[user]).intersection(info))
        x += 1*beta
    for  user in movie_dict[pred_movie].keys():
        if user not in commonusers:
            beta = 1+len(set(user_data[user]).intersection(info))
            y += 1*beta
    for user in movie_dict[movie].keys():
        if user not in commonusers:
            beta = 1+len(set(user_data[user]).intersection(info))
            z += 1*beta
    weight = float(x)/(y+z+x)
    return weight
    
###calculate Pearson correlation similarity
def Pearson(active_user,user,mean,commonpool,data):
    sum1,sum2,sum3 = 0,0,0
    for movie in commonpool:
        sum1 += (data[active_user][movie]-mean[active_user])*(data[user][movie]-mean[user])
        sum2 += (data[active_user][movie]-mean[active_user])**2
        sum3 += (data[user][movie]-mean[user])**2
    if sum2==0 or sum3==0:
        return 0
    else:
        weight = sum1/(math.sqrt(sum2*sum3))
        return weight
def Pearson1(pred_movie,movie,mean,commonusers,data):
    sum1,sum2,sum3=0,0,0
    for user in commonusers:
        sum1 += (data[pred_movie][user]-mean[pred_movie])*(data[movie][user]-mean[movie])
        sum2 += (data[pred_movie][user]-mean[pred_movie])**2
        sum3 += (data[movie][user]-mean[movie])**2
    if sum2==0 or sum3 == 0:
        return 0
    else:
        weight = sum1/math.sqrt(sum2*sum3)
        return weight
                
###calculate cosine similarity
def Cosine(active_user,user,commonpool,data):
    sum1,sum2,sum3 = 0,0,0
    for movie in commonpool:
        sum1 += data[active_user][movie]*data[user][movie]
    for movie in data[active_user].keys():
        sum2 += data[active_user][movie]**2
    for movie in data[user].keys():
        sum3 += data[user][movie]**2
    weight = sum1/math.sqrt(sum2*sum3)
    return weight
def Cosine1(pred_movie,movie,commonusers,data):
    sum1,sum2,sum3 = 0,0,0
    for user in commonusers:
        sum1 += data[pred_movie][user]*data[movie][user]
        sum2 += data[pred_movie][user]**2
        sum3 += data[movie][user]**2
    weight = sum1/math.sqrt(sum2*sum3)
    return weight
def readin():
    user_file = open(sys.argv[1],'r')
    movie_file = open(sys.argv[2],'r')
    user_data, movie_data = dict(),dict()
    for line in user_file:
        line = line.split(',')
        user_data.update({line[0]:line[1:]})
    for line in movie_file:
        line = line.split(',')
        movie_data.update({line[0]:line[1:]})
    user_file.close()
    movie_file.close()
    return user_data,movie_data
if __name__ == '__main__':
    main()
