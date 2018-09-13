import nltk
from stanfordcorenlp import StanfordCoreNLP
import json
from annotator import dependency_tree, shortest_path, extract_coreferences
from tweet_corpus import extract_entities, entity_corpus
import logging

nlp = StanfordCoreNLP(r'C:\\Users\\Irene\\Documents\\stanford-corenlp-full-2018-02-27\\', quiet=False, logging_level=logging.DEBUG)

#creation of opinion lexicon
lexicon_file = nltk.data.load('vader_lexicon.txt')
lex_dict = {}
for line in lexicon_file.split('\n'):
    (word, measure) = line.strip().split('\t')[0:2]
    lex_dict[word] = float(measure)

#tokens like extract modificator
def find_sentiment(indicators, targets, graph):
    sentiment = 0
    for indicator in indicators:
        sentiment_orientation = lex_dict[indicator[0]]
        length = shortest_path(graph, indicator[1], targets)
        if length:
            sentiment = sentiment + sentiment_orientation/length
    return sentiment

def sentiment_indicators(parsed):
    sentence = parsed['sentences'][0]
    dependencies = sentence['enhancedDependencies']
    indicators = []
    for token in sentence['tokens']:
        if token['originalText'] in lex_dict:
            indicators.append((token['originalText'], str(token['index'])))
    return indicators

def sentiment_targets(parsed, entity):
    sentence = parsed['sentences'][0]
    targets = []
    for token in sentence['tokens']:
        if token['originalText'] in entity.split(' '):
            targets.append(str(token['index']))
    if parsed['corefs']:
        corefs = extract_coreferences(parsed, entity)
        if corefs:
            targets += corefs
    return targets


def lexicon_based(text, entity):
    try:
        parsed = json.loads(nlp.annotate(text, properties={'annotators': 'tokenize,ssplit,pos,lemma,ner,depparse,coref',
                                                       'pinelineLanguage': 'en', 'outputFormat': 'json'}))
    except:
        print("StanfordTaggerError")
        nlp.close()
        return 0
    targets = sentiment_targets(parsed, entity)
    indicators = sentiment_indicators(parsed)
    graph = dependency_tree(parsed)
    print("sentiment indicators: ")
    print(indicators)
    print(" sentiment targets: ")
    print(targets)
    print(find_sentiment(indicators, targets, graph))

def main():
    entities = extract_entities('2018-06-13')
    entity = entities[0]
    corpus = entity_corpus(entity, '2018-06-13')
    for tweet in corpus:
        lexicon_based(tweet, entity)
    nlp.close()

if __name__ == "__main__":
    main()