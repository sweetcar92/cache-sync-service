import urllib.request
import re

url = 'https://www.frontpages.com/le-monde/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# Search for JS scripts setting img src or giornale-img
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for s in scripts:
    if 'giornale-img' in s or 'webp' in s or 't/' in s or 'g/' in s:
        print("SCRIPT:", s[:500])
