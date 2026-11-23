"""Build the installable zip from skills/concept-to-threejs using Python 3."""
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def main():
    root = Path(__file__).resolve().parents[1]
    skill = root / "skills/concept-to-threejs"
    if not (skill / "SKILL.md").is_file():
        raise SystemExit(f"Missing skill entry point in {skill}")
    output = root / "downloads/concept-to-threejs.zip"
    archive = BytesIO()
    with ZipFile(archive, "w") as bundle:
        for path in sorted(skill.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            entry = ZipInfo(path.relative_to(skill.parent).as_posix())
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            data = path.read_bytes()
            if path.suffix in {".py", ".yaml", ".md"}:
                data = data.replace(b"\r\n", b"\n")
            bundle.writestr(entry, data, compress_type=ZIP_DEFLATED, compresslevel=9)
    with ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise SystemExit("ZIP validation failed")
    output.parent.mkdir(exist_ok=True)
    temporary = output.with_suffix(".zip.tmp")
    temporary.write_bytes(archive.getvalue())
    temporary.replace(output)
    print(output)


if __name__ == "__main__":
    main()
