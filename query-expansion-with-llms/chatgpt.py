import openai
import os

client = openai.OpenAI() #only works in codespace, go to codespaces in settings and add secret "OPENAI_API_KEY"

def main():
    query = "machine learning"
    prompt = get_prompt(query=query)
    expanded_query = expand_query_with_gpt4(prompt=prompt)
    print(expanded_query)

def expand_query_with_gpt4(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content

def get_prompt(query):
    #add context before every prompt like I am building an retrieval system...
    prompt = f"""
        Your task is to expand a given query below delimited by tripple quotes by finding synonyms
        of any important word in the query and then adding them to the query.
        query: ``` {query} ```
    """
    return prompt


if __name__ == "__main__":
    main()