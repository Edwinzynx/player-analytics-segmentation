param([string]$DesktopBin = 'C:/Program Files/Microsoft Power BI Desktop/bin')
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$project = Join-Path $repo 'outputs/powerbi'
$definition = Join-Path $project 'ProductAnalytics.SemanticModel/definition'
Add-Type -Path (Join-Path $DesktopBin 'Microsoft.PowerBI.Amo.Core.dll')
Add-Type -Path (Join-Path $DesktopBin 'Microsoft.PowerBI.Tabular.dll')
Add-Type -Path (Join-Path $DesktopBin 'Microsoft.PowerBI.AdomdClient.dll')
$parsed = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder($definition)
$lineage = $parsed.Model.Tables.Find('fact_players').LineageTag
$workspaces = Join-Path $env:LOCALAPPDATA 'Microsoft/Power BI Desktop/AnalysisServicesWorkspaces'
$matches = @()
foreach ($file in Get-ChildItem $workspaces -Recurse -Filter msmdsrv.port.txt) {
    $port = (Get-Content $file.FullName -Raw) -replace '[^0-9]', ''
    $candidate = [Microsoft.AnalysisServices.Tabular.Server]::new()
    try {
        $candidate.Connect("Data Source=localhost:$port")
        foreach ($db in $candidate.Databases) {
            if ($db.Model.Tables.ContainsName('fact_players') -and $db.Model.Tables.Find('fact_players').LineageTag -eq $lineage) {
                $matches += [pscustomobject]@{ Server=$candidate; Database=$db; Port=$port }
            }
        }
    } catch { $candidate.Dispose() }
}
if ($matches.Count -ne 1) { throw 'Open exactly one generated ProductAnalytics project in Power BI Desktop.' }
$target = $matches[0]
try {
    foreach ($table in $parsed.Model.Tables) {
        $loaded=$target.Database.Model.Tables.Find($table.Name)
        # Desktop adds an internal RowNumber column; validate declared columns.
        if ($null -eq $loaded -or $loaded.Measures.Count -ne $table.Measures.Count) {
            throw "Model structure changed for $($table.Name): expected $($table.Columns.Count) columns and $($table.Measures.Count) measures; loaded $($loaded.Columns.Count) columns and $($loaded.Measures.Count) measures. Close and reopen the project."
        }
        foreach ($column in $table.Columns) {
            if ($null -eq $loaded.Columns.Find($column.Name) -or $loaded.Columns.Find($column.Name).DataType -ne $column.DataType) {
                throw "Column definition mismatch: $($table.Name).$($column.Name)"
            }
        }
        foreach ($measure in $table.Measures) {
            if ($null -eq $loaded.Measures.Find($measure.Name)) { throw 'Reopen the project to load its new measure names.' }
            $loaded.Measures.Find($measure.Name).Expression=$measure.Expression
            $loaded.Measures.Find($measure.Name).FormatString=$measure.FormatString
        }
        foreach ($partition in $table.Partitions) {
            $loaded.Partitions.Find($partition.Name).Source.Expression=$partition.Source.Expression
        }
    }
    # Refresh only this project, identified by its deterministic table lineage tag.
    $target.Database.Model.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
    $target.Database.Model.SaveChanges() | Out-Null
    $connection = [Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new("Data Source=localhost:$($target.Port);Initial Catalog=$($target.Database.ID)")
    $connection.Open()
    $output = [ordered]@{
        desktop_version=(Get-Item (Join-Path $DesktopBin 'PBIDesktop.exe')).VersionInfo.ProductVersion
        engine_version=$target.Server.Version
        model_refreshed=$true
        definition_sha256=[ordered]@{}
        queries=[ordered]@{}
    }
    foreach ($file in Get-ChildItem $definition -Recurse -File) {
        $relative=[IO.Path]::GetRelativePath($definition,$file.FullName).Replace('\','/')
        $canonical=[IO.File]::ReadAllText($file.FullName).Replace("`r`n","`n")
        $bytes=[Text.Encoding]::UTF8.GetBytes($canonical)
        $output.definition_sha256[$relative]=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
    }
    $cases = Get-Content (Join-Path $project 'validation_queries.json') -Raw | ConvertFrom-Json
    foreach ($case in $cases) {
        $command=$connection.CreateCommand()
        $command.CommandText=$case.query
        $reader=$command.ExecuteReader()
        $rows=@()
        while ($reader.Read()) {
            $row=[ordered]@{}
            for ($i=0; $i -lt $reader.FieldCount; $i++) {
                $name=$reader.GetName($i) -replace '^.*\[([^\]]+)\]$','$1'
                $row[$name]=if ($reader.IsDBNull($i)) { $null } else { $reader.GetValue($i) }
            }
            $rows+= $row
        }
        $reader.Close()
        $output.queries[$case.name]=$rows
        Write-Output "Executed $($case.name)"
    }
    $output | ConvertTo-Json -Depth 20 | Set-Content (Join-Path $project 'engine_results.json') -Encoding utf8
    $connection.Close()
} finally { $target.Server.Disconnect() }
