from requests_oauthlib import OAuth2Session
import requests, zipfile, os, json, sqlite3

HEADER = {"x-api-key": "6c05791cedb74b56bbcba241f99b90ce"}
client_id = '40606'
token = {
    "access_token": "CLGbBBKGAgAgpf88pgI+baSvNHoR0hcaGMYDcrqBFBaq8BOkB2S92DTgAAAAfCwIARXJUU8gobQgnbYlavm07PLtHlNvHTG/lYYt912AnEDl9c3oQjMkXgXII7BKyBnQoS/uLPg7ciVigz2eVTsBJ6pCtkzK8YqgRP03EbtS/G6viSqtQk+0iVC6oMb8M0y5GtpA9Kypa/imXyi2DchpjNAtOvposeueRA8U8RfuQU/n/u3M7NDiYFCcYF6x35+VvBYYoCenpeBtnah7pTCueqiuMcelXO6CuMVNj3K4bqkRL7JVrwdKWN1MFn/zbws2MzTjkcpAQk9/r+AmsVJo2i0XJfD+JmjH6LL5yUM=",
    "token_type": "Bearer",
    "expires_in": 605000,
    "refresh_token": "CLGbBBKGAgAg+4eMeLE4cV3WX6CrT6gbloxmpibygk1g6RGC4hdVopfgAAAA888F4CIdjn2FSb2DmxBIKY6UKOGexUrI2dlxk9cdyl2v5Gjy1HdDe+VyGTYexvz+SJrBb58wYIv3PUy8CClFI2kLZ8UHKJwEynTD/aIniXwHqHX0aQcoOJHyHCg8eIVF7fyO1wl9myLM5DvpyDC6Z/fmqQN4nK0vQqcYgNeCqNv7cpSG1QCPtQOJTSsrUM4O/GTmbwOSgYHlcxIUh/zbYhgMVtrcPrBcKdpvzVGgdK/ktoNbA4SmAEWv5beL027+UwKXCLUAX9E4htOX/jREH3kbSTIfvEBna1YKkXJ5b1Y=",
    "refresh_expires_in": 605000,
    "membership_id": "28393689"
}
auto_refresh_url='https://www.bungie.net/Platform/App/OAuth/Token/'
extra = {
    'client_id': client_id,
    'client_secret': 'uWEsGmGM91pjyp1b8AGDol9Sjmmacs-x4NqFD4S3oX8'
}

hashes = {'DestinyInventoryItemDefinition': 'itemHash'}

mods_wanted = ["Lucent Blade", "Energy Converter"]

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
    r = client.get('https://www.bungie.net/Platform/Destiny2/3/Profile/4611686018515469512/Character/2305843009834704246/Vendors/350061650/?components=402', headers=HEADER)
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
        'authorization': 'MjM3MzY3NzUzMDEzNDYwOTky.G3yG5P.0ExGK1ff8oN0e1Wq_g9ERMxQiZLhAo4PV6ruP8'

    }

    message = requests.post('https://discord.com/api/v9/channels/987167602675699754/messages', data=payload, headers=header)
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