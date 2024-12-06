#!/usr/bin/env python
import os
import sys

import dotenv


def initialize_debugpy():
    import debugpy

    try:
        debugpy.listen(("0.0.0.0", 5678))
        sys.stdout.write("debugpy listening on port 5678...\n")
    except Exception as exc:
        sys.stderr.write(f"Failed to initialize debugpy: {exc}\n")


if __name__ == "__main__":
    ENABLE_DEBUGPY = os.getenv("ENABLE_DEBUGPY")
    if ENABLE_DEBUGPY and ENABLE_DEBUGPY.lower() == "true":
        initialize_debugpy()

    dotenv.read_dotenv()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bakerydemo.settings.dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
