import os
import shutil
import sys

def get_skills_dir():
    """
    Retorna o diretório de dados padrão para as Skills do assistente Antigravity no Windows.
    """
    user_profile = os.environ.get("USERPROFILE")
    if not user_profile:
        print("[Erro] Variável de ambiente %USERPROFILE% não encontrada.")
        sys.exit(1)
        
    skills_dir = os.path.join(user_profile, ".gemini", "antigravity", "skills")
    return skills_dir

def install():
    print("="*60)
    print("  Instalador da Skill Delphi for Python Wizard para Antigravity")
    print("="*60)
    
    # 1. Localiza a pasta de origem (onde este script está rodando)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_skill_dir = os.path.join(current_dir, "delphi-for-python-wizard")
    
    if not os.path.exists(source_skill_dir):
        print(f"[Erro] Diretório da Skill de origem não encontrado em: {source_skill_dir}")
        print("Certifique-se de que está rodando o script na raiz do repositório clonado.")
        sys.exit(1)
        
    # 2. Localiza a pasta de destino das Skills da IA
    target_skills_base = get_skills_dir()
    target_skill_dir = os.path.join(target_skills_base, "delphi-for-python-wizard")
    
    print(f"[Info] Pasta de Skills da IA detectada: {target_skills_base}")
    print(f"[Info] Pasta de destino da Skill: {target_skill_dir}")
    
    # Cria a pasta de destino base se ela não existir
    os.makedirs(target_skills_base, exist_ok=True)
    
    # 3. Executa a cópia
    if os.path.exists(target_skill_dir):
        print("[Aviso] A Skill já estava instalada anteriormente. Atualizando arquivos...")
        try:
            shutil.rmtree(target_skill_dir)
        except Exception as e:
            print(f"[Erro] Falha ao remover a instalação antiga: {e}")
            print("Por favor, feche qualquer editor ou terminal que possa estar bloqueando a pasta e tente novamente.")
            sys.exit(1)
            
    try:
        shutil.copytree(source_skill_dir, target_skill_dir)
        print("\n" + "="*50)
        print("[Sucesso] A Skill 'delphi-for-python-wizard' foi instalada com sucesso!")
        print("O seu assistente de IA agora possui os superpoderes para criar novos projetos!")
        print("="*50 + "\n")
    except Exception as e:
        print(f"[Erro] Falha ao copiar a Skill para a pasta de dados da IA: {e}")
        sys.exit(1)

if __name__ == '__main__':
    install()
