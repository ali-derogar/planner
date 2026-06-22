"""Platform detection and Android-specific WebView helpers."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import toga


def is_android() -> bool:
    return importlib.util.find_spec("android") is not None


def hide_android_action_bar(window: toga.Window) -> None:
    """Hide the native Android toolbar — the WebView UI has its own header."""
    if not is_android():
        return
    impl = getattr(window, "_impl", None)
    if impl is None:
        return
    if hasattr(impl, "show_actionbar"):
        impl.show_actionbar(False)
    else:
        try:
            impl.app.native.getSupportActionBar().hide()
        except Exception:
            pass


def _android_status_bar_height_px(window: toga.Window) -> int:
    try:
        impl = window._impl
        resources = impl.app.native.getResources()
        rid = resources.getIdentifier("status_bar_height", "dimen", "android")
        if rid > 0:
            return resources.getDimensionPixelSize(rid)
    except Exception:
        pass
    return 28


def augment_html_for_android(html: str, window: toga.Window | None = None) -> str:
    """Inject real status-bar inset — WebView often reports env(safe-area) as 0."""
    if not is_android():
        return html
    top = _android_status_bar_height_px(window) if window else 28
    top = max(top + 8, 28)
    style = f"<style>:root{{--safe-top:{top}px;--safe-bottom:48px;}}</style>"
    if "<head>" in html:
        return html.replace("<head>", f"<head>{style}", 1)
    return style + html


def _webview_cache_dir(webview: toga.WebView) -> Path:
    return Path(toga.App.app.paths.cache) / f"toga/webview-{webview.id}"


def _load_via_asset_loader(webview: toga.WebView, entry: str = "index.html") -> bool:
    """Load bundled UI via Android WebViewAssetLoader (https only)."""
    impl = webview._impl
    if not getattr(impl, "SUPPORTS_LARGE_CONTENT", False):
        return False
    url = f"https://appassets.androidplatform.net/cache/toga/webview-{webview.id}/{entry}"
    impl.set_url(url)
    print(f"[webview] asset URL {url}")
    return True


def set_webview_bundle(
    webview: toga.WebView,
    files: dict[str, str],
    window: toga.Window | None = None,
    entry: str = "index.html",
) -> None:
    """Write HTML/CSS/JS to cache and load — avoids Android ~40KB loadData limit."""
    cache = _webview_cache_dir(webview)
    cache.mkdir(parents=True, exist_ok=True)

    for name, content in files.items():
        path = cache / name
        if name == entry:
            content = augment_html_for_android(content, window)
        path.write_text(content, encoding="utf-8")
        print(f"[webview] wrote {name} ({len(content)} chars)")

    impl = getattr(webview, "_impl", None)
    if impl is not None:
        settings = getattr(impl, "settings", None)
        if settings is not None:
            settings.setAllowFileAccess(True)
            settings.setAllowContentAccess(True)

    if _load_via_asset_loader(webview, entry):
        return

    # Desktop / fallback: single inlined page
    html = files.get(entry, "")
    if entry == "index.html" and "app.css" in files and "app.js" in files:
        html = html.replace(
            '<link rel="stylesheet" href="app.css">',
            f"<style>{files['app.css']}</style>",
        ).replace(
            '<script src="app.js"></script>',
            f"<script>{files['app.js']}</script>",
        )
    set_webview_html(webview, html, window=window)


def set_webview_html(
    webview: toga.WebView,
    html: str,
    root_url: str = "http://app.local/",
    window: toga.Window | None = None,
) -> None:
    """Load HTML into a Toga WebView (desktop / small pages)."""
    html = augment_html_for_android(html, window)
    impl = getattr(webview, "_impl", None)
    native = getattr(impl, "native", None) if impl else None

    if native is not None and hasattr(native, "loadDataWithBaseURL"):
        if len(html) > 35000:
            print(f"[webview] HTML too large ({len(html)}), use set_webview_bundle")
            set_webview_bundle(webview, {"index.html": html}, window=window)
            return
        try:
            native.loadDataWithBaseURL(
                root_url,
                html,
                "text/html",
                "utf-8",
                None,
            )
            print(f"[webview] loaded {len(html)} bytes via loadDataWithBaseURL")
            return
        except Exception as exc:
            print(f"[webview] loadDataWithBaseURL failed: {exc}")

    webview.set_content(root_url, html)
