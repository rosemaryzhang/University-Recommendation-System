#https://medium.com/@purnima.msb/diy-semantic-search-a-step-by-step-guide-37e0b6df2a1f

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import os
import re
import math
from InquirerPy import inquirer

os.environ["HF_HUB_DISABLE_XET"] = "1"

#User input
userLocation = inquirer.select(message="Choose your location: ", choices=[
    "London",
    "South East",
    "South West",
    "East of England",
    "West Midlands",
    "East Midlands",
    "Yorkshire and the Humber",
    "North West",
    "North East",
    "Scotland",
    "Wales",
    "Northern Ireland",
    "No Preference"
]).execute() #Only accept regions from uk
userGrades = inquirer.text(message="Enter your grades:", validate = lambda grades: (0 < len(re.findall(r'(?:A\*|[ABCDEU])', grades, re.IGNORECASE)) <= 4 and re.fullmatch(r'(?:A\*|[ABCDEU])+', grades, re.IGNORECASE)),
                           invalid_message="Input cannot be empty and cannot exceed 4 A Level grades").execute().replace(" ", "").upper()
userCourse = inquirer.text(message="Enter your course: ").execute() #User course input

#-- Semantic search for Course name--
#Courses to search for semantically
currentDir = os.path.dirname(__file__)
csvPath = os.path.join(currentDir, "../data/extractedData.csv")
dfCourse = pd.read_csv(csvPath, usecols=['course']) #get only the courses
dfCourse["course"] = dfCourse["course"].fillna("")

courses = dfCourse['course'].tolist() #Array of the courses to be used in semantic search

#Load pre-trained model
sentenceTransformerPath = os.path.join(currentDir, "../all-MiniLM-L6-v2")
model = SentenceTransformer(sentenceTransformerPath)

#Create embeddings for the documents
embeddings = model.encode(courses, convert_to_numpy=True, normalize_embeddings=True)

#Create index that uses inner product
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)

#Add all embeddings to the index
index.add(embeddings.astype(np.float32))

#Semantic Search Function
def semanticSearch(query: str, topk: int):
    #Embed the query
    queryEmbedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)

    #Search FAISS for the k nearest neighbors
    scores, indices = index.search(queryEmbedding, topk)

    #Return results with normalised scores and documents
    results = []
    for score, idx in zip(scores[0], indices[0]):
        results.append(
            courses[idx]
        )
    
    return results, scores

#Applying semantic search to query
topk = 5 #Retrieve top 5 matches

matchingCourses = semanticSearch(userCourse, topk)

#Gather the other info for the matching courses

#Import csv into SQL done in PostgreSQL

#Read SQL table where the courses match result from semantic search

connectionString = 'postgresql+pg8000://postgres:rosemary123@localhost:5432/uniRec'

#query the whole sql table
fullSqlDf = pd.read_sql('courses', connectionString)

matchingCoursesDf = fullSqlDf.loc[fullSqlDf['course'].isin(matchingCourses[0])] #dataframe where courses match semantic search

#-- Compare grade requirements
#Get the average tariff for each row
matchingTariff = []

for row in matchingCoursesDf.itertuples(index=False):
    rowMin = row.mintariff
    rowMax = row.maxtariff
    matchingTariff.append((rowMin + rowMax)/2)

#-- Compare location
#convert postcode to longitude and latitude with geopy
regions = {
    "North East": "E12000001",
     "North West": "E12000002", 
     "Yorkshire and The Humber": "E12000003", 
     "East Midlands": "E12000004", 
     "West Midlands": "E12000005", 
     "East of England": "E12000006", 
     "London": "E12000007", 
     "South East": "E12000008", 
     "South West": "E12000009", 
     "Scotland": "S", 
     "Wales": "W", 
     "Northern Ireland": "N", 
     "No Preference": ""
     }

#Import the csv to get gss codes
ONSPDcsvPath = os.path.join(currentDir, '../ONSPD_FEB_2025/Data/multi_csv')

#Loop through each matching course in the df
matchingRegions = []

