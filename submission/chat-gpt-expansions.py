#!/usr/bin/env python3
from tira.rest_api_client import Client
from tira.third_party_integrations import ensure_pyterrier_is_loaded, persist_and_normalize_run
import argparse
import openai
import pyterrier as pt
from tqdm import tqdm
import json

# Create a REST client to the TIRA platform for retrieving the pre-indexed data.
client = openai.OpenAI()
ensure_pyterrier_is_loaded()

def parse_args():
    parser = argparse.ArgumentParser(prog='chat-gpt-ir-expansions', description='Generate and cache ChatGPT Expansions for queries for the IR/ACL Anthology.')
    parser.add_argument('dataset_id', help='The dataset id, e.g., ir-lab-sose-2024/ir-acl-anthology-20240504-training.')

    return parser.parse_args()

def contains_abbreviations(queries):
    answers = dict()
    for qid, query in tqdm(queries.items(), 'Contains Abbreviation'):
        determine_abbrevation = f""" 
    You are an scientific expert especially in the domain of Information Retrieval. Your task is to detect whether
    a given query, which is given as a text below delimited by triple quotes, contains an abbrevation then answer with yes or not then answer with no.
    For example given a query 'What is crx' you should answer yes, since cxr is the abbrevation for the medical term
    'chest X-Ray'. However if the given query is 'What is Information Retrieval' you should answer no, since there is no
    abbrevation in the query.

    query: '''{query}'''
    """
        answer = ask_gpt(prompt=determine_abbrevation) #check answer more carefully perhaps model will return not only {yes,no}

        answers[str(qid)] = "yes" in answer.lower().strip()

    return answers

def expand_abbreviations(queries, abbreviations):
    ret = {}
    for qid, query in tqdm(queries.items(), 'Expand Abbreviations'):
        if not bool(abbreviations[qid]):
            ret[qid] = None
            continue

        #ask gpt to expand query
        expand = f""" 
        You are an scientific expert especially in the domain of Information Retrieval. Your are given a query, which is below
        delimited by triple quotes, which contains an abbrevation. Your task is to identify the abbrevation and write it, then
        concat the original query with the written out abbrevation and return this new query as string only.
        For example given a query 'What is crx' you should detect that the abbrevation is crx, since cxr is the abbrevation for the medical term
        'chest X-Ray', then you should concat the originial query with the abbrevation 'chest X-Ray' resulting in a new query 'What is crx chest x-ray' which
        you should return. Another example, given the query 'Algorithms of nlp' you should detect that the abbrevation is nlp, since nlp is the abbrevation
        for the term 'natural language processing', then you should concat the original query 'Algorithms of nlp' with the abbrevation 'natural language processing'  
        resulting in a new query 'Algorithms of nlp natural language processing' which you should return.
        Please only answer with the new query. So your answer should only include the original query and the detected abbreviated words and no additional information.
        Don't wrap your answer in quotation marks.

        query: '''{query}'''
        """
        new_query = ask_gpt(prompt=expand).lower().strip().replace("'", " ").replace('"', ' ')
        ret[qid] = new_query
    return ret

def extract_ngrams(queries):
    ret = {}
    for qid, query in tqdm(queries.items(), 'Extract NGramms'):
        determine_ngrams = f""" 
    You are an scientific expert in the domain of Information Retrieval and linguistics. Your task is to detect whether
    a given query, which is given as a text below delimited by triple quotes, contains bigrams. This means, you should check for all 
    bigrams in the query, if they are an existing term consisting of multiple words. Then, your answer should be the original query 
    with all the bigrams you found appended in the format word1$$word2. Your answer should only include the query and the bigrams, no additional information.
    This means that when there are no existing bigrams in the query, your answer should just be the original query. You should not wrap your answer in quotation marks.
    For example given a query 'usage of machine learning in image recognition' you should answer
      'usage of machine learning in image recognition machine$$learning image$$recognition'.

    query: '''{query}'''
    """
        ret[qid] = ask_gpt(prompt=determine_ngrams)
    return ret

def ask_gpt(prompt, model="gpt-4", temperature=0):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

def main(dataset_id):
    pt_dataset = pt.get_dataset(f'irds:{dataset_id}')
    queries = {i.query_id: i.default_text() for i in pt_dataset.irds_ref().queries_iter()}
    
    abbreviations = contains_abbreviations(queries)
    expanded_abbreviations = expand_abbreviations(queries, abbreviations)
    ngrams = extract_ngrams(queries)

    with open(f'gpt-annotations-{dataset_id.replace("/", "-")}.jsonl', 'w') as f:
        for qid, query in queries.items():
            f.write(json.dumps({'qid': str(qid), 'original_query': query, 'is_abbreviations': abbreviations[qid], 'expanded_abbreviation': expanded_abbreviations[qid], 'ngrams': ngrams[qid]}) + '\n')

if __name__ == '__main__':
    args = parse_args()
    main(args.dataset_id)

