from requests_oauthlib import OAuth2Session
import requests, zipfile, os, json, sqlite3

HEADER = {"x-api-key": "{bungie api key}"}
client_id = '{client id}'
token = {
    "access_token": "{access token}",
    "token_type": "Bearer",
    "expires_in": {expire time in seconds},
    "refresh_token": "{refresh token}",
    "refresh_expires_in": {refresh expire time},
    "membership_id": "{membershipId}"
}
auto_refresh_url='https://www.bungie.net/Platform/App/OAuth/Token/'
extra = {
    'client_id': client_id,
    'client_secret': ''
}

hashes = {'DestinyInventoryItemDefinition': 'itemHash'}

mods_wanted = ["Lucent Blade", "Energy Converter"] # some mods

def token_saver(self, token):
    self.token = token
    self.access_token = token['access_token']

def get_manifest(header):
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'

    # Get the manifest location from the json
    r = requests.get(manifest_url, headers=header)
    manifest = r.json()
    mani_url = 'http://www.bungie.net'+manifest['Response']['mobileWorldContentPaths']['en']

    # Download the file, write it to 'MANZIP'
    r = requests.get(mani_url)
    with open("MANZIP", "wb") as zip:
        zip.write(r.content)
    print("Download Complete!")

    # Extract the file contents, and rename the extracted file to 'Manifest.content'
    with zipfile.ZipFile('MANZIP') as zip:
        name = zip.namelist()
        zip.extractall()
    os.replace(name[0], 'Manifest.content')
    print('Unzipped!')

def build_dict(hashes):
    # Connect to the manifest
    con = sqlite3.connect('manifest.content')
    print('Connected')
    # Create a cursor object
    cur = con.cursor()
    
    # For every table name in the dictionary
    for table_name in hashes.keys():
        # Get a list of all the jsons from the table
        cur.execute('SELECT json from '+table_name)
        print('Generating '+table_name+' dictionary....')

        #this returns a list of tuples: the first item in each tuple is our json
        items = cur.fetchall()

        # Create a list of jsons
        item_jsons = [json.loads(item[0]) for item in items]
        return item_jsons

def mods_sold():
    client = OAuth2Session(client_id, token=token, auto_refresh_url=auto_refresh_url, auto_refresh_kwargs=extra, token_updater=token_saver)
    r = client.get('{ada-1 URL}', headers=HEADER)
    data = r.json().get('Response').get('sales').get('data')
    mods = list(data.keys())

    mod_ids = []
    for m in mods[5:9]:
        mod_ids.append(data.get(m).get('itemHash'))

    return mod_ids

def send_message(itemName):
    content = itemName + ' is being sold by Ada-1 today!' 
    payload = {
        'content': content
    }

    header = {
        'authorization': '{discord authorization}'

    }

    message = requests.post('https://discord.com/api/v9/channels/{channelId}/messages', data=payload, headers=header)
    print(message.status_code)

def main():
    get_manifest(HEADER)

    mods = mods_sold()
    items = build_dict(hashes)

    for item in items:
        hash = item.get('hash')
        name = item.get('displayProperties').get('name')

        if ((hash in mods) and (name in mods_wanted)):
            send_message(name)

main()
