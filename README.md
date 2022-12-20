# Shift-Codes-TTW
Automatically find and redeem shift codes for Tiny Tina’s Wonderlands

# Setup
Have python3 installed (Tested on 3.11)

pip install -r requirements.txt

Copy your JWT/Token to token.txt or within the prompt when running the script

# How to get your token
1. Log into your Shift account at https://borderlands.com/en-US/
2. Open your browsers dev tools and select the Network tab
3. Find the request header "X-SESSION" in one of the requests. (Reload page if needed)
4. Copy the value, this is your token. Double check you have copied the WHOLE token, it should have 3 periods(.) in it. (Your token should start with "ey")

Example Token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# Usage
Check that your token is correct and inside token.txt

Run script

Items should be in your in-game mail

# Extra info
The used_codes.txt keeps tracks of any codes you have used so it doesn't try to redeem them multiple times. 

This script is currently for North America(NA) Steam accounts for Tiny Tina's Wonderlands, but this script can easily be changed to support the other borderlands games,
regions, and platforms. Might make a config file for this later

# WARNING
DO NOT SHARE YOUR TOKEN!!!!

Anyone who has your token can log into your account!
