from google import genai

api_key = ""
client = None

def InitGemini():
    global api_key, client

    with open("APIKEY", "r") as f:
        api_key = f.read().strip()
    client = genai.Client(api_key=api_key)


def QueryGemini(message):
    global client
    response = client.models.generate_content(
    model="gemini-2.5-flash",  # or whichever model you want
    contents=message,
    )
    return response.text
InitGemini()
