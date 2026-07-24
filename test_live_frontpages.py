import urllib.request
import re

url = 'https://www.frontpages.com/le-monde/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

print("Page HTML length:", len(html))

# Find meta tags
metas = re.findall(r'<meta[^>]+>', html)
for m in metas:
    if 'og:image' in m or 'image' in m:
        print("Meta:", m)

# Find img tags
imgs = re.findall(r'<img[^>]+>', html)
for img in imgs:
    print("Img tag:", img)
