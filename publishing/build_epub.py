from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import uuid
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
TITLE = "用 Python 自己寫一個 Coding Agent"
SUBTITLE = "從對話迴圈、工具呼叫到可擴充的 AI 程式助手"
AUTHOR = "Happy eBook Authors"
PUBLISHER = "Happy eBook"
LANG = "zh-TW"
DATE = "2026-08-22"
MODIFIED = "2026-08-22T00:00:00Z"
ZIP_DATE_TIME = (2026, 8, 22, 0, 0, 0)
IDENTIFIER_FILE = WORK / "identifier.txt"

PARTS = [
    ("第一篇　先看懂 Coding Agent", [1, 2]),
    ("第二篇　建立 Agent 的資料模型", [3, 4, 5]),
    ("第三篇　讓模型可以呼叫工具", [6, 7, 8]),
    ("第四篇　打造 Coding Agent 的四大工具", [9, 10, 11, 12]),
    ("第五篇　完成 Agent Loop", [13, 14, 15, 16]),
    ("第六篇　從範例走向可用系統", [17, 18]),
]


def image_dimensions(data: bytes) -> tuple[int, int]:
    """Read PNG/JPEG dimensions with the standard library only."""
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        if width > 0 and height > 0:
            return width, height

    if data.startswith(b"\xff\xd8"):
        sof_markers = {
            0xC0, 0xC1, 0xC2, 0xC3,
            0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB,
            0xCD, 0xCE, 0xCF,
        }
        index = 2
        while index < len(data):
            if data[index] != 0xFF:
                index += 1
                continue
            while index < len(data) and data[index] == 0xFF:
                index += 1
            if index >= len(data):
                break
            marker = data[index]
            index += 1
            if marker in {0xD8, 0xD9}:
                continue
            if index + 2 > len(data):
                break
            segment_length = int.from_bytes(data[index:index + 2], "big")
            if segment_length < 2 or index + segment_length > len(data):
                break
            if marker in sof_markers and segment_length >= 7:
                height = int.from_bytes(data[index + 3:index + 5], "big")
                width = int.from_bytes(data[index + 5:index + 7], "big")
                if width > 0 and height > 0:
                    return width, height
            index += segment_length

    raise ValueError("Unsupported or invalid image data")


def identifier() -> str:
    if not IDENTIFIER_FILE.exists():
        IDENTIFIER_FILE.write_text(str(uuid.uuid4()) + "\n", encoding="utf-8")
    return "urn:uuid:" + IDENTIFIER_FILE.read_text(encoding="utf-8").strip()


