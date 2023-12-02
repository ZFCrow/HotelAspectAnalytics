from flask import Flask, render_template, request, send_file, url_for, redirect, jsonify
import hotel
import shutil
import pandas as pd
import time 
import path
import sys
import os


# directory reach
directory = path.Path(__file__).abspath()
 
# setting path
sys.path.append(directory.parent.parent)
import Fullflow
import confusionmatrix
import constants 
app = Flask(__name__, template_folder='frontend_template')

@app.route('/')
def index():
    hotels = hotel.hotel_list()
    return render_template("index.html",hotels = hotels) 




@app.route("/analyse/",methods=['POST'])
def flow1():

    input = request.form.get('analyse').split(":")
    hotelname = input[1]
    years = input[0]
    print(hotelname)
    print(years)
    #if hotelname cant be found in my databyhotel folders without the reviewData, i need to scrape it
    hotelnamePath = f'{hotelname} ReviewData'
    if hotelnamePath not in os.listdir('DatabyHotel'):
        # check if it is in tripadvisor.csv
        df = pd.read_csv('tripadvisor.csv')
        if hotelname not in df['hotelname'].values:

            regressionTrendOverall, bargraph, summaryResponseRegressionGraph, summaryResponseBarGraph, regressionTrendPos, summaryResponseRegressionGraphPos, regressionTrendNeg, summaryResponseRegressionGraphNeg = Fullflow.newhotelScrapeflow(hotelname, years)
            #! change the hotelname to the last row of the tripadvisor.csv/ should  try and return it from scraper but well.
            hotelname = pd.read_csv('tripadvisor.csv').iloc[-1]['hotelname']
        else:
            print('hotel found in tripadvisor.csv')
            regressionTrendOverall, bargraph, summaryResponseRegressionGraph, summaryResponseBarGraph, regressionTrendPos, summaryResponseRegressionGraphPos, regressionTrendNeg, summaryResponseRegressionGraphNeg = Fullflow.flow1(hotelname, years)   
    else:
        regressionTrendOverall, bargraph, summaryResponseRegressionGraph, summaryResponseBarGraph, regressionTrendPos, summaryResponseRegressionGraphPos, regressionTrendNeg, summaryResponseRegressionGraphNeg = Fullflow.flow1(hotelname, years)   

    bargraph_data = hotel.df_to_list(summaryResponseBarGraph)
    regression_data = hotel.df_to_list(summaryResponseRegressionGraph)
    regression_pos_data = hotel.df_to_list(summaryResponseRegressionGraphPos)
    regression_neg_data = hotel.df_to_list(summaryResponseRegressionGraphNeg)


    return render_template('analyse.html', hotel_name=hotelname,
                             regression=regressionTrendOverall, summary_regression=regression_data,
                             bargraph=bargraph, summary_bargraph=bargraph_data,
                             regressionPos = regressionTrendPos,summary_regression_pos=regression_pos_data,
                             regressionNeg = regressionTrendNeg, summary_regression_neg=regression_neg_data)

@app.route("/scrapAnalyse/",methods=['POST'])
def flow2():    
    input = request.form.get('scrap_analyse').split(":")

    hotelname = input[1]
    years = input[0]


    regressionTrendOverall, bargraph, summaryResponseRegressionGraph, summaryResponseBarGraph, regressionTrendPos, summaryResponseRegressionGraphPos, regressionTrendNeg, summaryResponseRegressionGraphNeg = Fullflow.flow2(hotelname, years) 

    bargraph_data = hotel.df_to_list(summaryResponseBarGraph)
    regression_data = hotel.df_to_list(summaryResponseRegressionGraph)
    regression_pos_data = hotel.df_to_list(summaryResponseRegressionGraphPos)
    regression_neg_data = hotel.df_to_list(summaryResponseRegressionGraphNeg)

    return render_template('analyse.html', hotel_name=hotelname,
                             regression=regressionTrendOverall, summary_regression=regression_data,
                             bargraph=bargraph, summary_bargraph=bargraph_data,
                             regressionPos = regressionTrendPos,summary_regression_pos=regression_pos_data,
                             regressionNeg = regressionTrendNeg, summary_regression_neg=regression_neg_data)

