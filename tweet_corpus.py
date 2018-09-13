import pymysql
from data_cleaning import clean_collection
from stanfordcorenlp import StanfordCoreNLP
from data_cleaning import clean_text
import math

#database connection
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='meacrouwro', db='tweet_data', autocommit=True)
conn.set_charset('utf8mb4')
c = conn.cursor()
c.execute('SET NAMES utf8mb4;')
c.execute('SET CHARACTER SET utf8mb4;')
c.execute('SET character_set_connection=utf8mb4;')

nlp = StanfordCoreNLP(r'C:\\Users\\Irene\\Documents\\stanford-corenlp-full-2018-02-27\\')
noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']

def extract_entities(date):
    query = 'SELECT `entity` FROM `data` WHERE DATE(`time`)=%s AND `entity` IS NOT NULL' \
            ' AND `entity` NOT LIKE %s GROUP BY `entity` ORDER BY COUNT(`entity`) DESC LIMIT 5 '
    c.execute(query, (date, ('%' + 'Not Found' + '%',) ))
    result = c.fetchall()
    allentities = []
    indices=[]
    entities = [row[0] for row in result]
    for item in entities:
        temp = item.split(',')
        for tempitem in temp:
            allentities.append(tempitem)
    allentities = sorted(list(set(allentities)), key = len)
    # for i in range((len(allentities)-1)):
    #     indices.append([s for j, s in enumerate(allentities[i+1:]) if allentities[i].lower() in s.lower()])
    #
    # print(indices)
    #result = []
    # for entity in allentities:
    #     if (len(result) == 0):
    #         result.append([entity])
    #     else:
    #         for i in range(0, len(result)):
    #             score = SequenceMatcher(None, entity, result[i][0]).ratio()
    #             if (score < 0.6):
    #                 if (i == len(result) - 1):
    #                     result.append([entity])
    #             else:
    #                 if (score != 1):
    #                     result[i].append(entity)
    # print(result)
    return allentities

def entity_corpus(entity, date):
    corpus = []
    terms = entity.split(' ')
    search = '%'
    for term in terms:
        search = search + term + '%'
    query = 'SELECT `id`,`text` FROM `data` WHERE `entity` LIKE %s AND DATE(`time`) = %s'
    c.execute(query, (search, date, ))
    result = c.fetchall()
    for row in result:
        corpus.append(row[1])
    return clean_collection(corpus)

def extended_targets(entity, date):
    corpus = entity_corpus(entity, date)
    nouns = []
    for tweet in corpus:
        tags = nlp.pos_tag(tweet)
        for tag in tags:
            if tag[1] in noun_tags:
                nouns.append(tag[0].lower())
    nouns = list(set(nouns))
    probT = (len(corpus)/36000)/6000
    for noun in nouns:
        counterC = 0
        for tweet in corpus:
            if noun in corpus:
                counterC += 1
        print(noun)
        print(math.log())





if __name__ == "__main__":
    extended_targets('Trump', '2018-05-28')
    nlp.close()