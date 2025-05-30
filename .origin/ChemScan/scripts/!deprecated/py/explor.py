import subprocess

def open_in_explorer(paths):
    script = '''
    $paths = @{}
    $shell = New-Object -ComObject Shell.Application
    $windows = $shell.Windows()

    $i = 0
    foreach ($window in $windows) {{
        if ($i -lt $paths.Count) {{
            $folder = Get-Item $paths[$i]
            if ($folder) {{
                $window.Navigate("file://$($paths[$i])")
            }}
            $i++
        }}
    }}

    # If not enough Explorer windows exist, open new ones
    while ($i -lt $paths.Count) {{
        Start-Process explorer.exe -ArgumentList "/select, `"$($paths[$i])`""
        $i++
    }}
    '''.replace("{}", str(paths))

    subprocess.run(["powershell", "-Command", script], shell=True)

# Example usage:
files = [
    r"C:\Path\To\File1.txt",
    r"C:\Path\To\File2.txt"
]
open_in_explorer(files)