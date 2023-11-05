# use selenium get to TripAdvisor and scrape the hotel information as well as reviews
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import os
import threading
import datetime
from selenium.common.exceptions import StaleElementReferenceException,ElementNotInteractableException



class Scraper:
    def __init__(self):

        self.listofReviews = []
        self.place = 'singapore' #* this is the place you want to scrape
        self.totalReviewsPage = 100  #* this is the number of pages of reviews you want to scrape per hotel
        self.jumppage = False
        self.stoppage = False
        self.pageinThread = [] # this is to store the page numbers that are being scraped in the thread
        self.hotelinThread = [] # this is to store the hotel names that are being scraped in the thread
        self.stopThread = False
        self.thismonthyear = datetime.datetime.now().strftime("%B %Y")
        self.webversion = 1 
        self.threadfailCount = 0

    def dataappend(self,hotelname, title, desc,reviewbubble, reviewDate, hotelClass, hotelRank):
        print('you are in dataappend here')
        try:
            listofReviews = []
   
            listofReviews.append({'hotelname':hotelname,'title':title,'desc':desc,'reviewRatings':reviewbubble,
                                'reviewDate':reviewDate,'hotelClass':hotelClass,'hotelRank':hotelRank})
            #! datatype of reviewRatings is string as it is a string of the number of stars out of 5
            df = pd.DataFrame(listofReviews)
            print(df)

                

            if os.path.isfile('tripadvisor.csv'):
                existdf = pd.read_csv('tripadvisor.csv')
                #if desc is found in the csv, we dont append it
                if df['desc'].isin(existdf['desc']).any():
                    print('desc found in csv')
                    self.jumppage = True
                    
                else:

                    df.to_csv('tripadvisor.csv', index=False, mode='a', header=False)

                    print('appended to csv')
                    self.jumppage = False

            else:
                df.to_csv('tripadvisor.csv', index=False, mode='a')

            
            #self.listofReviews.clear()
            listofReviews.clear()
            return self.jumppage
        except Exception as e:
            print(e)
            print('error in appending data to listofreviews')   



    def specificHotelScrape(self,hotelname,update = True,headless = True):
        reviewPage = 1 # current page of reviews
        webversion = 1
        jumpPageifinThread = False

        #! implement not showing the chrome
        if headless == True:
            chromeOptions = Options()
            chromeOptions.add_argument('--headless')
            driver = webdriver.Chrome(options=chromeOptions)

        else:
            driver = webdriver.Chrome()
        

