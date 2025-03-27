# amatak.ps1
$AMATAK_ROOT = (Get-Item $PSScriptRoot).Parent.FullName
$PYTHON_EXEC = if (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { "python" }
$env:PYTHONPATH = "$AMATAK_ROOT;$AMATAK_ROOT\Lib;$env:PYTHONPATH"

& $PYTHON_EXEC "$AMATAK_ROOT\amatak\bin\amatak.py" $args