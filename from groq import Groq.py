from groq import Groq

client = Groq(api_key='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')
print(client.models.list())  # should return available models
