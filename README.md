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
