import os
import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# --- CONFIGURAÇÃO DO POSTGRESQL ---
DB_CONFIG = {
    "dbname": os.environ.get("PGDATABASE", "sistema_estoque"),
    "user": os.environ.get("PGUSER", "postgres"),
    "password": os.environ.get("PGPASSWORD", "SUA SENHA AQUI"),
    "host": os.environ.get("PGHOST", "localhost"),
    "port": os.environ.get("PGPORT", "5432"),
    "client_encoding": os.environ.get("PGCLIENTENCODING", "WIN1252"),
}

CATEGORIAS_PADRAO = [
    "Geral",
    "Eletrônicos",
    "Periféricos",
    "Escritório",
    "Hardware",
    "Acessórios",
    "Robótica",
    "Outros",
]

produto_em_edicao_id = None


def conectar():
    return psycopg2.connect(**DB_CONFIG)


def inicializar_banco():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS produtos (
                        id SERIAL PRIMARY KEY,
                        nome TEXT NOT NULL,
                        categoria TEXT NOT NULL DEFAULT 'Geral',
                        quantidade INTEGER NOT NULL DEFAULT 0,
                        preco NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
                        codigo TEXT NOT NULL
                    );
                    """
                )
                cur.execute(
                    """
                    ALTER TABLE produtos
                    ADD COLUMN IF NOT EXISTS categoria TEXT NOT NULL DEFAULT 'Geral';
                    """
                )
            conn.commit()
    except Exception as e:
        messagebox.showerror(
            "Erro de Conexão (PostgreSQL)",
            f"Não foi possível conectar ou inicializar o banco de dados:\n{e}\n\n"
            "Verifique se o serviço do PostgreSQL está rodando e se o banco 'sistema_estoque' existe.",
        )


def parse_preco(valor_str):
    limpo = valor_str.strip().replace("R$", "").replace(" ", "")
    if "," in limpo and "." in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    elif "," in limpo:
        limpo = limpo.replace(",", ".")
    return float(limpo)


def atualizar_categorias():
    categorias_atuais = list(CATEGORIAS_PADRAO)
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT categoria
                    FROM produtos
                    WHERE categoria IS NOT NULL AND TRIM(categoria) <> ''
                    ORDER BY categoria ASC;
                    """
                )
                do_banco = [row[0] for row in cur.fetchall()]
    except Exception:
        do_banco = []

    combinadas = []
    for cat in categorias_atuais + do_banco:
        if cat not in combinadas:
            combinadas.append(cat)

    combo_categoria["values"] = combinadas


def limpar_campos():
    global produto_em_edicao_id
    entry_nome.delete(0, tk.END)
    combo_categoria.set("Geral")
    entry_qtd.delete(0, tk.END)
    entry_preco.delete(0, tk.END)
    entry_codigo.delete(0, tk.END)
    produto_em_edicao_id = None
    btn_salvar_edicao.config(state="disabled")
    btn_cadastrar.config(state="normal")


def cadastrar_produto():
    nome = entry_nome.get().strip()
    categoria = combo_categoria.get().strip() or "Geral"
    qtd_str = entry_qtd.get().strip()
    preco_str = entry_preco.get().strip()
    codigo = entry_codigo.get().strip()

    if not nome or not qtd_str or not preco_str or not codigo:
        messagebox.showwarning(
            "Campos obrigatórios",
            "Preencha Nome, Categoria, Quantidade, Preço e Código.",
        )
        return

    try:
        quantidade = int(qtd_str)
        preco = parse_preco(preco_str)
        if quantidade < 0 or preco < 0:
            raise ValueError("Valores negativos não são permitidos.")
    except ValueError as e:
        messagebox.showerror("Valor inválido", f"Verifique Quantidade e Preço.\n{e}")
        return

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO produtos (nome, categoria, quantidade, preco, codigo)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (nome, categoria, quantidade, round(preco, 2), codigo),
                )
            conn.commit()
        limpar_campos()
        atualizar_tela()
        messagebox.showinfo("Sucesso", "Produto cadastrado no PostgreSQL!")
    except Exception as e:
        messagebox.showerror("Erro ao cadastrar", str(e))


