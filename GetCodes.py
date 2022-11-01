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

# Check for Token
try:
    with open(api_token_file, 'r') as check_token:
        token_plz = check_token.readline().rstrip()
        if token_plz == (
                (
                re.match('^ey[\\w-]*\\.[\\w-]*\\.[\\w-]*', token_plz)).group()):  # Check if token matches regex pattern
            # print("API key found.")
            api_token = token_plz  # Set token to new variable, not really needed
        else:
            print("API key not found, please enter API Key")
            api_token = input("API Key: ")  # Couldn't find token so ask for it
            with open(api_token_file, 'w') as write_api:
                write_api.write(api_token)  # Write new token to file, overwrites old file
                write_api.close()
                print("API Key written to file: " + api_token_file)
    check_token.close()
except FileNotFoundError:  # if token.txt is not found, probably got deleted
    print("API key not found, please enter API Key")
    api_token = input("API Key: ")
    with open(api_token_file, 'w') as write_api:
        write_api.write(api_token)
        print("API Key written to file: " + api_token_file)
        write_api.close()
except AttributeError:  # Format is wrong, maybe the whole token wasn't copied? Extra characters?
    print("API key not found, please enter API Key")
    print("Possible format error with API key, check file to see if its correct")
    api_token = input("API Key: ")
    with open(api_token_file, 'w') as write_api:
        write_api.write(api_token)
        print("API Key written to file: " + api_token_file)
        write_api.close()

# Get Shift Codes, need to rewrite this with urllib3 and with json API
codes_url = 'https://shift.orcicorn.com/active/wonderlands/'
with urllib.request.urlopen(codes_url) as f:  # Opens url as f variable
    data = f.read()  # Read the response
    soup = BeautifulSoup(data, "html.parser")  # Use bs4 to format html and to search through it
    for tag in soup.find_all('a', class_="archive-item-link"):  # Find all 'a' tags with class of "archive-item-link"
        p = re.search('\\w{5}-\\w{5}-\\w{5}-\\w{5}-\\w{5}', tag.text)  # Get code with regex, the code being p.group()
        while True:  # Checking for Dupes
            try:
                with open("used_codes.txt", 'r') as dupe_check:  # Read used_codes for dupes
                    dupe = False
                    for line in dupe_check:
                        if re.search(p.group(), line):
                            dupe = True
                            # print('Found Dupe: ' + p.group())
                            break
                    if dupe is False:
                        print("Found new code: " + p.group())
                        shift_codes.append(p.group())  # No dupe found so add code to a list that will be redeemed
                        break
                    else:
                        break

            except FileNotFoundError:  # Could not find used_codes.txt, so make it and return to dupe check
                print("used_codes.txt not found! Creating file...")
                with open("used_codes.txt", 'w') as create_used_codes:
                    create_used_codes.close()
                print("Created File")
                continue

#  Headers fpr post request, probably don't need most of these
header = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5',
    'X-SESSION': api_token,  # Authorization
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

if not shift_codes:  # Check if any codes were added to the list when we were searching
    print("No new shift codes found")
else:
    for code in shift_codes:
        post_url = "https://api.2k.com/borderlands/code/" + code + "/redeem/steam"  # For every code we found make its own url to redeem it. can change "steam" to whatever platform you want
        r = requests.post(post_url, headers=header)  # Set request to a variable
        try:
            resp = r.json()  # Try to read json from the response, if we cant then go to exception
            job_id = resp['job_id']  # Grab the job_id from the json, so we can check if the code succeeded or failed
        except Exception as e:
            print("The error raised is: ", e)  # Generic error msg
            try:
                post_json_data = json.dumps(resp, indent=4)  # Mainly for debugging, if it failed to get the json this will fail too.
                print(post_json_data)
            except:
                print(r.content)  # Try to print the response without trying to load json. If it comes down to this then either your token is wrong/expired, cant connect to the website, or the website has had some major changes
        else:
            time.sleep(5)  # Wait 5 seconds before trying to see the status of the code redemption, so it has time to process it.
            get_url = "https://api.2k.com/borderlands/code/" + code + "/job/" + job_id  # Make the url to check the status
            get_status = requests.get(get_url, headers=header)
            try:
                resp = get_status.json()   # Try to read json
                status = resp['success']   # Get status variable
                if status is not True:  # Check if code failed
                    print(code + " Failed!")
                    # print(resp['errors'])
                    if 'CODE_ALREADY_REDEEMED' in (resp['errors']):  # Check a few common error messages to see what error it got
                        print("Already Redeemed!")
                        with open('used_codes.txt', 'a') as log:  # If the error was that the code has already been redeemed then add the code to the used_codes.txt file, so it will not try it again
                            log.write(code + '\n')
                            log.close()
                    elif 'CODE_HAS_EXPIRED' in (resp['errors']):
                        print("Code has Expired!")
                        with open('used_codes.txt', 'a') as log:  # If the error was that the code has expired then add the code to the used_codes.txt file, so it will not try it again
                            log.write(code + '\n')
                            log.close()
                    else:
                        print("Code Failed!")   # This means I have no idea why the code failed, just that it did. Prints the whole response which should hopefully explain why it failed, I should make a log file for this...
                        print(resp)
                        with open("ErrorLog.log", 'a+') as ErrorLog:
                            ErrorLog.write(resp)
                            ErrorLog.close()
                elif status is True:  # If the code was redeemed successfully
                    print("Successfully redeemed code: " + code)
                    with open('used_codes.txt', 'a+') as log:
                        log.write(code + '\n')  # Write code to used_codes.txt
                        log.close()
            except Exception as e:
                print("The error raised is: ", e)
                try:
                    get_json_data = json.dumps(resp, indent=4)
                    print(get_json_data)
                except:
                    print(r.content)

if AutoClose is False:  # If set to True the cmd window will close whenever the script finished even if it fails. Good for redeeming codes completely automatically but not for when you want to see if either the code or script failed
    input("Press enter to continue")
