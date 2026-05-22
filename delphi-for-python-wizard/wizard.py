import os
import sys
import argparse
import subprocess
import shutil

def find_best_python():
    """
    Procura no Windows pela versão mais recente compatível do Python (entre 3.8 e 3.13)
    usando o instalador 'py' launcher ou fallback do sistema.
    """
    # Lista de versões prioritárias (da mais nova à mais antiga que são compatíveis e possuem wheels)
    target_versions = ["3.13", "3.12", "3.11", "3.10", "3.9", "3.8"]
    
    # 1. Tenta usar o launcher 'py' do Windows que gerencia múltiplas versões
    for ver in target_versions:
        try:
            # Testa se o comando consegue iniciar sem erros
            result = subprocess.run(
                ["py", f"-{ver}", "-c", "import sys; print(sys.executable)"],
                capture_output=True,
                text=True,
                check=True
            )
            exe_path = result.stdout.strip()
            if os.path.exists(exe_path):
                print(f"[Wizard] Encontrado Python {ver} via 'py' launcher: {exe_path}")
                return exe_path, f"-{ver}"
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    # 2. Testa o executável atual do sistema se for compatível
    current_major = sys.version_info.major
    current_minor = sys.version_info.minor
    if current_major == 3 and (8 <= current_minor <= 13):
        print(f"[Wizard] Usando o executável ativo compatível (Python {current_major}.{current_minor}): {sys.executable}")
        return sys.executable, None

    # 3. Caso contrário, falha informando o usuário sobre a necessidade de uma versão compatível
    print("[Erro] Não foi encontrada nenhuma versão estável recomendada do Python (3.8 a 3.13) instalada e no PATH.")
    print("Por favor, instale o Python 3.12 ou 3.13 (https://www.python.org/downloads/) e marque 'Add python.exe to PATH'.")
    sys.exit(1)

