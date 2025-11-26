from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QUrl
from PyQt5.QtGui import QColor, QDesktopServices, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QTableView, QHeaderView,
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
)
from PIL import Image
from random import randint, random, choice
import sys
import os


# ============================================
# Estados epidemiológicos
# ============================================
SUSCEPTIBLE = 0  # Suscetível
EXPOSED = 1      # Exposto (incubação)
INFECTED = 2     # Infectado (contagioso)
RECOVERED = 3    # Recuperado (imune)
DEAD = 4         # Morto (não suscetível)

# Mapa de cor por estado (para exibição)
STATE_COLORS = {
    SUSCEPTIBLE: QColor("white"),
    EXPOSED: QColor(255, 165, 0),   # orange
    INFECTED: QColor(220, 20, 60),  # crimson / red
    RECOVERED: QColor(144, 238, 144), # lightgreen
    DEAD: QColor(105, 105, 105),    # dimgray
}


# ============================================
# Modelo da Matriz (agora com atributos epidemiológicos)
# ============================================
class MatrizModel(QAbstractTableModel):
    def __init__(self, rows=20, cols=20):
        super().__init__()
        self.rows = rows
        self.cols = cols

        # grid de estados
        self.data_matrix = [[SUSCEPTIBLE for _ in range(cols)] for _ in range(rows)]
        # grid de timers (por exemplo: dias restantes de incubação/infectividade)
        self.timers = [[0 for _ in range(cols)] for _ in range(rows)]

        # histórico (para desfazer)
        self.history = []

        # Parâmetros epidemiológicos padrão (pode ajustar)
        self.p_infection = 0.25     # probabilidade base de infecção por contato
        self.p_recovery = 0.05      # probabilidade (por passo) de recuperação
        self.p_mortality = 0.01     # probabilidade (por passo) de morrer se infectado
        self.incubation_period = 2  # passos E -> I
        self.infectious_period = 6  # passos I -> R (se não morrer)
        self.mobility_rate = 0.0    # probabilidade de trocar de posição com um vizinho

        # configuração de vizinhança: "moore" (8) por padrão
        self.use_moore = True

    # métodos QAbstractTableModel
    def rowCount(self, parent=None):
        return self.rows

    def columnCount(self, parent=None):
        return self.cols

    def data(self, index, role=Qt.DisplayRole):
        if not index or not index.isValid():
            return QVariant()
        r = index.row()
        c = index.column()
        value = self.data_matrix[r][c]
        if role == Qt.BackgroundRole:
            # retorna a cor baseada no estado
            return STATE_COLORS.get(value, QColor("white"))
        if role == Qt.DisplayRole:
            # opcional: mostrar estado numérico (comentado para não poluir)
            # return str(value)
            return QVariant()
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if not index or not index.isValid():
            return False
        r = index.row()
        c = index.column()
        self.data_matrix[r][c] = value
        # reset timer ao setar manualmente (se for E/I podemos setar timers manualmente)
        self.timers[r][c] = 0
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    # contabiliza vizinhos do tipo `state_type`
    def count_neighbors(self, r, c, state_type):
        total = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr = r + dr
                cc = c + dc
                if 0 <= rr < self.rows and 0 <= cc < self.cols:
                    if self.data_matrix[rr][cc] == state_type:
                        total += 1
        return total

    # Próxima geração — agora com lógica SEIRD + probabilidade e timers
    def next_generation(self):
        # salva histórico (cópia profunda)
        self.history.append(([row[:] for row in self.data_matrix], [row[:] for row in self.timers]))

        new_matrix = [row[:] for row in self.data_matrix]
        new_timers = [row[:] for row in self.timers]

        for r in range(self.rows):
            for c in range(self.cols):
                state = self.data_matrix[r][c]
                timer = self.timers[r][c]

                # Mobilidade simples: com probabilidade, troca com um vizinho aleatório
                if random() < self.mobility_rate:
                    # escolhe um vizinho válido aleatório e troca
                    neighs = []
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            rr = r + dr
                            cc = c + dc
                            if 0 <= rr < self.rows and 0 <= cc < self.cols:
                                neighs.append((rr, cc))
                    if neighs:
                        rr, cc = choice(neighs)
                        # troca estados e timers
                        new_matrix[r][c], new_matrix[rr][cc] = new_matrix[rr][cc], new_matrix[r][c]
                        new_timers[r][c], new_timers[rr][cc] = new_timers[rr][cc], new_timers[r][c]
                        # pular para próximo (essa célula já foi trocada)
                        continue

                if state == SUSCEPTIBLE:
                    # conta vizinhos infectados (contato local)
                    infected_neighbors = self.count_neighbors(r, c, INFECTED)
                    if infected_neighbors > 0:
                        # probabilidade combinada de não ser infectado por nenhum vizinho:
                        # p_no = (1 - p_infection) ** infected_neighbors
                        # p_get = 1 - p_no
                        p_get = 1 - (1 - self.p_infection) ** infected_neighbors
                        if random() < p_get:
                            new_matrix[r][c] = EXPOSED
                            new_timers[r][c] = self.incubation_period

                elif state == EXPOSED:
                    # decrementa timer de incubação
                    if timer <= 1:
                        # passa para infectado
                        new_matrix[r][c] = INFECTED
                        new_timers[r][c] = self.infectious_period
                    else:
                        new_timers[r][c] = timer - 1

                elif state == INFECTED:
                    # primeira: possibilidade de morrer
                    if random() < self.p_mortality:
                        new_matrix[r][c] = DEAD
                        new_timers[r][c] = 0
                    else:
                        # possibilidade de recuperação (podemos combinar timer + prob)
                        if timer <= 1:
                            # recupera
                            if random() < self.p_recovery:
                                new_matrix[r][c] = RECOVERED
                                new_timers[r][c] = 0
                            else:
                                # se não recuperar, mantem infectado com novo período (ou pode morrer próximo passo)
                                new_timers[r][c] = self.infectious_period
                        else:
                            new_timers[r][c] = timer - 1

                elif state in (RECOVERED, DEAD):
                    # permanecem no mesmo estado (poderíamos modelar perda de imunidade aqui)
                    new_timers[r][c] = 0

        # aplicar atualização
        self.data_matrix = new_matrix
        self.timers = new_timers
        self.layoutChanged.emit()

    # Voltar geração (undo)
    def previous_generation(self):
        if self.history:
            mat, tim = self.history.pop()
            self.data_matrix = mat
            self.timers = tim
            self.layoutChanged.emit()

    # Reseta matriz
    def reset(self):
        self.data_matrix = [[SUSCEPTIBLE for _ in range(self.cols)] for _ in range(self.rows)]
        self.timers = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.history = []
        self.layoutChanged.emit()

    # randomiza N infectados em posições aleatórias
    def randomize_infected(self, n=5):
        placed = 0
        attempts = 0
        while placed < n and attempts < n * 20:
            r = randint(0, self.rows - 1)
            c = randint(0, self.cols - 1)
            if self.data_matrix[r][c] == SUSCEPTIBLE:
                self.data_matrix[r][c] = INFECTED
                self.timers[r][c] = self.infectious_period
                placed += 1
            attempts += 1
        self.layoutChanged.emit()

    # definir parâmetros em lote (facilita testes)
    def set_default_params(self):
        self.p_infection = 0.25
        self.p_recovery = 0.05
        self.p_mortality = 0.01
        self.incubation_period = 2
        self.infectious_period = 6
        self.mobility_rate = 0.0
        self.layoutChanged.emit()


