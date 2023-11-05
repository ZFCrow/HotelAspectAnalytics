import pandas as pd

def hotel_list():
    hotel_list=[]
    data = pd.read_csv('tripadvisor.csv')
    for name in data['hotelname']:
        if name in hotel_list:
            continue
        else:
            hotel_list.append(name)
    hotel_list.sort()
    return hotel_list

def df_to_list(data):
    final_data = data.to_dict('records')
    list_data = []
    # print("Final data",final_data)
    for dict_data in final_data:
        for string in dict_data:
            list_data.append(dict_data.get(string).replace("\n","<br>").replace("\r",""))
    string_data = str(list_data).replace("[", "").replace("]", "").replace("\'", "").replace("\'", "")
    index = string_data.find("<br><br>")
    string_data = string_data[index+8:]
    return string_data

# final_data = [{'ChatGPT': '.\n\nIn 2017, the number of positive comments across all categories was 39 and the number of negative comments across all categories was 2. \n\nIn 2018, the number of positive comments across all categories was 34 and the number of negative comments across all categories was 13. \n\nIn 2019, the number of positive comments across all categories was 42 and the number of negative comments across all categories was 11. \n\nIn 2020, the number of positive comments across all categories was 31 and the number of negative comments across all categories was 7. \n\nIn 2021, the number of positive comments across all categories was 46 and the number of negative comments across all categories was 2.\n\nIn 2022, the number of positive comments across all categories was 36 and the number of negative comments across all categories was 3. \n\nIn 2023, the number of positive comments across all categories was 135 and the number of negative comments across all categories was 1.'}]
# list_data = []
# for dict_data in final_data:
#     for string in dict_data:
#         list_data.append(dict_data.get(string).replace("\n","<br>"))
# print(list_data)
# string_data = str(list_data).replace("[", "").replace("]", "").replace("\'", "").replace("\'", "")
# index = string_data.find("<br><br>")
# string_data = string_data[index+8:]

# print(string_data)

def df_to_list_sum(data):
    final_data = data.to_dict('records')
    list_data = []
    for dict_data in final_data:
        for string in dict_data:
            list_data.append(dict_data.get(string).replace("\n","<br>").replace("\r",""))
    print(list_data)
    openai_response = str(list_data[0])
    index = openai_response.find("Summary:")
    openai_response = openai_response[index:]
    accuracy_value = str(list_data[1])
    return openai_response, accuracy_value

    
# final_data = [{'OpenAI Response': "\n\nSummary:\nAmara Singapore has an average sentiment score of 74.29%, indicating that guests had an overall positive experience. The positive entities of hotel staff, great service, location, food, and thanks, combined with a lack of negative entities suggests that Amara Singapore is a hotel with great service and environment.\n\nRecommendations for People Who Wish to Book:\nThose who wish to book at Amara Singapore can be confident that they will have an enjoyable experience. The positive feedback on the hotel staff, service, location, food, and thanks suggest the hotel is able to provide a comfortable stay with excellent customer service. Additionally, the lack of any negative entities indicate that guests have had a satisfying and pleasant experience overall.\n\nAdditional Notes:\nIt is worth noting that the top two positive entities are hotel staff and service, which shows that customers are especially satisfied by the quality of the staff and the serviece. This is a particularly strong sign of Amara Singapore's commitment to delivering excellent experiences for its guests.", 'Accuracy': '89.75%'}]
# list_data = []
# for dict_data in final_data:
#         for string in dict_data:
#             list_data.append(dict_data.get(string).replace("\n","<br>").replace("\r",""))
# # print(list_data)
# openai_response = str(list_data[0])
# index = openai_response.find("Summary")
# openai_response = openai_response[index:]
# # index2 = openai_response.find("<br><br>")
# # openai_response = openai_response[index2+8:]
# accuracy = list_data[1]
# print(openai_response)
# print(accuracy)

