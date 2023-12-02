import openai
import constants

openai.api_key = constants.openAIAPIKEY

def chat_with_gpt(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use the GPT-3.5 turbo model
            prompt=prompt,
            max_tokens=1000  # 1 word is 0.75 Tokens, 1k Tokens is 0.0015 cents
        )

        return response.choices[0].text

    except Exception as e:
        print('what')
        return "                                        APIKEY not found. Please check your API key."





