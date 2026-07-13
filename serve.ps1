$root = $PSScriptRoot
$port = 5500
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()
Write-Host "Serving $root at http://localhost:$port/index.html"

$mimeMap = @{
  ".html" = "text/html; charset=utf-8"
  ".js"   = "text/javascript"
  ".css"  = "text/css"
  ".glb"  = "model/gltf-binary"
  ".gltf" = "model/gltf+json"
  ".json" = "application/json"
  ".png"  = "image/png"
  ".jpg"  = "image/jpeg"
  ".svg"  = "image/svg+xml"
  ".mp4"  = "video/mp4"
  ".ttf"  = "font/ttf"
}

while ($listener.IsListening) {
  try {
    $ctx = $listener.GetContext()
  } catch {
    break
  }
  $req = $ctx.Request
  $res = $ctx.Response
  $urlPath = [System.Uri]::UnescapeDataString($req.Url.LocalPath)
  if ($urlPath -eq "/") { $urlPath = "/index.html" }
  $filePath = Join-Path $root ($urlPath.TrimStart('/'))

  if (Test-Path $filePath -PathType Leaf) {
    $bytes = [System.IO.File]::ReadAllBytes($filePath)
    $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
    $mime = $mimeMap[$ext]
    if (-not $mime) { $mime = "application/octet-stream" }
    $res.ContentType = $mime
    $res.ContentLength64 = $bytes.Length
    $res.OutputStream.Write($bytes, 0, $bytes.Length)
  } else {
    $res.StatusCode = 404
    $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found: $urlPath")
    $res.OutputStream.Write($msg, 0, $msg.Length)
  }
  $res.OutputStream.Close()
}
