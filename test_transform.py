import urllib.request
import re
from io import BytesIO
from PIL import Image

def test_transform(slug):
    page_url = f'https://www.frontpages.com/{slug}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://www.frontpages.com/'
    }
    
    req = urllib.request.Request(page_url, headers=headers)
    html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    
    # Match any /2026/... path containing the paper slug
    matches = re.findall(r'/[a-z0-9]+/20\d{2}/\d{2}/\d{2}/[^\'"\s>]+\.(?:webp|jpg)', html)
    paper_matches = [m for m in matches if slug in m or slug.replace('the-', '') in m]
    
    if not paper_matches:
        print(f"❌ {slug}: No matches found")
        return
        
    raw_path = paper_matches[0]
    # Transform /share/ or /g/ into /t/ and .webp.jpg into @2x.webp
    clean_path = re.sub(r'^/(?:share|g|t)/', '/t/', raw_path)
    clean_path = clean_path.replace('.webp.jpg', '@2x.webp')
    if not clean_path.endswith('@2x.webp') and clean_path.endswith('.webp'):
        clean_path = clean_path.replace('.webp', '@2x.webp')
        
    full_url = 'https://www.frontpages.com' + clean_path
    print(f"Testing transformed URL for {slug}: {full_url}")
    
    try:
        img_req = urllib.request.Request(full_url, headers=headers)
        data = urllib.request.urlopen(img_req).read()
        im = Image.open(BytesIO(data))
        print(f"  SUCCESS! Size: {im.size}, Bytes: {len(data)}")
    except Exception as e:
        print(f"  FAILED @2x ({e}), trying 1x...")
        full_url_1x = full_url.replace('@2x.webp', '.webp')
        try:
            img_req = urllib.request.Request(full_url_1x, headers=headers)
            data = urllib.request.urlopen(img_req).read()
            im = Image.open(BytesIO(data))
            print(f"  SUCCESS 1x! Size: {im.size}, Bytes: {len(data)}")
        except Exception as e2:
            print(f"  FAILED 1x ({e2})")

if __name__ == '__main__':
    for slug in ['le-monde', 'le-figaro', 'le-parisien', 'les-echos', 'the-washington-post']:
        test_transform(slug)
