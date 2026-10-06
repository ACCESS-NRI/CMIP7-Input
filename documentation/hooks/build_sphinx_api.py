import subprocess
import sys
from pathlib import Path


def on_post_build(config):
    """Build Sphinx API documentation into the MkDocs site output directory."""
    docs_parent = Path(config["config_file_path"]).parent
    sphinx_src = docs_parent / "sphinx"
    output_dir = Path(config["site_dir"]) / "api"

    cmd = [
        sys.executable,
        "-m",
        "sphinx",
        "-b",
        "html",
        str(sphinx_src),
        str(output_dir),
    ]
    subprocess.run(cmd, check=True)
