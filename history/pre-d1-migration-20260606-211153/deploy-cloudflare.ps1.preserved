param(
    [string]$EnvFile = ".env.deploy.local"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Net.Http

function Read-DeployEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        throw "Missing $Path. Copy .env.deploy.local.example to .env.deploy.local and fill the values."
    }

    $map = @{}
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) { return }
        $idx = $line.IndexOf("=")
        if ($idx -lt 0) { return }
        $key = $line.Substring(0, $idx).Trim()
        $val = $line.Substring($idx + 1).Trim()
        $map[$key] = $val
    }
    return $map
}

function Require-Value {
    param($Map, [string]$Key)
    if (-not $Map.ContainsKey($Key) -or [string]::IsNullOrWhiteSpace($Map[$Key])) {
        throw "Missing required value: $Key"
    }
    return $Map[$Key]
}

function Invoke-Cf {
    param(
        [string]$Method,
        [string]$Path,
        $Body = $null,
        [string]$ContentType = "application/json"
    )

    $uri = "https://api.cloudflare.com/client/v4$Path"
    $headers = @{ Authorization = "Bearer $script:Token" }

    if ($null -eq $Body) {
        return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
    }

    if ($ContentType -eq "application/json") {
        return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType $ContentType -Body ($Body | ConvertTo-Json -Depth 20)
    }

    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType $ContentType -Body $Body
}

function Get-OrCreateKvNamespace {
    param([string]$AccountId, [string]$Title)

    $list = Invoke-Cf -Method "GET" -Path "/accounts/$AccountId/storage/kv/namespaces"
    $existing = $list.result | Where-Object { $_.title -eq $Title } | Select-Object -First 1
    if ($existing) { return $existing.id }

    $created = Invoke-Cf -Method "POST" -Path "/accounts/$AccountId/storage/kv/namespaces" -Body @{ title = $Title }
    return $created.result.id
}

function Set-WorkerSecret {
    param([string]$AccountId, [string]$WorkerName, [string]$Name, [string]$Text)

    $body = @{
        name = $Name
        text = $Text
        type = "secret_text"
    }
    Invoke-Cf -Method "PUT" -Path "/accounts/$AccountId/workers/scripts/$WorkerName/secrets" -Body $body | Out-Null
}

function Publish-WorkerModule {
    param(
        [string]$AccountId,
        [string]$WorkerName,
        [string]$WorkerPath,
        [string]$KvNamespaceId,
        [string]$StoreRawIp
    )

    $metadata = @{
        main_module = "worker.js"
        bindings = @(
            @{
                type = "kv_namespace"
                name = "ANALYTICS_KV"
                namespace_id = $KvNamespaceId
            },
            @{
                type = "plain_text"
                name = "STORE_RAW_IP"
                text = $StoreRawIp
            }
        )
    } | ConvertTo-Json -Depth 20 -Compress

    $client = [System.Net.Http.HttpClient]::new()
    $client.DefaultRequestHeaders.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $script:Token)

    $content = [System.Net.Http.MultipartFormDataContent]::new()
    $metadataContent = [System.Net.Http.StringContent]::new($metadata, [System.Text.Encoding]::UTF8, "application/json")
    $content.Add($metadataContent, "metadata")

    $workerCode = [System.IO.File]::ReadAllText((Resolve-Path $WorkerPath))
    $workerContent = [System.Net.Http.StringContent]::new($workerCode, [System.Text.Encoding]::UTF8, "application/javascript+module")
    $content.Add($workerContent, "worker.js", "worker.js")

    $uri = "https://api.cloudflare.com/client/v4/accounts/$AccountId/workers/scripts/$WorkerName"
    $response = $client.PutAsync($uri, $content).GetAwaiter().GetResult()
    $text = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    if (-not $response.IsSuccessStatusCode) {
        throw "Worker publish failed: HTTP $($response.StatusCode) $text"
    }
    return $text | ConvertFrom-Json
}

