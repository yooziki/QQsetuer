import requests

def tracemoe(params,):
    url = 'https://trace.moe/api/search'
    files = {
        'image': (params, open(params, 'rb')),
    }
    response = requests.post(url, files=files)
    print(response.json())

if __name__ == '__main__':
    tracemoe("Pixiv/test/食蜂操祈_id84280347.jpg")


