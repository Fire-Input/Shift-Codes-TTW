import json
import requests
from bs4 import BeautifulSoup
import re
import urllib.request
import time

AutoClose = False
shift_codes = []
api_token_file = 'token.txt'

# https://shift.orcicorn.com/about/json/
# https://shift.orcicorn.com/tags/wonderlands/index.json
# Update to use json instead of webpage search

try:
    with open(api_token_file, 'r') as check_token:
        token_plz = check_token.readline().rstrip()
        if token_plz == ((re.match('^ey[\\w-]*\\.[\\w-]*\\.[\\w-]*', token_plz)).group()):
            #print("API key found.")
            api_token = token_plz
        else:
            print("API key not found, please enter API Key")
            api_token = input("API Key: ")
            with open(api_token_file, 'w') as write_api:
                write_api.write(api_token)
                write_api.close()
                print("API Key written to file: " + api_token_file)
    check_token.close()
except FileNotFoundError:
    print("API key not found, please enter API Key")
    api_token = input("API Key: ")
    with open(api_token_file, 'w') as write_api:
        write_api.write(api_token)
        print("API Key written to file: " + api_token_file)
        write_api.close()
except AttributeError:
    print("API key not found, please enter API Key")
    print("Possible format error with API key, check file to see if its correct")
    api_token = input("API Key: ")
    with open(api_token_file, 'w') as write_api:
        write_api.write(api_token)
        print("API Key written to file: " + api_token_file)
        write_api.close()

codes_url = 'https://shift.orcicorn.com/active/wonderlands/'
with urllib.request.urlopen(codes_url) as f:  # Opens url as f variable
    data = f.read()
    soup = BeautifulSoup(data, "html.parser")
    for tag in soup.find_all('a', class_="archive-item-link"):
        p = re.search('\\w{5}-\\w{5}-\\w{5}-\\w{5}-\\w{5}', tag.text)
        while True:
            try:
                with open("used_codes.txt", 'r') as dupe_check:
                    dupe = False
                    for line in dupe_check:
                        if re.search(p.group(), line):
                            dupe = True
                            # print('Found Dupe: ' + p.group())
                            break
                    if dupe is False:
                        print("Found new code: " + p.group())
                        shift_codes.append(p.group())
                        break
                    else:
                        break

            except FileNotFoundError:
                print("used_codes.txt not found! Creating file...")
                with open("used_codes.txt", 'w') as create_used_codes:
                    create_used_codes.close()
                print("Created File")
                continue

header = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5',
    'X-SESSION': api_token,
    'Host': 'api.2k.com',
    'Content-Length': '0',
    'Connection': 'keep-alive',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://borderlands.com/',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-GPC': '1',
    'Origin': 'https://borderlands.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'
}

if not shift_codes:
    print("No new shift codes found")
else:
    for code in shift_codes:
        post_url = "https://api.2k.com/borderlands/code/" + code + "/redeem/steam"
        r = requests.post(post_url, headers=header)
        try:
            resp = r.json()
            job_id = resp['job_id']
        except Exception as e:
            print("The error raised is: ", e)
            try:
                post_json_data = json.dumps(resp, indent=4)
                print(post_json_data)
            except:
                print(r.content)
        else:
            time.sleep(5)
            get_url = "https://api.2k.com/borderlands/code/" + code + "/job/" + job_id
            get_status = requests.get(get_url, headers=header)
            try:
                resp = get_status.json()
                status = resp['success']
                if status is not True:
                    print(code + " Failed!")
                    # print(resp['errors'])
                    if 'CODE_ALREADY_REDEEMED' in (resp['errors']):
                        print("Already Redeemed!")
                        with open('used_codes.txt', 'a') as log:
                            log.write(code + '\n')
                            log.close()
                    elif 'CODE_HAS_EXPIRED' in (resp['errors']):
                        print("Code has Expired!")
                        with open('used_codes.txt', 'a') as log:
                            log.write(code + '\n')
                            log.close()
                    else:
                        print("Code Failed!")
                        print(resp)
                elif status is True:
                    print("Successfully redeemed code: " + code)
                    with open('used_codes.txt', 'a+') as log:
                        log.write(code + '\n')
                        log.close()
            except Exception as e:
                print("The error raised is: ", e)
                try:
                    get_json_data = json.dumps(resp, indent=4)
                    print(get_json_data)
                except:
                    print(r.content)

if AutoClose is False:
    input("Press enter to continue")
