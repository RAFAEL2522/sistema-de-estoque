📦 Sistema de Gestão de Estoque (Python + PostgreSQL)

Aplicação desktop completa para controle e gestão de inventário, desenvolvida em **Python** com interface gráfica em **Tkinter**, visualização de dados integrada com **Matplotlib** e persistência relacional em **PostgreSQL**. O projeto representa a evolução de uma versão inicial local em SQLite para uma arquitetura cliente-servidor mais robusta e escalável.

---

 ✨ Funcionalidades

- CRUD Completo de Produtos: Cadastro, edição, atualização de quantidades (entrada/saída) e exclusão de registros.
- **Categorização Dinâmica:** Seleção rápida por `Combobox` com categorias padrão (`Geral`, `Eletrônicos`, `Periféricos`, `Escritório`, `Hardware`, `Acessórios`, `Robótica`, `Outros`) e suporte à criação de novas categorias, atualizando automaticamente a lista a partir dos dados salvos no banco.
- **Busca e Filtragem em Tempo Real:** Pesquisa rápida para localizar itens no estoque por nome ou categoria.
- **Dashboard Analítico:** Indicadores resumidos do inventário acompanhados de gráfico de barras gerado via Matplotlib diretamente na janela principal.
- **Segurança nas Credenciais:** Leitura de parâmetros de conexão via variáveis de ambiente (`os.environ`), evitando senhas hardcoded no código-fonte.
- **Empacotamento Desktop:** Estrutura preparada para compilação em executável independente (`.exe`) no Windows com PyInstaller.

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia | Finalidade |
| **Linguagem** | Python 3 | Lógica principal da aplicação |
| **Interface Gráfica** | `tkinter` / `ttk` | Janelas, formulários, tabelas (`Treeview`) e eventos |
| **Banco de Dados** | PostgreSQL + `psycopg2-binary` | Armazenamento relacional e consultas SQL |
| **Visualização** | `matplotlib` (`FigureCanvasTkAgg`) | Gráficos estatísticos embutidos na interface |
| **Build / Deploy** | PyInstaller | Geração de executável `.exe` para Windows |

---

## 📁 Estrutura do Repositório

```text
sistema-de-estoque/
├── sistema_de_estoque.py    # Código-fonte principal (interface, banco e gráficos)
├── sistema_de_estoque.spec  # Arquivo de configuração de build do PyInstaller
├── requirements.txt         # Lista de dependências externas do projeto
├── .gitignore               # Regras de exclusão (.venv, __pycache__, .env, build/, dist/, *.db)
└── README.md                # Documentação do projeto
🚀 Como Executar Localmente1. Pré-requisitosPython 3.10+ instaladoPostgreSQL instalado e com o serviço ativoUm banco de dados criado no PostgreSQL (ex.: sistema_estoque)Caso ainda não tenha criado o banco de dados, execute no psql ou no pgAdmin:SQLCREATE DATABASE sistema_estoque;
(A aplicação cria automaticamente as tabelas necessárias na primeira execução.)2. Clonar e Instalar DependênciasPowerShellgit clone [https://github.com/RAFAEL2522/sistema-de-estoque.git](https://github.com/RAFAEL2522/sistema-de-estoque.git)
cd sistema-de-estoque

# Criar e ativar o ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar pacotes necessários
pip install -r requirements.txt
3. Configurar Variáveis de AmbienteDefina as variáveis de conexão com o PostgreSQL no terminal antes de iniciar o programa:VariávelDescriçãoValor PadrãoPGDATABASENome do banco de dadossistema_estoquePGUSERUsuário do PostgreSQLpostgresPGPASSWORDSenha do usuário do banco(obrigatório definir)PGHOSTEndereço do servidorlocalhostPGPORTPorta de conexão5432PGCLIENTENCODINGCodificação do clienteWIN1252Exemplo no PowerShell:PowerShell$env:PGDATABASE="sistema_estoque"
$env:PGUSER="postgres"
$env:PGPASSWORD="sua_senha_postgres"
$env:PGHOST="localhost"
$env:PGPORT="5432"
4. Iniciar a AplicaçãoPowerShellpython sistema_de_estoque.py
📦 Gerando o Executável (.exe)Para empacotar a aplicação em um único arquivo executável no Windows (sem abrir janela de console):PowerShellpip install pyinstaller
pyinstaller --noconsole --onefile --collect-all matplotlib --name "SistemaEstoque" sistema_de_estoque.py
O arquivo SistemaEstoque.exe será gerado dentro da pasta dist/. Lembre-se de que as variáveis de ambiente do PostgreSQL precisam estar configuradas no sistema operacional para que o executável se conecte ao banco.
