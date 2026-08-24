import pandas as pd
from dash import Dash, dcc, html
import sys
import os
import plotly.express as px
import ast

#Get path to matchingScores array
currentDir = os.path.dirname(__file__)
csvPath = os.path.join(currentDir, "../backend")
dataPath = os.path.join(currentDir, "../data/matchingCourses.csv")
sys.path.append(csvPath)

from compareData import matchScores

#Get the matching courses csv
matchingCourses = pd.read_csv(dataPath)

#Create the dashboard
app = Dash(__name__)

def score_bar(score):
    return html.Div([
        html.Div(
            f"Match Percentage: {round(score, 3)}%",
            style={
                "textAlign": "right",
                "fontWeight": "bold",
                "marginBottom": "5px"
            }
        ),

        html.Div(
            html.Div(
                style={
                    "width": f"{score}%",
                    "height": "10px",
                    "borderRadius": "2px",
                    "backgroundColor": "#4CAF50"
                }
            ),
            style={
                "width": "100%",
                "height": "10px",
                "backgroundColor": "#e0e0e0",
                "borderRadius": "2px"
            }
        )
    ])

#Get the html for each course
coursesHTML = []
n = 5 #top n recommendations

for i in range(len(matchScores[0])):
        coursesHTML.append(
             html.Div([
                  html.H1(f"{i + 1}. University: " + matchingCourses.iloc[i]["uni"]),
                  html.H2("Course: " + matchingCourses.iloc[i]["course"]),
                  html.H2("Postcode: " + matchingCourses.iloc[i]["postcode"]),
                  html.H2("Minimum A Level Grades: " + "".join(ast.literal_eval(matchingCourses.iloc[i]["minalevel"]))),
                  html.H2("Maximum A Level Grades: " + "".join(ast.literal_eval(matchingCourses.iloc[i]["maxalevel"]))),
                  score_bar(round(matchScores[0][i], 3))], 
             style={
                  "font-family": "Verdana, Arial, Tahoma, Serif"
             })
        )

app.layout = html.Div([
     html.Div(coursesHTML)
])

if __name__ == "__main__":
    app.run(debug=True)