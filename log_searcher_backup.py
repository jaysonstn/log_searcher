"""
Log Searcher - Busca palavras ou números em arquivos .log e .txt
"""

import os
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path


class LogSearcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Searcher")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        self.search_dir = tk.StringVar()
        self.search_term = tk.StringVar()
        self.case_sensitive = tk.BooleanVar(value=False)
        self.regex_mode = tk.BooleanVar(value=False)
        self.whole_word = tk.BooleanVar(value=False)
        self.include_subdirs = tk.BooleanVar(value=True)
        self.file_extensions = tk.StringVar(value=".log,.txt")

        self.results = []
        self.searching = False

        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e2e")
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4")
        style.configure("TCheckbutton", background="#1e1e2e", foreground="#cdd6f4")
        style.configure("TButton", background="#313244", foreground="#cdd6f4", borderwidth=0, relief="flat", padding=(12, 6))
        style.map("TButton", background=[("active", "#45475a")])
        style.configure("Search.TButton", background="#89b4fa", foreground="#1e1e2e", font=("Segoe UI", 10, "bold"))
        style.map("Search.TButton", background=[("active", "#74c7ec")])
        style.configure("TEntry", fieldbackground="#313244", foreground="#cdd6f4", insertcolor="#cdd6f4", borderwidth=0, relief="flat")
        style.configure("Treeview", background="#181825", foreground="#cdd6f4", fieldbackground="#181825", rowheight=24)
        style.configure("Treeview.Heading", background="#313244", foreground="#89b4fa", relief="flat", font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#313244")], foreground=[("selected", "#89b4fa")])
        style.configure("TScrollbar", background="#313244", troughcolor="#181825", borderwidth=0)
        style.configure("TLabelframe", background="#1e1e2e", foreground="#89b4fa")
        style.configure("TLabelframe.Label", background="#1e1e2e", foreground="#89b4fa", font=("Segoe UI", 9, "bold"))

        self.root.configure(bg="#1e1e2e")

        # ── Top bar ──────────────────────────────────────────────────────
        top = tk.Frame(self.root, bg="#181825", pady=14, padx=18)
        top.pack(fill="x")

        tk.Label(top, text="🔍 Log Searcher", font=("Segoe UI", 16, "bold"),
                 bg="#181825", fg="#89b4fa").pack(side="left")
        tk.Label(top, text="  busca em arquivos .log e .txt",
                 font=("Segoe UI", 10), bg="#181825", fg="#6c7086").pack(side="left", pady=4)

        # ── Main content ─────────────────────────────────────────────────
        main = tk.Frame(self.root, bg="#1e1e2e", padx=18, pady=14)
        main.pack(fill="both", expand=True)

        # Diretório
        dir_frame = tk.Frame(main, bg="#1e1e2e")
        dir_frame.pack(fill="x", pady=(0, 8))

        tk.Label(dir_frame, text="Diretório:", font=("Segoe UI", 9),
                 bg="#1e1e2e", fg="#a6adc8", width=10, anchor="w").pack(side="left")

        dir_entry = tk.Entry(dir_frame, textvariable=self.search_dir,
                             bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
                             relief="flat", font=("Segoe UI", 10), bd=6)
        dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ttk.Button(dir_frame, text="Escolher pasta", command=self._browse_dir).pack(side="left")

        # Termo de busca
        search_frame = tk.Frame(main, bg="#1e1e2e")
        search_frame.pack(fill="x", pady=(0, 10))

        tk.Label(search_frame, text="Buscar:", font=("Segoe UI", 9),
                 bg="#1e1e2e", fg="#a6adc8", width=10, anchor="w").pack(side="left")

        search_entry = tk.Entry(search_frame, textvariable=self.search_term,
                                bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
                                relief="flat", font=("Segoe UI", 10), bd=6)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        search_entry.bind("<Return>", lambda e: self._start_search())

        self.search_btn = ttk.Button(search_frame, text="▶  Buscar",
                                     style="Search.TButton", command=self._start_search)
        self.search_btn.pack(side="left")

        # Opções
        opt_frame = ttk.LabelFrame(main, text=" Opções ", padding=(12, 6))
        opt_frame.pack(fill="x", pady=(0, 12))

        opts_inner = tk.Frame(opt_frame, bg="#1e1e2e")
        opts_inner.pack(fill="x")

        ttk.Checkbutton(opts_inner, text="Maiúsc./minúsc.", variable=self.case_sensitive).pack(side="left", padx=(0, 16))
        ttk.Checkbutton(opts_inner, text="Palavra inteira", variable=self.whole_word).pack(side="left", padx=(0, 16))
        ttk.Checkbutton(opts_inner, text="Expressão regular (regex)", variable=self.regex_mode).pack(side="left", padx=(0, 16))
        ttk.Checkbutton(opts_inner, text="Subpastas", variable=self.include_subdirs).pack(side="left", padx=(0, 20))

        tk.Label(opts_inner, text="Extensões:", bg="#1e1e2e", fg="#a6adc8",
                 font=("Segoe UI", 9)).pack(side="left")
        tk.Entry(opts_inner, textvariable=self.file_extensions, width=18,
                 bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
                 relief="flat", font=("Segoe UI", 9), bd=4).pack(side="left", padx=(4, 0))

        # Barra de status
        status_bar = tk.Frame(main, bg="#1e1e2e")
        status_bar.pack(fill="x", pady=(0, 6))

        self.status_var = tk.StringVar(value="Pronto.")
        tk.Label(status_bar, textvariable=self.status_var, font=("Segoe UI", 9),
                 bg="#1e1e2e", fg="#6c7086", anchor="w").pack(side="left")

        self.result_count_var = tk.StringVar(value="")
        tk.Label(status_bar, textvariable=self.result_count_var, font=("Segoe UI", 9, "bold"),
                 bg="#1e1e2e", fg="#a6e3a1", anchor="e").pack(side="right")

        # Barra de progresso
        self.progress = ttk.Progressbar(main, mode="indeterminate", length=200)

        # Tabela de resultados
        tree_frame = tk.Frame(main, bg="#1e1e2e")
        tree_frame.pack(fill="both", expand=True)

        columns = ("arquivo", "linha", "conteudo")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("arquivo", text="Arquivo")
        self.tree.heading("linha", text="Linha")
        self.tree.heading("conteudo", text="Conteúdo")
        self.tree.column("arquivo", width=300, minwidth=160)
        self.tree.column("linha", width=70, minwidth=50, anchor="center")
        self.tree.column("conteudo", width=600, minwidth=200)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Alternância de cor nas linhas
        self.tree.tag_configure("odd", background="#1e1e2e")
        self.tree.tag_configure("even", background="#181825")
        self.tree.tag_configure("match", foreground="#f38ba8")

        self.tree.bind("<Double-1>", self._open_file_at_line)

        # Botões inferiores
        btn_frame = tk.Frame(main, bg="#1e1e2e", pady=8)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="Exportar .txt", command=self._export_txt).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Exportar .csv", command=self._export_csv).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Limpar", command=self._clear_results).pack(side="left")

        tk.Label(btn_frame, text="Duplo clique numa linha para abrir o arquivo",
                 font=("Segoe UI", 8), bg="#1e1e2e", fg="#45475a").pack(side="right")

    # ── Helpers ───────────────────────────────────────────────────────────

    def _browse_dir(self):
        d = filedialog.askdirectory(title="Selecionar diretório")
        if d:
            self.search_dir.set(d)

    def _clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.results.clear()
        self.result_count_var.set("")
        self.status_var.set("Pronto.")

    def _start_search(self):
        if self.searching:
            return
        term = self.search_term.get().strip()
        directory = self.search_dir.get().strip()

        if not term:
            messagebox.showwarning("Atenção", "Digite um termo para buscar.")
            return
        if not directory or not os.path.isdir(directory):
            messagebox.showwarning("Atenção", "Selecione um diretório válido.")
            return

        self._clear_results()
        self.searching = True
        self.search_btn.configure(state="disabled")
        self.progress.pack(fill="x", pady=(0, 4))
        self.progress.start(10)
        self.status_var.set("Buscando…")

        t = threading.Thread(target=self._search_worker, args=(term, directory), daemon=True)
        t.start()

    def _search_worker(self, term, directory):
        extensions = [e.strip().lower() for e in self.file_extensions.get().split(",") if e.strip()]
        subdirs = self.include_subdirs.get()
        case = self.case_sensitive.get()
        whole = self.whole_word.get()
        use_regex = self.regex_mode.get()

        # Monta o padrão
        try:
            if use_regex:
                flags = 0 if case else re.IGNORECASE
                pattern = re.compile(term, flags)
            else:
                escaped = re.escape(term)
                if whole:
                    escaped = r"\b" + escaped + r"\b"
                flags = 0 if case else re.IGNORECASE
                pattern = re.compile(escaped, flags)
        except re.error as e:
            self.root.after(0, lambda: messagebox.showerror("Regex inválido", str(e)))
            self.root.after(0, self._search_done)
            return

        # Coleta arquivos
        files = []
        if subdirs:
            for root_dir, _, fnames in os.walk(directory):
                for f in fnames:
                    if any(f.lower().endswith(ext) for ext in extensions):
                        files.append(os.path.join(root_dir, f))
        else:
            for f in os.listdir(directory):
                if any(f.lower().endswith(ext) for ext in extensions):
                    full = os.path.join(directory, f)
                    if os.path.isfile(full):
                        files.append(full)

        results = []
        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
                    for lineno, line in enumerate(fh, 1):
                        if pattern.search(line):
                            results.append((filepath, lineno, line.rstrip()))
            except (PermissionError, OSError):
                pass

        self.results = results
        self.root.after(0, self._populate_results)

    def _populate_results(self):
        self.tree.delete(*self.tree.get_children())
        prev_file = None
        color_idx = 0

        for i, (filepath, lineno, content) in enumerate(self.results):
            if filepath != prev_file:
                color_idx = (color_idx + 1) % 2
                prev_file = filepath
            tag = "odd" if color_idx == 0 else "even"
            short_path = filepath
            # mostra caminho relativo ao diretório de busca
            base = self.search_dir.get()
            try:
                short_path = os.path.relpath(filepath, base)
            except ValueError:
                pass
            self.tree.insert("", "end", values=(short_path, lineno, content), tags=(tag,))

        count = len(self.results)
        self.result_count_var.set(f"{count} ocorrência{'s' if count != 1 else ''} encontrada{'s' if count != 1 else ''}")
        self.status_var.set(f"Busca concluída em {len(set(r[0] for r in self.results))} arquivo(s).")
        self._search_done()

    def _search_done(self):
        self.searching = False
        self.progress.stop()
        self.progress.pack_forget()
        self.search_btn.configure(state="normal")

    def _open_file_at_line(self, event):
        item = self.tree.focus()
        if not item:
            return
        values = self.tree.item(item, "values")
        if not values:
            return
        rel_path, lineno, _ = values
        base = self.search_dir.get()
        full_path = os.path.join(base, rel_path) if not os.path.isabs(rel_path) else rel_path

        if not os.path.isfile(full_path):
            messagebox.showerror("Erro", f"Arquivo não encontrado:\n{full_path}")
            return

        # Abre com o editor padrão do sistema
        import subprocess, sys
        try:
            if sys.platform.startswith("win"):
                os.startfile(full_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", full_path])
            else:
                subprocess.Popen(["xdg-open", full_path])
        except Exception as e:
            messagebox.showerror("Erro ao abrir", str(e))

    def _export_txt(self):
        if not self.results:
            messagebox.showinfo("Exportar", "Nenhum resultado para exportar.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
            title="Salvar como…"
        )
        if not path:
            return
        term = self.search_term.get()
        base = self.search_dir.get()
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Log Searcher — Exportação\n")
            f.write(f"Termo: {term}\n")
            f.write(f"Diretório: {base}\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total de ocorrências: {len(self.results)}\n")
            f.write("=" * 70 + "\n\n")
            for filepath, lineno, content in self.results:
                try:
                    rel = os.path.relpath(filepath, base)
                except ValueError:
                    rel = filepath
                f.write(f"[{rel}] Linha {lineno}:\n{content}\n\n")
        messagebox.showinfo("Exportado", f"Salvo em:\n{path}")

    def _export_csv(self):
        if not self.results:
            messagebox.showinfo("Exportar", "Nenhum resultado para exportar.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Salvar como…"
        )
        if not path:
            return
        import csv
        base = self.search_dir.get()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Arquivo", "Linha", "Conteúdo"])
            for filepath, lineno, content in self.results:
                try:
                    rel = os.path.relpath(filepath, base)
                except ValueError:
                    rel = filepath
                writer.writerow([rel, lineno, content])
        messagebox.showinfo("Exportado", f"Salvo em:\n{path}")


def main():
    root = tk.Tk()
    app = LogSearcher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
