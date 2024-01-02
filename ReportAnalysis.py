import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pandas as pd
import mpld3
import numpy as np
from scipy.interpolate import make_interp_spline, BSpline
from matplotlib.ticker import FuncFormatter
from scipy.interpolate import CubicSpline
import time
import chatgpt
import os


class ReportAnalysis:
    def __init__(self):
        self.aspects = ['Cleaniness', 'Services', 'Value', 'Amenities', 'Location', 'General']
        
    def newsubplot(self,hotelname,yearsofprediction=1):
    # Load data from csv file
        try:
            data = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/AnalysisReport.csv')
        except:
            print('no data found')
            return
        
    #filter away the year that says General
        data = data[data['year'] != 'General']
        
        data['year'] = data['year'].astype(int)

    # Extract x and y values from the DataFrame
        for i,aspects in enumerate(self.aspects):
            y = data[aspects].astype(float)        
        #y = data['Cleaniness'].astype(float)
        
        x = data['year'].astype(int) 

        #currentyear
        currentyear = data['year'].max()
        yearsPredicting = [x for x in range(currentyear+1,currentyear+yearsofprediction+1)]
        print(f'years predicting: {yearsPredicting}')

        predictingYear = data['year'].max()
        print(currentyear)
        
        # Create a figure with 2 rows and 3 columns of subplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Flatten the axes array for easier iteration
        axes = axes.flatten()
             
        # Loop through the columns and create a subplot for each
        for i, aspects in enumerate(self.aspects):
            # Create a subplot
            ax = axes[i]
            
            # Plot the column data using cubic spline interpolation
            x = data['year'] 
            y = data[aspects]

            # Filter out zero values from the data
            mask = (y != 0)
            x = x[mask]
            y = y[mask]

            # Check if x is empty
            if len(x) == 0:
                continue  # Skip this aspect if there's no valid data

            if len(x) > 2:
                cs = CubicSpline(x, y)
                x_smooth = np.linspace(x.min(), x.max(), 300)
                #y_smooth = make_interp_spline(x, y, k=3)(x_smooth)
                y_smooth = cs(x_smooth)
                            
            else:
                x_smooth = np.linspace(min(x), max(x), 100)
                y_smooth = np.interp(x_smooth, x, y)

            ax.plot(x_smooth, y_smooth)
            
            # Plot the original data points
            ax.scatter(x, y, color='red', label='Data Points')

            
            # Fit a linear regression model
            model = LinearRegression()
            model.fit(x.values.reshape(-1, 1), y)
            x_current = np.arange(x.min() , x.max() + 1).astype(float)
            y_current = model.predict(x_current.reshape(-1,1))
            x_pred = np.arange(x.max() + 1, x.max() + yearsofprediction + 1).astype(float)  # Generate x values for prediction
            y_pred = model.predict(x_pred.reshape(-1,1))
            #y_pred = model.predict(x.values.reshape(-1, 1))
            
            #clip predictions at 100
            y_pred = np.clip(y_pred, 0, 100)
            
            # Line for Current Tred
            ax.plot(x_current, y_current, label='Current Trend', color='green')
            
            # Add data points as dots (curve) and Scatter the  points to create hover over
            scatter = ax.scatter(x, y, color='blue', label='Data Points')
            yvalues = data[aspects].tolist()
            tooltip = [f'Value:{y}' for y in yvalues]
            tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=tooltip)
            mpld3.plugins.connect(fig, tooltip)

            # Create a list to store predicted values for this aspect
            aspect_predicted_values = []

            # Display predicted values for upcoming years
            for year, pred_value in zip(x_pred, y_pred):
                # Append the predicted values to the list
                aspect_predicted_values.append(pred_value)

            #Scatter the  points to create hover over
            predictscatter = ax.scatter(x_pred, y_pred, label='Predicted Trend', color='red')

            yvalues = aspect_predicted_values
            tooltip = [f'Value:{y}' for y in yvalues]
            tooltip = mpld3.plugins.PointLabelTooltip(predictscatter, labels=tooltip)
            mpld3.plugins.connect(fig, tooltip)

               
            # Set title and labels
            ax.set_title(f'{aspects} Sentiment Analysis Over Time')
            ax.set_xlabel('Year')
            ax.set_ylabel('Overall Sentiment Percentage by Year')
            
            # Clip y-values to not exceed 100
            y = np.clip(y, 0, 100)
            
            # Set y-axis limits to 0 and 100
            ax.set_ylim(0, 100)
        

        #add a text in between the 2 rows of subplots
        fig.text(0.5, 0.5, 'Regression Trend', ha='center', va='center', fontsize=20)

        plt.legend(bbox_to_anchor=(1.5, 0.5), ncol=1)
        # Adjust spacing between subplots
        plt.tight_layout()
        #adjust the spacing between the subplots to fit the text give enough spacing

        fig.subplots_adjust(hspace=0.5)        
        #plt.show()
        
        # Check if OverallRegression folder exists, if not create it
        if os.path.exists(f'DatabyHotel/{hotelname} ReviewData/OverallRegression'):
            
            plt.savefig(f'DatabyHotel/{hotelname} ReviewData/OverallRegression/OverallRegression.png')
        else:
            os.mkdir(f'DatabyHotel/{hotelname} ReviewData/OverallRegression')
            plt.savefig(f'DatabyHotel/{hotelname} ReviewData/OverallRegression/OverallRegression.png')


        interactive = mpld3.fig_to_html(fig)


        #! chatgpt
        # check if chatgpt.csv exist, only run if not
        if os.path.exists(f'DatabyHotel/{hotelname} ReviewData/OverallRegression/ChatGPT.csv'):
            print('chatgpt.csv exist')
            #read the csv file then 
            df = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/OverallRegression/ChatGPT.csv')
            #response = df['ChatGPT'].iloc[0]

        else:
            df = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/AnalysisReport.csv')
            # print cleaniness,location,service,general,value and over the years 
            df = df[['year','Cleaniness','Amenities','Location','Services','General','Value']]
            print(df)

            prompt = f'{df} Generate a report based on the dataframe. Disregard years for values are 0. Tell me how the overall sentiment percentages are over the years for each aspect. After that, tell me suggestions on what can be done to improve in each aspect based on the dataframe!'
            response = chatgpt.chat_with_gpt(prompt)
            print(response)
            #write the response into a csv under OverallRegression folder
            df = pd.DataFrame({'ChatGPT':response},index=[0])
            df.to_csv(f'DatabyHotel/{hotelname} ReviewData/OverallRegression/ChatGPT.csv',index=False)
            
        return interactive, df
    
    def newsubplot_pos(self,hotelname,yearsofprediction=1):
    # Load data from csv file
        try:
            data = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/AnalysisReport.csv')
        except:
            print('no data found')
            return
        
    #filter away the year that says General
        data = data[data['year'] != 'General']
        
        data['year'] = data['year'].astype(int)

    # Extract x and y values from the DataFrame
        for i,aspects in enumerate(self.aspects):
            y = data[aspects].astype(float)        
        #y = data['Cleaniness'].astype(float)
        
        x = data['year'].astype(int) 

        #currentyear
        currentyear = data['year'].max()
        yearsPredicting = [x for x in range(currentyear+1,currentyear+yearsofprediction+1)]
        print(f'years predicting: {yearsPredicting}')

        predictingYear = data['year'].max()
        print(currentyear)
        
        # Create a figure with 2 rows and 3 columns of subplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Flatten the axes array for easier iteration
        axes = axes.flatten()
             
        # Loop through the columns and create a subplot for each
        for i, aspects in enumerate(self.aspects):
            # Create a subplot
            ax = axes[i]
            
            # Plot the column data using cubic spline interpolation
            x = data['year'] 
            y = data[aspects + '_POS']
            
            # Filter out NaN and zero values from the data
            mask = (~np.isnan(y)) & (y != 0)
            x = x[mask]
            y = y[mask]

            print(y)

            # Check if x is empty
            if len(x) == 0:
                continue  # Skip this aspect if there's no valid data
            
            if len(x) > 2:
                cs = CubicSpline(x, y, bc_type='natural')  # Set boundary conditions to 'natural'
                x_smooth = np.linspace(x.min(), x.max(), 300)
                y_smooth = cs(x_smooth)
                            
            else:
                x_smooth = np.linspace(min(x), max(x), 100)
                y_smooth = np.interp(x_smooth, x, y)

            ax.plot(x_smooth, y_smooth)
            
            # Plot the original data points
            ax.scatter(x, y, color='red', label='Data Points')

            
            # Fit a linear regression model
            model = LinearRegression()
            model.fit(x.values.reshape(-1, 1), y)
            x_current = np.arange(x.min() , x.max() + 1).astype(float)
            y_current = model.predict(x_current.reshape(-1,1))
            x_pred = np.arange(x.max() + 1, x.max() + yearsofprediction + 1).astype(float)  # Generate x values for prediction
            y_pred = model.predict(x_pred.reshape(-1,1))
            #y_pred = model.predict(x.values.reshape(-1, 1))
            
            #clip predictions at 100
            y_pred = np.clip(y_pred, 0, 100)
            
            # Line for Current Tred
            ax.plot(x_current, y_current, label='Current Trend', color='green')
            
            # Add data points as dots (curve) and Scatter the  points to create hover over
            scatter = ax.scatter(x, y, color='blue', label='Data Points')
            yvalues = data[aspects + '_POS'].tolist()
            tooltip = [f'Value:{y}' for y in yvalues]
            tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=tooltip)
            mpld3.plugins.connect(fig, tooltip)

            # Create a list to store predicted values for this aspect
            aspect_predicted_values = []

            # Display predicted values for upcoming years
            for year, pred_value in zip(x_pred, y_pred):
                # Append the predicted values to the list
                aspect_predicted_values.append(pred_value)

            #Scatter the  points to create hover over
            predictscatter = ax.scatter(x_pred, y_pred, label='Predicted Trend', color='red')
            
            # Create a legend for all subplots
            fig.legend(['Smooth Curve', 'Predicted Trend', 'Current Trend', 'Data Points'], loc='lower left')
            
            yvalues = aspect_predicted_values
            tooltip = [f'Value:{y}' for y in yvalues]
            tooltip = mpld3.plugins.PointLabelTooltip(predictscatter, labels=tooltip)
            mpld3.plugins.connect(fig, tooltip)

               
            # Set title and labels
            ax.set_title(f'{aspects} Positive Sentiment Analysis Over Time')
            ax.set_xlabel('Year')
            ax.set_ylabel('Overall Positive Sentiment Percentage by Year')
            
            # Clip y-values to not exceed 100
            y = np.clip(y, 0, 100)
            
            # Set y-axis limits to 0 and 100
            ax.set_ylim(0, 100)

    # Adjust spacing between subplots
        plt.tight_layout()
        
        #plt.show()
        # Check if OverallRegression_POS folder exists, if not create it
        if os.path.exists(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_POS'):
            
            plt.savefig(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_POS/OverallRegression_POS.png')
        else:
            os.mkdir(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_POS')
            plt.savefig(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_POS/OverallRegression_POS.png')
        

        interactive = mpld3.fig_to_html(fig)


        #! chatgpt
        # check if chatgpt.csv exist, only run if not
        if os.path.exists(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_POS/ChatGPT.csv'):
            print('chatgpt.csv exist')
            #read the csv file then 
            df = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_POS/ChatGPT.csv')
           # response = df['ChatGPT'].iloc[0]

        else:
            df = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/AnalysisReport.csv')
            # print cleaniness,location,service,general,value and over the years 
            df = df[df['year'] != 'General'][['year', 'Cleaniness_POS', 'Amenities_POS', 'Location_POS', 'Services_POS', 'General_POS', 'Value_POS']]
            print(df)

            prompt = f'{df} Generate a report based on the dataframe. Disregard years for values are 0. Tell me how the overall positive sentiment percentages are over the years for each aspect. Do not include the POS in the naming of the aspects. After that, tell me suggestions on what can be done to improve in each aspect based on the dataframe!'
            response = chatgpt.chat_with_gpt(prompt)
            print(response)
            #write the response into a csv under OverallRegression folder
            df = pd.DataFrame({'ChatGPT':response},index=[0])
            df.to_csv(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_POS/ChatGPT.csv',index=False)

        return interactive, df
    
    def newsubplot_neg(self,hotelname,yearsofprediction=1):
    # Load data from csv file
        try:
            data = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/AnalysisReport.csv')
        except:
            print('no data found')
            return
        
    #filter away the year that says General
        data = data[data['year'] != 'General']
        
        data['year'] = data['year'].astype(int)

    # Extract x and y values from the DataFrame
        for i,aspects in enumerate(self.aspects):
            y = data[aspects + '_NEG'].astype(float)        
        #y = data['Cleaniness'].astype(float)
        
        x = data['year'].astype(int) 

        #currentyear
        currentyear = data['year'].max()
        yearsPredicting = [x for x in range(currentyear+1,currentyear+yearsofprediction+1)]
        print(f'years predicting: {yearsPredicting}')

        predictingYear = data['year'].max()
        print(currentyear)
        
        # Create a figure with 2 rows and 3 columns of subplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Flatten the axes array for easier iteration
        axes = axes.flatten()
             
        # Loop through the columns and create a subplot for each
        for i, aspects in enumerate(self.aspects):
            # Create a subplot
            ax = axes[i]
            
            # Plot the column data using cubic spline interpolation
            x = data['year'] 

            y = data[aspects + '_NEG']    

            # Filter out NaN and zero values from the data
            mask = (~np.isnan(y)) & (y != 0)
            x = x[mask]
            y = y[mask]

            print (y)
            
            # Check if x is empty
            if len(x) == 0:
                continue  # Skip this aspect if there's no valid data

            if len(x) > 2:

                cs = CubicSpline(x, y, bc_type='natural')  # Set boundary conditions to 'natural'
                x_smooth = np.linspace(x.min(), x.max(), 300)
                y_smooth = cs(x_smooth)
                            
            else:
                x_smooth = np.linspace(min(x), max(x), 100)
                y_smooth = np.interp(x_smooth, x, y)


            ax.plot(x_smooth, y_smooth)
            
            # Plot the original data points
            ax.scatter(x, y, color='red', label='Data Points')

            
            # Fit a linear regression model
            model = LinearRegression()
            model.fit(x.values.reshape(-1, 1), y)
            x_current = np.arange(x.min() , x.max() + 1).astype(float)
            y_current = model.predict(x_current.reshape(-1,1))
            x_pred = np.arange(x.max() + 1, x.max() + yearsofprediction + 1).astype(float)  # Generate x values for prediction
            y_pred = model.predict(x_pred.reshape(-1,1))
            #y_pred = model.predict(x.values.reshape(-1, 1))
            
            #clip predictions at 100
            y_pred = np.clip(y_pred, 0, 100)
            
            # Line for Current Tred
            ax.plot(x_current, y_current, label='Current Trend', color='green')
            
            # Add data points as dots (curve) and Scatter the  points to create hover over
            scatter = ax.scatter(x, y, color='blue', label='Data Points')
            yvalues = data[aspects + '_NEG'].tolist()
            tooltip = [f'Value:{y}' for y in yvalues]
            tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=tooltip)
            mpld3.plugins.connect(fig, tooltip)

            # Create a list to store predicted values for this aspect
            aspect_predicted_values = []

            # Display predicted values for upcoming years
            for year, pred_value in zip(x_pred, y_pred):
                # Append the predicted values to the list
                aspect_predicted_values.append(pred_value)

            #Scatter the  points to create hover over
            predictscatter = ax.scatter(x_pred, y_pred, label='Predicted Trend', color='red')
            
            # Create a legend for all subplots
            fig.legend(['Smooth Curve', 'Predicted Trend', 'Current Trend', 'Data Points'], loc='lower left')
            
            yvalues = aspect_predicted_values
            tooltip = [f'Value:{y}' for y in yvalues]
            tooltip = mpld3.plugins.PointLabelTooltip(predictscatter, labels=tooltip)
            mpld3.plugins.connect(fig, tooltip)

               
            # Set title and labels
            ax.set_title(f'{aspects} Negative Sentiment Analysis Over Time')
            ax.set_xlabel('Year')
            ax.set_ylabel('Overall Negative Sentiment Percentage by Year')
            
            # Clip y-values to not exceed 100
            y = np.clip(y, 0, 100)
            
            # Set y-axis limits to 0 and 100
            ax.set_ylim(0, 100)

    # Adjust spacing between subplots
        plt.tight_layout()
        
        #plt.show()
        # Check if OverallRegression_NEG folder exists, if not create it
        if os.path.exists(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_NEG'):
            
            plt.savefig(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_NEG/OverallRegression_NEG.png')
        else:
            os.mkdir(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_NEG')
            plt.savefig(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_NEG/OverallRegression_NEG.png')

        # turn it interactive
        interactive = mpld3.fig_to_html(fig)


        #! chatgpt
        # check if chatgpt.csv exist, only run if not
        if os.path.exists(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_NEG/ChatGPT.csv'):
            print('chatgpt.csv exist')
            #read the csv file then 
            df = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_NEG/ChatGPT.csv')

        else:
            df = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/AnalysisReport.csv')
            # print cleaniness,location,service,general,value and over the years
            df = df[df['year'] != 'General'][['year', 'Cleaniness_NEG', 'Amenities_NEG', 'Location_NEG', 'Services_NEG', 'General_NEG', 'Value_NEG']]
            print(df)

            prompt = f'{df} Generate a report based on the dataframe. Disregard years for values are 0. Tell me how the overall negative sentiment percentages are over the years for each aspect. Do not include the NEG in the naming of the aspects. After that, tell me suggestions on what can be done to improve in each aspect based on the dataframe!'
            response = chatgpt.chat_with_gpt(prompt)
            print(response)
            #write the response into a csv under OverallRegression folder
            df = pd.DataFrame({'ChatGPT':response},index=[0])
            df.to_csv(f'DatabyHotel/{hotelname} ReviewData/OverallRegression_NEG/ChatGPT.csv',index=False)

        return interactive, df

    #? bargraph for cleaniness, x axis is the year, y axis is the cleaniness(number of reviews) (2 bar per year, 1 for positive, 1 for negative)
    def bargraph (self,hotelname):
        try:
            data = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/AnalysisReport.csv')
        except:
            print('no data found')
            return
        
        #filter away the year that says General
        data = data[data['year'] != 'General']

        for i,aspects in enumerate(self.aspects):
            data[aspects] = data[aspects].astype(float)
        data['year'] = data['year'].astype(int)

        for i,aspects in enumerate(self.aspects):
            data[[f'{aspects}Positive', f'{aspects}Total']] = data[f'{aspects}Numbers'].str.split('/', expand=True).astype(int)
            data[f'{aspects}Negative'] = data.apply(lambda x: x[f'{aspects}Total'] - x[f'{aspects}Positive'], axis=1)
        
        print('added positive, negative and total columns')
        print(data)

        #! this creates the df to have a positivity column so i can hue it, 1 year will have 2 rows 1 postive 1 negative for all aspects !
        df = pd.DataFrame(columns=['Year','Positivity','Number','Category'])

        for i in range(len(data)): #for each year , each aspect will have 2 rows, 1 for positive and 1 for negative
            for aspect in self.aspects:

                # use concat instead of append 
                dfpostiive = pd.DataFrame({'Year':data['year'].iloc[i],'Positivity':'Positive','Number':data[f'{aspect}Positive'].iloc[i],'Category':aspect},index=[0])
                dfnegative = pd.DataFrame({'Year':data['year'].iloc[i],'Positivity':'Negative','Number':data[f'{aspect}Negative'].iloc[i],'Category':aspect},index=[0])
                df = pd.concat([df,dfpostiive,dfnegative],ignore_index=True)
        
        print('df for bargraph')
        print(df)

        # creates a subplot for each aspect
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))

        # Loop through the aspects and create subplots
        for i, aspect in enumerate(self.aspects):
            #create a df for each aspect with the years 
            dfAspect = df[df['Category'] == aspect]
            print(dfAspect)
            print(type(dfAspect['Year'].iloc[0]))
            row = i // 3
            col = i % 3
            
            ax = axes[row, col]

            # Create the bar plot using Seaborn with green as positive and red as negative
            sns.barplot(x='Year', y='Number', data=dfAspect, palette={'Positive':'green','Negative':'red'},hue='Positivity',ax=ax)

            # set xticklabels to int instead of float
            ax.set_xticklabels(map(int,dfAspect['Year'].unique().tolist()),rotation=45)
            #ax.set_xticks(dfAspect['Year'].unique().tolist())
            # Add labels and legend
            ax.set_xlabel('Year')
            ax.set_ylabel('Count')
            ax.set_title(f'{aspect} Positive and Negative Reviews Over the Years')

        
        # Adjust spacing between subplots
        plt.tight_layout()




        # interactive plot 
        interactive = mpld3.fig_to_html(fig)
        

        if os.path.exists(f'DatabyHotel/{hotelname} ReviewData/OverallBargraph'):

            plt.savefig(f'DatabyHotel/{hotelname} ReviewData/OverallBargraph/OverallBarGraph.png')
        else:
            os.mkdir(f'DatabyHotel/{hotelname} ReviewData/OverallBargraph')
            plt.savefig(f'DatabyHotel/{hotelname} ReviewData/OverallBargraph/OverallBarGraph.png')



        #! chatgpt
        # check if chatgpt.csv exist, only run if not
        if os.path.exists(f'DatabyHotel/{hotelname} ReviewData/OverallBargraph/ChatGPT.csv'):
            print('chatgpt.csv exist')
            #read the csv file then
            df = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/OverallBargraph/ChatGPT.csv')
            #response = responsefdf['ChatGPT'].iloc[0]


        else:
            print(df)
            #time.sleep(30)

            prompt = f'{df} Generate a report based on the dataframe. Tell me the number of each positive against negative in every single year'
            response = chatgpt.chat_with_gpt(prompt)
            print(response)
            #write the response into a csv under OverallRegression folder
            df = pd.DataFrame({'ChatGPT':response},index=[0])
            df.to_csv(f'DatabyHotel/{hotelname} ReviewData/OverallBargraph/ChatGPT.csv',index=False)




        return interactive, df



    #? bargraph for cleaniness between 2 hotels, x axis is the year, y axis is the cleaniness percentage between hotel (1 bar for hotel 1, 1 bar for hotel 2)
    def bargraph_cmp (self,hotel1name,hotel2name):
        try:
            data1 = pd.read_csv(f'DatabyHotel/{hotel1name} ReviewData/AnalysisReport.csv')
            data2 = pd.read_csv(f'DatabyHotel/{hotel2name} ReviewData/AnalysisReport.csv')
        except:
            print('no data found')
            return
        
        #filter away the year that says General for both datas
        data1 = data1[data1['year'] != 'General']
        data2 = data2[data2['year'] != 'General']


        for i,aspects in enumerate(self.aspects):
            data1[aspects] = data1[aspects].astype(float)
            data2[aspects] = data2[aspects].astype(float)

        # change all the column to float and year to int
        #data['Cleaniness'] = data['Cleaniness'].astype(float) 
        data1['year'] = data1['year'].astype(int)
        data2['year'] = data2['year'].astype(int)
        
        #add new column HotelName to identify the Hotel for the csv file
        data1['HotelName'] = hotel1name
        data2['HotelName'] = hotel2name
        
        print('added HotelName columns')
        print(data1)
        print(data2)

        #! this creates the df to have a positivity column so i can hue it, 1 year will have 2 rows 1 postive 1 negative for all aspects !
        df = pd.DataFrame(columns=['Year','Percentage','HotelName','Category'])

        for i in range(len(data1)): #for Data1 ,insert hotelname and percentage data
            for aspect in self.aspects:                
                # use concat instead of append 
                percentage_hotelname = pd.DataFrame({'Year':data1['year'].iloc[i],'Percentage': data1[aspect].iloc[i],'HotelName':data1['HotelName'].iloc[i],'Category':aspect},index=[0])
                df = pd.concat([df,percentage_hotelname],ignore_index=True)
        
        for i in range(len(data2)): #for Data2 ,insert hotelname and percentage data
            for aspect in self.aspects:                
                # use concat instead of append 
                percentage_hotelname = pd.DataFrame({'Year':data2['year'].iloc[i],'Percentage': data2[aspect].iloc[i],'HotelName':data2['HotelName'].iloc[i],'Category':aspect},index=[0])
                df = pd.concat([df,percentage_hotelname],ignore_index=True)
        
        print('df for bargraph')
        print(df)

        # creates a subplot for each aspect
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))

        # Loop through the aspects and create subplots
        for i, aspect in enumerate(self.aspects):
            #create a df for each aspect with the years 
            dfAspect = df[df['Category'] == aspect]
            print(dfAspect)
            print(type(dfAspect['Year'].iloc[0]))
            row = i // 3
            col = i % 3
            
            ax = axes[row, col]

            # Create the bar plot using Seaborn with teal as hotel1 and yellow as hotel2
            sns.barplot(x='Year', y='Percentage', data=dfAspect, palette={hotel1name:'teal',hotel2name:'yellow'},hue='HotelName',ax=ax)

            ax.set_xticklabels(dfAspect['Year'].unique().tolist(),rotation=45)
            # Add labels and legend
            ax.set_xlabel('Year')
            ax.set_ylabel('Percentage')
            ax.set_title(f'{aspect} % Between the Hotels Over the Years')
            #!set y axis from 0 to 100 
            ax.set_ylim(0, 100)

          
        
        # Adjust spacing between subplots
        plt.tight_layout()
        plt.savefig(f'Comparision/' + hotel1name + '_' + hotel2name + '_CMP.png')

        respone = 'The above comparison bargraph shows the Overall Sentiment Percentage in each aspect for the respective hotel. A more specific data analysis can be found using the analyzing function for your chosen hotel!'

        # interactive plot 
        interactive = mpld3.fig_to_html(fig)

 
        return interactive, respone

    #? this is 6 plots in one figure
    def subplot(self,hotelname,yearsofprediction=1):

        try:
            data = pd.read_csv(f'DatabyHotel/{hotelname} ReviewData/AnalysisReport.csv')
        except:
            print('no data found')
            return

        print(data)
        #print(data.info())

        #filter away the year that says General
        data = data[data['year'] != 'General']
        # change all the column to float and year to int
        data['Cleaniness'] = data['Cleaniness'].astype(float) 
        data['Services'] = data['Services'].astype(float)
        data['Value'] = data['Value'].astype(float)
        data['Amenities'] = data['Amenities'].astype(float)
        data['General'] = data['General'].astype(float)
        data['Location'] = data['Location'].astype(float)

        data['year'] = data['year'].astype(int)
        
        #currentyear
        currentyear = data['year'].max()
        yearsPredicting = [x for x in range(currentyear+1,currentyear+yearsofprediction+1)]
        print(f'years predicting: {yearsPredicting}')

        predictingYear = data['year'].max()
        print(currentyear)

        # Create a single figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))



        # Create a LinearRegression instance
        lri = LinearRegression()



        # Loop through the aspects and create subplots
        for i, aspect in enumerate(self.aspects):
            #create a df for each aspect with the years 

            dfAspect = data[['year',aspect]]
            print(dfAspect)

            lri.fit(data[['year']],data[[aspect]])
            
            predictedResult = []
            for x in range(yearsofprediction):
                #predictingYear += 1
                result = lri.predict([[yearsPredicting[x]]])
                print(f'predicted {aspect} in {yearsPredicting[x]}: {result[0][0]}%')
                predictedResult.append({yearsPredicting[x]:result[0][0]})

            print(predictedResult)
            #concat the dataframe with the predicted value, the keys should be in the year column and the values should be in the aspect column
            predicteddf = pd.DataFrame(columns=['year',aspect])
            # Iterate through the dictionary and append rows to the DataFrame
            for j in predictedResult: #? list of dict that contains the year and the predicted value
                for year, aspect_value in j.items():
                    #predicteddf = predicteddf.append({'year': year, aspect: aspect_value}, ignore_index=True)

                    #use concat instead of append
                    predictedResultDF = pd.DataFrame({'year':year,aspect:aspect_value},index=[0])
                    predicteddf = pd.concat([predicteddf,predictedResultDF],ignore_index=True)

            dfAspect = pd.concat([dfAspect,predicteddf])
            
            print(f'predicted df of {aspect} after using concat')
            print(dfAspect)


            row = i // 3
            col = i % 3
            
            ax = axes[row, col]


            # Regression plot for the current aspect
            hello = sns.regplot(x='year', y=aspect, data=data, ax=ax, label = 'Data Values')


            
            # Set labels and title for the subplot
            ax.set_xlabel('Year')

            #? set the xtick to data year as well as the predicted year
            ax.set_xticks(data['year'].unique().tolist() + yearsPredicting)

            ax.set_ylabel(f'{aspect} (out of 100)')
            ax.set_title(f'Regression Plot of {aspect} Over Time')
            ax.set_ylim(0, 100)

            #! scatter the same points so i can use it to create interactive plot
            scatter = ax.scatter(x='year', y=aspect, data=data,label = None)
            yvalues = data[aspect].tolist()
            # Customize the tooltip labels with "Hello" followed by y-values
            tooltip = [f'Value:{y}' for y in yvalues]
            #!xvaluelabels = [f'Year: {x}<br>Value: {y}' for x,y in zip(xvalues,yvalues)]  
            tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=tooltip)
            mpld3.plugins.connect(fig, tooltip)

            #change the predicteddf values that are more than 100 to 100 and less than 0 to 0
            predicteddf[aspect] = predicteddf[aspect].apply(lambda x: 100 if x > 100 else x)
            predicteddf[aspect] = predicteddf[aspect].apply(lambda x: 0 if x < 0 else x)
            print('df after changing the values')
            print(predicteddf)
            #instead of looping the predictedresult, i scatter all at once, created a pandas of the predicted result and scatter it
            predictScatter = ax.scatter(x='year', y=aspect, data=predicteddf,color='red',marker='o',s=50,label='Predicted Value')
            yvalues = predicteddf[aspect].tolist()
            tooltip = [f'Value:{y}' for y in yvalues]
            tooltip = mpld3.plugins.PointLabelTooltip(predictScatter, labels=tooltip)
            mpld3.plugins.connect(fig, tooltip)


        print(data)
        plt.legend(bbox_to_anchor=(1.5, 0.5), ncol=1)
        # Adjust spacing between subplots
        plt.tight_layout()
    
  
        

        #* Save the figure
        plt.savefig(f'DatabyHotel/{hotelname} ReviewData/OldOverallRegression.png')

        #* turn it interactive

        interactive = mpld3.fig_to_html(fig)


        return interactive





