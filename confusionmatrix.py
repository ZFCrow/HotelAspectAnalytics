from sklearn.metrics import confusion_matrix,classification_report
import os
import pandas as pd
import random
import Fullflow
import time

def categoryCMGUI(df,hotel):
    #confusion matrix 
    cm = confusion_matrix(df['Category'],df['actual'])
    print(cm)
    time.sleep(10)
    # classification report
    report = classification_report(df['Category'],df['actual'])     
    #compute accuracy 
    try:
        #take out accuracy score from confusion matrix
        accuracy = cm.diagonal().sum()/cm.sum()
        accuracy = accuracy * 100
    except:
        accuracy = 'no data'
    
    cmReportGeneration(f'DatabyHotel/{hotel} ReviewData/categoryCM.txt', cm, report, accuracy)
    #return the filepath
    return f'DatabyHotel/{hotel} ReviewData/categoryCM.txt'


def categoryCM():
    #read the hotel folder and give me 1 random hotel 
    if os.path.exists('DatabyHotel'):
        hotel = os.listdir('DatabyHotel')
        hotel = random.choice(hotel)
        #hotel = 'Aloft Singapore Novena ReviewData'
        print(hotel)
        hotelname = hotel[:-11]
        print(hotelname)
        time.sleep(10)

    # actual values vs predicted values 

    #print the desc and category only 
    try:
        df = pd.read_csv(f'DatabyHotel/{hotel}/hotelData.csv')
        df = df[['desc','Category']]
        #df = df[['desc','Category','reviewRatings', 'polarity']]

    except: 
        Fullflow.flow1(hotelname)
        df = pd.read_csv(f'DatabyHotel/{hotel}/hotelData.csv')
        df = df[['desc','Category']]
        #df = df[['desc','Category','reviewRatings', 'polarity']]

    #empty df
    df5samples = pd.DataFrame()
    # random 5 rows from each aspect
    for i in df['Category'].unique():
        df1 = df[df['Category'] == i]
        try:
            df1 = df1.sample(5)
        except: 
            #sample size stated is larger than population size
            df1 = df1.sample(len(df1))
        df5samples = df5samples.append(df1,ignore_index=True)

    print (df5samples)
    #mix up the df
    df = df5samples.sample(frac=1).reset_index(drop=True)
    time.sleep(15)

    #iterow df top 10 column to print the desc 
    for index,row in df.iterrows():
        # print(row['desc'], row['Category'])
        print (f"{row['desc']}\npredicted category: {row['Category']}")
        aspects = list(df['Category'].unique())
        aspect = random.choice(aspects)
        input1 = aspect
        #add the input to the df categoryActual 
        df.loc[index,'categoryActual'] = input1




    #confusion matrix 
    cm = confusion_matrix(df['Category'],df['categoryActual'])
    print(cm)
    time.sleep(10)
    # classification report
    report = classification_report(df['Category'],df['categoryActual'])     
    #compute accuracy 
    try:
        #take out accuracy score from confusion matrix
        accuracy = cm.diagonal().sum()/cm.sum()
        accuracy = accuracy * 100
    except:
        accuracy = 'no data'
    
    cmReportGeneration(f'DatabyHotel/{hotel}/categoryCM.txt', cm, report, accuracy)


def SpecificpolarityCM(hotel):
    #this is for polarity, for each hotel folder, look at hoteldata.csv and get the polarity as predictedvalue and reviewRatings as true value
    # reviewrating 2.5 and above is positive, below is negative
    path = f'DatabyHotel/{hotel} ReviewData'

    df = pd.read_csv(f'{path}/hotelData.csv')
    df = df[['reviewRatings', 'polarity']]
    df = df.dropna()
    df['polarity'] = df['polarity'].apply(lambda x: 1 if x > 0 else 0)
    # turn the reviewRatings to just the first digit as int, then turn it to 1 if its above 2.5, 0 if its below 2.5
    df['reviewRatings'] = df['reviewRatings'].astype(str).str[0].astype(int)
    df['reviewRatings'] = df['reviewRatings'].apply(lambda x: 1 if x > 2.5 else 0)
    print(df)
    cm = confusion_matrix(df['reviewRatings'],df['polarity'])
    report = classification_report(df['reviewRatings'],df['polarity'])
    #get the accuracy score
    try:
        tp, fp, fn, tn = confusion_matrix(df['reviewRatings'],df['polarity']).ravel()
    except:
        tp, fp, fn, tn = 0,0,0,0

    print('accuracy score')
    if tp == 0 and fp == 0 and fn == 0 and tn == 0:
        accuracy = 'no data'
    else:
        accuracy = (tp + tn)/(tp+fp+fn+tn)
        #turn it to percentage
        accuracy = accuracy * 100

    cmReportGeneration(f'{path}/polarityCM.txt', cm, report, accuracy)



def polarityCM():
    #* this runs SpecificpolarityCM for every hotel folder in DatabyHotel
    path = 'DatabyHotel'
    for i in os.listdir(path):
        #run specific polarityCM for each hotel folder
        SpecificpolarityCM(i[:-11])

def cmReportGeneration(fullpath, cm , report , accuracy):
        # save all 3 into 1 file into the hotel folder
    with open(f'{fullpath}', 'w') as f:
        f.write(f'confusion matrix: \n{cm}\n')
        f.write(f'classification report: \n{report}\n')
        f.write(f'accuracy score: {accuracy}%\n')
        #explain the f1 score, precision and recall and support and acc score

        f.write('Explanation Generated by Chatgpt.\n')
        f.write('''f1 score:\nIt is the harmonic mean of precision and recall. It balances the trade-off between precision and recall.
It is particularly useful when you want to find an optimal balance between false positives and false negatives.\n\n''')
        
        f.write('''precision:\nmeasures the accuracy of positive predictions made by a model.
It is the ratio of true positive predictions to all positive predictions (true positives + false positives).
High precision means that the model makes few false positive errors.\n\n''')
        
        f.write('''recall:\nmeasures the models ability to find all the positive instances in the dataset. 
It is the ratio of true positive predictions to all actual positive instances (true positives + false negatives). 
High recall means the model does not miss many positive instances.\n\n''')
        
        f.write('''support:\nIt represents the number of occurrences of each class in the dataset. 
It helps provide context about the distribution of classes.\n\n''')
        
        f.write(f'accuracy score:\nIt is the ratio of correct predictions to total predictions made.')

        #put everything in 1 f.write

        f.close()


if __name__ == "__main__":
    categoryCM()
    #polarityCM()