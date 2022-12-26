import os
import selenium.webdriver
import csv
import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

url_sets=["https://www.walmart.com/browse/tv-video/all-tvs/3944_1060825_447913",
    "https://www.walmart.com/browse/computers/desktop-computers/3944_3951_132982",
         "https://www.walmart.com/browse/electronics/all-laptop-computers/3944_3951_1089430_132960",
         "https://www.walmart.com/browse/prepaid-phones/1105910_4527935_1072335",
         "https://www.walmart.com/browse/electronics/portable-audio/3944_96469",
         "https://www.walmart.com/browse/electronics/gps-navigation/3944_538883/",
         "https://www.walmart.com/browse/electronics/sound-bars/3944_77622_8375901_1230415_1107398",
         "https://www.walmart.com/browse/electronics/digital-slr-cameras/3944_133277_1096663",
         "https://www.walmart.com/browse/electronics/ipad-tablets/3944_1078524"]

categories=["TVs","Desktops","Laptops","Prepaid_phones","Audio","GPS","soundbars","cameras","tablets","graphiccards"]


# scraper
for pg in range(len(url_sets)):
    # number of pages per category
    top_n= ["1","2","3","4","5","6","7","8","9","10","11"]
    # extract page number within sub-category
    url_category=url_sets[pg]
    print("Category:",categories[pg])
    final_results = []
    for i_1 in range(len(top_n)):
        print("Page number within category:",i_1)
        url_cat=url_category+"?page="+top_n[i_1]
        driver= webdriver.Chrome(executable_path='C:/Drivers/chromedriver.exe')
        driver.get(url_cat)
        body_cat = driver.find_element_by_tag_name("body").get_attribute("innerHTML")
        driver.quit()
        soupBody_cat = BeautifulSoup(body_cat)
 
 
        for tmp in soupBody_cat.find_all('div', {'class':'search-result-gridview-item-wrapper'}):
            final_results.append(tmp['data-id'])
            
    # save final set of results as a list        
    codelist=list(set(final_results))
    print("Total number of prods:",len(codelist))
    # base URL for product page
    url1= "https://walmart.com/ip"


    # Data Headers
    WLMTData = [["Product_code","Product_name","Product_description","Product_URL",
   "Breadcrumb_parent","Breadcrumb_active","Product_price",         
   "Rating_Value","Rating_Count","Recommended_Prods"]]
 
    for i in range(len(codelist)):
        #creating a list without the place taken in the first loop
        print(i)
        item_wlmt=codelist[i]
        url2=url1+"/"+item_wlmt
        #print(url2)


        try:
            driver= webdriver.Chrome(executable_path='C:/Drivers/chromedriver.exe') # Chrome driver is being used.
            print ("Requesting URL: " + url2)


            driver.get(url2)   # URL requested in browser.
            print ("Webpage found ...")
            time.sleep(3)
            # Find the document body and get its inner HTML for processing in BeautifulSoup parser.
            body = driver.find_element_by_tag_name("body").get_attribute("innerHTML")
            print("Closing Chrome ...") # No more usage needed.
            driver.quit()     # Browser Closed.


            print("Getting data from DOM ...")
            soupBody = BeautifulSoup(body) # Parse the inner HTML using BeautifulSoup


            h1ProductName = soupBody.find("h1", {"class": "prod-ProductTitle prod-productTitle-buyBox font-bold"})
            divProductDesc = soupBody.find("div", {"class": "about-desc about-product-description xs-margin-top"})
            liProductBreadcrumb_parent = soupBody.find("li", {"data-automation-id": "breadcrumb-item-0"})
            liProductBreadcrumb_active = soupBody.find("li", {"class": "breadcrumb active"})
            spanProductPrice = soupBody.find("span", {"class": "price-group"})
            spanProductRating = soupBody.find("span", {"itemprop": "ratingValue"})
            spanProductRating_count = soupBody.find("span", {"class": "stars-reviews-count-node"})
 
            ################# exceptions #########################
            if divProductDesc is None:
                divProductDesc="Not Available"
            else:
                divProductDesc=divProductDesc
 
            if liProductBreadcrumb_parent is None:
                liProductBreadcrumb_parent="Not Available"
            else:
                liProductBreadcrumb_parent=liProductBreadcrumb_parent
 
            if liProductBreadcrumb_active is None:
                liProductBreadcrumb_active="Not Available"
            else:
                liProductBreadcrumb_active=liProductBreadcrumb_active
 
            if spanProductPrice is None:
                spanProductPrice="NA"
            else:
                spanProductPrice=spanProductPrice


            if spanProductRating is None or spanProductRating_count is None:
                spanProductRating=0.0
                spanProductRating_count="0 ratings"


            else:
                spanProductRating=spanProductRating.text
                spanProductRating_count=spanProductRating_count.text




            ### Recommended Products
            reco_prods=[]
            for tmp in soupBody.find_all('a', {'class':'tile-link-overlay u-focusTile'}):
                reco_prods.append(tmp['data-product-id'])


            if len(reco_prods)==0:
                reco_prods=["Not available"]
            else:
                reco_prods=reco_prods
            WLMTData.append([codelist[i],h1ProductName.text,ivProductDesc.text,url2, liProductBreadcrumb_parent.text, liProductBreadcrumb_active.text, spanProductPrice.text, spanProductRating, spanProductRating_count,reco_prods])


        except Exception as e:
            print (str(e))

# save final result as dataframe
    df=pd.DataFrame(WLMTData)
    df.columns = df.iloc[0]
    df=df.drop(df.index[0])


# Export dataframe to SQL
import sqlalchemy
database_username = 'ENTER USERNAME'
database_password = 'ENTER USERNAME PASSWORD'
database_ip       = 'ENTER DATABASE IP'
database_name     = 'ENTER DATABASE NAME'
database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'. format(database_username, database_password, database_ip, base_name))
df.to_sql(con=database_connection, name='‘product_info’', if_exists='replace',flavor='mysql')


# CODED BY C3YS