function Enable-WorkersDev {
    param([string]$AccountId, [string]$WorkerName)

    $body = @{ enabled = $true }
    try {
        Invoke-Cf -Method "POST" -Path "/accounts/$AccountId/workers/scripts/$WorkerName/subdomain" -Body $body | Out-Null
        return $true
    } catch {
        try {
            Invoke-Cf -Method "PUT" -Path "/accounts/$AccountId/workers/scripts/$WorkerName/subdomain" -Body $body | Out-Null
            return $true
        } catch {
            Write-Warning "Could not explicitly enable workers.dev subdomain. Continuing; it may already be enabled."
            return $false
        }
    }
}

function Get-WorkerSubdomain {
    param([string]$AccountId)
    $res = Invoke-Cf -Method "GET" -Path "/accounts/$AccountId/workers/subdomain"
    return $res.result.subdomain
}

function Replace-Endpoint {
    param([string]$Path, [string]$CollectUrl)
    if (-not (Test-Path $Path)) {
        Write-Warning "Endpoint target not found: $Path"
        return
    }
    $resolved = Resolve-Path $Path
    $content = [System.IO.File]::ReadAllText($resolved)
    $pattern = 'endpoint:\s*"[^"]*"'
    $updated = [regex]::Replace($content, $pattern, 'endpoint: "' + $CollectUrl + '"', 1)
    [System.IO.File]::WriteAllText($resolved, $updated, [System.Text.UTF8Encoding]::new($false))
}

$envMap = Read-DeployEnv -Path $EnvFile
$script:Token = Require-Value $envMap "CLOUDFLARE_API_TOKEN"
$accountId = Require-Value $envMap "CLOUDFLARE_ACCOUNT_ID"
$workerName = if ($envMap["WORKER_NAME"]) { $envMap["WORKER_NAME"] } else { "erick-site-analytics" }
$kvTitle = if ($envMap["KV_NAMESPACE_TITLE"]) { $envMap["KV_NAMESPACE_TITLE"] } else { "erick_site_analytics_kv" }
$adminToken = Require-Value $envMap "ADMIN_TOKEN"
$storeRawIp = if ($envMap["STORE_RAW_IP"]) { $envMap["STORE_RAW_IP"] } else { "true" }

Write-Host "Creating or reusing KV namespace: $kvTitle"
$kvId = Get-OrCreateKvNamespace -AccountId $accountId -Title $kvTitle
Write-Host "KV namespace id: $kvId"

Write-Host "Publishing Worker: $workerName"
Publish-WorkerModule -AccountId $accountId -WorkerName $workerName -WorkerPath "worker.js" -KvNamespaceId $kvId -StoreRawIp $storeRawIp | Out-Null

Write-Host "Setting ADMIN_TOKEN secret"
Set-WorkerSecret -AccountId $accountId -WorkerName $workerName -Name "ADMIN_TOKEN" -Text $adminToken

Enable-WorkersDev -AccountId $accountId -WorkerName $workerName | Out-Null
$subdomain = Get-WorkerSubdomain -AccountId $accountId
if (-not $subdomain) { throw "Cloudflare did not return a workers.dev subdomain." }

$baseUrl = "https://$workerName.$subdomain.workers.dev"
$collectUrl = "$baseUrl/collect"
$dashboardUrl = "$baseUrl/dashboard?token=$adminToken"

Write-Host "Updating frontend endpoint configs"
Replace-Endpoint -Path "..\index.html" -CollectUrl $collectUrl
Replace-Endpoint -Path "..\bean-model\index.html" -CollectUrl $collectUrl
Replace-Endpoint -Path "..\privacy\index.html" -CollectUrl $collectUrl
Replace-Endpoint -Path "..\..\usdcny-tracker\docs\index.html" -CollectUrl $collectUrl

Write-Host ""
Write-Host "DEPLOYED"
Write-Host "Collect URL:   $collectUrl"
Write-Host "Dashboard URL: $dashboardUrl"
Write-Host ""
Write-Host "Next: commit and push the endpoint updates so the live pages start sending analytics."
