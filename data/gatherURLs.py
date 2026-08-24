from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import certifi
import truststore
truststore.inject_into_ssl()
import requests

#Gather the URLs for each course on the UCAS courses page
url = "https://www.ucas.com/explore/search/courses/"
courseURLs = []

#Extract all the urls to the courses
#Loop through the page numbers - use next page pagination
while url:
    response = requests.get(url, verify=certifi.where())
    soup = BeautifulSoup(response.content, 'html.parser')

    #Extract the URLs from page here
    courseBoxes = soup.find_all('article', class_="card card--quiet detail-card ext-exclude card-size--regular") #get the boxes for each course

    for course in courseBoxes:
        courseArticle = course.find('a', href=True)
        courseURL = courseArticle['href']
        courseURLs.append("https://www.ucas.com" + courseURL)
    
    next_link = soup.find('a', {"aria-label": "Next Page"}) #Find the 'next' button
    url = urljoin(url, next_link['href']) if next_link else None

#Save the URLs to CSV
filename = "courseURLs.csv"
scriptDir = os.path.dirname(os.path.abspath(__file__))
csvFilePath = os.path.join(scriptDir, filename)


with open(csvFilePath, mode="w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    for url in courseURLs:
        writer.writerow([url])