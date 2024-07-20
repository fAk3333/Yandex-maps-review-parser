import json
import cfscrape
import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd

def json_to_dict():
    try:
        with open('company_reviews.json') as json_file:
            data = json.load(json_file)
        # print("Type:", type(data))
        #
        # print(data["company_reviews"])
        reviews = []
        stars = []
        data = data['company_reviews']
        for i in range(len(data)):
            if data[i]['star_count'] == 5:
                continue
            review = data[i]['review_text']
            if review == None:
                pass
            else:
                reviews.append(review.replace('\n', ''))
            star = data[i]['star_count']
            if star == None:
                pass
            else:
                stars.append((star))

        for string in reviews:
            string.replace('\n', '')

        print(reviews)
        print(stars)
        if len(reviews) != len(stars):
            return False, False
        else:
            return reviews, stars
    except TypeError:
        return False, False

def get_count_star(review_stars):
    star_count = 0
    for review_star in review_stars:
        if '_empty' in review_star.get('class'):
            continue
        elif '_half' in review_star.get('class'):
            star_count = star_count + 0.5
        else:
            star_count = star_count + 1
    return star_count


def get_session():
    session = requests.Session()
    session.headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
        'viewport-width': '1920'
    }
    return cfscrape.create_scraper(sess=session)


def parsing_data(data_result, r):
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        reviews = soup.find('div', {"data-chunk": "reviews"})
    except:
        return None
    try:
        summary_rating__main = reviews.find('div', {"class": "business-summary-rating__main-rating"})
    except:
        summary_rating__main = None
    try:
        rank_summary_rating__main = summary_rating__main.find('span',
                                                              {
                                                                  "class": "business-summary-rating-badge-view__rating"}).text
    except:
        rank_summary_rating__main = None
    try:
        count_summary_rating__main = summary_rating__main.find('div', {
            "class": "business-summary-rating-badge-view__rating-count"}).text
    except:
        count_summary_rating__main = None
    try:
        stars_summary_rating__main = get_count_star(
            summary_rating__main.find('div', {"class": "business-rating-badge-view__stars"}))
    except:
        stars_summary_rating__main = None
    data_result['company_info'] = {
        'company_rating': rank_summary_rating__main,
        'company_count_reviews': count_summary_rating__main,
        'company_count_stars': stars_summary_rating__main
    }
    try:
        reviews_list = reviews.find('div', {"class": "business-reviews-card-view__reviews-container"})
    except:
        reviews_list = None
    if reviews_list:
        review_id = 0
        for review in reviews_list:
            try:
                review_text = review.find('span', {"class": "business-review-view__body-text"}).text
            except:
                review_text = None
            try:
                star_count = get_count_star(review.find('div', {"class": "business-rating-badge-view__stars"}))
            except:
                star_count = None
            data_result['company_reviews'].append({
                'review_text': review_text,
                'star_count': star_count
            })
            review_id = review_id + 1
    return data_result


with open('id.txt', 'r') as file:
    ids = [line.rstrip() for line in file]

reviews = []
stars = []
for id in ids:
    yandex_id = id
    url = 'https://yandex.ru/maps/org/' + yandex_id + '/reviews/'
    session = get_session()
    r = session.get(url)
    data_result = {
        'company_info': {},
        'company_reviews': []
    }
    data_result = parsing_data(data_result, r)
    if len(data_result['company_reviews']) == 0 or len(data_result['company_info']) == 0:
        data_result = None
    with open('company_reviews.json', 'w') as f:
        json.dump(data_result, f, ensure_ascii=True, indent=4)
    print('Parsing Success')

    new_reviews, new_stars = json_to_dict()
    if new_reviews is False or new_stars is False:
        time.sleep(300)
        continue
    time.sleep(300)
    for item in new_reviews:
        reviews.append(item)
    for star in new_stars:
        stars.append(star)

# else:
#     f = open( 'отзывы.txt', 'w', encoding="utf8" )
#     for item in reviews:
#         f.write("%s\n" % item)
#
#     f = open( 'звёзды.txt', 'w', encoding="utf8")
#     for item in stars:
#         f.write("%s\n" % item)
else:
    df = pd.DataFrame(reviews, stars)
    df.to_excel('Results.xlsx')







