"""Platform detection and Android-specific WebView helpers."""
from __future__ import annotations

import hashlib
import importlib.util
import shutil
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


def bundle_fingerprint(files: dict[str, str]) -> str:
    """Stable hash of bundled UI files — changes whenever JS/CSS/HTML updates."""
    digest = hashlib.sha256()
    for name in sorted(files):
        digest.update(name.encode("utf-8"))
        digest.update(files[name].encode("utf-8"))
    return digest.hexdigest()[:12]


def _bundle_dir(webview: toga.WebView, fingerprint: str) -> Path:
    return _webview_cache_dir(webview) / f"bundle-{fingerprint}"


def _purge_stale_bundles(webview: toga.WebView, keep_fingerprint: str) -> None:
    root = _webview_cache_dir(webview)
    if not root.exists():
        return
    keep_name = f"bundle-{keep_fingerprint}"
    for child in root.iterdir():
        if child.name.startswith("bundle-") and child.name != keep_name:
            shutil.rmtree(child, ignore_errors=True)
    # Legacy flat layout (pre fingerprint dirs) — remove so WebView cannot reload it.
    for legacy in ("index.html", "app.js", "app.css"):
        legacy_path = root / legacy
        if legacy_path.exists():
            legacy_path.unlink(missing_ok=True)


def _clear_webview_browser_cache(webview: toga.WebView) -> None:
    impl = getattr(webview, "_impl", None)
    native = getattr(impl, "native", None) if impl else None
    if native is None:
        return
    if hasattr(native, "clearCache"):
        try:
            native.clearCache(True)
            print("[webview] cleared browser cache")
        except Exception as exc:
            print(f"[webview] clearCache failed: {exc}")
    if hasattr(native, "getSettings"):
        try:
            settings = native.getSettings()
            # WebSettings.LOAD_NO_CACHE — always fetch fresh UI after an app update.
            settings.setCacheMode(2)
        except Exception as exc:
            print(f"[webview] setCacheMode failed: {exc}")


def _inline_bundle(index_html: str, files: dict[str, str]) -> str:
    """Embed CSS/JS into HTML (needed when sub-resources cannot be served correctly)."""
    html = index_html
    if "app.css" in files:
        html = html.replace(
            '<link rel="stylesheet" href="app.css">',
            f"<style>{files['app.css']}</style>",
        )
    if "app.js" in files:
        html = html.replace(
            '<script src="app.js"></script>',
            f"<script>{files['app.js']}</script>",
        )
    return html


def _supports_asset_loader(webview: toga.WebView) -> bool:
    impl = getattr(webview, "_impl", None)
    return impl is not None and getattr(impl, "SUPPORTS_LARGE_CONTENT", False)


def _asset_url(webview: toga.WebView, rel_path: str) -> str:
    return f"https://appassets.androidplatform.net/cache/toga/webview-{webview.id}/{rel_path}"


def _load_via_asset_loader(webview: toga.WebView, rel_path: str) -> bool:
    """Load bundled UI via Android WebViewAssetLoader (https only)."""
    if not _supports_asset_loader(webview):
        return False
    url = _asset_url(webview, rel_path)
    webview._impl.set_url(url)
    print(f"[webview] asset URL {url}")
    return True


def _load_via_file_url(webview: toga.WebView, path: Path) -> bool:
    """Load from cache via file:// — WebKit resolves CSS/JS MIME types correctly."""
    impl = getattr(webview, "_impl", None)
    if impl is None or not hasattr(impl, "set_url"):
        return False
    if not path.exists():
        return False
    url = path.resolve().as_uri()
    impl.set_url(url)
    print(f"[webview] file URL {url}")
    return True


def set_webview_bundle(
    webview: toga.WebView,
    files: dict[str, str],
    window: toga.Window | None = None,
    entry: str = "index.html",
) -> None:
    """Write HTML/CSS/JS to cache and load — avoids Android ~40KB loadData limit."""
    fingerprint = bundle_fingerprint(files)
    root = _webview_cache_dir(webview)
    cache = _bundle_dir(webview, fingerprint)
    marker = root / "active-fingerprint"
    prev = marker.read_text(encoding="utf-8").strip() if marker.exists() else ""
    if prev != fingerprint:
        _clear_webview_browser_cache(webview)
        _purge_stale_bundles(webview, fingerprint)
    root.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    marker.write_text(fingerprint, encoding="utf-8")

    impl = getattr(webview, "_impl", None)
    if impl is not None:
        settings = getattr(impl, "settings", None)
        if settings is not None:
            settings.setAllowFileAccess(True)
            settings.setAllowContentAccess(True)

    use_asset_loader = _supports_asset_loader(webview)
    rel_entry = f"bundle-{fingerprint}/{entry}"

    # Toga's Android cache handler serves every file as text/html, so external
    # app.css / app.js never execute — inline everything into index.html.
    if use_asset_loader and entry in files:
        html = _inline_bundle(files[entry], files)
        html = augment_html_for_android(html, window)
        meta = f'<meta name="app-ui-build" content="{fingerprint}">'
        html = html.replace("<head>", f"<head>{meta}", 1)
        (cache / entry).write_text(html, encoding="utf-8")
        print(f"[webview] wrote {rel_entry} inlined ({len(html)} chars, build={fingerprint})")
        _load_via_asset_loader(webview, rel_entry)
        return

    for name, content in files.items():
        path = cache / name
        if name == entry:
            content = augment_html_for_android(content, window)
            meta = f'<meta name="app-ui-build" content="{fingerprint}">'
            content = content.replace("<head>", f"<head>{meta}", 1)
        path.write_text(content, encoding="utf-8")
        print(f"[webview] wrote bundle-{fingerprint}/{name} ({len(content)} chars)")

    entry_path = cache / entry
    if _load_via_file_url(webview, entry_path):
        return

    # Last resort: one inlined document via load_html / loadData
    html = files.get(entry, "")
    if entry == "index.html" and "app.css" in files and "app.js" in files:
        html = _inline_bundle(html, files)
    set_webview_html(webview, html, root_url=entry_path.resolve().as_uri(), window=window)


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

    # loadDataWithBaseURL has a ~40KB limit on Android; large pages use the bundle path.
    if (
        native is not None
        and hasattr(native, "loadDataWithBaseURL")
        and len(html) <= 35000
    ):
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
    print(f"[webview] loaded {len(html)} bytes via set_content")