# ============================================
# View da Matriz (suporta paint ao arrastar)
# - clique agora cicla entre estados (S->E->I->R->D->S)
# ============================================
class MatrizView(QTableView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)

        self.setMouseTracking(True)
        self.mouse_pressed = False
        self.toggle_value = None

        # Remover barras de navegação
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Remover cabeçalhos
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

    def adjust_cell_sizes(self, width_px, height_px):
        cols = self.model().columnCount()
        rows = self.model().rowCount()

        cell_size = min(width_px // cols, height_px // rows)
        total_width = cell_size * cols
        total_height = cell_size * rows

        self.setFixedSize(total_width, total_height)

        for c in range(cols):
            self.setColumnWidth(c, cell_size)
        for r in range(rows):
            self.setRowHeight(r, cell_size)

    # Eventos do mouse para clicar + arrastar
    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.mouse_pressed = True

            index = self.indexAt(event.pos())
            if index.isValid():
                r = index.row()
                c = index.column()
                current = self.model().data_matrix[r][c]
                # cicla para o próximo estado (útil para montar cenários)
                next_state = (current + 1) % (len(STATE_COLORS))
                self.toggle_value = next_state
                self.model().setData(index, self.toggle_value)

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            index = self.indexAt(event.pos())
            if index.isValid():
                r = index.row()
                c = index.column()
                if self.model().data_matrix[r][c] != self.toggle_value:
                    self.model().setData(index, self.toggle_value)

    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False
        self.toggle_value = None


# ============================================
# Janela principal
# ============================================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # garantir pasta gifs existe
        if not os.path.exists("gifs"):
            os.makedirs("gifs")

        # LAYOUT PRINCIPAL HORIZONTAL (matriz esquerda, botões direita)
        main_layout = QHBoxLayout(self)

        # Matriz
        self.model = MatrizModel(rows=40, cols=60)  # default maior para ver padrões espaciais
        self.view = MatrizView(self.model)
        main_layout.addWidget(self.view)

        # ===============================================
        # PAINEL DE BOTÕES (vertical, lado direito)
        # ===============================================
        side_panel = QVBoxLayout()

        # Botões
        btn_next = QPushButton("Próxima Geração ⏭️")
        btn_prev = QPushButton("Voltar Geração ⏮️")
        btn_25 = QPushButton("GIF 25 Gerações 📷")
        btn_100 = QPushButton("GIF 100 Gerações 🎥 ")
        btn_reset = QPushButton("Resetar Matriz 🧼")
        btn_filmoteca = QPushButton("Filmoteca 💾 ")
        btn_random_inf = QPushButton("Randomizar Infectados 🔥")
        btn_default_params = QPushButton("Parâmetros Padrão ⚙️")

        # BOTÕES ESTILO RETANGULAR & GRANDES
        for btn in (btn_next, btn_prev, btn_25, btn_100, btn_reset, btn_filmoteca, btn_random_inf, btn_default_params):
            btn.setFixedSize(220, 52)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 15px;
                    background-color: #d0d0d0;
                    border: 2px solid #555;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #c0c0c0;
                }
            """)

        # Conectar sinais
        btn_next.clicked.connect(self.handle_next_gen)
        btn_prev.clicked.connect(self.handle_prev_gen)
        btn_25.clicked.connect(self.handle_25_gens_gif)
        btn_100.clicked.connect(self.handle_100_gens_gif)
        btn_reset.clicked.connect(self.handle_reset_matrix)
        btn_filmoteca.clicked.connect(self.handle_open_gif_folder)
        btn_random_inf.clicked.connect(self.handle_randomize_infected)
        btn_default_params.clicked.connect(self.handle_set_default_params)

        # Adicionar botões ao painel lateral (ordem visual)
        side_panel.addWidget(btn_next)
        side_panel.addWidget(btn_prev)
        side_panel.addWidget(btn_random_inf)
        side_panel.addWidget(btn_default_params)
        side_panel.addWidget(btn_25)
        side_panel.addWidget(btn_100)
        side_panel.addWidget(btn_filmoteca)
        side_panel.addWidget(btn_reset)

        # ============================
        # ÁREA DE MINIATURAS (FILMOTECA)
        # ============================
        side_panel.addSpacing(10)

        lbl_title = QLabel("Últimos GIFs")
        lbl_title.setAlignment(Qt.AlignCenter)  # CENTRALIZA O TEXTO
        lbl_title.setStyleSheet("""
            font-weight: bold;
            font-size: 18px;
        """)

        side_panel.addWidget(lbl_title)

        self.thumb_container = QVBoxLayout()
        self.thumb_labels = []
        self.thumb_paths = []  # caminhos correspondentes

        for _ in range(4):
            lbl = QLabel()
            lbl.setFixedSize(220, 120)
            lbl.setStyleSheet("background-color: #eeeeee; border: 1px solid #444;")
            lbl.setAlignment(Qt.AlignCenter)
            self.thumb_labels.append(lbl)
            self.thumb_container.addWidget(lbl)

        side_panel.addLayout(self.thumb_container)

        # empurra os botões para cima
        side_panel.addStretch()

        # adiciona o painel lateral ao layout principal
        main_layout.addLayout(side_panel)

        # Carregar miniaturas existentes ao iniciar
        self.update_thumbnails()

        # ============================
        # FULLSCREEN SEM BORDA (mantive como estava)
        # ============================
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        # pegar resolução da tela
        screen = QApplication.primaryScreen().availableGeometry()
        screen_w = screen.width()
        screen_h = screen.height()

        # a matriz ocupa tudo menos a largura do painel lateral
        matriz_width = screen_w - 240   # 220 px dos botões + margem
        matriz_height = screen_h

        self.view.adjust_cell_sizes(matriz_width, matriz_height)

    # --------------------------------------------------
    # Atualiza as miniaturas (4 mais recentes)
    # --------------------------------------------------
    def update_thumbnails(self):
        folder = "gifs"
        # se pasta não existe, limpa miniaturas
        if not os.path.exists(folder):
            for lbl in self.thumb_labels:
                lbl.clear()
                lbl.setText("Sem GIF")
            self.thumb_paths = []
            return

        files = sorted(
            [f for f in os.listdir(folder) if f.lower().endswith(".gif")],
            key=lambda x: os.path.getmtime(os.path.join(folder, x)),
            reverse=True
        )

        last4 = files[:4]
        self.thumb_paths = []

        for i, lbl in enumerate(self.thumb_labels):
            if i < len(last4):
                gif_path = os.path.abspath(os.path.join(folder, last4[i]))
                self.thumb_paths.append(gif_path)

                # Carrega com QPixmap (mostra primeira frame estática)
                pix = QPixmap(gif_path)
                if not pix.isNull():
                    pix = pix.scaled(
                        lbl.width(), lbl.height(),
                        Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    lbl.setPixmap(pix)
                else:
                    lbl.clear()
                    lbl.setText(last4[i])
                # Conectar clique: abrir arquivo
                lbl.mousePressEvent = lambda ev, p=gif_path: QDesktopServices.openUrl(QUrl.fromLocalFile(p))
            else:
                lbl.clear()
                lbl.setText("Sem GIF")

    # --------------------------------------------------
    # Abrir pasta gifs/
    # --------------------------------------------------
    def handle_open_gif_folder(self):
        folder = os.path.abspath("gifs")
        if not os.path.exists(folder):
            os.makedirs(folder)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    # --------------------------------------------------
    # Reseta toda a matriz para susceptível
    # --------------------------------------------------
    def handle_reset_matrix(self):
        self.model.reset()

    # --------------------------------------------------
    # Randomizar infectados (coloca N infectados aleatórios)
    # --------------------------------------------------
    def handle_randomize_infected(self):
        # por padrão colocamos 10 infectados
        self.model.randomize_infected(10)

    # --------------------------------------------------
    # Setar parâmetros padrão
    # --------------------------------------------------
    def handle_set_default_params(self):
        self.model.set_default_params()

    # --------------------------------------------------
    # Gera GIF N gerações (gen_count)
    # - agora com cores para cada estado
    # --------------------------------------------------
    def _generate_gif(self, gen_count, scale=4):
        frames = []
        temp_matrix = [row[:] for row in self.model.data_matrix]  # backup
        temp_timers = [row[:] for row in self.model.timers]
        temp_history = self.model.history[:]

        img_width = self.model.cols * scale
        img_height = self.model.rows * scale

        for i in range(gen_count):
            img = Image.new("RGB", (img_width, img_height), color=(255, 255, 255))
            pixels = img.load()
            for r in range(self.model.rows):
                for c in range(self.model.cols):
                    state = self.model.data_matrix[r][c]
                    color_q = STATE_COLORS.get(state, QColor("white"))
                    # extrai RGB de QColor
                    col = (color_q.red(), color_q.green(), color_q.blue())
                    if state != SUSCEPTIBLE:  # desenha apenas não-susceptíveis para preservar branco
                        for dr in range(scale):
                            for dc in range(scale):
                                pixels[c*scale+dc, r*scale+dr] = col
            frames.append(img.copy())
            self.model.next_generation()

        gif_path = f"gifs/{randint(1000000,9999999)}_{gen_count}gens_seird.gif"
        # garante pasta
        if not os.path.exists("gifs"):
            os.makedirs("gifs")
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=120,
            loop=0,
        )
        print(f"GIF salvo como {gif_path}")

        # restaurar estado
        self.model.data_matrix = temp_matrix
        self.model.timers = temp_timers
        self.model.history = temp_history
        self.model.layoutChanged.emit()

        # atualizar miniaturas
        self.update_thumbnails()

    def handle_25_gens_gif(self):
        self._generate_gif(25, scale=4)

    def handle_100_gens_gif(self):
        self._generate_gif(100, scale=3)

    def handle_next_gen(self):
        self.model.next_generation()

    def handle_prev_gen(self):
        self.model.previous_generation()


# ============================================
# Executar o aplicativo
# ============================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