@app.route("/updateDatabase/",methods=['POST'])
def flow3():
    input = request.form.get('updateDB')
    print(input)

    # ! the modal??
    if input.isdigit():
        Fullflow.flow3(int(input))
        return redirect(url_for('index'))
    else:
        time.sleep(2)
        return redirect(url_for('index'))  # Render the current page

@app.route("/compare/", methods=['POST'])
def flow5():
    input = request.form.get('compareHotels').split(":")
    print(input)
    hotel1 = input[0]
    hotel2 = input[1]

    bargraph, compareSummary = Fullflow.flow5(hotel1, hotel2) 

    return render_template('compare.html', hotel1 = hotel1, hotel2 = hotel2,
                            bargraph=bargraph, summary_compare = compareSummary)


@app.route("/review_summary/", methods=['POST'])
def flow6():
    input = request.form.get('next')
    #*check if qr.jpg exist, if it does, means user need to pay so we raise exception 
    #*check if qr1.jpg exist, if it does, means user  no need to pay so we proceed on , in static folder
    try:
        qr_loc = path.Path(__file__).abspath().parent.parent + r'\frontend\static\images\qr.jpg'
        qr1_loc = path.Path(__file__).abspath().parent.parent + r'\frontend\static\images\qr1.jpg'
        # if qr_loc.exists():
        #     #change it to qr1.jpg
        #     qr_loc.rename(qr_loc.parent / f'qr1.jpg')
        #     raise
        
        # if qr1_loc.exists():
        #     #change it to qr.jpg and proceed on, so user needs to pay next time, pass through this time
        #     qr1_loc.rename(qr1_loc.parent / f'qr.jpg')
        
        if constants.googleNLPAPIKEY != None:
            
        
            response = Fullflow.flow6(input)
            print(response.to_dict('records'))
            openai_response, accuracy_value = hotel.df_to_list_sum(response)
        else: #! it equals to none so we raise 
            raise 
    except:
        openai_response,accuracy_value = "apikey notfound", "google nlp apikey notfound so there will not be a review summary generated! "
    
    print(openai_response)
    print(accuracy_value)

    # openai_response = response_df['OpenAI Response'].values[0]
    # accuracy_value = response_df['Accuracy'].values[0]
    
    
    csv_loc = path.Path(__file__).abspath().parent.parent + f'\DatabyHotel\{input} ReviewData\hotelData.csv'
    data = pd.read_csv(csv_loc)
    data = data.drop(columns=['hotelname', 'hotelRank','hotelClass','polarity','subjectivity','Category'])
    data = data.rename(columns={'title':'Title','desc':'Description','reviewRatings':'Rating','reviewDate':'Date'})

    return render_template("reviewSum.html", hotel_name = input, tables=data.to_dict('records'), summary = openai_response, accuracy = accuracy_value)

@app.route('/download/', methods=['POST'])
def download_file():
    input = request.form.get('download').split(":")
    print(input)
    hotelname = input[0]
    graphtype = input[1]
    print(hotelname)
    print(graphtype)

    if graphtype=="OverallRegression":
        filename = path.Path(__file__).abspath().parent.parent + f'\DatabyHotel\{hotelname} ReviewData\OverallRegression\{graphtype}.png'
    elif graphtype=="OverallBarGraph":
        filename = path.Path(__file__).abspath().parent.parent + f'\DatabyHotel\{hotelname} ReviewData\OverallBargraph\{graphtype}.png'
    elif graphtype=="OverallRegression_POS":
        filename = path.Path(__file__).abspath().parent.parent + f'\DatabyHotel\{hotelname} ReviewData\OverallRegression_POS\{graphtype}.png'
    elif graphtype=="OverallRegression_NEG":
        filename = path.Path(__file__).abspath().parent.parent + f'\DatabyHotel\{hotelname} ReviewData\OverallRegression_NEG\{graphtype}.png'
    elif graphtype=="polarityCM.txt":
        filename = path.Path(__file__).abspath().parent.parent + f'\DatabyHotel\{hotelname} ReviewData\{graphtype}'


    print(filename)
    return send_file(filename, as_attachment=True)

