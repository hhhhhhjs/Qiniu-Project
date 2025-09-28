# pdf_to_jpg_batch.py
# pip install pymupdf tqdm
import os
import re
import sys
from pathlib import Path
from typing import Iterable
import fitz  # PyMuPDF
from tqdm import tqdm

# ==== 配置（按需修改）====
PDF_DIR   = Path("/home/wmy/workspace/server/veterinarian_rag_project/data/pet/texts")
OUT_DIR   = Path("/home/wmy/workspace/server/veterinarian_rag_project/data/pet/care_jpg")
DPI       = 300         # 输出图像分辨率（72 * zoom）
JPEG_QLT  = 95          # JPEG 质量 0-100
RECURSIVE = True        # 是否递归扫描子目录

# ==== 工具 ====
def slugify(name: str) -> str:
    """去除不适合做文件名的字符，保留中文、数字、字母，下划线、中划线。"""
    name = name.strip()
    # 替换空白为下划线
    name = re.sub(r"\s+", "_", name)
    # 删除不安全字符（保留中文 \u4e00-\u9fff）
    name = re.sub(rf"[^\w\-\u4e00-\u9fff]+", "", name)
    # 避免空名
    return name or "untitled"

def iter_pdfs(root: Path, recursive: bool = True) -> Iterable[Path]:
    if recursive:
        yield from sorted(root.rglob("*.pdf"))
        yield from sorted(root.rglob("*.PDF"))
    else:
        yield from sorted(root.glob("*.pdf"))
        yield from sorted(root.glob("*.PDF"))

def unique_path(base: Path) -> Path:
    """
    如果目标文件已存在，在末尾加 -1, -2...，确保不覆盖。
    正常情况下（不同 PDF 文件名 + 页码），不会冲突，此为额外保险。
    """
    if not base.exists():
        return base
    stem, suffix = base.stem, base.suffix
    i = 1
    while True:
        cand = base.with_name(f"{stem}-{i}{suffix}")
        if not cand.exists():
            return cand
        i += 1

# ==== 主逻辑 ====
def render_pdf_to_jpg(pdf_path: Path, out_dir: Path, dpi: int = DPI,
                      qlt: int = JPEG_QLT) -> int:
    """
    返回导出的页数
    文件命名：{pdf_slug}__p{page:04d}.jpg
    例如：  GoldenRetriever__p0001.jpg
    """
    pdf_slug = slugify(pdf_path.stem)
    out_dir.mkdir(parents=True, exist_ok=True)

    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    count = 0
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=mat, alpha=False)  # RGB
            out_name = f"{pdf_slug}__p{i:04d}.jpg"
            out_path = unique_path(out_dir / out_name)
            pix.save(out_path.as_posix(), jpg_quality=qlt)
            count += 1
    return count

def main(pdf_dir: Path = PDF_DIR, out_dir: Path = OUT_DIR, recursive: bool = RECURSIVE):
    if not pdf_dir.exists():
        print(f"[ERROR] PDF 目录不存在：{pdf_dir}")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = list(iter_pdfs(pdf_dir, recursive=recursive))
    if not pdfs:
        print(f"[WARN] 未在 {pdf_dir} 下找到 PDF 文件")
        return

    total_pages = 0
    for pdf in tqdm(pdfs, desc="Converting PDFs", unit="pdf"):
        try:
            cnt = render_pdf_to_jpg(pdf, out_dir, dpi=DPI, qlt=JPEG_QLT)
            total_pages += cnt
        except Exception as e:
            print(f"[ERROR] 处理失败：{pdf} -> {e}")

    print(f"[DONE] 共处理 {len(pdfs)} 个 PDF，导出 {total_pages} 张 JPG 到：{out_dir}")

if __name__ == "__main__":
    main()
