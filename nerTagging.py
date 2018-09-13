import nltk
from nltk.tokenize import TweetTokenizer
from stanfordcorenlp import StanfordCoreNLP
from data_cleaning import clean_collection
from nltk.collocations import *
import pymysql
from datetime import date
import json
import logging
from difflib import SequenceMatcher
bigram_measures = nltk.collocations.BigramAssocMeasures()
import wikipedia

nlp = StanfordCoreNLP(r'C:\\Users\\Irene\\Documents\\stanford-corenlp-full-2018-02-27\\')

#database connection
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='meacrouwro', db='tweet_data', autocommit=True)
conn.set_charset('utf8mb4')
c = conn.cursor()
c.execute('SET NAMES utf8mb4;')
c.execute('SET CHARACTER SET utf8mb4;')
c.execute('SET character_set_connection=utf8mb4;')


def ner_chunk(ner_tag):
    chunked, pos, prev_tag = [], "", ""
    for i, word_pos in enumerate(ner_tag):
        wordpos, pos = word_pos
        if pos in ['PERSON', 'ORGANIZATION', 'LOCATION'] and pos == prev_tag:
            chunked[-1] += word_pos
        else:
            chunked.append(word_pos)
        prev_tag = pos

    clean_chunked = [tuple([" ".join(wordpos[::2]), wordpos[-1]]) if len(wordpos)!=2 else wordpos for wordpos in chunked]

    return clean_chunked

def tag_text(text):
    ner_text = nlp.ner(text)
    chunk_tag = ner_chunk(ner_text)
    final_tag = []
    for tag in chunk_tag:
        if tag[1] == 'PERSON':
            final_tag.append(tag[0])
    return ','.join(final_tag)

def ner_tag():
    query = 'SELECT `id`, `text`  FROM `data` WHERE `entity` IS NULL;'
    c.execute(query)
    result = c.fetchall()
    raw_collection = [row[1] for row in result]
    cleaned_collection = clean_collection(raw_collection)
    found_count = 0
    notfound_count = 0
    for i,row in enumerate(result):
        cleaned_text = cleaned_collection[i]
        print(cleaned_text)
        tweet_id = row[0]
        tag = tag_text(cleaned_text)
        if tag != '':
            query = 'UPDATE `data` set `entity` = %s WHERE `id` = %s;'
            c.execute(query, (tag, tweet_id,))
            print(tag)
            found_count += 1

        else:
            query = 'UPDATE `data` set `entity` = %s WHERE `id` = %s;'
            c.execute(query, ('Not Found', tweet_id,))
            print("not found")
            notfound_count += 1

    print("Found: " + str(found_count) + " Not Found: " + str(notfound_count) )
    nlp.close()


# class Entity:
#
#     def __init__(self, name):
#         self.name = name
#         self.corpus = create_corpus(name)
#         self.extended_targets = []
#         self.entity_filter = lambda *w: name not in w
#
#
#     def extract_extended(self, K=5):
#         # for sentence in self.corpus:
#         #       pos_tags = nlp.pos_tag(sentence)
#         #       tagged_corpus.append(pos_tags)
#         #tagged_corpus = " ".join(remove_stopwords(" ".join(self.corpus)))
#         tagged_corpus = ' '.join(clean_collection(self.corpus))
#
#         #print(tagged_corpus)
#
#         finder = BigramCollocationFinder.from_words(tknzr.tokenize(tagged_corpus))
#         finder.apply_freq_filter(3)
#         finder.apply_ngram_filter(self.entity_filter)
#         for i in finder.nbest(bigram_measures.pmi, K):
#             self.extended_targets.append(i)
#             print(i)

if __name__ == "__main__":
    ner_tag()









