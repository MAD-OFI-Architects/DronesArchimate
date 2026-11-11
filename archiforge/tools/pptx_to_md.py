"""Convierte un .pptx a Markdown (texto de cada diapositiva, incluido el código). Uso: python tools/pptx_to_md.py in.pptx out.md "Título" """
import sys
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


def walk(shapes):
    for sh in shapes:
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from walk(sh.shapes)
        else:
            yield sh


def main(src, dst, title):
    prs = Presentation(src)
    out = [f"# {title}", "", f"_Fuente: {src}. Texto extraído automáticamente de las diapositivas._", ""]
    for i, slide in enumerate(prs.slides, 1):
        blocks = []
        shapes = sorted(walk(slide.shapes), key=lambda s: (s.top or 0, s.left or 0))
        for sh in shapes:
            if sh.has_text_frame:
                t = "\n".join(p.text for p in sh.text_frame.paragraphs).strip()
                if t:
                    code = any(k in t for k in ("public ", "private ", "class ", "=>", "{", "await ", "using ")) and "\n" in t
                    blocks.append(f"```csharp\n{t}\n```" if code else t)
            elif getattr(sh, "has_table", False) and sh.has_table:
                rows = [[c.text.replace("\n", " ") for c in r.cells] for r in sh.table.rows]
                blocks.append("\n".join("| " + " | ".join(r) + " |" for r in rows))
        notes = slide.notes_slide.notes_text_frame.text.strip() if slide.has_notes_slide else ""
        out.append(f"\n## Diapositiva {i}\n")
        out.append("\n\n".join(blocks))
        if notes:
            out.append(f"\n> Notas: {notes}")
    open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:4])
