import pandas as pd
import numpy as np
import spacy 
import classy_classification
import os
from textblob import TextBlob
from datetime import datetime
import threading





class AnalysisReportGeneration():

    def __init__(self):
        self.isTextblob = False
        self.isClassified = False
        self.reportGenerated = False
        self.hotelData = 'hotelData.csv'
        self.aspects = ['Cleaniness', 'Services', 'Value', 'Amenities', 'Location', 'General']
        self.dfCollection = []
        self.threads = []

    #? This function will create a csv file for each hotel and each monthyear
    #? unless a hotel name is specified, then it will create a csv file for that hotel only
    def breakdown(self, hotel = None):

        print('Breakdown() function!')
        # we gonna break down the tripadvisor.csv into their own hotels, separated by monthsyear and create a csv for each 
        df = pd.read_csv('tripadvisor.csv') 

        if hotel != None:
            # we are looking to update an existing hotel csv file or we are looking to create a specific hotel folder
            if os.path.exists(f'DatabyHotel/{hotel} ReviewData/{self.hotelData}'):
                # if it exist already, i am skipping the save, if not i will create the directory and save it
                print('file found, updating the file!')
                # filter the df to just that hotel 
                df = df[df['hotelname'] == hotel]
                df1 = pd.read_csv(f'DatabyHotel/{hotel} ReviewData/{self.hotelData}')
                #append those rows that doesnt exist in the df1
               #! df1 = df1.append(df[~df['desc'].isin(df1['desc'])])
                #? use concat instead of append as append is deprecating soon!
                df1 = pd.concat([df1,df[~df['desc'].isin(df1['desc'])]],ignore_index=True)
                df1.to_csv(f'DatabyHotel/{hotel} ReviewData/{self.hotelData}',index=False)
            
            else:
                #create the directory 
                os.makedirs(f'DatabyHotel/{hotel} ReviewData',exist_ok=True)
                df = df[df['hotelname'] == hotel]
                df.to_csv(f'DatabyHotel/{hotel} ReviewData/{self.hotelData}',index=False)
                print(f'created {hotel} {self.hotelData} along with the directory')
        else:

            for i in df['hotelname'].unique(): #? creates a df for each hotel
                #remove the open and close brackets from the hotel name
                #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
                df1 = df.copy()
                df1 = df1[df1['hotelname'] == i]
                
                df1['reviewDate'] = pd.to_datetime(df1['reviewDate'],format='%B %Y',errors='coerce')

                df1 = df1.sort_values(by=['reviewDate'])
                #! Format the 'reviewDate' column as '%B %Y' for display
                df1['reviewDate'] = df1['reviewDate'].dt.strftime('%B %Y')

                df1.reset_index(drop=True, inplace=True)

                #? creates a csv for each hotel
                #?=================================================================================================
                #?=================================================================================================
                try:
                    # if it exist already, i am skipping the save, if not i will create the directory and save it
                    if os.path.exists(f'DatabyHotel/{i} ReviewData/{self.hotelData}'):
                        print(f'hoteldata file found for {i}, no overwriting is needed!')
                        continue #? continue to the next hotel since this csv exist

                    df1.to_csv(f'DatabyHotel/{i} ReviewData/{self.hotelData}', index=False) #? creates a csv for each hotel
                    print(f'created {i} {self.hotelData}')

                except:
                    #create the directory 
                    print(f'creating directory for {i}')
                    print(f'{i}')
                    os.makedirs(f'DatabyHotel/{i} ReviewData',exist_ok=True)

                    try: #! oasia somehow cant be saved inside the directory i created 
                        df1.to_csv(f'DatabyHotel/{i} ReviewData/{self.hotelData}', index=False)

                    except:
                        print(f'still got error for {i}')
                       #df1.to_csv(f"DatabyHotel/{i} ReviewData/Oasia Hotel Downtown, Singapore By Far East Hospital.csv", index=False)
                        #change directory to the directory i created
                        # os.chdir(f'DatabyHotel/{i} ReviewData')
                        # df1.to_csv(f'{i}.csv', index=False)
                        # os.chdir('../../')

                        #create an error directory
                        #os.makedirs(f'DatabyHotel/Error',exist_ok=True)
                        #df1.to_csv(f'DatabyHotel/Error/{i}.csv', index=False)
   
                    print(f'created {i} {self.hotelData} along with the directory')

                #?=================================================================================================
                #?=================================================================================================



    def textblobSentimentAnalysisForEverything(self):

        df = pd.read_csv('tripadvisor.csv')
        df['polarity'] = df['desc'].apply(lambda x: TextBlob(x).sentiment.polarity)
        df['subjectivity'] = df['desc'].apply(lambda x: TextBlob(x).sentiment.subjectivity)
        df.to_csv('tripadvisor.csv',index=False)

        

