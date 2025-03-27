import requests
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
from datetime import datetime

# Configurações
BLOG_URL = "https://www.otempo.com.br/blogs/blog-do-voloch"
FEED_FILE = "blog_voloch.xml"

def gerar_rss():
    try:
        print("Acessando o blog...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        }
        response = requests.get(BLOG_URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Criar feed RSS
        feed = Rss201rev2Feed(
            title="Blog do Voloch",
            link=BLOG_URL,
            description="Feed RSS das últimas postagens do Blog do Voloch",
            language="pt-br"
        )

        # Seletores (ajustados para pegar TODAS as postagens)
        artigos = soup.select('article.wrapper__hardnews--06')  # Lista de artigos

        for artigo in artigos:
            # Extrair título (ajuste conforme necessário)
            titulo = artigo.select_one('span h2').text.strip() if artigo.select_one('span h2') else "Sem título"
            
            # Extrair link (href do <a> dentro do artigo)
            link = artigo.find('a')['href'] if artigo.find('a') else BLOG_URL
            
            # Verificar se o link é absoluto ou relativo
            if not link.startswith('http'):
                link = f"https://www.otempo.com.br{link}"
            
            # Adicionar ao feed
            feed.add_item(
                title=titulo,
                link=link,
                pubdate=datetime.now(),  # Substitua pela data real se disponível
                description=titulo  # Use o subtítulo se quiser
            )

        # Salvar feed
        with open(FEED_FILE, 'w', encoding='utf-8') as f:
            feed.write(f, 'utf-8')
        print(f"Feed RSS gerado em {FEED_FILE}!")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    gerar_rss()
