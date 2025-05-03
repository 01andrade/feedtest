import requests
from lxml import html
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

# ========== AUXILIAR: EXTRAI DATA DA MATÉRIA DO VOLOCH ==========
def extrair_data_voloch(link):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(link, headers=headers, timeout=10)
        tree = html.fromstring(r.content)
        data_txt = tree.xpath('//span[@class="cmp__author-publication"]/span/text()')
        if data_txt:
            data_txt = data_txt[0].strip()  # Ex: "02 de maio de 2025 | 10:07"
            dia, mes_ext, ano_hora = data_txt.split(" de ")
            ano, hora = ano_hora.split(" | ")
            meses = {
                "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
            }
            mes = meses[mes_ext.lower()]
            data_completa = f"{dia.zfill(2)}/{mes}/{ano.strip()} {hora.strip()}"
            return datetime.strptime(data_completa, "%d/%m/%Y %H:%M")
    except Exception as e:
        print(f"❌ Erro ao extrair data de {link}: {e}")
    return datetime.min

# ========== FEED DO VOLOCH ==========
def gerar_feed_voloch():
    URL = "https://www.otempo.com.br/blogs/blog-do-voloch"
    DOMINIO = "https://www.otempo.com.br"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(URL, headers=headers)
    tree = html.fromstring(response.content)

    noticias = tree.xpath('//a[contains(@class, "list__link")]')
    entradas = []

    for noticia in noticias[:10]:
        link = noticia.xpath("./@href")
        titulo = noticia.xpath('.//h2[@class="list__description"]/text()')
        subtitulo = noticia.xpath('.//span[@class="list__mustac"]/text()')

        full_link = DOMINIO + link[0] if link else "#"
        titulo = titulo[0].strip() if titulo else "Sem título"
        subtitulo = subtitulo[0].strip() if subtitulo else ""

        data_pub = extrair_data_voloch(full_link)
        entradas.append((data_pub, titulo, subtitulo, full_link))

    entradas.sort(reverse=True)

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Blog do Voloch - O Tempo"
    ET.SubElement(channel, "link").text = URL
    ET.SubElement(channel, "description").text = "Últimas postagens do Blog do Voloch"
    ET.SubElement(channel, "language").text = "pt-br"

    for data_pub, titulo, subtitulo, full_link in entradas:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = titulo
        ET.SubElement(item, "link").text = full_link
        ET.SubElement(item, "description").text = subtitulo
        ET.SubElement(item, "pubDate").text = data_pub.strftime('%a, %d %b %Y %H:%M:%S GMT')

    tree = ET.ElementTree(rss)
    tree.write("feed_voloch.xml", encoding="utf-8", xml_declaration=True)
    print("✅ Feed do Voloch gerado")


# ========== FEED DO NETVASCO ==========
def gerar_feed_netvasco():
    URL = "https://netvasco.com.br"
    DOMINIO = "https://netvasco.com.br"
    headers = { "User-Agent": "Mozilla/5.0" }

    response = requests.get(URL, headers=headers)
    tree = html.fromstring(response.content)

    blocos = tree.xpath('//ul[starts-with(@id, "posts")]/li')

    noticias = []
    for bloco in blocos:
        link_el = bloco.xpath(".//a")[0]
        texto = link_el.xpath("string()").strip()
        link = link_el.get("href")
        full_link = DOMINIO + link if link else "#"

        data = bloco.xpath('.//span[contains(@class, "data")]/text()')
        hora = bloco.xpath('.//span[contains(@class, "noticia-hora")]/text()')

        data_str = data[0].strip() if data else "01 de janeiro"
        hora_str = hora[0].strip() if hora else "00:00"

        # Converte "Sábado, 03 de maio" para "03/05" e junta com hora
        try:
            dia_mes = data_str.split(",")[-1].strip()
            dt_completa = datetime.strptime(dia_mes + " " + hora_str, "%d de %B %H:%M")
            dt_completa = dt_completa.replace(year=datetime.now().year)
        except Exception:
            dt_completa = datetime.now()

        noticias.append({
            "title": texto,
            "link": full_link,
            "description": texto,
            "pubDate": dt_completa.strftime('%a, %d %b %Y %H:%M:%S GMT'),
            "datetime": dt_completa
        })

    # Ordena da mais recente para a mais antiga
    noticias.sort(key=lambda x: x["datetime"], reverse=True)

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Netvasco - Últimas Notícias"
    ET.SubElement(channel, "link").text = URL
    ET.SubElement(channel, "description").text = "Feed gerado a partir da página inicial do Netvasco"
    ET.SubElement(channel, "language").text = "pt-br"

    for item in noticias[:15]:
        entry = ET.SubElement(channel, "item")
        ET.SubElement(entry, "title").text = item["title"]
        ET.SubElement(entry, "link").text = item["link"]
        ET.SubElement(entry, "description").text = item["description"]
        ET.SubElement(entry, "pubDate").text = item["pubDate"]

    tree = ET.ElementTree(rss)
    tree.write("feed_netvasco.xml", encoding="utf-8", xml_declaration=True)
    print("✅ Feed do Netvasco gerado!")

# ========== EXECUTA OS DOIS FEEDS ==========
gerar_feed_voloch()
gerar_feed_netvasco()
