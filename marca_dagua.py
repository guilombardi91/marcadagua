"""
Aplica marca d'água diagonal ("atravessada") em todas as páginas de documentos.

Formatos suportados:
  - PDF  (.pdf)                 -> gera <nome>_MARCA_DAGUA.pdf
  - Imagens (.jpg .jpeg .png)   -> gera <nome>_MARCA_DAGUA.<ext>
  - Word (.docx .doc)           -> convertido para PDF via Microsoft Word e marcado

Uso:
  python marca_dagua.py                      (abre janela para escolher arquivos)
  python marca_dagua.py arq1.pdf pasta\\ ...  (arquivos e/ou pastas)
  Ou arraste arquivos/pastas sobre o MARCAR.bat
"""

import io
import math
import os
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

TEXTO = "PARA USO EXCLUSIVO DA ARTTICAPITAL"
COR = (0.6, 0.6, 0.6)   # cinza (RGB 0-1)
OPACIDADE = 0.30        # 0 = invisível, 1 = sólido
OCUPACAO = 0.85         # fração da diagonal da página ocupada pelo texto
SUFIXO = "_MARCA_DAGUA"

EXT_PDF = {".pdf"}
EXT_IMG = {".jpg", ".jpeg", ".png"}
EXT_WORD = {".docx", ".doc"}


def _pagina_marca(largura, altura):
    """Cria um PDF de 1 página (largura x altura) contendo só a marca d'água."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(largura, altura))
    fonte = "Helvetica-Bold"

    diagonal = math.hypot(largura, altura)
    tamanho = OCUPACAO * diagonal / stringWidth(TEXTO, fonte, 1)

    # Ângulo da diagonal: canto inferior esquerdo -> canto superior direito
    angulo = math.degrees(math.atan2(altura, largura))
    c.setFillColorRGB(*COR)
    c.setFillAlpha(OPACIDADE)
    c.setFont(fonte, tamanho)
    c.translate(largura / 2, altura / 2)
    c.rotate(angulo)
    c.drawCentredString(0, -tamanho * 0.35, TEXTO)
    c.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def marcar_pdf(origem, destino):
    leitor = PdfReader(origem)
    if leitor.is_encrypted and not leitor.decrypt(""):
        raise RuntimeError("PDF protegido por senha")
    escritor = PdfWriter(clone_from=leitor)
    cache = {}
    for pagina in escritor.pages:
        # Incorpora a rotação da página ao conteúdo, para a marca ficar
        # alinhada com o que o leitor vê na tela
        if pagina.rotation:
            pagina.transfer_rotation_to_content()
        caixa = pagina.cropbox  # área visível
        larg, alt = float(caixa.width), float(caixa.height)
        chave = (round(larg, 1), round(alt, 1))
        if chave not in cache:
            cache[chave] = _pagina_marca(larg, alt)
        pagina.merge_translated_page(cache[chave], float(caixa.left), float(caixa.bottom), over=True)
    with open(destino, "wb") as f:
        escritor.write(f)


def _fonte_imagem(tamanho):
    for nome in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default(size=tamanho)


def marcar_imagem(origem, destino):
    img = Image.open(origem)
    formato = img.format
    base = img.convert("RGBA")
    larg, alt = base.size

    diagonal = math.hypot(larg, alt)
    tamanho = 100
    fonte = _fonte_imagem(tamanho)
    largura_texto = fonte.getlength(TEXTO)
    tamanho = max(8, int(tamanho * OCUPACAO * diagonal / largura_texto))
    fonte = _fonte_imagem(tamanho)

    # Desenha o texto numa camada quadrada, gira e cola no centro
    lado = int(diagonal) + 2
    camada = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    desenho = ImageDraw.Draw(camada)
    cor = tuple(int(c * 255) for c in COR) + (int(OPACIDADE * 255),)
    desenho.text((lado / 2, lado / 2), TEXTO, font=fonte, fill=cor, anchor="mm")
    angulo = math.degrees(math.atan2(alt, larg))
    camada = camada.rotate(angulo, resample=Image.Resampling.BICUBIC)
    camada = camada.crop(((lado - larg) // 2, (lado - alt) // 2,
                          (lado - larg) // 2 + larg, (lado - alt) // 2 + alt))

    resultado = Image.alpha_composite(base, camada)
    if formato == "JPEG":
        resultado.convert("RGB").save(destino, "JPEG", quality=95)
    else:
        resultado.save(destino, formato or "PNG")


def word_para_pdf(origem, destino_pdf):
    try:
        import win32com.client  # pywin32
    except ImportError:
        raise RuntimeError("para arquivos Word instale: pip install pywin32 (requer MS Word)")
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    try:
        documento = word.Documents.Open(os.path.abspath(origem), ReadOnly=True)
        documento.SaveAs(os.path.abspath(destino_pdf), FileFormat=17)  # 17 = PDF
        documento.Close(False)
    finally:
        word.Quit()


def processar(caminho):
    raiz, ext = os.path.splitext(caminho)
    ext = ext.lower()
    if raiz.endswith(SUFIXO):
        return None  # já marcado
    if ext in EXT_PDF:
        destino = raiz + SUFIXO + ".pdf"
        marcar_pdf(caminho, destino)
    elif ext in EXT_IMG:
        destino = raiz + SUFIXO + ext
        marcar_imagem(caminho, destino)
    elif ext in EXT_WORD:
        destino = raiz + SUFIXO + ".pdf"
        with tempfile.TemporaryDirectory() as tmp:
            pdf_tmp = os.path.join(tmp, "convertido.pdf")
            word_para_pdf(caminho, pdf_tmp)
            marcar_pdf(pdf_tmp, destino)
    else:
        return None
    return destino


def expandir(entradas):
    suportadas = EXT_PDF | EXT_IMG | EXT_WORD
    for entrada in entradas:
        if os.path.isdir(entrada):
            for pasta, _, arquivos in os.walk(entrada):
                for nome in sorted(arquivos):
                    if os.path.splitext(nome)[1].lower() in suportadas and not nome.startswith("~$"):
                        yield os.path.join(pasta, nome)
        else:
            yield entrada


def escolher_arquivos():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    arquivos = filedialog.askopenfilenames(
        title="Escolha os documentos para aplicar a marca d'água",
        filetypes=[("Documentos", "*.pdf *.jpg *.jpeg *.png *.docx *.doc"),
                   ("Todos", "*.*")],
    )
    root.destroy()
    return list(arquivos)


def main(args):
    entradas = args or escolher_arquivos()
    if not entradas:
        print("Nenhum arquivo selecionado.")
        return 1
    ok = falhas = 0
    for caminho in expandir(entradas):
        try:
            destino = processar(caminho)
            if destino:
                ok += 1
                print(f"[OK]    {caminho}\n        -> {destino}")
            else:
                print(f"[PULO]  {caminho} (formato não suportado ou já marcado)")
        except Exception as erro:
            falhas += 1
            print(f"[ERRO]  {caminho}: {erro}")
    print(f"\nConcluído: {ok} arquivo(s) marcado(s), {falhas} erro(s).")
    return 0 if falhas == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
