# University-Recommendation-System

--Data Extraction--

BeautifulSoup4 was used to scrape the UCAS Courses webpage to obtain the URLs for each course page. This was done in gatherURLs.py and obtained data is stored in courseURLs.csv. Currently, it is recommended to not run gatherURLs.py to overwrite courseURLs.csv due to a bot checker which has recently been added to the UCAS course page. To run the machine learning model, use the default version of courseURLs.csv.

From each course URL, the following was extracted from each course in courseData.py:
- University Name (uni)
- Course Name (course)
- Minimum Required Tariff Score (minTariff)
- Maximum Required Tariff Score (maxTariff)
- Postcode (postcode)
- Minimum Required A Level Grades (minALevel)
- Maximum Required A Level Grades (maxALevel)

This data is stored in extractedData.csv



--Machine Learning Model--

Use k-nearest neighbors 
