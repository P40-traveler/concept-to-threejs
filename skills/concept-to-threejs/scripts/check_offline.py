"""Smoke-test one self-contained Three.js HTML file in headless Chromium."""

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit


# Observe the renderer acquiring its context. Calling getContext() on every canvas
# in the readiness check would create contexts and could pass a static poster.
OBSERVE_WEBGL = """
(() => {
  const contexts = new Set();
  const original = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function(kind, ...args) {
    const gl = original.call(this, kind, ...args);
    if (gl && ['webgl2', 'webgl', 'experimental-webgl'].includes(kind)) contexts.add(gl);
    return gl;
  };
  window.__offlineSceneHasWebGL = () => [...contexts].some(gl => {
    const canvas = gl.canvas;
    return !gl.isContextLost() && gl.drawingBufferWidth > 0 && gl.drawingBufferHeight > 0
      && canvas.isConnected && canvas.getClientRects().length > 0
      && canvas.checkVisibility({checkOpacity: true, checkVisibilityCSS: true});
  });
})();
"""

DEFAULT_READY = "document.documentElement.dataset.state === undefined || document.documentElement.dataset.state === 'live'"
SHADER_ERROR = re.compile(r"shader.*(?:error|fail)|(?:error|fail).*shader|(?:GL_|WebGL: )INVALID_OPERATION", re.I)


def file_key(url):
    parts = urlsplit(url)
    return (parts.netloc.lower(), unquote(parts.path))


def check(playwright, source, ready, timeout):
    errors = []

    def report(message):
        if message not in errors:
            errors.append(message)

    with tempfile.TemporaryDirectory(prefix="scene-offline-") as directory:
        entry = Path(shutil.copyfile(source, Path(directory) / source.name)).as_uri()
        entry_key = file_key(entry)

        def dependency(url):
            if url.startswith(("http:", "https:", "ws:", "wss:")):
                return "Network dependency: " + url
            if url.startswith("file:") and file_key(url) != entry_key:
                return "Local dependency outside the HTML: " + unquote(url)
            return None

        def route_request(route):
            problem = dependency(route.request.url)
            if problem:
                report(problem)
                route.abort()
            else:
                route.continue_()

        def console_message(message):
            if message.type == "error" or (message.type == "warning" and SHADER_ERROR.search(message.text)):
                report("Browser console: " + message.text)

        browser = playwright.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        try:
            context = browser.new_context(offline=True, service_workers="block", viewport={"width": 800, "height": 450})
            context.add_init_script(OBSERVE_WEBGL)
            context.route(re.compile(r"^(?:https?|file):"), route_request)
            # Chromium may report file requests without sending them through a route.
            def observe(request):
                problem = dependency(request.url)
                if problem:
                    report(problem)

            context.on("request", observe)
            context.on("console", console_message)
            context.on("weberror", lambda error: report("Page error: " + str(error.error)))
            page = context.new_page()
            page.on("websocket", lambda socket: report("WebSocket dependency: " + socket.url))
            page.set_default_timeout(timeout * 1000)
            try:
                page.goto(entry, wait_until="load")
                if not errors:
                    predicate = f"""async () => {{
                        if (!window.__offlineSceneHasWebGL()) return false;
                        const ready = ({ready});
                        return typeof ready === 'function' ? await ready() : await ready;
                    }}"""
                    page.wait_for_function(predicate)
                    # Allow immediately scheduled startup work and renderer diagnostics to arrive.
                    page.wait_for_timeout(300)
                    if not page.evaluate(predicate):
                        report("Scene lost readiness during startup.")
            except Exception as exc:
                report(str(exc))
        finally:
            browser.close()
    return errors


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Requires Python 3, the playwright package, and its Chromium browser "
               "(python -m pip install playwright, then python -m playwright install chromium). "
               "Exercises startup only. Review camera interaction, image quality and lighting separately.",
    )
    parser.add_argument("html", type=Path, help="standalone HTML to open via file:// in an empty temporary directory")
    parser.add_argument("--ready", default=DEFAULT_READY, metavar="JS",
                        help="additional readiness expression or zero-argument function. By default an existing "
                             "html[data-state] must be live. A visible canvas with an active WebGL context is required.")
    parser.add_argument("--timeout", default=90, type=int, metavar="SECONDS",
                        help="maximum time for each navigation or readiness wait (default: 90)")
    args = parser.parse_args()
    if not args.html.is_file() or args.timeout < 1:
        parser.error("Supply an existing HTML file and a positive timeout.")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            errors = check(playwright, args.html, args.ready, args.timeout)
    except Exception as exc:
        errors = [str(exc)]
    if errors:
        for issue in errors:
            print("FAIL:", issue, file=sys.stderr)
        return 1
    print(f"PASS: {args.html.name} started with live WebGL from the isolated, offline HTML.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
