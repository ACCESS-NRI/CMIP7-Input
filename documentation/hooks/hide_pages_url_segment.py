import os

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