#*===================================================================================================================================================================
#* 
#*===================================================================================================================================================================

    def normalise_score_polarity(self,score):
            return ((score + 1) / 2) * 100

    def normalise_score_subjectivity(self,score):
            return score * 100

    #? This function will apply textblob sentiment analysis on the desc column of each csv file in the stated hotel
    def textblobSentimentAnalysis(self, hotelname):
        # read every csv file in the data folder and apply textblob sentiment analysis on the desc column
        print('in textblobSentimentAnalysis')
        try:
            folders = f'DatabyHotel/{hotelname} ReviewData'

            if not os.path.exists(folders):
                    raise FileNotFoundError(f'Data folder not found: {folders}')
            
        except FileNotFoundError as e:
            print(e)
            print('No data found')
            return

        file = f'Databyhotel/{hotelname} ReviewData/{self.hotelData}'
        df = pd.read_csv(f'{file}')   
        # #! for files in os.listdir(f'Data/{folders}'):
        # for files in os.listdir(f'{folders}'):
        #     if files == f'{hotelname}.csv':
        #         #!df = pd.read_csv(f'Data/{folders}/{files}')
        #         df = pd.read_csv(f'{folders}/{files}')
        df['polarity'] = df['desc'].apply(lambda x: TextBlob(x).sentiment.polarity)
        df['subjectivity'] = df['desc'].apply(lambda x: TextBlob(x).sentiment.subjectivity)
        #df.to_csv(f'Data/{files}',index=False)

        df['Normalized_Polarity'] = df['polarity'].apply(self.normalise_score_polarity)
        df['Normalized_Subjectivity'] = df['subjectivity'].apply(self.normalise_score_subjectivity)
        df['Normalized_Polarity_POS_NEG'] = df['polarity'].apply(lambda x: abs(x)).apply(self.normalise_score_subjectivity)

        df.to_csv(f'{file}',index=False)

        self.isTextblob = True



    def classy(self, df,nlp = None):

        #* create a filtered df for rows with no category columns
        try:
            df1 = df[df['Category'].isnull()] #pandas
            print(df1)
            print('comparing df now')


            df1["Category"] = df1["desc"].apply(lambda x: max(nlp(x)._.cats, key=nlp(x)._.cats.get))

            print('category successfully categorized for those that are not categorized')
            #* update the original df with the filtered df
            df.update(df1)
            #df.to_csv(f'{file}',index=False)
            self.dfCollection.append(df)
            return

        except Exception as e:
            print(e)
            
            # means theres no category column, means we need to create it
            print('at the error loop now')
            print(df)

            #* create a category column for each review in the csv file
            df["Category"] = df["desc"].apply(lambda x: max(nlp(x)._.cats, key=nlp(x)._.cats.get))
            print('category successfully categorized for whole DF')
            self.dfCollection.append(df)
            print('appended df to dfCollection')
            #print(self.dfCollection)
            return 

    def classyClassificationAnalysis(self, hotelname):
        #* read the hoteldata.csv, if null skip this whole function, if not load the model and apply classyClassification on the desc column(classy function)
        file = f'Databyhotel/{hotelname} ReviewData/{self.hotelData}'
        df = pd.read_csv(f'{file}')
 
        # if df category is empty, means it is already classified, skip this function
        try:
            df = df[df['Category'].isnull()]
            print(df)
         

            if df.empty:
                print('it is empty!')
                self.isClassified = True
                return
        except:
            #category column doesnt exist, we proceed 
            pass

        df = pd.read_csv(f'{file}')


        #! prep trainingData
        data = {} # dict - > training Data! 

        #read the csv files in the TrainingData folder, every file only has1 column
        for trainingDataFile in os.listdir("TrainingData"):
            if trainingDataFile.endswith(".csv"):
                #print(file)
                dfTrainingData = pd.read_csv(f"TrainingData/{trainingDataFile}",delimiter=";",header=None)

                #the file name is the key of the dictionary, use column 0 
                #append the list to the existing list in the dictionary
                try:
                    data[trainingDataFile[:-4]].extend(dfTrainingData[dfTrainingData.columns[0]].tolist())
                except:
                    data[trainingDataFile[:-4]] = dfTrainingData[dfTrainingData.columns[0]].tolist()

        for key,value in data.items():
            print(f'{key} : {len(value)}')

        print('loading Training data into classyClassification')

        nlp = spacy.load('en_core_web_md')
        nlp = spacy.blank("en")
        nlp.add_pipe(
            "classy_classification", 
            config={
                "data": data, 
                "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "device": "cpu"
            }
        )

        print('proceeding to read the hoteldata file now')
        
   

