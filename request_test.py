import requests

def fastAPI_conversation(input:str):
    msg={'input': {'question': input}}
    url = "http://127.0.0.1:1233/chatwithvector/invoke/"
    response = requests.post(url, json=msg)
    return response.json()


if __name__ == "__main__":
    print(fastAPI_conversation('hello, who are you?'))