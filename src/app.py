from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QUrl
from PyQt5.QtGui import QColor, QDesktopServices, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QTableView, QHeaderView,
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
)
from PIL import Image
from random import randint
import sys
import os


# ============================================
# Modelo da Matriz
# ============================================
class MatrizModel(QAbstractTableModel):
    def __init__(self, rows=20, cols=20):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.data_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
        self.history = []

    def rowCount(self, parent=None):
        return self.rows

    def columnCount(self, parent=None):
        return self.cols

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        value = self.data_matrix[index.row()][index.column()]
        if role == Qt.BackgroundRole:
            return QColor("black") if value == 1 else QColor("white")
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        self.data_matrix[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    # Próxima geração
    def next_generation(self):
        self.history.append([row[:] for row in self.data_matrix])
        new_matrix = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                alive = self.data_matrix[r][c]
                neighbors = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        rr = r + dr
                        cc = c + dc
                        if 0 <= rr < self.rows and 0 <= cc < self.cols:
                            neighbors += self.data_matrix[rr][cc]
                if alive:
                    new_matrix[r][c] = 1 if neighbors in (2, 3) else 0
                else:
                    new_matrix[r][c] = 1 if neighbors == 3 else 0
        self.data_matrix = new_matrix
        self.layoutChanged.emit()

    # Voltar geração
    def previous_generation(self):
        if self.history:
            self.data_matrix = self.history.pop()
            self.layoutChanged.emit()


# ============================================
# View da Matriz (suporta paint ao arrastar)
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
                self.toggle_value = 1 - current
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
        self.model = MatrizModel()
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

        # BOTÕES ESTILO RETANGULAR & GRANDES
        for btn in (btn_next, btn_prev, btn_25, btn_100, btn_reset, btn_filmoteca):
            btn.setFixedSize(200, 60)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
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

        # Adicionar botões ao painel lateral (ordem visual)
        side_panel.addWidget(btn_next)
        side_panel.addWidget(btn_prev)
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
            lbl.setFixedSize(200, 120)
            lbl.setStyleSheet("background-color: #eeeeee; border: 1px solid #444;")
            lbl.setAlignment(Qt.AlignCenter)
            # deixar espaço para clicar - usaremos mousePressEvent via função lambda
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
        # FULLSCREEN SEM BORDA
        # ============================
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        # pegar resolução da tela
        screen = QApplication.primaryScreen().availableGeometry()
        screen_w = screen.width()
        screen_h = screen.height()

        # a matriz ocupa tudo menos a largura do painel lateral
        matriz_width = screen_w - 220   # 200 px dos botões + margem
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
                # Conectar clique: abrir a pasta / arquivo
                # precisamos definir um closure porque estamos dentro de loop
                def make_open(path):
                    return lambda ev: QDesktopServices.openUrl(QUrl.fromLocalFile(path))
                # substituir evento mousePressEvent do label
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
    # Reseta toda a matriz para branco
    # --------------------------------------------------
    def handle_reset_matrix(self):
        self.model.data_matrix = [
            [0 for _ in range(self.model.cols)]
            for _ in range(self.model.rows)
        ]
        self.model.history = []
        self.model.layoutChanged.emit()

    # --------------------------------------------------
    # Gera GIF 25 gerações
    # --------------------------------------------------
    def handle_25_gens_gif(self):
        frames = []
        temp_matrix = [row[:] for row in self.model.data_matrix]  # backup
        temp_history = self.model.history[:]

        scale = 5
        img_width = self.model.cols * scale
        img_height = self.model.rows * scale

        for i in range(25):
            img = Image.new("RGB", (img_width, img_height), color="white")
            pixels = img.load()
            for r in range(self.model.rows):
                for c in range(self.model.cols):
                    if self.model.data_matrix[r][c]:
                        for dr in range(scale):
                            for dc in range(scale):
                                pixels[c*scale+dc, r*scale+dr] = (0, 0, 0)
            frames.append(img.copy())
            self.model.next_generation()

        gif_path = f"gifs/{randint(1000000,9999999)}_25gens.gif"
        # garante pasta
        if not os.path.exists("gifs"):
            os.makedirs("gifs")
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
        )
        print(f"GIF salvo como {gif_path}")

        # restaurar estado
        self.model.data_matrix = temp_matrix
        self.model.history = temp_history
        self.model.layoutChanged.emit()

        # atualizar miniaturas
        self.update_thumbnails()

    # --------------------------------------------------
    # Gera GIF 100 gerações
    # --------------------------------------------------
    def handle_100_gens_gif(self):
        frames = []
        temp_matrix = [row[:] for row in self.model.data_matrix]  # backup
        temp_history = self.model.history[:]

        scale = 5
        img_width = self.model.cols * scale
        img_height = self.model.rows * scale

        for i in range(100):
            img = Image.new("RGB", (img_width, img_height), color="white")
            pixels = img.load()
            for r in range(self.model.rows):
                for c in range(self.model.cols):
                    if self.model.data_matrix[r][c]:
                        for dr in range(scale):
                            for dc in range(scale):
                                pixels[c*scale+dc, r*scale+dr] = (0, 0, 0)
            frames.append(img.copy())
            self.model.next_generation()

        gif_path = f"gifs/{randint(1000000,9999999)}_100gens.gif"
        if not os.path.exists("gifs"):
            os.makedirs("gifs")
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
        )
        print(f"GIF salvo como {gif_path}")

        # restaurar estado
        self.model.data_matrix = temp_matrix
        self.model.history = temp_history
        self.model.layoutChanged.emit()

        # atualizar miniaturas
        self.update_thumbnails()

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
