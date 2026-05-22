# Self-contained PowerShell Installer for Delphi for Python Wizard Skill
# Usage:
#   powershell -ExecutionPolicy Bypass -File install.ps1
# Or one-liner download and run:
#   irm https://raw.githubusercontent.com/gaitolini/delphi-for-python-wizard/main/install.ps1 | iex

$RepoUrl = "https://github.com/gaitolini/delphi-for-python-wizard.git"
$SkillFolderName = "delphi-for-python-wizard"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Delphi for Python Wizard - AI Skill & Workspace Installer" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Determine Source Directory (Clone if run remotely)
$CurrentDir = Get-Location
$TempDir = $null
$SourceSkillPath = Join-Path $CurrentDir $SkillFolderName

if (!(Test-Path (Join-Path $SourceSkillPath "SKILL.md"))) {
    Write-Host "[Info] Executando fora de um repositório clonado localmente." -ForegroundColor Yellow
    Write-Host "[Info] Clonando o repositório temporariamente a partir de $RepoUrl..." -ForegroundColor Yellow
    
    $TempDir = Join-Path $env:TEMP "delphi-for-python-wizard-temp"
    if (Test-Path $TempDir) {
        Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    try {
        git clone $RepoUrl $TempDir
        $SourceSkillPath = Join-Path $TempDir $SkillFolderName
    } catch {
        Write-Host "[Erro] Falha ao clonar o repositório. Certifique-se de que o Git está instalado no PATH." -ForegroundColor Red
        Exit 1
    }
}

# 2. Detect Target Folders (.agent or Global Antigravity)
$InstallPaths = @()

# Check local workspace for .agent / .agent/skills
$LocalAgentDir = Join-Path $CurrentDir ".agent"
if (Test-Path $LocalAgentDir) {
    Write-Host "[Info] Diretório do agente local (.agent) detectado na pasta atual." -ForegroundColor Green
    $LocalSkillsDir = Join-Path $LocalAgentDir "skills"
    New-Item -ItemType Directory -Force -Path $LocalSkillsDir | Out-Null
    $InstallPaths += Join-Path $LocalSkillsDir $SkillFolderName
}

# Check global Antigravity path
$GlobalSkillsDir = Join-Path $env:USERPROFILE ".gemini" "antigravity" "skills"
if (Test-Path $GlobalSkillsDir) {
    $InstallPaths += Join-Path $GlobalSkillsDir $SkillFolderName
} else {
    # If not present but user profile exists, we can still install globally
    $GlobalBase = Join-Path $env:USERPROFILE ".gemini" "antigravity"
    if (Test-Path $GlobalBase) {
        New-Item -ItemType Directory -Force -Path $GlobalSkillsDir | Out-Null
        $InstallPaths += Join-Path $GlobalSkillsDir $SkillFolderName
    }
}

# Default Fallback if none found
if ($InstallPaths.Count -eq 0) {
    $DefaultLocalDir = Join-Path (Join-Path $CurrentDir ".agent") "skills"
    New-Item -ItemType Directory -Force -Path $DefaultLocalDir | Out-Null
    $InstallPaths += Join-Path $DefaultLocalDir $SkillFolderName
}

# 3. Copy Skill Files to Targets
foreach ($Target in $InstallPaths) {
    Write-Host "[Info] Instalando Skill em: $Target" -ForegroundColor Cyan
    if (Test-Path $Target) {
        Remove-Item $Target -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    Copy-Item -Path (Join-Path $SourceSkillPath "*") -Destination $Target -Recurse -Force
    Write-Host "[Sucesso] Arquivos copiados com sucesso!" -ForegroundColor Green
}

# 4. Automate Virtual Environment (.venv) Creation
$VenvPath = Join-Path $CurrentDir ".venv"
if (!(Test-Path $VenvPath)) {
    Write-Host "[Info] Nenhum ambiente virtual (.venv) encontrado na pasta de destino." -ForegroundColor Yellow
    Write-Host "[Info] Verificando versões de Python compatíveis instaladas..." -ForegroundColor Yellow
    
    $PythonExe = $null
    $PyArg = $null
    $TargetVersions = @("3.13", "3.12", "3.11", "3.10", "3.9", "3.8")
    
    # Check via 'py' launcher
    foreach ($ver in $TargetVersions) {
        try {
            $pyPath = py -$ver -c "import sys; print(sys.executable)" -ErrorAction Stop
            $pyPath = $pyPath.Trim()
            if (Test-Path $pyPath) {
                $PythonExe = $pyPath
                $PyArg = "-$ver"
                break
            }
        } catch {}
    }
    
    # Fallback to system 'python' if compatible
    if ($PythonExe -eq $null) {
        try {
            $major = python -c "import sys; print(sys.version_info.major)" -ErrorAction Stop
            $minor = python -c "import sys; print(sys.version_info.minor)" -ErrorAction Stop
            $major = $major.Trim()
            $minor = $minor.Trim()
            if ($major -eq "3" -and [int]$minor -ge 8 -and [int]$minor -le 13) {
                $PythonExe = "python"
            }
        } catch {}
    }
    
    if ($PythonExe -eq $null) {
        Write-Host "[Aviso] Nenhuma versão estável recomendada (Python 3.8 a 3.13) foi encontrada." -ForegroundColor Red
        Write-Host "Por favor, instale o Python 3.12 ou 3.13 para obter a melhor compatibilidade." -ForegroundColor Red
    } else {
        Write-Host "[Info] Criando ambiente virtual (.venv) usando $PythonExe..." -ForegroundColor Green
        if ($PyArg -ne $null) {
            & py $PyArg -m venv $VenvPath
        } else {
            & $PythonExe -m venv $VenvPath
        }
        
        # Configure local dependencies
        $VenvPython = Join-Path $VenvPath "Scripts" "python.exe"
        if (Test-Path $VenvPython) {
            Write-Host "[Info] Atualizando o pip no ambiente virtual..." -ForegroundColor Green
            & $VenvPython -m pip install --upgrade pip | Out-Null
            Write-Host "[Info] Instalando delphivcl no ambiente virtual (.venv)..." -ForegroundColor Green
            & $VenvPython -m pip install delphivcl | Out-Null
            Write-Host "[Sucesso] Ambiente virtual (.venv) criado e configurado!" -ForegroundColor Green
        }
    }
} else {
    Write-Host "[Info] Ambiente virtual (.venv) já existe. Ignorando criação." -ForegroundColor Green
}

# 5. Cleanup Temp Directory
if ($TempDir -ne $null -and (Test-Path $TempDir)) {
    Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Instalação concluída com sucesso! Nova Skill ativa." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
