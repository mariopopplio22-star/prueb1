import tkinter as tk
from tkinter import ttk, messagebox

class EliminatoriasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Eliminatorias Sudamericanas")
        self.root.geometry("1150x650")
        self.root.configure(bg="#1e1e2f")

        self.teams = []
        self.results = {}
        self.fixture = []
        self.current_jornada = 1

        self.num_classify = 4
        self.num_repechage = 1

        # Evento global para quitar focus (evita barrita activa en los Entry)
        self.root.bind("<Button-1>", self.remove_focus)

        self.setup_ui()

    def setup_ui(self):
        # Entrada de equipos
        frame_top = tk.Frame(self.root, bg="#1e1e2f")
        frame_top.pack(pady=10)

        tk.Label(frame_top, text="Nombres de equipos (separados por coma):",
                 fg="white", bg="#1e1e2f", font=("Arial", 12, "bold")).pack(side="left", padx=5)

        self.entry_teams = tk.Entry(frame_top, width=60, justify="center",
                                    font=("Arial", 11))
        self.entry_teams.pack(side="left", padx=5)

        tk.Button(frame_top, text="Cargar equipos", command=self.load_teams,
                  bg="#007acc", fg="white", font=("Arial", 11, "bold")).pack(side="left", padx=5)

        # Estilo para tabla con retículas
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                        background="#2e2e40",
                        foreground="white",
                        rowheight=28,
                        fieldbackground="#2e2e40",
                        bordercolor="#888",
                        borderwidth=1,
                        relief="ridge",
                        font=("Arial", 11))
        style.map("Treeview", background=[("selected", "#444")])

        style.configure("Treeview.Heading",
                        background="#444",
                        foreground="white",
                        relief="ridge",
                        borderwidth=1,
                        font=("Arial", 11, "bold"))

        # Tabla de posiciones
        self.table_frame = tk.Frame(self.root, bg="#1e1e2f")
        self.table_frame.pack(pady=10)

        columns = ("#", "Equipo", "PJ", "G", "E", "P", "GF", "GC", "DG", "Pts")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=12, style="Treeview")

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=80, anchor="center")

        self.tree.column("#", width=40, anchor="center")
        self.tree.column("Equipo", width=180, anchor="center")
        self.tree.column("Pts", width=120, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Área partidos
        self.match_frame = tk.Frame(self.root, bg="#2e2e40")
        self.match_frame.pack(pady=10, fill="x")

        self.match_labels = []
        self.score_entries = []

        # Botones navegación
        self.nav_frame = tk.Frame(self.root, bg="#1e1e2f")
        self.nav_frame.pack(pady=10)

        self.jornada_label = tk.Label(self.nav_frame, text="Jornada 1",
                                      fg="yellow", bg="#1e1e2f", font=("Arial", 14, "bold"))
        self.jornada_label.pack(side="left", padx=10)

        tk.Button(self.nav_frame, text="Anterior", command=self.prev_jornada,
                  bg="#444", fg="white", font=("Arial", 11, "bold")).pack(side="left", padx=5)

        tk.Button(self.nav_frame, text="Guardar", command=self.save_results,
                  bg="green", fg="white", font=("Arial", 11, "bold")).pack(side="left", padx=5)

        tk.Button(self.nav_frame, text="Siguiente", command=self.next_jornada,
                  bg="#444", fg="white", font=("Arial", 11, "bold")).pack(side="left", padx=5)

    def load_teams(self):
        names = self.entry_teams.get().split(",")
        self.teams = [n.strip() for n in names if n.strip()]

        if len(self.teams) % 2 != 0:
            messagebox.showerror("Error", "Debe ingresar un número PAR de equipos")
            return

        self.fixture = self.generate_balanced_fixture(self.teams)
        self.results = {j+1: {} for j in range(len(self.fixture))}
        self.current_jornada = 1
        self.show_matches()
        self.update_table()

    def generate_balanced_fixture(self, teams):
        n = len(teams)
        jornadas = []

        equipos = teams[:]
        if n % 2 != 0:
            equipos.append("DESCANSA")

        n = len(equipos)
        mitad = n // 2

        for i in range(n-1):
            jornada = []
            for j in range(mitad):
                t1 = equipos[j]
                t2 = equipos[n-1-j]
                if t1 != "DESCANSA" and t2 != "DESCANSA":
                    if i % 2 == 0:
                        jornada.append((t1, t2))
                    else:
                        jornada.append((t2, t1))
            equipos = [equipos[0]] + [equipos[-1]] + equipos[1:-1]
            jornadas.append(jornada)

        jornadas_vuelta = []
        for jornada in jornadas:
            jornadas_vuelta.append([(b, a) for (a, b) in jornada])

        return jornadas + jornadas_vuelta

    def show_matches(self):
        for widget in self.match_frame.winfo_children():
            widget.destroy()

        self.match_labels.clear()
        self.score_entries.clear()

        jornada = self.current_jornada
        partidos = self.fixture[jornada-1]

        tk.Label(self.match_frame, text=f"Partidos Jornada {jornada}",
                 fg="white", bg="#2e2e40", font=("Arial", 14, "bold")).pack(pady=5)

        for local, visitante in partidos:
            frame = tk.Frame(self.match_frame, bg="#2e2e40")
            frame.pack(pady=3)

            lbl_local = tk.Label(frame, text=f"{local}",
                                 fg="white", bg="#2e2e40", width=15, anchor="center", font=("Arial", 11, "bold"))
            lbl_local.pack(side="left", padx=5)

            score1 = tk.Entry(frame, width=4, justify="center", font=("Arial", 11, "bold"))
            score1.pack(side="left", padx=3)

            lbl_vs = tk.Label(frame, text="vs", fg="yellow", bg="#2e2e40", font=("Arial", 11, "bold"))
            lbl_vs.pack(side="left", padx=3)

            score2 = tk.Entry(frame, width=4, justify="center", font=("Arial", 11, "bold"))
            score2.pack(side="left", padx=3)

            lbl_visit = tk.Label(frame, text=f"{visitante}",
                                 fg="white", bg="#2e2e40", width=15, anchor="center", font=("Arial", 11, "bold"))
            lbl_visit.pack(side="left", padx=5)

            self.score_entries.append((score1, score2))

            if (local, visitante) in self.results[jornada]:
                g1, g2 = self.results[jornada][(local, visitante)]
                score1.insert(0, g1)
                score2.insert(0, g2)

    def save_results(self):
        jornada = self.current_jornada
        partidos = self.fixture[jornada-1]

        for i, (score1, score2) in enumerate(self.score_entries):
            try:
                g1 = int(score1.get())
                g2 = int(score2.get())
            except ValueError:
                continue
            local, visitante = partidos[i]
            self.results[jornada][(local, visitante)] = (g1, g2)

        self.update_table()

    def calculate_table(self):
        stats = {team: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "Pts": 0}
                 for team in self.teams}

        for jornada in self.results.values():
            for (t1, t2), (g1, g2) in jornada.items():
                stats[t1]["PJ"] += 1
                stats[t2]["PJ"] += 1
                stats[t1]["GF"] += g1
                stats[t1]["GC"] += g2
                stats[t2]["GF"] += g2
                stats[t2]["GC"] += g1

                if g1 > g2:
                    stats[t1]["G"] += 1
                    stats[t1]["Pts"] += 3
                    stats[t2]["P"] += 1
                elif g2 > g1:
                    stats[t2]["G"] += 1
                    stats[t2]["Pts"] += 3
                    stats[t1]["P"] += 1
                else:
                    stats[t1]["E"] += 1
                    stats[t2]["E"] += 1
                    stats[t1]["Pts"] += 1
                    stats[t2]["Pts"] += 1

        for t in stats:
            stats[t]["DG"] = stats[t]["GF"] - stats[t]["GC"]

        return sorted(stats.items(),
                      key=lambda x: (x[1]["Pts"], x[1]["DG"], x[1]["GF"]),
                      reverse=True)

    def update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        table = self.calculate_table()

        for idx, (team, data) in enumerate(table, start=1):
            values = [idx, team, data["PJ"], data["G"], data["E"], data["P"],
                      data["GF"], data["GC"], data["DG"], f"★ {data['Pts']} ★"]

            if idx <= self.num_classify:
                tag = "clasificado"
            elif idx <= self.num_classify + self.num_repechage:
                tag = "repechaje"
            else:
                tag = "eliminado"

            self.tree.insert("", "end", values=values, tags=(tag,))

        # Colores para filas
        self.tree.tag_configure("clasificado", background="#228B22", foreground="white", font=("Arial", 11, "bold"))
        self.tree.tag_configure("repechaje", background="#FFD700", foreground="black", font=("Arial", 11, "bold"))
        self.tree.tag_configure("eliminado", background="#B22222", foreground="white", font=("Arial", 11, "bold"))

    def next_jornada(self):
        if self.current_jornada < len(self.fixture):
            self.current_jornada += 1
            self.jornada_label.config(text=f"Jornada {self.current_jornada}")
            self.show_matches()

    def prev_jornada(self):
        if self.current_jornada > 1:
            self.current_jornada -= 1
            self.jornada_label.config(text=f"Jornada {self.current_jornada}")
            self.show_matches()

    def remove_focus(self, event):
        """ Quita el foco del Entry cuando se hace click afuera """
        widget = event.widget
        if not isinstance(widget, tk.Entry):
            self.root.focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    app = EliminatoriasApp(root)
    root.mainloop()
