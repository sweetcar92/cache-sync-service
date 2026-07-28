import os
import sys
import zipfile
import re
from datetime import datetime

DAYS_FR = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

def update_epub_metadata(epub_path, series_name):
    if not os.path.exists(epub_path):
        print(f"File not found: {epub_path}")
        return

    author_name = series_name
    series_index = datetime.now().strftime('%Y%m%d%H%M')
    print(f"Updating {os.path.basename(epub_path)}: Author='{author_name}', Series='{series_name}', SeriesIndex='{series_index}'")

    temp_epub = epub_path + ".tmp"
    with zipfile.ZipFile(epub_path, 'r') as zin:
        with zipfile.ZipFile(temp_epub, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                
                # 1. Update titlepage.xhtml to use clean HTML <img> instead of SVG
                if 'titlepage' in item.filename and item.filename.endswith('.xhtml'):
                    html_cover = (
                        '<?xml version="1.0" encoding="utf-8"?>\n'
                        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n'
                        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n'
                        '  <head>\n'
                        '    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n'
                        '    <title>Cover</title>\n'
                        '    <style type="text/css">\n'
                        '      @page { margin: 0; padding: 0; }\n'
                        '      html, body { margin: 0 !important; padding: 0 !important; width: 100% !important; height: 100% !important; text-align: center; background-color: #ffffff; }\n'
                        '      div.cover-wrapper { margin: 0 !important; padding: 0 !important; width: 100% !important; height: 100% !important; display: block; }\n'
                        '      img.cover-img { width: 100% !important; height: 100% !important; object-fit: contain; display: block; margin: 0 auto; }\n'
                        '    </style>\n'
                        '  </head>\n'
                        '  <body>\n'
                        '    <div class="cover-wrapper"><img class="cover-img" src="cover.jpg" alt="Cover" /></div>\n'
                        '  </body>\n'
                        '</html>'
                    )
                    data = html_cover.encode('utf-8')

                # 2. Update content.opf
                elif item.filename.endswith('.opf'):
                    content = data.decode('utf-8', errors='ignore')

                    # A. Force <dc:creator> to newspaper name
                    if '<dc:creator' in content:
                        content = re.sub(
                            r'<dc:creator[^>]*>.*?</dc:creator>',
                            f'<dc:creator opf:role="aut">{author_name}</dc:creator>',
                            content,
                            flags=re.DOTALL
                        )
                    else:
                        content = content.replace(
                            '</metadata>',
                            f'<dc:creator opf:role="aut">{author_name}</dc:creator>\n</metadata>'
                        )

                    # B. Strip ALL existing cover meta tags (handling all attribute orders)
                    content = re.sub(r'<meta[^>]+cover[^>]*>', '', content, flags=re.IGNORECASE)
                    content = re.sub(r'<meta[^>]+calibre:series[^>]*>', '', content, flags=re.IGNORECASE)

                    # C. Inject clean Kobo cover & series metadata
                    kobo_meta = (
                        f'<meta name="cover" content="cover-image"/>\n'
                        f'<meta name="calibre:series" content="{series_name}"/>\n'
                        f'<meta name="calibre:series_index" content="{series_index}"/>'
                    )
                    if '</metadata>' in content:
                        content = content.replace('</metadata>', f'{kobo_meta}\n</metadata>')

                    # D. Ensure cover.jpg is in manifest with properties="cover-image" and id="cover-image"
                    content = re.sub(r'<item[^>]+href="cover\.jpg"[^>]*>', '', content, flags=re.IGNORECASE)
                    if '</manifest>' in content:
                        content = content.replace(
                            '</manifest>',
                            '<item id="cover-image" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>\n</manifest>'
                        )

                    data = content.encode('utf-8')

                zout.writestr(item, data)

    os.replace(temp_epub, epub_path)
    print(f"SUCCESS: Successfully updated metadata and Kobo cover manifest for {os.path.basename(epub_path)}")

if __name__ == '__main__':
    if len(sys.argv) > 2:
        update_epub_metadata(sys.argv[1], sys.argv[2])
