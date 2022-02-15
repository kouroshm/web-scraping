import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import re
import pandas as pd

url = 'https://ca.trustpilot.com/review/www.skype.com'
URL = []
URL.append(url)
companyName = []
reviewBody = []
datePublished = []
ratingValue = []


def getdata(url):
    '''This function will get all the data from trustpilot'''
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    sleep(randint(2, 10))
    return soup


def findreviewnum(soup):
    '''The function counts the number of reviews'''

    script = soup.find('script', {'data-initial-state': 'review-list'})
    script = str(script.contents)
    n = re.findall(r"\d+", script)
    return "total numbers of reviews:" + n[0]


def getnextpage(soup):
    '''The function finds the next button and return the url'''
    next_btn = soup.find('a', {'class': 'button button--primary next-page'})
    if next_btn:
        url = 'https://ca.trustpilot.com' + next_btn['href']
        return url
    else:
        return


def reviewBodyStrip(reviewBody):
    '''Replaced all break lines with nothing and remove characters
    from the beginning and the end of the string.'''
    reviewBody = reviewBody.replace('\n', '')
    reviewBody = reviewBody.lstrip()
    reviewBody = reviewBody.rstrip()

# Getting the reviews from url and finding number of reviews.
soup = getdata(url)
print(findreviewnum(soup))  # number of reviews
while True:
    soup = getdata(url)
    url = getnextpage(soup)
    if url:
        URL.append(url)
    else:
        break

# This for loop will input all different column in the review columns
# into different columns and at the end write it to a csv file.
for url in URL:
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    reviewContainer = soup.find_all('p', {'class': 'review-content__text'})
    name = soup.find_all('span', {'class': 'multi-size-header__big'})
    for reviews in reviewContainer:
        reviewBody.append(reviews.text)
        for i in range(len(reviewBody)):
            reviewBody[i] = reviewBody[i].replace('\n', ' ')
            reviewBody[i] = reviewBody[i].lstrip()
            reviewBody[i] = reviewBody[i].rstrip()
        for names in name:
            companyName.append(names.text)
            for i in range(len(companyName)):
                companyName[i] = companyName[i].replace('\n', ' ')
                companyName[i] = companyName[i].lstrip()
                companyName[i] = companyName[i].rstrip()
    for script in soup.find_all('script',
                                {'data-initial-state': 'review-dates'}):
        script = str(script.contents)
        n = re.findall(
                        r"([0-9]{4}\-[0-9]{2}\-[0-9]{2}T[0-9]{2}\:[0-9]{2}\:[0-9]{2})",
                        script)
        datePublished.append(n[0])
    for script in soup.find_all('script',
                                {'data-initial-state': 'review-info'}):
        script = str(script.contents)
        n = re.findall(r"\"stars\"\:\d+", script)
        n = str(n)
        ratingValue.append(n[-3])

'''Making a dictionary ready to input all the information and write it 
to the csv file.'''
dict = {'companyName': companyName,
        'datePublished': datePublished,
        'ratingValue': ratingValue,
        'reviewBody': reviewBody}
df = pd.DataFrame({key: pd.Series(value) for key, value in dict.items()})
df['companyName'] = df['companyName'].fillna('Skype')
df['reviewBody'] = df['reviewBody'].fillna('-')
df.to_csv('reviews.csv', index=False)