for row in matchingCoursesDf.itertuples(index=False):
    #Get the GSS Code from the postcode
    rowPostcode = row.postcode
    #get the area from the postcode
    rowArea = re.search('[A-Z]+', rowPostcode).group()
    #Find the relevant csv file for GSS conversion
    rowCSV = f"ONSPD_FEB_2025_UK_{rowArea}.csv"
    rowONSPDcsvPath = os.path.join(currentDir, '../ONSPD_FEB_2025/Data/multi_csv/'+rowCSV)
    dfRowCsv = pd.read_csv(rowONSPDcsvPath, usecols=['pcds','rgn'])
    #Get the GSS code from the postcode in the df
    rowGssDf = dfRowCsv.loc[dfRowCsv['pcds'] == rowPostcode, 'rgn'].values

    if len(rowGssDf) != 0: 
        rowGssVal = rowGssDf[0]
        #Find region from GSS

        if "E" in rowGssVal:
            #get region if in England
            rowRegion = [key for key, val in regions.items() if val == rowGssVal]
            matchingRegions.append(rowRegion[0])
        else:
            #get the country if not in England
            countryLetter = re.search('[A-Z]+', rowGssVal).group()
            rowCountry = [key for key,val in regions.items() if val == countryLetter]
            matchingRegions.append(rowCountry[0])
        
    else:
        matchingRegions.append("No Preference")

#Compare the user's region to the regions of the matching courses using k nearest neighbours
#quantify the regions
regionQuantifier = {
    "North East": [55, 1.9],
     "North West": [54, -2], 
     "Yorkshire and The Humber": [53, -1.1], 
     "East Midlands": [52.6, 0], 
     "West Midlands": [52, -2], 
     "East of England": [52, 0], 
     "London": [51.5, -0.12], 
     "South East": [51, 0], 
     "South West": [50, -3], 
     "Scotland": [56, -4], 
     "Wales": [52, -4], 
     "Northern Ireland": [54.5, -6], 
     "No Preference": ""
     }
#[N, E] for DMS locations
userCoord = regionQuantifier[userLocation]
matchingCoord = list(map(lambda x: regionQuantifier[x], matchingRegions)) #Coordinates for the matching courses in the df

#-- Compare the tariff points required
#Convert user A Level grade to tariff
grades = {"A*": 56, "A": 48, "B": 40, "C": 32, "D": 24, "E": 16, "U": 0}
        
userTariff = 0
parsedUserGrades = re.findall(r'A\*|[ABCDEU]', userGrades, re.IGNORECASE)

for i in parsedUserGrades:
    userTariff += grades[i]

#user vector is form [avg tariff, N, E]
userVector = [userTariff, userCoord[0], userCoord[1]]

#Create vectors for the matching courses
matchingVectors = []

matchingVectors = [[val, matchingCoord[index][0], matchingCoord[index][1]] for index, val in enumerate(matchingTariff)] #Create vectors [avg tariff, N, E]

#Use unsupervised NN to compare the matchingVectors to userVector and get the top 5 recommendations
#Use ball tree
from sklearn.neighbors import BallTree
tree = BallTree(matchingVectors, leaf_size=2, metric='euclidean')
dist, ind = tree.query([userVector], k=3)
#Display the top 5 matches

#Write the matchingCourses to a csv
matchingPath = os.path.join(currentDir, "../data/matchingCourses.csv")
matchingCoursesDf.to_csv(matchingPath)

#Get match score
gradeDiff = [abs(userTariff - i) for i in matchingTariff] #Difference in grades
gradeScores = [max(0, (1 - (i/40))) for i in gradeDiff] #Convert grade to a score

locationDiff = [math.sqrt((matchingCoord[i][0] - userCoord[0])**2 + (matchingCoord[i][1] - userCoord[1])**2) for i in range(len(matchingCoord))] #Difference in location
locationScores = [max(0, (1 - (i/5))) for i in locationDiff]

semanticScores = matchingCourses[1]

#Calculate overall match scores
#Weights
nameWeight = 0.7
gradeWeight = 0.15
locationWeight = 0.15

matchScores = [(nameWeight*semanticScores[i] + gradeWeight*gradeScores[i] + locationWeight*locationScores[i])*100 for i in range(len(semanticScores))]

    





