import os
import re

from mkdocs.plugins import event_priority


@event_priority(-100)
def on_files(files, config):
    for file in files:
        if file.src_uri.startswith("pages/"):
            file.dest_uri = file.dest_uri.removeprefix("pages/")
            file.dest_path = file.dest_path.removeprefix("pages/")
            file.url = file.url.removeprefix("pages/")
            if not file.url:
                file.url = "./"
            file.abs_dest_path = os.path.normpath(
                os.path.join(file.dest_dir, file.dest_uri)
            )
    return files


@event_priority(-100)
def on_page_markdown(markdown, *, page, config, files):
    if config.site_url:
        page.canonical_url = (
            config.site_url.rstrip("/") + "/" + page.file.url.lstrip("/")
        )
    else:
        page.canonical_url = None


@event_priority(-100)
def on_post_page(output, *, page, config):
    def replace_href(match):
        href = match.group(1)
        if href.startswith(
            ("http://", "https://", "mailto:", "#", "javascript:", "data:")
        ):
            return match.group(0)

        parts = href.split("#", 1)
        path_query = parts[0]
        anchor = ("#" + parts[1]) if len(parts) > 1 else ""

        pq = path_query.split("?", 1)
        path = pq[0]
        query = ("?" + pq[1]) if len(pq) > 1 else ""

        if path.endswith("/"):
            path = path + "index.html"
        elif path == ".":
            path = "./index.html"
        elif path == "..":
            path = "../index.html"
        elif path.endswith("/."):
            path = path[:-1] + "index.html"
        elif path.endswith("/.."):
            path = path + "/index.html"
        elif path != "" and not os.path.splitext(path)[1]:
            path = path + "/index.html"

        return f'href="{path}{query}{anchor}"'

    return re.sub(r'href="([^"]+)"', replace_href, output)
