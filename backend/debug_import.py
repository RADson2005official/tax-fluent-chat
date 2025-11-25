import sys
import traceback

try:
    import app.server
    print("Import successful")
except Exception:
    with open("import_error.txt", "w") as f:
        traceback.print_exc(file=f)
