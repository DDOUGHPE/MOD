import requests 
response = requests.get('https://pokeapi.co/api/v2/pokemon/pikachu')
if response.status_code == 200:
    data = response.json()
    print(data['name'])
    print(data['height'])
else:
    print(f'error: {response.status.code}')

