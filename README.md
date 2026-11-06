# Proteção de Documentos Strong Business School

Sistema de proteção de documentos: grava uma marca d'água diagonal em todas as páginas e bloqueia o PDF para edição. O texto padrão da marca é **"PARA USO EXCLUSIVO DA ARTTICAPITAL"**. Os arquivos gerados ganham o final `_PROTEGIDO` no nome.

## Versão web (`web/index.html`)

Página única que processa PDFs, JPGs e PNGs no próprio navegador: os arquivos não são enviados a nenhum servidor.

Texto da marca:

- O texto padrão vem pré-selecionado sempre que a página abre.
- Dá para escrever outro texto no campo livre (até 80 caracteres) e clicar em **Salvar** (ou Enter) para guardá-lo na lista. Os textos salvos ficam no `localStorage` do navegador: valem só naquele navegador/computador e somem se os dados do site forem apagados.
- Sem texto escolhido (campo livre vazio ou texto selecionado removido), o envio de arquivos fica travado.
Como a marca é aplicada: o texto é repetido na diagonal pela página inteira e cada página vira uma imagem (200 dpi) com a marca gravada nela. O PDF sai bloqueado para edição e cópia (impressão liberada), com senha de proprietário aleatória e descartada. O texto original deixa de ser selecionável. Imagens (JPG/PNG) recebem o mesmo mosaico.

Deploy (Easypanel): serviço **App** com source GitHub, build por **Dockerfile**, porta interna **80**.
O acesso exige login e senha, definidos pelas variáveis `AUTH_USER` e `AUTH_PASSWORD` (veja `.env.example`). Sem elas o container não sobe.

Para testar localmente:

```
docker build -t marca-dagua .
docker run --rm -p 8080:80 --env-file .env marca-dagua
```

## Versão desktop (`marca_dagua.py`)

Aceita também Word (`.docx`/`.doc`, requer MS Word instalado). Diferente da versão web, aplica uma única marca diagonal em texto sobre o PDF original (o texto do documento continua pesquisável, mas a marca pode ser apagada num editor de PDF).

```
pip install -r requirements.txt
python marca_dagua.py arquivo.pdf pasta\
```

Ou arraste arquivos/pastas sobre o `MARCAR.bat`. O resultado é salvo ao lado do original com o sufixo `_PROTEGIDO`. Arquivos que já terminam em `_PROTEGIDO` (ou no antigo `_MARCA_DAGUA`) são pulados.

A versão desktop usa sempre o texto da constante `TEXTO`, no início de `marca_dagua.py`. Cor, opacidade e tamanho da marca ficam nas constantes do início de `marca_dagua.py` e do `<script>` em `web/index.html` (onde o texto padrão é `TEXTO_PADRAO`).
