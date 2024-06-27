import openai

client = openai.OpenAI() #only works in codespace, go to codespaces in settings and add secret "OPENAI_API_KEY"

context = """
You are an expert in Information Retrieval. I am building an Information Retrieval System. Therefore I want to use a technique
called query expansion to improve the retrieval systems effectiveness or more specificially I aim to improve the recall of the retrieval system.
Recall is a measure that rates the fraction of relevant documents that are retrieved. Query Expansions works by taking a given query and
adding additional terms to it, such that the information need of the user which entered the query is met more precisely by finding more
relevant documents through the additional terms. 
"""

def main():
    query = "retrieval system improving effectiveness"
    print(transform_query(query=query, prompt_technique="cot"))
    print(transform_query(query=query, prompt_technique="synonym"))

def transform_query(query, prompt_technique):
    if prompt_technique == "synonym":
        #print("SYNONYM EXPANSION")
        prompt = synonym_prompt(query)
        return expand_query_with_gpt4(prompt, temperature=0.3)
    elif prompt_technique == "cot":
        #print("CHAIN OF THOUGHT:")
        prompt = chain_of_thoughts(query)
        return query + expand_query_with_gpt4(prompt, temperature=0.3).replace('"', ' ')

def expand_query_with_gpt4(prompt, model="gpt-4", temperature=0):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

def synonym_prompt(query):
    prompt = f"""
        {context}
        Your task is to expand a given query below delimited by triple quotes by
        first extracting keywords, for example in the query: Machine learning
        the keyword can be interpreted as \'Machine Learning\'.
        Second, try to understand the information need the user which provided
        the query might have.
        Then given the information need: for every keyword find synonyms and add them to the query,
        aiming to improve the recall of the retrieval system.
        Return the query as a string format containing only the query words, for example if
        the given query was \' retrieval system improving effectiveness\' then the returned expanded query could be
        \' retrieval system improving effectiveness extraction system improving performance\'. 
        query: ``` {query} ```
    """
    return prompt

def  chain_of_thoughts(query):
    #not really cot
    prompt = f"""
    Your task is to answer the query below delimited by triple quotes.
    The output should be in a string format containing only words, remove punctuation.
    query: ``` {query} ```
    """
    return prompt




if __name__ == "__main__":
    main()