def chapter_path(number: int) -> Path:
    matches = list((ROOT / "manuscript/chapters").glob(f"{number:02d}-*.md"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one chapter {number}, found {matches}")
    return matches[0]


def normalize_images(text: str) -> str:
    return text.replace("(../assets/", "(manuscript/assets/")


def shift_markdown_headings(text: str) -> str:
    """Move real Markdown headings down one level, excluding fenced code."""
    lines = []
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            lines.append(line)
            continue
        match = re.match(r"^(#{1,5})(\s+.+)$", line) if not in_fence else None
        lines.append("#" + line if match else line)
    return "\n".join(lines)


def build_combined_markdown() -> Path:
    chunks = []
    for part_title, chapter_numbers in PARTS:
        chunks.append(f"# {part_title}\n")
        for number in chapter_numbers:
            text = normalize_images(chapter_path(number).read_text(encoding="utf-8"))
            lines = text.splitlines()
            if not lines or not re.match(r"^#\s+\d+\.", lines[0]):
                raise RuntimeError(f"Unexpected chapter heading: {chapter_path(number)}")
            chunks.append(shift_markdown_headings(text) + "\n")

    chunks.append("# 附錄\n")
    for appendix_name in [
        "exercise-solutions.md",
        "advanced-production-examples.md",
    ]:
        appendix = (ROOT / "manuscript/appendices" / appendix_name).read_text(encoding="utf-8")
        chunks.append(shift_markdown_headings(appendix) + "\n")

    build_dir = ROOT / ".hermes-work/publishing"
    build_dir.mkdir(parents=True, exist_ok=True)
    out = build_dir / "book-combined.md"
    out.write_text("\n".join(chunks), encoding="utf-8")
    return out


def rewrite_nav_labels(epub_path: Path) -> None:
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        with zipfile.ZipFile(epub_path) as zf:
            zf.extractall(temp)
        container = ET.parse(temp / "META-INF/container.xml")
        ns_container = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
        opf_rel = container.find(".//c:rootfile", ns_container).attrib["full-path"]
        opf = ET.parse(temp / opf_rel)
        opf_root = opf.getroot()
        opf_ns = {"opf": "http://www.idpf.org/2007/opf"}
        dc_ns = "http://purl.org/dc/elements/1.1/"
        metadata = opf_root.find("opf:metadata", opf_ns)
        if metadata is None:
            raise RuntimeError("OPF metadata element not found")
        subtitle = ET.SubElement(metadata, f"{{{dc_ns}}}title", {"id": "epub-subtitle-1"})
        subtitle.text = SUBTITLE
        subtitle_type = ET.SubElement(
            metadata,
            f"{{{opf_ns['opf']}}}meta",
            {"refines": "#epub-subtitle-1", "property": "title-type"},
        )
        subtitle_type.text = "subtitle"
        for meta in metadata.findall(f"{{{opf_ns['opf']}}}meta"):
            if meta.attrib.get("property") == "dcterms:modified":
                meta.text = MODIFIED
        opf.write(temp / opf_rel, encoding="utf-8", xml_declaration=True)
        manifest = {
            item.attrib["id"]: item.attrib
            for item in opf_root.findall(".//opf:manifest/opf:item", opf_ns)
        }
        opf_dir = (temp / opf_rel).parent
        targets = []
        for item in manifest.values():
            props = item.get("properties", "")
            media = item.get("media-type", "")
            if "nav" in props or media == "application/x-dtbncx+xml":
                targets.append(opf_dir / item["href"])

        for target in targets:
            tree = ET.parse(target)
            changed = False
            for element in tree.iter():
                if element.text:
                    new = re.sub(r"^\s*\d+\.\s+", "", element.text)
                    new = re.sub(r"^\s*第\s*\d+\s*章[：:\s]*", "", new)
                    if new != element.text and new.strip():
                        element.text = new
                        changed = True
            if changed:
                tree.write(target, encoding="utf-8", xml_declaration=True)

        rebuilt = epub_path.with_suffix(".rebuilt.epub")
        def add_bytes(zf: zipfile.ZipFile, name: str, data: bytes, compression: int) -> None:
            info = zipfile.ZipInfo(name, date_time=ZIP_DATE_TIME)
            info.compress_type = compression
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            zf.writestr(
                info,
                data,
                compress_type=compression,
                compresslevel=None if compression == zipfile.ZIP_STORED else 9,
            )

        with zipfile.ZipFile(rebuilt, "w") as zf:
            mimetype = temp / "mimetype"
            add_bytes(zf, "mimetype", mimetype.read_bytes(), zipfile.ZIP_STORED)
            for path in sorted(temp.rglob("*")):
                if path.is_file() and path != mimetype:
                    add_bytes(
                        zf,
                        path.relative_to(temp).as_posix(),
                        path.read_bytes(),
                        zipfile.ZIP_DEFLATED,
                    )
        rebuilt.replace(epub_path)


def validate_epub(epub_path: Path) -> dict:
    with zipfile.ZipFile(epub_path) as zf:
        infos = zf.infolist()
        assert infos[0].filename == "mimetype"
        assert infos[0].compress_type == zipfile.ZIP_STORED
        assert zf.read("mimetype") == b"application/epub+zip"
        container = ET.fromstring(zf.read("META-INF/container.xml"))
        ns_c = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
        opf_rel = container.find(".//c:rootfile", ns_c).attrib["full-path"]
        opf = ET.fromstring(zf.read(opf_rel))
        ns = {
            "opf": "http://www.idpf.org/2007/opf",
            "dc": "http://purl.org/dc/elements/1.1/",
        }
        values = {
            "title": opf.findtext(".//dc:title", namespaces=ns),
            "creator": opf.findtext(".//dc:creator", namespaces=ns),
            "publisher": opf.findtext(".//dc:publisher", namespaces=ns),
            "language": opf.findtext(".//dc:language", namespaces=ns),
            "date": opf.findtext(".//dc:date", namespaces=ns),
        }
        assert values["title"] == TITLE
        title_values = [e.text for e in opf.findall(".//dc:title", ns)]
        assert SUBTITLE in title_values
        assert values["creator"] == AUTHOR
        assert values["publisher"] == PUBLISHER
        assert values["language"] == LANG
        opf_dir = Path(opf_rel).parent
        cover_items = [
            item for item in opf.findall(".//opf:manifest/opf:item", ns)
            if "cover-image" in item.attrib.get("properties", "")
        ]
        assert len(cover_items) == 1
        cover_rel = (opf_dir / cover_items[0].attrib["href"]).as_posix()
        cover_size = image_dimensions(zf.read(cover_rel))
        assert cover_size == (1600, 2400)
        nav_items = [
            item for item in opf.findall(".//opf:manifest/opf:item", ns)
            if "nav" in item.attrib.get("properties", "")
        ]
        assert len(nav_items) == 1
        nav_rel = (opf_dir / nav_items[0].attrib["href"]).as_posix()
        nav_text = zf.read(nav_rel).decode("utf-8")
        assert not re.search(r">\s*\d+\.\s+[^<]+</a>", nav_text)
        return {
            **values,
            "subtitle": SUBTITLE,
            "identifier": identifier(),
            "epub_bytes": epub_path.stat().st_size,
            "zip_entries": len(infos),
            "cover_path": cover_rel,
            "cover_size": cover_size,
            "nav_path": nav_rel,
        }


def main() -> None:
    combined = build_combined_markdown()
    cover = WORK / "cover/cover-1600x2400.jpg"
    css = WORK / "ebook.css"
    output_dir = ROOT / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "python-coding-agent-book.epub"
    cmd = [
        "pandoc", str(combined),
        "--from=gfm", "--to=epub3", f"--output={output}",
        "--toc", "--toc-depth=2", "--split-level=2",
        f"--css={css}", f"--epub-cover-image={cover}",
        f"--metadata=title:{TITLE}", f"--metadata=subtitle:{SUBTITLE}",
        f"--metadata=author:{AUTHOR}", f"--metadata=publisher:{PUBLISHER}",
        f"--metadata=lang:{LANG}", f"--metadata=date:{DATE}",
        f"--metadata=identifier:{identifier()}",
        "--metadata=toc-title:目錄",
        "--metadata=rights:Copyright © 2026 Happy eBook Authors. Published by Happy eBook.",
        "--resource-path=.",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)
    rewrite_nav_labels(output)
    result = validate_epub(output)
    print(result)


if __name__ == "__main__":
    main()