def create_venv(python_exe, py_ver_arg, dest_path):
    """
    Cria o ambiente virtual (venv) utilizando a versão especificada do Python.
    """
    venv_path = os.path.join(dest_path, "venv")
    print(f"[Wizard] Criando ambiente virtual em '{venv_path}'...")
    
    # Comando de inicialização do venv
    if py_ver_arg:
        cmd = ["py", py_ver_arg, "-m", "venv", venv_path]
    else:
        cmd = [python_exe, "-m", "venv", venv_path]
        
    try:
        subprocess.run(cmd, check=True)
        print("[Wizard] Ambiente virtual criado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"[Erro] Falha ao criar ambiente virtual: {e}")
        sys.exit(1)

def install_dependencies(dest_path, framework):
    """
    Atualiza o pip e instala o framework desejado (delphivcl ou delphifmx)
    rodando 'python -m pip' para evitar erros de bloqueio de arquivo no Windows.
    """
    # Mapeia caminho do executável do Python dentro do venv
    venv_python = os.path.join(dest_path, "venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = os.path.join(dest_path, "venv", "Scripts", "python")

    if not os.path.exists(venv_python):
        print(f"[Erro] Executável do Python não encontrado no venv em: {venv_python}")
        sys.exit(1)

    print(f"[Wizard] Atualizando pip no ambiente virtual...")
    try:
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[Erro] Falha ao atualizar o pip: {e}")
        sys.exit(1)

    library = "delphivcl" if framework == "vcl" else "delphifmx"
    print(f"[Wizard] Instalando a biblioteca '{library}' via pip...")
    try:
        subprocess.run([venv_python, "-m", "pip", "install", library], check=True)
        print(f"[Wizard] Biblioteca '{library}' instalada com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"[Erro] Falha ao instalar a biblioteca '{library}': {e}")
        sys.exit(1)

def write_vcl_template(dest_path, project_name):
    """
    Escreve os arquivos base do esqueleto para projetos VCL.
    """
    # 1. Criar main.py
    main_py_path = os.path.join(dest_path, "main.py")
    main_py_content = f"""import os
from delphivcl import *

class MainForm(Form):
    def __init__(self, owner):
        # Declare as variáveis de componentes criadas na IDE do Delphi como None.
        # Exemplo: self.Button1 = None
        self.lblWelcome = None
        self.btnAction = None
        
        # Carrega as propriedades visuais do arquivo .pydfm gerado pelo Expert do Delphi IDE
        pydfm_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MainForm.pydfm")
        self.LoadProps(pydfm_file)
        
        # Inscreva-se nos eventos programados em Python
        self.btnAction.OnClick = self.do_action_click
        
        # DICA DE ESTILIZAÇÃO (StyleElements):
        # Se você aplicar uma cor ou fonte customizada em componentes e a IDE do Delphi
        # ignorá-la na execução devido ao Estilo do Windows (VCL Style), limpe os StyleElements:
        # self.lblWelcome.StyleElements = "" # Ignora tema para aplicar customizações

    def do_action_click(self, sender):
        self.lblWelcome.Caption = "Ação disparada com sucesso em Python!"
        self.lblWelcome.Font.Size = 14
        
        # EXEMPLO DE ESTILO DE FONTE:
        # No Python, TFontStyles são representados por um Set contendo Strings:
        self.lblWelcome.Font.Style = {{"fsBold", "fsItalic"}} 

def main():
    Application.Initialize()
    Application.Title = "{project_name}"
    
    # Instancia o formulário principal
    form = MainForm(Application)
    form.Show()
    
    # Oculta o terminal em background para dar foco à GUI
    FreeConsole()
    
    # Executa o loop principal da aplicação
    Application.Run()
    form.Destroy()

if __name__ == '__main__':
    main()
"""
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(main_py_content)

    # 2. Criar MainForm.pydfm de teste (DFM legível em texto contendo a estrutura básica)
    pydfm_path = os.path.join(dest_path, "MainForm.pydfm")
    pydfm_content = """object MainForm: TMainForm
  Left = 0
  Top = 0
  Caption = 'Delphi VCL for Python MainForm'
  ClientHeight = 240
  ClientWidth = 460
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  TextHeight = 15
  object lblWelcome: TLabel
    Left = 40
    Top = 50
    Width = 380
    Height = 30
    Alignment = taCenter
    AutoSize = False
    Caption = 'Bem-vindo ao DelphiVCL4Python!'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -16
    Font.Name = 'Segoe UI'
    Font.Style = []
    ParentFont = False
  end
  object btnAction: TButton
    Left = 160
    Top = 120
    Width = 140
    Height = 35
    Caption = 'Disparar Ação'
    TabOrder = 0
  end
end
"""
    with open(pydfm_path, "w", encoding="utf-8") as f:
        f.write(pydfm_content)

    # 3. Criar arquivo INSTRUCTIONS.md
    instructions_path = os.path.join(dest_path, "INSTRUCTIONS.md")
    instructions_content = f"""# Instruções do Projeto VCL - {project_name}

Seu ambiente virtual e projeto inicial estão configurados com sucesso!

## Como Executar o Projeto de Teste
1. Ative o ambiente virtual no PowerShell:
   ```powershell
   .\\venv\\Scripts\\Activate.ps1
   ```
2. Execute o script principal:
   ```powershell
   python main.py
   ```

## Como Integrar com a IDE do Delphi (WYSIWYG)
1. Instale o Add-in **dclDelphiVCLExperts** na IDE do Delphi (copie da pasta `experts` do repositório oficial do GitHub).
2. Abra a IDE do Delphi, vá em **File > New > Windows VCL Application**.
3. Desenhe sua tela arrastando botões, rótulos e elementos. Nomeie os componentes (ex: `btnAction` e `lblWelcome`).
4. Clique com o botão direito no Formulário e selecione **Export to Python**.
5. Salve o arquivo sobrepondo os arquivos `MainForm.py` e `MainForm.pydfm` gerados na raiz desta pasta!
6. Se você adicionar novos botões ou controles, lembre-se de declará-los com `None` no construtor `__init__` do `main.py` e associar os eventos da mesma forma que os exemplos incluídos.
"""
    with open(instructions_path, "w", encoding="utf-8") as f:
        f.write(instructions_content)

def write_fmx_template(dest_path, project_name):
    """
    Escreve os arquivos base do esqueleto para projetos FMX (FireMonkey).
    """
    # 1. Criar main.py
    main_py_path = os.path.join(dest_path, "main.py")
    main_py_content = f"""import os
from delphifmx import *

class MainForm(Form):
    def __init__(self, owner):
        super().__init__(owner)
        # Declare as variáveis de componentes criadas na IDE como None
        self.lblWelcome = None
        self.btnAction = None
        
        # Carrega as propriedades visuais do arquivo .pyfmx gerado pelo Expert
        pyfmx_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MainForm.pyfmx")
        self.LoadProps(pyfmx_file)
        
        # Inscreva-se nos eventos programados em Python
        self.btnAction.OnClick = self.do_action_click

    def do_action_click(self, sender):
        self.lblWelcome.Text = "Ação disparada com sucesso em Python (FMX)!"
        self.lblWelcome.TextSettings.Font.Size = 16

def main():
    Application.Initialize()
    Application.Title = "{project_name}"
    
    # Instancia o formulário principal
    Application.MainForm = MainForm(Application)
    Application.MainForm.Show()
    
    # Executa o loop principal da aplicação
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
"""
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(main_py_content)

    # 2. Criar MainForm.pyfmx de teste (FMX legível em texto contendo a estrutura básica)
    pyfmx_path = os.path.join(dest_path, "MainForm.pyfmx")
    pyfmx_content = """object MainForm: TMainForm
  Left = 0
  Top = 0
  Caption = 'Delphi FMX for Python MainForm'
  ClientHeight = 240
  ClientWidth = 460
  Fill.Kind = Solid
  FormFactor.Width = 320
  FormFactor.Height = 480
  FormFactor.Devices = [Desktop]
  DesignerMasterStyle = 0
  object lblWelcome: TLabel
    Position.X = 40.000000000000000000
    Position.Y = 50.000000000000000000
    Size.Width = 380.000000000000000000
    Size.Height = 30.000000000000000000
    Size.PlatformDefault = False
    TextSettings.Font.Size = 14.000000000000000000
    TextSettings.HorzAlign = Center
    Text = 'Bem-vindo ao DelphiFMX4Python!'
  end
  object btnAction: TButton
    Position.X = 160.000000000000000000
    Position.Y = 120.000000000000000000
    Size.Width = 140.000000000000000000
    Size.Height = 35.000000000000000000
    Size.PlatformDefault = False
    Text = 'Disparar Ação'
    TabOrder = 0
  end
end
"""
    with open(pyfmx_path, "w", encoding="utf-8") as f:
        f.write(pyfmx_content)

    # 3. Criar arquivo INSTRUCTIONS.md
    instructions_path = os.path.join(dest_path, "INSTRUCTIONS.md")
    instructions_content = f"""# Instruções do Projeto FMX - {project_name}

Seu ambiente virtual e projeto inicial multiplataforma estão configurados!

## Como Executar o Projeto de Teste
1. Ative o ambiente virtual no PowerShell:
   ```powershell
   .\\venv\\Scripts\\Activate.ps1
   ```
2. Execute o script principal:
   ```powershell
   python main.py
   ```

## Como Integrar com a IDE do Delphi (Multiplataforma)
1. Instale o Add-in do FMX para Python na IDE do Delphi (copie da pasta `experts` do repositório oficial do DelphiFMX4Python).
2. Abra a IDE do Delphi, vá em **File > New > Multi-Device Application**.
3. Desenhe sua tela arrastando botões, rótulos e elementos. Nomeie os componentes (ex: `btnAction` e `lblWelcome`).
4. Clique com o botão direito no Formulário e selecione **Export to Python**.
5. Salve o arquivo sobrepondo os arquivos `MainForm.py` e `MainForm.pyfmx` gerados na raiz desta pasta!
"""
    with open(instructions_path, "w", encoding="utf-8") as f:
        f.write(instructions_content)

def main():
    parser = argparse.ArgumentParser(description="Wizard para inicializar projetos Delphi + Python")
    parser.add_argument("command", choices=["init"], help="Comando para executar")
    parser.add_argument("--name", required=True, help="Nome do projeto a ser criado")
    parser.add_argument("--framework", required=True, choices=["vcl", "fmx"], help="Framework visual: vcl (Windows) ou fmx (Multiplataforma)")
    parser.add_argument("--path", required=True, help="Caminho completo de destino para criar a pasta do projeto")
    
    args = parser.parse_args()
    
    if args.command == "init":
        dest_path = os.path.abspath(args.path)
        project_name = args.name
        framework = args.framework
        
        print(f"[Wizard] Inicializando novo projeto Delphi + Python...")
        print(f"[Wizard] Nome: {project_name}")
        print(f"[Wizard] Framework: {framework.upper()}")
        print(f"[Wizard] Destino: {dest_path}")
        
        # Cria a pasta de destino
        os.makedirs(dest_path, exist_ok=True)
        
        # Encontra a melhor versão do Python compatível
        python_exe, py_ver_arg = find_best_python()
        
        # Cria o ambiente virtual
        create_venv(python_exe, py_ver_arg, dest_path)
        
        # Instala as bibliotecas de dependência
        install_dependencies(dest_path, framework)
        
        # Escreve os templates de código
        if framework == "vcl":
            write_vcl_template(dest_path, project_name)
        else:
            write_fmx_template(dest_path, project_name)
            
        print("\n" + "="*50)
        print(f"[Sucesso] Projeto '{project_name}' inicializado com sucesso!")
        print(f"Caminho: {dest_path}")
        print(f"Abra o arquivo 'INSTRUCTIONS.md' na pasta de destino para começar a usar!")
        print("="*50 + "\n")

if __name__ == '__main__':
    main()