#!===========================================================================
#? Threading 
#!===========================================================================
        #break it down into 2 df 
        rowsPerDF = df.shape[0] // 2
        smallerDF = [] 
        if rowsPerDF == 0:
            rowsPerDF = 1

        for i in range(0,df.shape[0],rowsPerDF):
            smallerDF.append(df[i:i+rowsPerDF])
        print(f'length of smallerDF is {len(smallerDF)}')

        for i, smalldf in enumerate(smallerDF):
            print(f'========================={i}=========================')
            print(smalldf)
            #create a thread to run the classy function
            t = threading.Thread(target=self.classy, args=(smalldf,nlp))
            t.start()
            self.threads.append(t)


        print('waiting for all threads to finish')
        #print(threading.enumerate())
        print(f'number of threads using: {len(self.threads)} ')

        
        for t in self.threads:
            t.join()
       
        print('all threads finished')
        #concat all the df in dfCollection
        df = pd.concat(self.dfCollection,ignore_index=True)
        print(df)
        print(file)
        df.to_csv(f'{file}',index=False)
        print('file saved')
   
        

        self.isClassified = True
    
    #function to print out reviews for each category where their polarity is more than or less than 0 
    def positiveNegativeReviews(self,hotelname):
        df = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/{self.hotelData}')
        dfPositive = df[df['polarity'] > 0]
        dfNegative = df[df['polarity'] < 0]
        return dfPositive,dfNegative


    #this function is for the calculations done in the report generation
    def PercentageCalculation(self,df1,reportDF,year = None):
        dictStorage = {}
        if year != None:
            df2 = df1[df1['reviewDate'].dt.year == year]
            print (f'created df for the year {year}')
            print('==============================================================================')
            print(df2)
            print('==============================================================================')
        else:
            df2 = df1
            pass

        
        # #* count the number of reviews for each aspect in aspects
        for i in self.aspects:
            dictStorage[i] = df2[df2['Category'] == i].shape[0]

        # #* count the number of reviews for each aspect in aspects(if the review has a polarity of more than 0, it is positive)
        for i in self.aspects:
            dictStorage[f'{i}Positive'] = df2[(df2['Category'] == i) & (df2['polarity'] > 0)].shape[0]

        # #*calc avg normalized polarity
        for i in self.aspects:
            dictStorage[f'{i}_np_avg'] = (df2[(df2['Category'] == i)]['Normalized_Polarity'].sum()) / dictStorage[i]

        # #*calc avg normalized subjectivity
        for i in self.aspects:
            dictStorage[f'{i}_ns_avg'] = (df2[(df2['Category'] == i)]['Normalized_Subjectivity'].sum()) / dictStorage[i]

        # #*calc avg normalized polarity for Positive only
        for i in self.aspects:
            dictStorage[f'{i}_np_pos_avg'] = (df2[(df2['Category'] == i) & (df2['polarity'] > 0)]['Normalized_Polarity_POS_NEG'].sum()) / dictStorage[f'{i}Positive']

        # #*calc avg normalized polarity for Negative only
        for i in self.aspects:
            dictStorage[f'{i}_np_neg_avg'] = (df2[(df2['Category'] == i) & (df2['polarity'] < 0)]['Normalized_Polarity_POS_NEG'].sum()) / (dictStorage[i] - dictStorage[f'{i}Positive']) 

        # #*calc avg normalized subjectivity for Positive only
        for i in self.aspects:
            dictStorage[f'{i}_ns_pos_avg'] = (df2[(df2['Category'] == i) & (df2['polarity'] > 0)]['Normalized_Subjectivity'].sum()) / dictStorage[f'{i}Positive']

        # #*calc avg normalized subjectivity for Negative only
        for i in self.aspects:
            dictStorage[f'{i}_ns_neg_avg'] = (df2[(df2['Category'] == i) & (df2['polarity'] < 0)]['Normalized_Subjectivity'].sum()) / (dictStorage[i] - dictStorage[f'{i}Positive'])
 
        #* calculate the overall avg percentage of positive & negative review for each aspect for each year, if the total is 0 then it is 0

        #Define weighting factors to calculate percentage
        polarity_weight = 0.6
        subjectivity_weight = 0.4




        # do all in a loop instead 

        for i in self.aspects:
            if dictStorage[i] == 0:
                dictStorage[f'{i}Percentage'] = 0
                dictStorage[f'{i}Percentage_pos'] = 0
                dictStorage[f'{i}Percentage_neg'] = 0
            else:
                dictStorage[f'{i}Percentage'] = (dictStorage[f'{i}_np_avg'] * polarity_weight) + (dictStorage[f'{i}_ns_avg'] * subjectivity_weight)
                dictStorage[f'{i}Percentage_pos'] = (dictStorage[f'{i}_np_pos_avg'] * polarity_weight) + (dictStorage[f'{i}_ns_pos_avg'] * subjectivity_weight)
                dictStorage[f'{i}Percentage_neg'] = (dictStorage[f'{i}_np_neg_avg'] * polarity_weight) + (dictStorage[f'{i}_ns_neg_avg'] * subjectivity_weight)

            
        
        #* append it to reportDF 
        if year: 
            #? create a dictionary for each year's data then concat it with the reportDF (replaces my previous append instead as append is deprecating soon!)



            #do whatever on top in a dictionary instead and a loop

            yeardata = {'year':year}
            for i in self.aspects:
                yeardata[f'{i}'] = dictStorage[f'{i}Percentage']
                yeardata[f'{i}_POS'] = dictStorage[f'{i}Percentage_pos']
                yeardata[f'{i}_NEG'] = dictStorage[f'{i}Percentage_neg']
                yeardata[f'{i}Numbers'] = f'{dictStorage[f"{i}Positive"]}/{dictStorage[i]}'
            
            YearDF = pd.DataFrame(yeardata, index=[0])
            reportDF = pd.concat([reportDF,YearDF],ignore_index=True)

        else: 

            yeardata = {'year':'General'}
            for i in self.aspects:
                yeardata[f'{i}'] = dictStorage[f'{i}Percentage']
                yeardata[f'{i}Numbers'] = f'{dictStorage[f"{i}Positive"]}/{dictStorage[i]}'


            YearDF = pd.DataFrame(yeardata, index=[0]) 
            reportDF = pd.concat([reportDF,YearDF],ignore_index=True)
        print(reportDF)
        return reportDF


    def reportGenerationperYear(self, hotelname): #if its doing by year, i need to create a df for each year and append it to a df, then save it as a csv file
        #* look at the csv files of the hotelname, create a df for every year 
        #* calculate the number of positive reviews for each aspect and get the percentage of it
        #* append it to a df, then save it as a csv file (aspect1,aspect2,aspect3,aspect4,monthyear)
        #* after it go through all the monthyear csv files, save it to a csv file
        
        aspects = ['Cleaniness','Amenities','Service','Value','General','Location']
        #reportDF = pd.DataFrame(columns=['year','Cleaniness','Amenities','Service','Value','Location','General'])
        reportDF = pd.DataFrame(columns=['year','Cleaniness','Cleaniness_POS','Cleaniness_NEG','CleaninessNumbers','Amenities','Amenities_POS','Amenities_NEG','AmenitiesNumbers','Services','Services_POS', 'Services_NEG','ServicesNumbers','Value','Value_POS','Value_NEG','ValueNumbers','Location','Location_POS','Location_NEG','LocationNumbers','General','General_POS','General_NEG','GeneralNumbers'])
        folders = f'DatabyHotel/{hotelname} ReviewData/{self.hotelData}'


        df1 = pd.read_csv(f'{folders}')

        # transform into 1 df for each year 
        df1['reviewDate'] = pd.to_datetime(df1['reviewDate'],format='%B %Y',errors='coerce')
        firstyear = df1['reviewDate'].min().year

        #create a df for this year and append it to reportDF
        for i in range (firstyear,datetime.now().year+1):

            reportDF = self.PercentageCalculation(df1,reportDF,i)

  

    
        #* convert the year column to date time and sort it by year
        
        #remove all .0s in the year column
        reportDF['year'] = reportDF['year'].astype(int)
        print('this is the reportDF after percentage calculation')
        print('===================================================')
        print (reportDF)
        #!==========
        reportDF['year'] = pd.to_datetime(reportDF['year'],format='%Y')
        reportDF = reportDF.sort_values(by=['year'])
        
        #* convert it back to just %Y string for display
        reportDF['year'] = reportDF['year'].dt.strftime('%Y')

        
        #* count for overall
        print('==============================================================================')
        print('=======================This is the overall df from earliest year till present===================')
        print(df1)
        print('==============================================================================')
        print('==============================================================================')

        reportDF = self.PercentageCalculation(df1,reportDF)


        print('Final reportDF')
        print('===================================================')
        print(reportDF)
        reportDF.to_csv(f'DatabyHotel/{hotelname} ReviewData/AnalysisReport.csv',index=False)
#*===================================================================================================================================================================  
#*===================================================================================================================================================================





    def testflow(self,hotelname):
        try:
            self.textblobSentimentAnalysis(hotelname) # this will create a polarity and subjectivity column for each csv file in the hotel

            if self.isTextblob == True:
                
                self.classyClassificationAnalysis(hotelname) # this will create a category column for each csv file in the hotel
            else:
                print('textblobSentimentAnalysisPerHotel1 didnt run')
                raise

            if self.isClassified == True:

                self.reportGenerationperYear(hotelname) # this will create a csv file for the hotel with the percentage of positive reviews for each aspect in each monthyear
            else:
                print('classyClassificationPerHotel1 didnt run')
                raise

        except Exception as e:
            print(e)
            print('failed!')






if __name__ == '__main__':
    x = AnalysisReportGeneration()
    x.breakdown('Raffles Hotel Singapore')
    x.testflow('Raffles Hotel Singapore')





