"""Single-page shell for the WebView SPA."""
from pathlib import Path

from dailyplanner.ui.css import get_css


def _load_app_js() -> str:
    path = Path(__file__).parent / "static" / "app.js"
    return path.read_text(encoding="utf-8")


def build_web_bundle() -> dict[str, str]:
    """Return cache files for the SPA (keeps each file under Android load limits)."""
    index_html = """<!DOCTYPE html>
<html dir="rtl" lang="fa" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#0A0A0F">
<title>Daily Planner</title>
<link rel="stylesheet" href="app.css">
</head>
<body>
<div class="screen">
  <div class="content" id="app-root">
    <div class="loading-state"><div class="loading-spinner" aria-hidden="true"></div><div class="loading-text">در حال بارگذاری...</div></div>
  </div>
  <div class="bottom-nav" id="bottom-nav" role="navigation" aria-label="ناوبری اصلی"></div>
</div>
<div id="toast" class="toast"></div>
<div id="modal" class="modal-overlay" style="display:none">
  <div class="modal-box" id="modal-box">
    <div class="modal-handle" aria-hidden="true"></div>
    <div class="modal-title" id="modal-title"></div>
    <div id="modal-fields"></div>
    <div class="modal-error" id="modal-error"></div>
    <div class="modal-btns">
      <button class="modal-confirm" onclick="confirmModal()">تأیید</button>
      <button class="modal-cancel" onclick="closeModal()">انصراف</button>
    </div>
  </div>
</div>
<script src="app.js"></script>
</body>
</html>"""
    return {
        "index.html": index_html,
        "app.css": get_css(),
        "app.js": _load_app_js(),
    }


def shell_page() -> str:
    """Legacy single-file HTML (desktop fallback)."""
    bundle = build_web_bundle()
    return bundle["index.html"].replace(
        '<link rel="stylesheet" href="app.css">',
        f"<style>{bundle['app.css']}</style>",
    ).replace(
        '<script src="app.js"></script>',
        f"<script>{bundle['app.js']}</script>",
    )
