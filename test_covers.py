import urllib.request
import re

slugs = ['le-monde', 'le-figaro', 'le-parisien', 'les-echos', 'the-washington-post']

for slug in slugs:
    url = f'https://www.frontpages.com/{slug}/'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        
        # Find front page image URL: look for /t/... or main image tag or og:image
        og_img = re.search(r'property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html)
        if not og_img:
            og_img = re.search(r'content=["\']([^"\']+)["\']\s+property=["\']og:image["\']', html)
            
        imgs = re.findall(r'src=["\']([^"\']+/t/[^"\']+)["\']', html)
        
        print(f"=== {slug} ===")
        if og_img:
            print("  og:image ->", og_img.group(1))
        if imgs:
            print("  img srcs ->", imgs[:2])
    except Exception as e:
        print(f"=== {slug} === Error: {e}")