@app.route('/downloadCompare/', methods=['POST'])
def download_compare_file():
    input = request.form.get('downloadCmp')
    print(input)

    filename = path.Path(__file__).abspath().parent.parent + f'\Comparision\{input}'

    print(filename)
    return send_file(filename, as_attachment=True)

#return a df of the hotel data the cm is based on
@app.route('/CMQuestions/', methods=['GET'])
def fetchQuestions():
    hotel = request.args.get('hotel_name')
    print('hotel name gotten from frontend')
    print(hotel)
    time.sleep(5)
    try:
        df = pd.read_csv(f'DatabyHotel/{hotel} ReviewData/hotelData.csv')
        df = df[['desc','Category']]
    except:
        return "no data"
    

        #empty df
    df5samples = pd.DataFrame()#empty df
    for i in df['Category'].unique():
        df1 = df[df['Category'] == i]
        try:
            df1 = df1.sample(5)
        except: 
            #sample size stated is larger than population size
            df1 = df1.sample(len(df1))
        df5samples = df5samples.append(df1,ignore_index=True)
    
    #mix up the df
    df = df5samples.sample(frac=1).reset_index(drop=True)

    aspects = list(df['Category'].unique())

    return df.to_json(orient='records')


#receive the user answers as actual category and return the result
@app.route('/CMAnswers/', methods=['POST'])
def receiveFeedback():
    response = request.get_json()
    #break it into df, '-' is a delimiter for desc, predicted category and actual category
    hotel = response.get('hotel_name')
    paragraph = response.get('paragraphs')
    print(paragraph)
    df = pd.DataFrame(columns=['desc','actual'])
    for item in paragraph:
        parts = item.split('---')
        print(parts)
        #trim the space in front and back
        parts = [i.strip() for i in parts]
        if len(parts) == 1:
            df1 = pd.DataFrame([[parts[0],'None']],columns=['desc','actual'])
        else:
            df1 = pd.DataFrame([[parts[0],parts[1]]],columns=['desc','actual'])
        #concat
        df = pd.concat([df,df1],ignore_index=True)
    
        #datatype to str
    df['desc'] = df['desc'].astype(str)

       
    print('df of the user answers')
    print(df)
    print('-----')
    print('-------')

    #hotelbydatapath 
    lol = path.Path(__file__).abspath().parent.parent + f'\DatabyHotel\{hotel} ReviewData'
    dfFull = pd.read_csv(f'{lol}/hotelData.csv')


    df1 = dfFull[dfFull['desc'].isin(df['desc'])]


    # Update df1 with 'value2' from df2 based on the 'desc' column
    df1 = df1.merge(df[['desc', 'actual']], on='desc', how='left')

    #filter to just desc and category and categoryActual
    df1 = df1[['desc','Category','actual']]
    print(df1)
    #change the 'Cleanliness' to 'Cleaniness' in actual column
    df1['actual'] = df1['actual'].replace('Cleanliness','Cleaniness')
    print('df1 changed')
    print(df1)
    # time.sleep(10)
    file = confusionmatrix.categoryCMGUI(df1,hotel)
    print(file)
    filename = path.Path(__file__).abspath().parent.parent + f'\DatabyHotel\{hotel} ReviewData\categoryCM.txt'

    #return the file as attachment
    return send_file(filename, as_attachment=True)



if __name__ =="__main__":
    app.run(debug=True)