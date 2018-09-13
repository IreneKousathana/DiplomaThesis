# Simple usage
from __future__ import print_function
from stanfordcorenlp import StanfordCoreNLP
import networkx as nx
import logging
from nltk import ParentedTree
import json

mydeps = ['nsubj', 'nsubjpass', 'amod', 'dep']
verbs = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

#nlp = StanfordCoreNLP(r'C:\\Users\\Irene\\Documents\\stanford-corenlp-full-2018-02-27\\', quiet=False, logging_level=logging.DEBUG)

def extract_coreferences(r_dict, entity):
    results = []
    cluster_id = ''
    for key, value in r_dict['corefs'].items():
        for i in range(len(value)):
            # if int(entity) in range(value[i]['startIndex'], value[i]['endIndex']) :
              if value[i]['text'] == entity:
                cluster_id = key
    if cluster_id:
        for ref in (r_dict['corefs'].get(cluster_id)):
            if ref['text'] != entity:
                results.append(str(ref['startIndex']))
    return results

def extract_dependencies(r_dict):
    return [(str(dep['governor']), str(dep['dependent'])) for s in r_dict['sentences'] for dep in
            s['enhancedDependencies']]

def extract_ner(r_dict):
    words = []
    ner_tags = []
    for s in r_dict['sentences']:
        for token in s['tokens']:
            words.append(token['word'])
            ner_tags.append(token['ner'])
    return list(zip(words, ner_tags))

def extract_modificators(parsed, entity):
    corefs = []
    if parsed['corefs']:
        corefs = extract_coreferences(parsed, entity)
    modificators = []
    for s in parsed['sentences']:
        for token in s['tokens']:
            if token['originalText'] in entity or str(token['index']) in corefs :
                for dep in s['enhancedDependencies']:

                    if token['index'] == dep['dependent'] and dep['dep'] in mydeps:
                        modificators.append(dep['governorGloss'])
    return modificators

def dependency_tree(r_dict):
    edges = extract_dependencies(r_dict)
    return nx.DiGraph(edges)

def relations_extractor(r_dict):
    dependencies = [(dep['dep'], str(dep['governor']), str(dep['dependent'])) for s in r_dict['sentences'] for dep in
            s['enhancedDependencies']]
    verb_index = []
    for s in r_dict['sentences']:
        for token in s['tokens']:
            if token['pos'] in verbs:
                verb_index.append(token['index'])





    nlp.close()




def shortest_path(graph,source, targets):
    lengths = []
    for target in targets:
        if nx.has_path(graph, source=source, target=target):
            lengths.append(nx.shortest_path_length(graph, source=source, target=target))
    if lengths:
        return min(lengths)
    else:
        return 0




#relations_extractor("If Fallout 76 is just an online multiplayer to latch onto the battle royale hype i'm gonna be pissed")



#
# parsed = json.loads(nlp.annotate("I like big butts", properties={'annotators': 'tokenize,ssplit,pos,lemma,ner,depparse',
#                                                        'pinelineLanguage': 'en', 'outputFormat': 'json'}))
# print(parsed['sentences'])
# print(parsed['enhancedDependencies'])
# nlp.close()

#print(parsed['corefs'])
#print(shortest_path(parsed, '8' , '1' ))
#print(extract_modificators(text, 'Donald Trump'))
#print(extract_coreferences(parsed, 'Donald'))
#print(parsed['sentences'])
# try:
#    annotated = parsed['sentences'][0]
#    print(annotated['entitymentions'])
# except :
#     print("RuntimeError")
#     nlp.close()
#nlp.close()


