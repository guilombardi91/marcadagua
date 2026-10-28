# Marca d'água ArttiCapital

Aplica a marca d'água diagonal **"PARA USO EXCLUSIVO DA ARTTICAPITAL"** em todas as páginas de documentos.

## Versão web (`web/index.html`)

Página única que processa PDFs, JPGs e PNGs no próprio navegador: os arquivos não são enviados a nenhum servidor.

Dois modos:

- **Protegido** (padrão): a marca é repetida pela página inteira e cada página vira uma imagem (200 dpi) com a marca gravada nela. O PDF sai bloqueado para edição e cópia (impressão liberada), com senha de proprietário aleatória e descartada. O texto deixa de ser selecionável.
- **Simples**: uma marca diagonal em texto sobre o PDF original. Mantém o texto pesquisável, mas a marca pode ser apagada num editor de PDF.

Deploy (Easypanel): serviço **App** com source GitHub, build por **Dockerfile**, porta interna **80**.
O acesso exige login e senha, definidos pelas variáveis `AUTH_USER` e `AUTH_PASSWORD` (veja `.env.example`). Sem elas o container não sobe.

Para testar localmente:

```
docker build -t marca-dagua .
docker run --rm -p 8080:80 --env-file .env marca-dagua
```

## Versão desktop (`marca_dagua.py`)

Aceita também Word (`.docx`/`.doc`, requer MS Word instalado).

```
pip install -r requirements.txt
python marca_dagua.py arquivo.pdf pasta\
```

Ou arraste arquivos/pastas sobre o `MARCAR.bat`. O resultado é salvo ao lado do original com o sufixo `_MARCA_DAGUA`.

Texto, cor, opacidade e tamanho da marca ficam nas constantes do início de `marca_dagua.py` e do `<script>` em `web/index.html`.
