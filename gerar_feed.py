import requests
from lxml import html
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

# ========== FEED DO VOLOCH ==========
def gerar_feed_voloch():
    URL = "https://www.otempo.com.br/blogs/blog-do-voloch"
    DOMINIO = "https://www.otempo.com.br"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    tree = html.fromstring(response.content)

    noticias = tree.xpath('//a[contains(@class, "list__link")]')
    lista_itens = []

    for noticia in noticias[:10]:
        link = noticia.xpath("./@href")
        full_link = DOMINIO + link[0] if link else "#"

        # Acessa a página da notícia para buscar a data real
        data_pub = datetime.now(timezone.utc)
        try:
            resp_noticia = requests.get(full_link, headers=headers)
            arvore_noticia = html.fromstring(resp_noticia.content)
            data_texto = arvore_noticia.xpath('string(//span[@class="cmp__author-publication"]/span)')
            if data_texto:
                data_pub = datetime.strptime(data_texto.strip(), "%d de %B de %Y | %H:%M")
                data_pub = data_pub.replace(tzinfo=timezone.utc)
        except Exception:
            pass

        titulo = noticia.xpath('.//h2[@class="list__description"]/text()')
        subtitulo = noticia.xpath('.//span[@class="list__mustac"]/text()')

        titulo = titulo[0].strip() if titulo else "Sem título"
        subtitulo = subtitulo[0].strip() if subtitulo else ""

        lista_itens.append({
            "titulo": titulo,
            "link": full_link,
            "descricao": subtitulo,
            "data": data_pub
        })

    # Ordena por data decrescente
    lista_itens.sort(key=lambda x: x["data"], reverse=True)

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Blog do Voloch - O Tempo"
    ET.SubElement(channel, "link").text = URL
    ET.SubElement(channel, "description").text = "Últimas postagens do Blog do Voloch"
    ET.SubElement(channel, "language").text = "pt-br"

    for item in lista_itens:
        node = ET.SubElement(channel, "item")
        ET.SubElement(node, "title").text = item["titulo"]
        ET.SubElement(node, "link").text = item["link"]
        ET.SubElement(node, "description").text = item["descricao"]
        ET.SubElement(node, "pubDate").text = item["data"].strftime('%a, %d %b %Y %H:%M:%S GMT')

    tree = ET.ElementTree(rss)
    tree.write("feed_voloch.xml", encoding="utf-8", xml_declaration=True)
    print("✅ Feed do Voloch gerado")


# ========== FEED DO NETVASCO ==========
def gerar_feed_netvasco():
    URL = "https://netvasco.com.br"
    DOMINIO = "https://netvasco.com.br"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    tree = html.fromstring(response.content)

    itens = tree.xpath('//ul[starts-with(@id, "posts")]/li/a')

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Netvasco - Últimas Notícias"
    ET.SubElement(channel, "link").text = URL
    ET.SubElement(channel, "description").text = "Feed gerado a partir da página inicial do Netvasco"
    ET.SubElement(channel, "language").text = "pt-br"

    for item in itens[:15]:
        link = item.get("href")
        texto = item.xpath("string()").strip()
        full_link = DOMINIO + link if link else "#"

        entry = ET.SubElement(channel, "item")
        ET.SubElement(entry, "title").text = texto
        ET.SubElement(entry, "link").text = full_link
        ET.SubElement(entry, "description").text = texto
        ET.SubElement(entry, "pubDate").text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

    tree = ET.ElementTree(rss)
    tree.write("feed_netvasco.xml", encoding="utf-8", xml_declaration=True)
    print("✅ Feed do Netvasco gerado")


# ========== EXECUTA OS DOIS FEEDS ==========
gerar_feed_voloch()
gerar_feed_netvasco()