#!=========================================
        
        

        driver.maximize_window()

        driver.get("https://www.tripadvisor.com.sg/")
        

        
        wait = WebDriverWait(driver, 10)
        print ('reached here before the issue')
        #! uses the searchbar, then click hotel --> this will show you things other than hotels as well
        try:

            searchbar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='search']")))
            webversion = 1

        except:
            print('searchbar not found') 
            searchbar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.hUpcN._G.G_.B-.z.F1._J.w.Cj.R0.JGewE.H3')))
            webversion = 2

        try:
            searchbar.click()
            print('clicked without going into error')

        except StaleElementReferenceException or ElementNotInteractableException:
            print('error from staleelement')
            if webversion == 1:
                searchbar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='search']")))
            else:
                searchbar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.hUpcN._G.G_.B-.z.F1._J.w.Cj.R0.JGewE.H3')))

            searchbar.click()
            print('clicked again')

        print(driver.current_url)
        trycount =0

        while(trycount<3):
            searchbar.send_keys(hotelname)
            #click arrow down and enter
            time.sleep(1)
            searchbar.send_keys(Keys.ARROW_DOWN)
            searchbar.send_keys(Keys.ENTER)
            if driver.current_url != "https://www.tripadvisor.com.sg/":
                break
        


        #? scraping part
        ##hotelname 
        try:
            hotelname = wait.until(EC.presence_of_element_located((By.XPATH,"//h1[@id='HEADING']")))
            print(f'{hotelname.text} found in the heading')
            hotelname = hotelname.text
        except:
            print('no hotelname found')
             
        #! scrape the hotel class
        try:
            hClass = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.JXZuC.d.H0')))
            hotelClass = hClass.get_attribute('aria-label')
            print(hotelClass)
            
        except:
            print('no hotel class found')
            hotelClass = 'no hotel class found'
        

        #! scrape the hotel rankings 
        try:
            hRank = wait.until(EC.presence_of_element_located((By.XPATH,"//div[@class='cGAqf']//span")))
            hotelRank = hRank.text
        except:
            print('no hotel rank found')
            hotelRank = 'no hotel rank found'

        for i in range(self.totalReviewsPage):
            print(f'page {reviewPage} of reviews of {hotelname}')
            time.sleep(1)

            #? add in pagenumber to self.pageinThread, if already exist, break the loop and jump to the next page
            if reviewPage in self.pageinThread:
                print('page already in thread, moving on to next page')
                jumpPageifinThread = True
             

            else:
                self.pageinThread.append(reviewPage)
                print(f'dealing with pages {self.pageinThread}')
                time.sleep(2)
            

            if jumpPageifinThread == False:

                reviews = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.WAllg._T')))

                for review in reviews:

    


                    print('--------------------')

                    #* review date
                    try:
                        rdate = review.find_element(By.XPATH,".//span[@class='teHYY _R Me S4 H3']")
                        reviewDate = rdate.text[14:]
                        print(reviewDate)

                    except Exception as e:
                        print(e)
                        print('no review date')
                        reviewDate = 'no review date found'
                        
                    #*print review bubble
                    try:
                     
                        rb = review.find_element(By.XPATH,".//div[@data-test-target='review-rating']//span")
                       
                        reviewbubble = rb.get_attribute('class')
                        #take the last 2nd character of the class name and add '/5' to the string 
                        reviewbubble = reviewbubble[-2]+' out of 5'
                        print(reviewbubble)

                        time.sleep(0.5)
                    except:
                        reviewbubble = 'no review ratings found'
                        print('unable to find rb')
                        
                    #* print review title 
                    #! please note the . is important as in xpath, without the . it will just look for the first element in the whole dom
                    try:
                        rt = review.find_element(By.XPATH,".//div[@data-test-target='review-title']//span//span") 
                        print(rt.text)
                        reviewTitle = rt.text
                    except:
                        print('no review title')
                        reviewTitle = 'no review title found'

                    #* print review description    
                    try:
                        #!rd = review.find_element(By.XPATH,".//div[@class='_T FKffI']//span//span")
                        rd = review.find_element(By.XPATH,".//span[@class='QewHA H4 _a']//span")
                        print(rd.text)
                        reviewDesc = rd.text



                    except:
                        print('no review description')
                        reviewDesc = 'no review description found'


                    #* append hotelname and both into the listofreviews as a dictionary in the dataappend function
                    try:
                      

                    #! if dataappend returns true, it means that the review has already been found in the csv, so we jump to the next page
                        self.stoppage = self.dataappend(hotelname=hotelname,title=reviewTitle,desc=reviewDesc,reviewbubble=reviewbubble,reviewDate=reviewDate,hotelClass=hotelClass,hotelRank=hotelRank)
                        if self.stoppage == True:
                            if update == True:
                            
                                #stop scraping
                                print('stopping the scrape as reviews in this page has been found!')
                                self.stopThread = True
                                break
                                
                            else:
                                print('not breaking as this is a new scrape and we want to get all the reviews')
                       
                    #! =========================================================================================================================


                    except Exception as e:
                        print(e)
                        print('error in dataappend')

                    print('-------------------')

            
            if self.stoppage == True and update == True:
                self.stoppage = False
                break

            #! this is to click the next page after scraping all the reviews in the current page
            try:
                if self.stopThread == True:
                    return
                
                nextpage = driver.find_element(By.XPATH,"//a[@class='ui_button nav next primary ']")
                nextpage.click()
                jumpPageifinThread = False


      
                reviewPage+=1
                
            except Exception as e :
                print(e)
                print('no next page')
                break

            
        
        #* ==================================================================================================
        #* ==================================================================================================
        #* ==================================================================================================
        try:
            driver.close()

        except Exception as e:
            print(e)
            print('driver unable to close')


    


    def generalHotelScrape(self,place,headless = True):
        webversion = 1 #? tripadvisor renders differently on different browsers, this is to check which version it is
        #dont show the chromes
        #! implement not showing the chrome
        if headless == True:
            chromeOptions = Options()
            chromeOptions.add_argument('--headless')
            driver = webdriver.Chrome(options=chromeOptions)

        else:
            driver = webdriver.Chrome()

        driver.maximize_window()

        driver.get("https://www.tripadvisor.com.sg/")
       

        
        wait = WebDriverWait(driver, 10)
        #! uses the searchbar, then click hotel --> this will show you things other than hotels as well
        try:

            searchbar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='search']")))
            webversion = 1

        except:
            print('searchbar not found') 
            searchbar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.hUpcN._G.G_.B-.z.F1._J.w.Cj.R0.JGewE.H3')))
            webversion = 2


        try:
            searchbar.click()
            print('clicked without going into error')

        except StaleElementReferenceException or ElementNotInteractableException:
            print('error from staleelement')
            if webversion == 1:
                searchbar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='search']")))
            else:
                searchbar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.hUpcN._G.G_.B-.z.F1._J.w.Cj.R0.JGewE.H3')))

            searchbar.click()
            print('clicked again')


        print(driver.current_url)
        trycount =0

        while(trycount<3):
            searchbar.send_keys(place)
            searchbar.send_keys(Keys.ENTER)
            if driver.current_url != "https://www.tripadvisor.com.sg/":
                break

        time.sleep(2)
        hoteltab = driver.find_element(By.XPATH,"//a[@data-tab-name='Hotels']")

      
        hoteltab.click()
      


        #! figure out how many pages this is going 
        #page = driver.find_element(By.CLASS_NAME,'pageNumbers')
        page = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'pageNumbers')))
        lastpage = page.find_elements(By.CLASS_NAME,'pageNum')[-1] #? lastpage is the number of pages of hotels you want to scrape
        print(lastpage.text)
        lastpage = int(lastpage.text)

        for i in range(1,lastpage+1):
            print(f'page {i}')
            try:
                print('trying to find hotel card')
                hotelCard = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.ui_column.is-12.content-column.result-card')))
                #hotelCard = driver.find_elements(By.CSS_SELECTOR,'.ui_column.is-12.content-column.result-card')
                print('found hotel card')
                print(len(hotelCard))
            except: 
                print('element not found')





            #! (this is just the first page)
            for hotel in hotelCard: 
                #! if i = 2 (for debug purposes)

                #* if text exists, we click in to get the reviews
                try:
                    reviewPage = 1 # current page of reviews
                    title=hotel.find_element(By.CLASS_NAME,'result-title')
                    print(title.text)
                    hotelname = title.text

                    #* if hotelname is found in the skiplist, we skip it
                    if os.path.isfile(f'skiplist/skiplist{self.thismonthyear}.csv'):
                        # no columns, set header to none
                        hotelDF = pd.read_csv(f'skiplist/skiplist{self.thismonthyear}.csv',header=None)
                        print(hotelDF)
                        if hotelname in hotelDF[hotelDF.columns[0]].values:
                            print('hotel found in skiplist')
                            time.sleep(3)
                            continue
                    else:
                        print('skiplist not found')
                    
                    #?==================================================================================================
                    #?==================================================================================================
                    #* if hotelname in thread, we skip it
                    if hotelname in self.hotelinThread:
                        print('hotel found in thread')
                        time.sleep(3)
                        continue
                    else:
                        pass
                    #?==================================================================================================
                    #?==================================================================================================
                    
                    print('hotel not found in skiplist')
                    title.click()

                    #?==================================================================================================
                    #?==================================================================================================
                    #* append it into the thread list so that we dont scrape it again in another thread2
                    self.hotelinThread.append(hotelname)
                    #?==================================================================================================
                    #?==================================================================================================

                    print(f'-------------start of {title.text} ---------------------')
                    
                    #* this is to shift control from the main window to the hotel window that we just opened
                    original_window = driver.window_handles[0]
                    new_window = driver.window_handles[1]
                    driver.switch_to.window(new_window)
                    #* THIS IS WHERE WE ACTUALLY SCRAPE THE REVIEWS
                    #* ==================================================================================================
                    #* ==================================================================================================
                    #* ==================================================================================================
                    #! scrape the hotel class
                    try:
                        hClass = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.JXZuC.d.H0')))
                        hotelClass = hClass.get_attribute('aria-label')
                        print(hotelClass)
                        
                    except:
                        print('no hotel class found')
                        hotelClass = 'no hotel class found'
                    
                    #! scrape the hotel rankings 
                    try:
                        hRank = wait.until(EC.presence_of_element_located((By.XPATH,"//div[@class='cGAqf']//span")))
                        hotelRank = hRank.text
                    except:
                        print('no hotel rank found')
                        hotelRank = 'no hotel rank found'



                    for i in range(self.totalReviewsPage):
                        print(f'page {reviewPage} of reviews of {hotelname}')
                        time.sleep(1)

                        #! the time changed from 10 to 3 cos it was taking too long to load the reviews
                        #!!reviews = driver.find_elements(By.CSS_SELECTOR,'.WAllg._T')
                        reviews = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.WAllg._T')))
                        for review in reviews:
                            
                            print('--------------------')

                            #* review date
                            try:
                                rdate = review.find_element(By.XPATH,".//span[@class='teHYY _R Me S4 H3']")
                                reviewDate = rdate.text[14:]
                                print(reviewDate)

                            except Exception as e:
                                print(e)
                                print('no review date')
                                reviewDate = 'no review date found'
                                
                            #*print review bubble
                            try:
          
                                rb = review.find_element(By.XPATH,".//div[@data-test-target='review-rating']//span")
                                reviewbubble = rb.get_attribute('class')
                                #take the last 2nd character of the class name and add '/5' to the string 
                                reviewbubble = reviewbubble[-2]+' out of 5'
                                print(reviewbubble)

                                time.sleep(0.5)
                            except:
                                reviewbubble = 'no review ratings found'
                                print('unable to find rb')
                                
                            #* print review title 
                            #! please note the . is important as in xpath, without the . it will just look for the first element in the whole dom
                            try:
                                rt = review.find_element(By.XPATH,".//div[@data-test-target='review-title']//span//span") 
                                print(rt.text)
                                reviewTitle = rt.text
                            except:
                                print('no review title')
                                reviewTitle = 'no review title found'

                            #* print review description    
                            try:
                                #!rd = review.find_element(By.XPATH,".//div[@class='_T FKffI']//span//span")
                                rd = review.find_element(By.XPATH,".//span[@class='QewHA H4 _a']//span")
                                print(rd.text)
                                reviewDesc = rd.text



                            except:
                                print('no review description')
                                reviewDesc = 'no review description found'


                            #* append hotelname and both into the listofreviews as a dictionary in the dataappend function
                            try:
                              

                            #! if dataappend returns true, it means that the review has already been found in the csv, so we jump to the next page
                                jump = self.dataappend(hotelname=hotelname,title=reviewTitle,desc=reviewDesc,reviewbubble=reviewbubble,reviewDate=reviewDate,hotelClass=hotelClass,hotelRank=hotelRank)
                                if jump == True:
                                    print('jumping page as reviews in this page has been found!')
                                    # sleep to prevent the host from blocking us
                                    time.sleep(5)
                                    break
                            #! =========================================================================================================================


                            except Exception as e:
                                print(e)
                                print('error in dataappend')

                            print('-------------------')

                        #! this is to click the next page after scraping all the reviews in the current page
                        try:
                            nextpage = driver.find_element(By.XPATH,"//a[@class='ui_button nav next primary ']")

                            if self.stopThread == True:
                                return
                            
                            nextpage.click()
                            reviewPage+=1
                        
                        except Exception as e :
                            print(e)
                            print('no next page')
                            break

                        
                    
                    #* ==================================================================================================
                    #* ==================================================================================================
                    #* ==================================================================================================
                    try:
                        driver.close()
                    #* switch the driver back to main window
                        driver.switch_to.window(driver.window_handles[0])
                    except Exception as e:
                        print(e)
                        print('driver unable to close')
                    

                    self.hotelinThread.remove(hotelname)
                    print(f'-------------end of {title.text} ---------------------')

                    #* append the hotelname to a skiplist so that we dont scrape it again the next time we run, should differ by month  

                    hotelDF = pd.DataFrame({'hotelname':[hotelname]})
                    hotelDF.to_csv(f'skiplist/skiplist{self.thismonthyear}.csv', index=False, mode='a', header=False)
                    print('appended hotel to skiplist')

                except Exception as e:
                    print(e)  
                    print('title not found')
                


            #! this is to click the next page
            time.sleep(5)

            try:
                nextpage = driver.find_element(By.XPATH,"//a[@class='ui_button nav next primary ']")
                if self.stopThread == True:
                    return
                nextpage.click()
            except:
                print('no next page')
                break






    def start(self,func=generalHotelScrape,funcARGs = None):
        startCount = 0
        while(startCount<3):
            try:

                if funcARGs == None:
                    print('Generic hotel scrape started')
                    func(self, place = self.place)

                    
                else:
                    if(type(funcARGs) == list):

                        func(hotelname=funcARGs[0],update=funcARGs[1])
                    else:
                        func(hotelname=funcARGs)
                break
            except Exception as e:
                print(e)
                print('error in hotelScrape')
                startCount+=1
                self.threadfailCount+=1
                print(f'retrying {startCount} time')
                time.sleep(5)


    def threadhandlers(self,timer=100, hotelname = None ,update = False ):
        threadlist = []
                #scrape with 2 threads
        if hotelname == None:
            for i in range(3):
                thread = threading.Thread(target=self.start)
                threadlist.append(thread)
     
        else:
            for i in range(3):
                thread = threading.Thread(target=self.start, args=(self.specificHotelScrape,[hotelname,update]))
                threadlist.append(thread) 
        

       
        for thread in threadlist:
            thread.start()
            time.sleep(1.5)
        
        print('waiting for threads to finish')


        # sleep for 1s then check if stopthread has been change to true, if so we continue
        for i in range(timer):
            time.sleep(1)
            if self.stopThread == True:
                print('thread has finish completion')
                break
            if self.threadfailCount == 9:
                print('thread has failed 9 times')
                self.stopThread = True #! not rly useful but i wont print the timer has passed when it hasnt! 
                break

        
        if self.stopThread == False:
            self.stopThread = True
            print(f'{timer} has passed and done!')
        
        for thread in threadlist:
            thread.join()


#? u can run in 2 ways, either with threads or without threads
#? 3 specific ways to run without threads, 3 specific ways to run with threads
#? 1. x.start() -> this will run the generalHotelScrape function
#? 2. x.start(func = x.specificHotelScrape, funcARGs = 'Amara Singapore') -> this will run the specificHotelScrape function, stops when it finds a review that is already in the csv
#? (so its like updating new reviews until it finds a review that is already in the csv)
#? 3. x.start(func = x.specificHotelScrape, funcARGs = ['Amara Singapore',False]) -> this will run the specificHotelScrape function like in 2, 
#? but it will not stop when it finds a review that is already in the csv, this is for trying to find a hotel that is not in the csv yet so i am getting all the reviews
#? 4. x.threadhandlers() -> this will run the generalHotelScrape function with 3 threads
#? 5. x.threadhandlers(hotelname = 'Amara Singapore') -> this will run the specificHotelScrape function with 3 threads, jumps when it finds a review that is already in the csv
#? 6. x.threadhandlers(hotelname = 'Amara Singapore', update = True) -> this will run the specificHotelScrape function with 3 threads, stops when it finds a review that is already in the csv
