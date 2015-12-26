import time
import sys

def toberate(datalist):
    time1 = time.time()
    user_dict,movie_dict,u_mean,i_mean=dict(),dict(),dict(),dict()
    for item in datalist:
        if user_dict.get(item[0],None)==None:
            user_dict.update({item[0]:{item[1]:item[2]}})
            u_mean.update({item[0]:item[2]})
        else:
            user_dict[item[0]].update({item[1]:item[2]})
            u_mean.update({item[0]:u_mean[item[0]]+item[2]})
        if movie_dict.get(item[1],None)==None:
            movie_dict.update({item[1]:{item[0]:item[2]}})
            i_mean.update({item[1]:item[2]})
        else:
            movie_dict[item[1]].update({item[0]:item[2]})
            i_mean.update({item[1]:i_mean[item[1]]+item[2]})
    for key in u_mean:
        u_mean.update({key:float(u_mean[key])/len(user_dict)})
    for key in i_mean:
        i_mean.update({key:float(i_mean[key])/len(movie_dict)})
    testfile = open(sys.argv[2],'r')
    testdata = list()
    for line in testfile:
        row = line.split(',')
        row[1] = row[1].rstrip('\n')
        testdata.append(row)
    testfile.close()
    if sys.argv[1]=='1':
        outfile = open('results1.csv','w')
        ratings = train_user(user_dict,testdata,u_mean)
    elif sys.argv[1]=='2':
        outfile = open('results2.csv','w')
        ratings = train_item(movie_dict,testdata,i_mean)
    else:
        outfile = open('results3.csv','w')
        user_file = open('users.csv','r')
        movie_file = open('movies.csv','r')
        user_data, movie_data = dict(),dict()
        for line in user_file:
            line = line.split(',')
            user_data.update({line[0]:line[1:]})
        for line in movie_file:
            line = line.split(',')
            movie_data.update({line[0]:line[1:]})
        user_file.close()
        movie_file.close()
        ratings = train_combine(user_dict,movie_dict,u_mean,i_mean,user_data,movie_data,testdata)
    for rating in ratings:
        outfile.write(repr(rating)+'\n')
    outfile.close()
    time2= time.time()
    print 'time = ',time2-time1
def train_user(user_dict,testdata,u_mean):
    users = user_dict.keys()
    weight = dict()
    count = 0
    ratings = list()
    for active_user,pred_movie in testdata:
        temp_weight = list()
        for user in users:
            if user != active_user and user_dict[user].has_key(pred_movie):
                if weight.get((active_user,user))==None and weight.get((user,active_user))==None:
                    commonpool = set(user_dict[active_user].keys()).intersection(user_dict[user].keys())
                    if len(commonpool) != 0:
                        weight.update({(active_user,user):Jaccard(active_user,user,commonpool,user_dict)})
                        if weight[(active_user,user)]!=0:
                            temp_weight.append([weight.get((active_user,user)),user])
                elif weight.get((active_user,user),weight.get(user,active_user))!=0:
                    temp_weight.append([weight.get((active_user,user),weight.get((user,active_user))),user])
        prediction = 0
        weight_sum = 0
        if len(temp_weight)!=0:
            temp_weight.sort(reverse = True)
            if len(temp_weight)>=100:
                temp_weight = temp_weight[:100]
            for item in temp_weight:
                weight_sum += abs(item[0])
                prediction += item[0]*(user_dict[item[1]][pred_movie]-u_mean[item[1]])
        if weight_sum!=0:
            prediction /= weight_sum
            prediction += u_mean[active_user]
        else:
            prediction = u_mean[active_user]
        prediction = int(min(max(round(prediction),1.0),5.0))
        ratings.append(prediction)
        count += 1
        print count
    return ratings
        
def train_item(movie_dict,testdata,i_mean):        
    movies = movie_dict.keys()
    weight = dict()
    count = 0
    ratings = list()
    for active_user,pred_movie in testdata:
        temp_weight = list()
        for movie in movies:
            if movie!=pred_movie and movie_dict[movie].has_key(active_user):
                if weight.get((pred_movie,movie))==None and weight.get((movie,pred_movie))==None:
                    commonusers = set(movie_dict.get(pred_movie,dict()).keys()).intersection(movie_dict[movie].keys())
###if two movies have no common user to rate the weight will be zero and not continue calculate 
                    if len(commonusers)!= 0:
                        weight.update({(pred_movie,movie):Jaccard1(pred_movie,movie,commonusers,movie_dict)})
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
                prediction += item[0]*movie_dict[item[1]][active_user]
        if weight_sum != 0:
            prediction = float(prediction)/weight_sum
        prediction = int(min(max(round(prediction),1.0),5.0))
        ratings.append(prediction)
        count += 1
        print count
    return ratings
###combine information from users and movies
def train_combine(user_dict,movie_dict,u_mean,i_mean,user_data,movie_data,testdata):  
    count = 0
    weight = dict()
    ratings = list()
    for active_user,pred_movie in testdata:
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
        prediction = int(min(max(prediction,1.0),5.0))
        ratings.append(prediction)
        count += 1
        print count
    return ratings
    
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