def carregar_para_editar():
    global produto_em_edicao_id
    selecionado = tree.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um produto na tabela para editar.")
        return

    valores = tree.item(selecionado[0], "values")
    produto_em_edicao_id = int(valores[0])

    entry_nome.delete(0, tk.END)
    entry_nome.insert(0, valores[1])

    combo_categoria.set(valores[2])

    entry_qtd.delete(0, tk.END)
    entry_qtd.insert(0, valores[3])

    preco_num = str(valores[4]).replace("R$", "").strip()
    entry_preco.delete(0, tk.END)
    entry_preco.insert(0, preco_num)

    entry_codigo.delete(0, tk.END)
    entry_codigo.insert(0, valores[5])

    btn_salvar_edicao.config(state="normal")
    btn_cadastrar.config(state="disabled")


def salvar_edicao():
    global produto_em_edicao_id
    if produto_em_edicao_id is None:
        messagebox.showwarning("Atenção", "Nenhum produto carregado para edição.")
        return

    nome = entry_nome.get().strip()
    categoria = combo_categoria.get().strip() or "Geral"
    qtd_str = entry_qtd.get().strip()
    preco_str = entry_preco.get().strip()
    codigo = entry_codigo.get().strip()

    if not nome or not qtd_str or not preco_str or not codigo:
        messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
        return

    try:
        quantidade = int(qtd_str)
        preco = parse_preco(preco_str)
        if quantidade < 0 or preco < 0:
            raise ValueError("Valores negativos não são permitidos.")
    except ValueError as e:
        messagebox.showerror("Valor inválido", f"Verifique Quantidade e Preço.\n{e}")
        return

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE produtos
                    SET nome = %s, categoria = %s, quantidade = %s, preco = %s, codigo = %s
                    WHERE id = %s;
                    """,
                    (nome, categoria, quantidade, round(preco, 2), codigo, produto_em_edicao_id),
                )
            conn.commit()
        limpar_campos()
        atualizar_tela()
        messagebox.showinfo("Sucesso", "Produto atualizado!")
    except Exception as e:
        messagebox.showerror("Erro ao salvar edição", str(e))


def movimentar_unidades(delta):
    selecionado = tree.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um produto na tabela.")
        return

    valores = tree.item(selecionado[0], "values")
    prod_id = int(valores[0])
    qtd_atual = int(valores[3])
    nova_qtd = qtd_atual + delta

    if nova_qtd < 0:
        messagebox.showwarning("Estoque insuficiente", "A quantidade em estoque não pode ficar negativa.")
        return

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE produtos SET quantidade = %s WHERE id = %s;",
                    (nova_qtd, prod_id),
                )
            conn.commit()
        atualizar_tela()
    except Exception as e:
        messagebox.showerror("Erro na movimentação", str(e))


def excluir_produto():
    selecionado = tree.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um produto para excluir.")
        return

    valores = tree.item(selecionado[0], "values")
    prod_id = int(valores[0])
    nome = valores[1]

    confirmar = messagebox.askyesno("Confirmar exclusão", f"Deseja excluir '{nome}' (ID {prod_id})?")
    if not confirmar:
        return

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM produtos WHERE id = %s;", (prod_id,))
            conn.commit()
        if produto_em_edicao_id == prod_id:
            limpar_campos()
        atualizar_tela()
    except Exception as e:
        messagebox.showerror("Erro ao excluir", str(e))


def buscar_produtos(filtro=""):
    for item in tree.get_children():
        tree.delete(item)

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                if filtro.strip():
                    termo = f"%{filtro.strip()}%"
                    cur.execute(
                        """
                        SELECT id, nome, categoria, quantidade, preco, codigo
                        FROM produtos
                        WHERE nome ILIKE %s OR categoria ILIKE %s OR codigo ILIKE %s
                        ORDER BY id ASC;
                        """,
                        (termo, termo, termo),
                    )
                else:
                    cur.execute(
                        """
                        SELECT id, nome, categoria, quantidade, preco, codigo
                        FROM produtos
                        ORDER BY id ASC;
                        """
                    )
                linhas = cur.fetchall()

        for row in linhas:
            preco_float = float(row[4])
            tree.insert(
                "",
                tk.END,
                values=(row[0], row[1], row[2], row[3], f"{preco_float:.2f}", row[5]),
            )
    except Exception as e:
        messagebox.showerror("Erro na consulta", str(e))


def atualizar_dashboard_e_grafico():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT nome, quantidade, preco FROM produtos ORDER BY id ASC;")
                dados = cur.fetchall()
    except Exception:
        dados = []

    total_produtos = len(dados)
    total_itens = sum(int(d[1]) for d in dados)
    valor_total = sum(int(d[1]) * float(d[2]) for d in dados)

    lbl_produtos.config(text=f"Produtos: {total_produtos}")
    lbl_itens.config(text=f"Itens em Estoque: {total_itens}")
    lbl_valor_total.config(text=f"Valor Total: R$ {valor_total:.2f}")

    ax.clear()
    ax.set_title("Quantidade em Estoque por Produto", fontsize=10, fontweight="bold")

    if not dados:
        ax.text(0.5, 0.5, "Sem dados no estoque", ha="center", va="center", transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    else:
        nomes = [d[0][:14] for d in dados]
        quantidades = [int(d[1]) for d in dados]
        ax.bar(nomes, quantidades, color="#1d4ed8")
        ax.set_ylabel("Qtd")
        ax.tick_params(axis="x", rotation=20, labelsize=8)

    fig.tight_layout()
    canvas.draw()


def atualizar_tela():
    filtro_atual = entry_busca.get()
    atualizar_categorias()
    buscar_produtos(filtro_atual)
    atualizar_dashboard_e_grafico()


# --- INTERFACE GRÁFICA ---
root = tk.Tk()
root.title("Sistema de Gestão de Estoque com PostgreSQL")
root.geometry("1280x780")

# Banner superior
banner = tk.Label(
    root,
    text="Sistema de Gestão de Estoque (PostgreSQL)",
    bg="#0000ff",
    fg="white",
    font=("Arial", 14, "bold"),
    pady=6,
)
banner.pack(fill="x")

# Resumo superior
resumo_frame = tk.Frame(root, bg="#e5e7eb", pady=5)
resumo_frame.pack(fill="x", padx=10, pady=(6, 2))

lbl_produtos = tk.Label(resumo_frame, text="Produtos: 0", bg="#e5e7eb", font=("Arial", 10, "bold"))
lbl_produtos.pack(side="left", expand=True)

lbl_itens = tk.Label(resumo_frame, text="Itens em Estoque: 0", bg="#e5e7eb", font=("Arial", 10, "bold"))
lbl_itens.pack(side="left", expand=True)

lbl_valor_total = tk.Label(
    resumo_frame, text="Valor Total: R$ 0.00", bg="#e5e7eb", fg="#047857", font=("Arial", 10, "bold")
)
lbl_valor_total.pack(side="left", expand=True)

# Gráfico Matplotlib
fig = Figure(figsize=(5.5, 2.0), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=4)

# Formulário de cadastro / edição
form_frame = tk.Frame(root)
form_frame.pack(fill="x", padx=20, pady=4)
form_frame.columnconfigure(1, weight=1)
form_frame.columnconfigure(3, weight=1)

tk.Label(form_frame, text="Nome:", bg="#86efac", width=16, anchor="w", padx=4).grid(
    row=0, column=0, padx=(0, 6), pady=3, sticky="w"
)
entry_nome = tk.Entry(form_frame)
entry_nome.grid(row=0, column=1, padx=(0, 16), pady=3, sticky="ew")

tk.Label(form_frame, text="Categoria:", bg="#86efac", width=16, anchor="w", padx=4).grid(
    row=0, column=2, padx=(0, 6), pady=3, sticky="w"
)
combo_categoria = ttk.Combobox(form_frame, values=CATEGORIAS_PADRAO)
combo_categoria.set("Geral")
combo_categoria.grid(row=0, column=3, pady=3, sticky="ew")

tk.Label(form_frame, text="Quantidade:", bg="#86efac", width=16, anchor="w", padx=4).grid(
    row=1, column=0, padx=(0, 6), pady=3, sticky="w"
)
entry_qtd = tk.Entry(form_frame)
entry_qtd.grid(row=1, column=1, padx=(0, 16), pady=3, sticky="ew")

tk.Label(form_frame, text="Preço (R$):", bg="#86efac", width=16, anchor="w", padx=4).grid(
    row=1, column=2, padx=(0, 6), pady=3, sticky="w"
)
entry_preco = tk.Entry(form_frame)
entry_preco.grid(row=1, column=3, pady=3, sticky="ew")

tk.Label(form_frame, text="Código do produto:", bg="#86efac", width=16, anchor="w", padx=4).grid(
    row=2, column=0, padx=(0, 6), pady=3, sticky="w"
)
entry_codigo = tk.Entry(form_frame)
entry_codigo.grid(row=2, column=1, padx=(0, 16), pady=3, sticky="ew")

# Botões principais
acoes_frame = tk.Frame(root)
acoes_frame.pack(fill="x", padx=20, pady=4)
acoes_frame.columnconfigure(0, weight=1)
acoes_frame.columnconfigure(1, weight=1)

btn_cadastrar = tk.Button(
    acoes_frame,
    text="Cadastrar Produto",
    bg="#008000",
    fg="white",
    font=("Arial", 10, "bold"),
    command=cadastrar_produto,
)
btn_cadastrar.grid(row=0, column=0, padx=(0, 6), sticky="ew")

btn_salvar_edicao = tk.Button(
    acoes_frame,
    text="Salvar Edição",
    bg="#00008b",
    fg="white",
    font=("Arial", 10, "bold"),
    state="disabled",
    command=salvar_edicao,
)
btn_salvar_edicao.grid(row=0, column=1, padx=(6, 0), sticky="ew")

# Barra de pesquisa
busca_frame = tk.Frame(root)
busca_frame.pack(fill="x", padx=20, pady=4)
busca_frame.columnconfigure(1, weight=1)
busca_frame.columnconfigure(3, weight=2)

tk.Label(busca_frame, text="Pesquisar (Nome/Cat/Cód):", bg="#fef08a", padx=4).grid(
    row=0, column=0, padx=(0, 6), sticky="w"
)
entry_busca = tk.Entry(busca_frame)
entry_busca.grid(row=0, column=1, padx=(0, 8), sticky="ew")

tk.Button(
    busca_frame,
    text="Buscar",
    bg="#f59e0b",
    fg="black",
    font=("Arial", 9, "bold"),
    width=14,
    command=lambda: buscar_produtos(entry_busca.get()),
).grid(row=0, column=2, padx=(0, 8))

tk.Button(
    busca_frame,
    text="Limpar",
    bg="#d1d5db",
    fg="black",
    font=("Arial", 9, "bold"),
    command=lambda: (entry_busca.delete(0, tk.END), limpar_campos(), atualizar_tela()),
).grid(row=0, column=3, sticky="ew")

# Tabela
tabela_frame = tk.Frame(root)
tabela_frame.pack(fill="both", expand=True, padx=20, pady=6)

colunas = ("ID", "Nome", "Categoria", "Quantidade", "Preço", "Código")
tree = ttk.Treeview(tabela_frame, columns=colunas, show="headings", height=7)

larguras = {
    "ID": 70,
    "Nome": 310,
    "Categoria": 180,
    "Quantidade": 180,
    "Preço": 200,
    "Código": 220,
}
for col in colunas:
    tree.heading(col, text=col)
    tree.column(col, width=larguras[col], anchor="center")

scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Botões inferiores
rodape_frame = tk.Frame(root)
rodape_frame.pack(fill="x", padx=20, pady=(2, 12))
rodape_frame.columnconfigure(0, weight=1)
rodape_frame.columnconfigure(1, weight=1)

tk.Button(
    rodape_frame,
    text="+ Adicionar Unidades",
    bg="#0f766e",
    fg="white",
    font=("Arial", 10, "bold"),
    command=lambda: movimentar_unidades(1),
).grid(row=0, column=0, padx=(0, 6), pady=3, sticky="ew")

tk.Button(
    rodape_frame,
    text="- Retirar Unidades",
    bg="#92400e",
    fg="white",
    font=("Arial", 10, "bold"),
    command=lambda: movimentar_unidades(-1),
).grid(row=0, column=1, padx=(6, 0), pady=3, sticky="ew")

tk.Button(
    rodape_frame,
    text="Carregar para Editar",
    bg="#6b21a8",
    fg="white",
    font=("Arial", 10, "bold"),
    command=carregar_para_editar,
).grid(row=1, column=0, padx=(0, 6), pady=3, sticky="ew")

tk.Button(
    rodape_frame,
    text="Excluir Produto Selecionado",
    bg="#dc2626",
    fg="white",
    font=("Arial", 10, "bold"),
    command=excluir_produto,
).grid(row=1, column=1, padx=(6, 0), pady=3, sticky="ew")

inicializar_banco()
atualizar_tela()
root.mainloop()