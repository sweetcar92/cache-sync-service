import urllib.request
import re
from io import BytesIO
from PIL import Image

def download_frontpage_cover(slug):
    page_url = f'https://www.frontpages.com/{slug}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.frontpages.com/'
    }
    
    req = urllib.request.Request(page_url, headers=headers)
    html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    
    matches = re.findall(r'/t/\d{4}/\d{2}/\d{2}/[^\'"\s>]+\.webp', html)
    
    img_url = None
    if matches:
        # 1. Exact match (e.g. /t/.../le-monde-XXXX.webp)
        exact = [m for m in matches if f"/{slug}-" in m and not any(sub in m for sub in ['sports', 'des-livres', 'economie', 'diplomatique'])]
        if exact:
            img_url = exact[0]
        else:
            img_url = matches[0]
            
    if img_url and not img_url.startswith('http'):
        img_url = 'https://www.frontpages.com' + img_url
        
    urls_to_try = [img_url.replace('.webp', '@2x.webp'), img_url]
    img_data = None
    final_url = None
    
    for url in urls_to_try:
        try:
            img_req = urllib.request.Request(url, headers=headers)
            img_data = urllib.request.urlopen(img_req).read()
            final_url = url
            break
        except Exception:
            continue
            
    if not img_data:
        print(f"FAILED {slug}: Download failed!")
        return None
        
    im = Image.open(BytesIO(img_data))
    if im.mode != 'RGB':
        im = im.convert('RGB')
        
    out = BytesIO()
    im.save(out, format='JPEG', quality=95)
    jpg_bytes = out.getvalue()
    print(f"EXACT MATCH {slug}: {final_url} ({len(jpg_bytes)} bytes, size={im.size})")
    return jpg_bytes

if __name__ == '__main__':
    for slug in ['le-monde', 'le-figaro', 'le-parisien', 'les-echos', 'the-washington-post']:
        print(f"\n--- Testing {slug} ---")
        download_frontpage_cover(slug)
