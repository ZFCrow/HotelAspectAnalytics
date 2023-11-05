from AnalysisReportGeneration import AnalysisReportGeneration
from Scraper import Scraper
from ReportAnalysis import ReportAnalysis
import AINLP
import threading
import os
import pandas as pd
import confusionmatrix

#! flow 1 (i have the hotel folder already, so i will do the 3 functions + subplots)

def flow1(hotel, years = 3):
    try:
        x = AnalysisReportGeneration()
        x.breakdown(hotel)
        x.testflow(hotel)
        x = ReportAnalysis()
        regressionTrendOverall, summaryResponseRegressionGraph = x.newsubplot(hotel,yearsofprediction=int(years))
        bargraph, summaryResponseBarGraph= x.bargraph(hotel)
        regressionTrendPos, summaryResponseRegressionGraphPos = x.newsubplot_pos(hotel,yearsofprediction=int(years))
        regressionTrendNeg, summaryResponseRegressionGraphNeg = x.newsubplot_neg(hotel,yearsofprediction=int(years))
        try:
            confusionmatrix.SpecificpolarityCM(hotel)
        except Exception as e:
            print(e)
        return regressionTrendOverall, bargraph, summaryResponseRegressionGraph, summaryResponseBarGraph, regressionTrendPos, summaryResponseRegressionGraphPos, regressionTrendNeg, summaryResponseRegressionGraphNeg
    except Exception as e:
        print(e)

#! flow 2 user wants to updateScrape a hotel, so i do specificscrape, breakdown(), and then the 3 functions + subplots

def flow2(hotel, years=3):
    try:
        #del all chatgpt.csv in the hotel folder
        deletegptcsv(hotel)
        print('gpt deleted')
        x = Scraper()
        #x.start(func = x.specificHotelScrape, funcARGs = 'Holiday Inn Express Singapore Clarke Quay')
        x.threadhandlers(timer = 50, hotelname = hotel, update = True)
        x = AnalysisReportGeneration() #1026 
        x.breakdown(hotel)
        x.testflow(hotel)
        x = ReportAnalysis()
        regressionTrendOverall, summaryResponseRegressionGraph = x.newsubplot(hotel,yearsofprediction=int(years))
        bargraph, summaryResponseBarGraph  = x.bargraph(hotel)

        regressionTrendPos, summaryResponseRegressionGraphPos = x.newsubplot_pos(hotel,yearsofprediction=int(years))
        regressionTrendNeg, summaryResponseRegressionGraphNeg = x.newsubplot_neg(hotel,yearsofprediction=int(years))
        try:
            confusionmatrix.SpecificpolarityCM(hotel)
        except Exception as e:
            print(e)

        return regressionTrendOverall, bargraph, summaryResponseRegressionGraph, summaryResponseBarGraph, regressionTrendPos, summaryResponseRegressionGraphPos, regressionTrendNeg, summaryResponseRegressionGraphNeg
    except Exception as e:
        print(e)


#! flow 3 user wants to update the entire data of reviews, so i will do threadhandler into 3 scrapers.

def flow3(timervalue):
    try: 
        x = Scraper()
        x.threadhandlers(timer = timervalue)
    except Exception as e:
        print(e)

#! flow 4 breakdown() , this will look into tripadvisor csv and breakdown per hotel into the databyhotel folder
# try:
#     x = AnalysisReportGeneration()
#     x.breakdown()
# except Exception as e:
#     print("?")
#     print(e)

#! flow 5 (i have the hotel folder already for both hotel, so i will do the function to compare the bargrpaphs
def flow5(hotel1, hotel2):
    print("in flow 5")
    print(hotel1)
    print(hotel2)
    try:
        x = AnalysisReportGeneration()

        for i in (hotel1,hotel2):
            x.breakdown(i)
            x.testflow(i)

        x = ReportAnalysis()

        bargraph, compareSummary = x.bargraph_cmp(hotel1,hotel2)

        return bargraph, compareSummary
    except Exception as e:
        print(e)

def newhotelScrapeflow(hotel,years = 3 ):
    try:
        x = Scraper()
        x.threadhandlers(timer = 900, hotelname = hotel, update = False)
        # go and read csv and get the hotel name 
        df = pd.read_csv('tripadvisor.csv')
        #last row 
        lastrow = df.iloc[-1]
        hotel = lastrow['hotelname']
        x = AnalysisReportGeneration() #1026 
        x.breakdown(hotel)
        x.testflow(hotel)
        x = ReportAnalysis()
        regressionTrendOverall, summaryResponseRegressionGraph = x.newsubplot(hotel,yearsofprediction=int(years))
        bargraph, summaryResponseBarGraph= x.bargraph(hotel)
        regressionTrendPos, summaryResponseRegressionGraphPos = x.newsubplot_pos(hotel,yearsofprediction=int(years))
        regressionTrendNeg, summaryResponseRegressionGraphNeg = x.newsubplot_neg(hotel,yearsofprediction=int(years))
        try:
            confusionmatrix.SpecificpolarityCM(hotel)
        except Exception as e:
            print(e)
        return regressionTrendOverall, bargraph, summaryResponseRegressionGraph, summaryResponseBarGraph, regressionTrendPos, summaryResponseRegressionGraphPos, regressionTrendNeg, summaryResponseRegressionGraphNeg
    except Exception as e:
        print(e)

#! flow 6 Review summary 
def flow6(hotel):
    try:
        response_df= AINLP.analyze_hotel_reviews(hotel)

        return response_df
    except Exception as e:
        print(e)

def runatyourownrisk():
    thread = []
    # for every hotel reviewdata folder, i do the flow1 (3 threads)
    try:
        for i in os.listdir('DatabyHotel'):
            newi = i[:-11]

            print(newi)
            #print(newi1)
            
            x = threading.Thread(target=flow1, args=(newi,))
            x.start()
            thread.append(x)
            # stop it at 5 then continue after a thread is done 
            if len(thread) == 3:
                for i in thread:
                    i.join()
                thread = []


    except Exception as e:
        print(e)



def deletegptcsv(hotel):
    print(os.listdir('DatabyHotel'))
    path = f'DatabyHotel/{hotel} ReviewData'
    #under a certain condition, i will delete all chatgpt.csv found in the hotel folder
    if os.path.exists(f'DatabyHotel'):
        print('found DatabyHotel folder')
        
        if f'{hotel} ReviewData' in os.listdir('DatabyHotel'):
            print(f'found {hotel} reviewData folder' )

            for i in os.listdir(path):
                # if i is a folder, look into it and delete all chatgpt.csv
                if os.path.isdir(path + '/' + i):
                    print('found a folder,checking for gpt csv')

                    for j in os.listdir(path + '/' + i):
                        if j == 'ChatGPT.csv':
                            os.remove(path + '/' + i + '/' + j)
    else:
        print(f'no {hotel} reviewData folder found' )


if __name__ == "__main__":

    flow1('Aloft Singapore Novena')
    flow2('Aloft Singapore Novena')
    flow3(60)
    #!flow4() #not a flow for user, more of backend management
    flow5('Aloft Singapore Novena','Amara Singapore')
    newhotelScrapeflow('Any hotel name')
    flow6('Aloft Singapore Novena') 
