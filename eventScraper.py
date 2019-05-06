# Web scraping script for event/news metadata.
# Author : Megha Jain
#

from bs4 import BeautifulSoup
import requests

# Set the given langing page's URL as a constant variable.
LANDING_URL = "https://www.wolfsberg-principles.com/news-events"

# Create/open an output file that will store the results containing metadata.
outfile = open("metadata_output.json","w+")

# A utility function to parse date into a standardised year-month-day format. 
def dateParser(date_string):
    
    # Dictonary for month name to number conversion. 
    months = {
        'January' : '01',
        'February' : '02',
        'March' : '03',
        'April' : '04',
        'May' : '05',
        'June' : '06',
        'July' : '07',
        'August' : '08',
        'September' : '09',
        'October' : '10',
        'November' : '11',
        'December' : '12' 
    }
    
    words = [word.strip(',') for word in date_string.split()]
    
    # Find the corresponding month number from the name by lookup in dictionary.
    month = months[words[0]]
    yyyy_mm_dd = words[2] + '-' + month + '-' + words[1]
    return yyyy_mm_dd
        
        

# Function to send a get reuqest to an input url, and use BeautifulSoup object and methods to extract publication date and title metadata.
def scrapeFromURL(url_to_scrape):
    
    # Try-except block to catch Page Not Found and other erroneous status codes. 
    try:
        response = requests.get(url_to_scrape)
        # If status code not OK (200), raise an exception.
        if response.status_code != 200:
            response.raise_for_status()
    except requests.HTTPError as error:
        # Print specific error code and description if exception raised.
        print("Something went wrong! Error:", error)
  
    
    # Initialise a BeautifulSoup object with lxml parser and xml/html source content retrieved from the get request.
    contents = BeautifulSoup(response.content, 'lxml')
    
    # Scrape for news dates by finding all instances of div tag with the spcific class name found from the source file. 
    news_dates = contents.find_all('div', class_='news-6-pod__info')
    # Scrape for news titles by finding all instances of div tag with the spcific class name found from the source file. 
    news_titles = contents.find_all('div', class_='news-6-pod__title')
            
    
    num_items = len(news_dates)
    
    
    for x in range(num_items):
        # Convert date to correct format.
        date = dateParser(news_dates[x].text)
        # Find corresponding title and strip it of whitespaces.
        title = news_titles[x].text.strip()
        
        # Formatted string to write to output file.
        string_to_write = "{'publication_date': '%s',\n'title': '%s'}" % (date, title)
        outfile.write(string_to_write)
        
        if x < num_items - 1:
            outfile.write(",\n")
        
    
# Main function that scrapes the landing page source file for URL's for pages 2,3 etc that also contain publication metadata. 
def main():
    
    # Array of all URL's on which there is publication metadata.
    urls = [LANDING_URL]
    
    # Try-except to obtain page source html/xml and report error if any. 
    try:
        response = requests.get(LANDING_URL)
        if response.status_code != 200:
            response.raise_for_status()
    except requests.HTTPError as error:
        print("Something went wrong! Error:", error)
    
    contents = BeautifulSoup(response.content, 'lxml')
    # Find all ul tags with the class name 'pager' found from reviewing the source.
    ul = contents.find_all("ul", class_="pager")
    
    
    for u in ul:
        # Find all li tags with classname pager-item that list hrefs containing url params for pages 2,3 etc.
        # This is done in a loop assuming the web page is dynamic and may have pages beyond 3 containing publication metadata in the future. 
        lis = u.find_all("li", class_="pager-item")
        for li in lis:
            # Find all a tags containing href field. 
            url = li.find("a", href=True)
            # Retrieve only the href part to extract url params for pages 2,3 etc.
            url = url['href']
            params = url.split("?")
            # Append to landing url to form the correct url for rquesting data from pages 2,3 etc.
            path = LANDING_URL + "?" + params[1]
            urls.append(path)
            
     
    
    outfile.write("[")       
       
      
    # Call the main scraping function for all URLs for pages that could contain publication metadata. 
    for x in range(len(urls)):
        scrapeFromURL(urls[x]) 
        if x < len(urls) - 1:
            outfile.write(",\n")
    
    outfile.write("]")
    
    outfile.close()
    


if __name__ == "__main__":
    main()
    
    
    
        
        




