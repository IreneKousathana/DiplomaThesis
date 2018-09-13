import re
import html
import itertools
import string
import json
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords

mention_pat = r'@[A-Za-z0-9]+'
url_pat = r'http[s]?://[A-Za-z0-9./]+'
hashtag_pat = r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"
punct = ''
slang = json.load(open('slangdict.json'))
contractions = json.load(open('contrdict.json'))
tknzr = TweetTokenizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    #escaping HTML characters
    text = html.unescape(text)
    #remove @mentions
    text = re.sub(mention_pat, ' ', text)
    #remove URLs
    text = re.sub(url_pat, ' ', text)
    #remove hashtags
    text = re.sub(hashtag_pat, ' ', text)
    # #Remove anything apart  a-z or 0-9
    # text = re.sub(r'[^A-Za-z0-9]', ' ', text)
    # #standardize words
    # text = "".join("".join(s)[:2] for _, s in itertools.groupby(text))
    # # Remove spaces apart from single spaces text
    # text = re.sub(r" +", ' ', text)
    return text

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def text_normalization(text):
    text = clean_text(text)
    # standardize words
    text = "".join("".join(s)[:2] for _, s in itertools.groupby(text))
    tokenized_text = tknzr.tokenize(text)
    for i, word in enumerate(tokenized_text):
        if word.lower() in slang:
            tokenized_text[i] = slang[word.lower()]
        if word.lower() in contractions:
            tokenized_text[i] = contractions[word.lower()]
    text = ' '.join(tokenized_text)
    # Remove anything apart  a-z or 0-9
    text = re.sub(r'[^A-Za-z]', ' ', text)

    # Remove spaces apart from single spaces text
    text = re.sub(r" +", ' ', text)
    return text

def clean_collection(collection):
    cleaned_collection = []
    for text in collection:
        cleaned_collection.append(text_normalization(text))
    return cleaned_collection

def remove_stopwords(text):
    tokenized_text = tknzr.tokenize(text)
    wordsList = [w for w in tokenized_text if not w in stop_words]
    return wordsList

