import urllib.request
import re

req = urllib.request.Request('https://www.frontpages.com', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

print("Searching newspaper matches on frontpages.com:")
papers = ['lemonde', 'le-monde', 'monde', 'lefigaro', 'figaro', 'lesechos', 'echos', 'leparisien', 'parisien', 'washington-post', 'wapo', 'courrier']

links = re.findall(r'href=["\']([^"\']+)["\']', html)
for link in links:
    for p in papers:
        if p in link.lower():
            print(f"Matched paper '{p}': {link}")

images = re.findall(r'src=["\']([^"\']+)["\']', html)
for img in images:
    for p in papers:
        if p in img.lower():
            print(f"Matched image '{p}': {img}")
