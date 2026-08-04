import pandas as pd
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"

#Gather the other info for the matching courses

#Import csv into SQL

currentDir = os.path.dirname(__file__)
csvPath = os.path.join(currentDir, "../data/extractedData.csv")

dfAll = pd.read_csv(csvPath) #Get the entire extractedData csv