# Lightweight .NET HttpListener Static Web Server for Myntra Sense Frontend
$Port = 3000
$RootPath = (Resolve-Path "frontend").Path

$Listener = [System.Net.HttpListener]::new()
$Listener.Prefixes.Add("http://localhost:$Port/")
$Listener.Start()

Write-Host "Myntra Sense Web Server running at: http://localhost:$Port/" -ForegroundColor Green
Write-Host "Serving files from: $RootPath" -ForegroundColor Cyan

$MimeTypes = @{
    ".html" = "text/html; charset=utf-8"
    ".css"  = "text/css; charset=utf-8"
    ".js"   = "application/javascript; charset=utf-8"
    ".json" = "application/json; charset=utf-8"
    ".png"  = "image/png"
    ".jpg"  = "image/jpeg"
    ".svg"  = "image/svg+xml"
}

try {
    while ($Listener.IsListening) {
        $Context = $Listener.GetContext()
        $Request = $Context.Request
        $Response = $Context.Response

        $UrlPath = $Request.Url.LocalPath.TrimStart('/')
        if ([string]::IsNullOrWhiteSpace($UrlPath) -or $UrlPath -eq "/") {
            $UrlPath = "index.html"
        }

        $FilePath = [System.IO.Path]::Combine($RootPath, $UrlPath.Replace('/', '\'))

        if ([System.IO.File]::Exists($FilePath)) {
            $Ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
            $ContentType = if ($MimeTypes.ContainsKey($Ext)) { $MimeTypes[$Ext] } else { "application/octet-stream" }

            $Bytes = [System.IO.File]::ReadAllBytes($FilePath)
            $Response.ContentType = $ContentType
            $Response.ContentLength64 = $Bytes.Length
            $Response.StatusCode = 200
            $Response.AddHeader("Access-Control-Allow-Origin", "*")
            $Response.OutputStream.Write($Bytes, 0, $Bytes.Length)
        } else {
            $Response.StatusCode = 404
            $NotFoundMsg = "404 Not Found"
            $NotFoundBytes = [System.Text.Encoding]::UTF8.GetBytes($NotFoundMsg)
            $Response.OutputStream.Write($NotFoundBytes, 0, $NotFoundBytes.Length)
        }
        $Response.Close()
    }
} finally {
    $Listener.Stop()
}
