#https://medium.com/@purnima.msb/diy-semantic-search-a-step-by-step-guide-37e0b6df2a1f

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"

#-- Semantic search for Course name--

#Courses to search for semantically
currentDir = os.path.dirname(__file__)
csvPath = os.path.join(currentDir, "../data/extractedData.csv")
df = pd.read_csv(csvPath, usecols=['course'])
df["course"] = df["course"].fillna("")

courses = df['course'].tolist() #Array of the courses to be used in semantic search

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

    #Return results with scores and documents
    results = []
    for score, idx in zip(scores[0], indices[0]):
        results.append(
            #"score": float(score),
            #"similarity_pct": f"{score * 100:.1f}%",
            courses[idx]
        )
    
    return results

#Applying semantic search to query

query = "theatre" #User course input
topk = 5 #Retrieve top 5 matches

matchingCourses = semanticSearch(query, topk)

#Gather the other info for the matching courses

#Import csv into SQL
from sqlalchemy import create_engine

engine = create_engine('post')