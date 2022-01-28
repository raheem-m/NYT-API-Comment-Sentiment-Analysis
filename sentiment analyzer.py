# this is a program which takes in a search term from the user, then takes ten articles using the NYT Article Search API, goes through as many comments as the article has
# up to 25, then analyzing the comments using TextBlob's sentiment analyzer to see if the searched term is viewed positively or negatively by the NYT community. 

#importing all necessary modules
import requests, time, csv, pathlib
from textblob import TextBlob

#assigning all API URLs and the API key to variables for easy calling
API_KEY = {api-key}
comment_url = "https://api.nytimes.com/svc/community/v3/user-content/url.json"
article_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

#creating an empty list to be populated by dictionaries that will be loaded into a .csv file
csv_data = []

def sentiment_analyzer(comment):
    """
    This function analyzes the sentiment of a body of text, and returns the sentiment: a number ranging from -1 to +1 indicating the negativity or positivity of a statement
    The operation is as follows:
    1. assign text as TextBlob object
    2. use sentiment method to determine positivity
    3. return value of sentiment
    """
    comment = TextBlob(comment)
    sentiment = comment.sentiment.polarity
    return sentiment


def comment_processor(article_url_to_be_processed):
    """
    this function proccesses comments, being passed the url for the article and going through up to 25 comments, keeping track of the amount of comments, average sentiment of all comments 
    on the article, then appending a dictionary containing that information to a list.
    The operation is as follows:
    1. parameters are set to call to an API that will return comments from a page
    2. comments are converted to json format for processing
    3. comments are iterated through to analyze sentiment
    4. sentiment is averaged per article
    5. average sentiment and number of comments is appended to a list of dictionaries.
    """
    params = {"url":article_url_to_be_processed, "api-key":API_KEY}
    comments = requests.get(comment_url,params=params)
    comments = comments.json()
    
    sentiment = 0
    num_of_comments = 0
    avg_sent = 0
    
    #iterates through comments and analyzes sentiment
    for i in comments ["results"]["comments"]:
        num_of_comments +=1
        sentiment += sentiment_analyzer(i["commentBody"])
    
    #averages sentiment for all comments on an article
    if (num_of_comments != 0):
        avg_sent = sentiment/num_of_comments
    
    #appends data to list as dictionary
    csv_data.append ({"number_of_comments":num_of_comments, "avg_sentiment":avg_sent, "url":article_url_to_be_processed})

#prompts user to search for a topic
article_search = input("Enter the title of an article: ")
#setting parameters and calling on API URL to get response
article_search_params = {"q":article_search,"api-key":API_KEY, 'page':0}
response = requests.get(article_url,params=article_search_params)
#response is converted to json for processing
response = response.json()

count = 0
for i in response ["response"] ["docs"]:
    #URL that is being processed is printed on the screen along with number to show user that something is happening
    count += 1
    print (str(count) +": "+ i["web_url"])
    
    if ("video" in i["web_url"]):
        #video pages result in error due to lack of comments; video articles are passed through
        pass
    else:
        #API call halted for three seconds to prevent errors
        time.sleep(3)
        comment_processor (i["web_url"])

#while loop in place to ensure proper data entry from user
while (True):
    #asks user if data would like to be trimmed to exclude 0 comment results
    comment_excluder = input("Exclude articles with zero comments? Y/n: ")
    if (comment_excluder.upper() == "Y"):
        for i in csv_data:
            if (i ["number_of_comments"] == 0):
                csv_data.remove(i)
        break
    elif (comment_excluder.upper()=="N"):
        break
    else:
        print ("invalid entry!")

#path of .csv file to which data will be loaded into is defined
path = pathlib.Path.cwd()
path = path/"comments.csv"
#path is opened and headers along with data are written to .csv file using list of dictionaries
with path.open(mode="w",encoding="utf-8",newline="") as csv_file:
    writer=csv.DictWriter(csv_file,fieldnames=["number_of_comments","avg_sentiment","url"])
    writer.writeheader()
    writer.writerows(csv_data)
#confirmation message displayed to show user processing is done, including file path.
print(f"Data has been processed and loaded into {path}")
    