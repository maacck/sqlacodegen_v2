from __future__ import annotations

import logging
import sys
from contextlib import ExitStack
from typing import TextIO, Optional, List

from sqlalchemy.engine import create_engine
from sqlalchemy.schema import MetaData

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points, version
else:
    from importlib.metadata import entry_points, version

def generate_models(
        db_url: str,
        generator: str = "declarative",
        options: Optional[dict] = None,
        outfile_path: Optional[str] = None,
) -> None:
    generators = {ep.name: ep for ep in entry_points(group="sqlacodegen.generators")}

    # Convert db_url from a string to a URL object so we can access methods
    URL.make_url(db_url)
    # Check driver type and handle it accordingly for known mssql+pyodbc case
    if db_url.drivername == "mssql+pyodbc":
        engine = create_engine(db_url, use_setinputsizes=False)
    else:
        engine = create_engine(db_url)
    # Use reflection to fill in the metadata
    metadata = MetaData()
    # Instantiate the generator
    generator_class = generators[generator].load()
    generator = generator_class(metadata, engine, options if options else {})
    tables = None
    schemas = [None]
    for schema in schemas:
        metadata.reflect(engine, schema, False, tables)

    # Open the target file (if given)
    with ExitStack() as stack:
        outfile: TextIO
        if outfile_path:
            outfile = open(outfile_path, "w", encoding="utf-8")
            stack.enter_context(outfile)
        else:
            outfile = sys.stdout
        # Write the generated model code to the specified file or standard output
        outfile.write(generator.generate())

