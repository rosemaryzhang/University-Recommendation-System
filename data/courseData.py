import csv
import os
from bs4 import BeautifulSoup
import requests
from lxml import etree
import re
import time
#Gather the required data for each course
#University, Course name, Subject, Grades, Location

coursesInfo = []

#Read the URLs for each course
scriptDir = os.path.dirname(os.path.abspath(__file__))
csvFilePath = os.path.join(scriptDir, "courseURLs.csv")


with open(csvFilePath, "r") as f:
    courseURLs = csv.reader(f)
    for url in courseURLs:
        print("running")
        minTariff = 0
        maxTariff = 0

        #Extract the data
        response = requests.get(url[0])
        print(url[0])
        soup = BeautifulSoup(response.content, 'lxml')

        #University
        uniTag = soup.find('a', class_="font-yard link-secondary")
        print(uniTag)
        if uniTag != None:
            uni = uniTag.text
        else:
            uni = ""
        print(uniTag)

        #Course name
        courseNameTag = soup.find('h1', class_="word-wrap")
        print(courseNameTag)
        if courseNameTag != None:
            courseName = courseNameTag.text
        else:
            courseName = ""

        #Grades
        entryRequirementsBox = soup.find('df-accordion', {"id": "academicEntryRequirements"})
        grades = {"A*": 56, "A": 48, "B": 40, "C": 32, "D": 24, "E": 16}
        
        if entryRequirementsBox != None:
            aLevelDiv = entryRequirementsBox.find('div', text="A level")
            if aLevelDiv == None:
                #no A Levels
                aLevelGradeReq = ""
            else:
                #need A Levels
                #Get the A Level grade requirements
                aLevelGradeReqTag = aLevelDiv.find_parent().find('strong')
                aLevelGradeReq = aLevelGradeReqTag.text.strip('"')

                #Seperate the min and max A level grades
                
                if '-' in aLevelGradeReq:
                    #Use RegEx to get grades
                    minAndMax = aLevelGradeReq.split(' - ')
                        
                    minALevel = re.findall('A\*|[ABCDE]', minAndMax[0])
                    maxALevel = re.findall('A\*|[ABCDE]', minAndMax[1])
    
                else:
                    minALevel = maxALevel = re.findall('A\*|[ABCDE]', aLevelGradeReq)

                #Convert to tariff

                for i in minALevel:
                    minTariff += grades[i]
                for i in maxALevel:
                    maxTariff += grades[i]
        else:
            #no academic entry requirements
            aLevelGradeReq = ""

        #Location
        address = soup.find("span", class_="adr")
        if address != None:
            for br in address.find_all("br"):
                br.replace_with("\n")

            lines = [line.strip() for line in address.get_text().split("\n") if line.strip()]

            postcode = lines[-1] if lines else None
        else:
            postcode = ""
        
        #Write data to csv

        extractedDataFilePath = os.path.join(scriptDir, "extractedData.csv")

        #Gather data
        courseInfo = {
            'uni': uni,
            'course': courseName,
            'minTariff': minTariff,
            'maxTariff': maxTariff,
            'postcode': postcode
        }

        print(courseInfo)

        coursesInfo.append(courseInfo)

        time.sleep(2)

#Write extracted data to csv
with open(extractedDataFilePath, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=['uni', 'course', 'minTariff', 'maxTariff', 'postcode'])

    writer.writeheader()

    for course in coursesInfo:
        writer.writerow(course)
        


        