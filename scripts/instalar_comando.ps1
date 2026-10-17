[CmdletBinding(SupportsShouldProcess)]
param()

$ErrorActionPreference = 'Stop'
$repoPath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$pythonPath = Join-Path $repoPath '.venv\Scripts\python.exe'
$appPath = Join-Path $repoPath 'scripts\iniciar_guara.py'
$binPath = Join-Path $env:LOCALAPPDATA 'Programs\OrbeIA\bin'
$launcherPath = Join-Path $binPath 'guara.cmd'
$marker = 'REM Gerenciado pelo projeto OrbeIA.'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw 'Crie o ambiente .venv e instale requirements.txt antes de instalar o comando.'
}
if (-not (Test-Path -LiteralPath $appPath -PathType Leaf)) {
    throw 'O ponto de entrada scripts/iniciar_guara.py nao foi encontrado.'
}

$existingCommand = Get-Command guara -ErrorAction SilentlyContinue
if ($existingCommand -and $existingCommand.Source -ne $launcherPath) {
    throw 'Ja existe outro comando guara. A instalacao foi interrompida para preserva-lo.'
}
if ((Test-Path -LiteralPath $launcherPath) -and
    -not ([IO.File]::ReadAllText($launcherPath).Contains($marker))) {
    throw 'O arquivo guara.cmd existente nao pertence a este instalador e foi preservado.'
}

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$pathEntries = @($userPath -split ';' | Where-Object { $_ })
$hasEntry = @($pathEntries | Where-Object {
    $_.Trim().TrimEnd('\') -eq $binPath.TrimEnd('\')
}).Count -gt 0

$launcher = @(
    '@echo off'
    $marker
    ('"{0}" "{1}" %*' -f $pythonPath, $appPath)
    'exit /b %errorlevel%'
) -join "`r`n"

if ($PSCmdlet.ShouldProcess($launcherPath, 'Instalar comando guara e adicionar a pasta ao PATH do usuario')) {
    [IO.Directory]::CreateDirectory($binPath) | Out-Null
    [IO.File]::WriteAllText($launcherPath, $launcher + "`r`n", [Text.UTF8Encoding]::new($false))
    if (-not $hasEntry) {
        $updatedPath = if ([string]::IsNullOrEmpty($userPath)) {
            $binPath
        } else {
            $userPath.TrimEnd(';') + ';' + $binPath
        }
        [Environment]::SetEnvironmentVariable('Path', $updatedPath, 'User')
    }
    $env:Path = $binPath + ';' + $env:Path
    Write-Output 'Comando guara instalado. Abra um novo terminal para usa-lo em qualquer pasta.'
}
