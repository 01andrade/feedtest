import requests
from lxml import html
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

URL = "https://www.otempo.com.br/blogs/blog-do-voloch"
DOMINIO = "https://www.otempo.com.br"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)
tree = html.fromstring(response.content)

noticias = tree.xpath('//a[contains(@class, "list__link")]')

# Criar estrutura do RSS
rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")

ET.SubElement(channel, "title").text = "Blog do Voloch - O Tempo"
ET.SubElement(channel, "link").text = URL
ET.SubElement(channel, "description").text = "Últimas postagens do Blog do Voloch"
ET.SubElement(channel, "language").text = "pt-br"

for noticia in noticias[:10]:
    link = noticia.xpath("./@href")
    titulo = noticia.xpath('.//h2[@class="list__description"]/text()')
    subtitulo = noticia.xpath('.//span[@class="list__mustac"]/text()')

    full_link = DOMINIO + link[0] if link else "#"
    titulo = titulo[0].strip() if titulo else "Sem título"
    subtitulo = subtitulo[0].strip() if subtitulo else ""

    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = titulo
    ET.SubElement(item, "link").text = full_link
    ET.SubElement(item, "description").text = subtitulo
    ET.SubElement(item, "pubDate").text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

# Salvar como XML
tree = ET.ElementTree(rss)
tree.write("feed_voloch.xml", encoding="utf-8", xml_declaration=True)

print("✅ Feed RSS gerado como 'feed_voloch.xml'")
