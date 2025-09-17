"""
Copy the Verzeichnis.xlsb from network (live) or local testing path to the
script directory and convert it to Verzeichnis.xlsx using Excel COM.

Live (preferred): \\\\deberdna-c010a\\DocumentManagement\\Ofs\\obl\\Dokumentenservice\\TeileundStoffe\\Datei\\Verzeichnis.xlsb
Testing (fallback): D:\\DocumentManagement\\Ofs\\obl\\Dokumentenservice\\TeileundStoffe\\Datei\\Testing.xlsb
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


LIVE_SRC = "\\\\deberdna-c010a\\GlobalDE\\DocumentManagement\\Ofs\\obl\\Dokumentenservice\\TeileundStoffe\\Datei\\Verzeichnis.xlsb"
TEST_SRC = "D:\\GlobalDE\\DocumentManagement\\Ofs\\obl\\Dokumentenservice\\TeileundStoffe\\Datei\\Verzeichnis.xlsb"


def pick_source_path() -> Path:
    """Return the first available source path (live first, then testing)."""
    live = Path(LIVE_SRC)
    if live.exists():
        return live
    test = Path(TEST_SRC)
    if test.exists():
        return test
    raise FileNotFoundError(
        "Neither live nor testing source file was found.\n"
        f"Live: {LIVE_SRC}\n"
        f"Test: {TEST_SRC}"
    )


def copy_to_work_dir(src_path: Path, work_dir: Path) -> Path:
    """Copy to script directory as Verzeichnis.xlsb; return destination path."""
    work_dir.mkdir(parents=True, exist_ok=True)
    dest_path = work_dir / "Verzeichnis.xlsb"
    shutil.copy2(src_path, dest_path)
    return dest_path


def convert_xlsb_to_xlsx(xlsb_path: Path, xlsx_path: Path) -> None:
    """Use Excel COM to convert .xlsb to .xlsx (overwrites destination)."""
    try:
        import win32com.client  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "pywin32 is required. Install with: pip install pywin32"
        ) from exc

    if xlsx_path.exists():
        xlsx_path.unlink()

    excel = None
    workbook = None
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        # UpdateLinks=0, ReadOnly=1 speeds up and prevents dialogs
        workbook = excel.Workbooks.Open(str(xlsb_path), UpdateLinks=0, ReadOnly=1)

        # 51 = xlOpenXMLWorkbook (.xlsx)
        workbook.SaveAs(str(xlsx_path), FileFormat=51)
        workbook.Close(SaveChanges=False)
    finally:
        try:
            if workbook is not None:
                workbook.Close(SaveChanges=False)
        except Exception:
            pass
        try:
            if excel is not None:
                excel.Quit()
        except Exception:
            pass

def main() -> int:
    script_dir = Path(__file__).resolve().parent
    try:
        src = pick_source_path()
        print(f"Source: {src}")

        local_xlsb = copy_to_work_dir(src, script_dir)
        print(f"Copied to: {local_xlsb}")

        local_xlsx = script_dir / "Verzeichnis.xlsx"
        convert_xlsb_to_xlsx(local_xlsb, local_xlsx)
        print(f"Converted to: {local_xlsx}")
        try:
            local_xlsb.unlink()
            print(f"Deleted source: {local_xlsb}")
        except Exception as del_err:
            print(f"Warning: could not delete source {local_xlsb}: {del_err}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
