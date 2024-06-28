import os
import openai

# Access the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Print the API key for verification (remove this line in production)
print("Using API Key:", api_key)

# Check if the API key is correctly accessed
if not api_key:
    raise ValueError("API key not found. Ensure that the 'OPENAI_API_KEY' secret is set in GitHub.")

openai.api_key = api_key

# Make a simple API call to verify the key works
def verify_key():
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="This is a test.",
            max_tokens=5
        )
        print("API call successful. Response:", response.choices[0].text.strip())
    except openai.error.AuthenticationError:
        print("Invalid API key.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    verify_key()
