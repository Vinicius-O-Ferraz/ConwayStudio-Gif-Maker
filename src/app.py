from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt5.QtGui import QColor, QDesktopServices
from PyQt5.QtWidgets import (
    QApplication, QTableView, QHeaderView,
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout
)
from PIL import Image
from random import randint
import sys
from PyQt5.QtCore import QUrl
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
# View da Matriz
# ============================================
class MatrizView(QTableView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)

        self.setMouseTracking(True)   # permite capturar movimento sem clique
        self.mouse_pressed = False    # controle do clique
        self.toggle_value = None      # valor que será "pintado" ao arrastar

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

    # =============================
    #   Eventos do Mouse
    # =============================
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

        btn_next = QPushButton("Próxima Geração")
        btn_prev = QPushButton("Voltar Geração")
        btn_25 = QPushButton("GIF 25 Gerações")
        btn_reset = QPushButton("Resetar Matriz")
        btn_filmoteca = QPushButton("Filmoteca")


        
        # BOTÕES ESTILO RETANGULAR & GRANDES
        for btn in (btn_next, btn_prev, btn_25, btn_reset,btn_filmoteca):
            btn.setFixedSize(200, 60)   # retangulares
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

        btn_next.clicked.connect(self.handle_next_gen)
        btn_prev.clicked.connect(self.handle_prev_gen)
        btn_25.clicked.connect(self.handle_25_gens_gif)
        btn_reset.clicked.connect(self.handle_reset_matrix)
        btn_filmoteca.clicked.connect(self.handle_open_gif_folder)




        # Adicionar botões ao painel lateral
        side_panel.addWidget(btn_next)
        side_panel.addWidget(btn_prev)
        side_panel.addWidget(btn_25)
        side_panel.addWidget(btn_filmoteca)
        side_panel.addWidget(btn_reset)


        # empurra os botões para cima
        side_panel.addStretch()

        # adiciona o painel lateral ao layout principal
        main_layout.addLayout(side_panel)

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

    def handle_open_gif_folder(self):
        folder = os.path.abspath("gifs")
        
        # Se a pasta não existir, criar
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Abrir no explorador de arquivos
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def handle_reset_matrix(self):
        # Zera toda a matriz
        self.model.data_matrix = [
            [0 for _ in range(self.model.cols)]
            for _ in range(self.model.rows)
        ]

        # Reseta histórico
        self.model.history = []

        # Atualiza visualização
        self.model.layoutChanged.emit()


    def handle_25_gens_gif(self):
        frames = []
        temp_matrix = [row[:] for row in self.model.data_matrix]  # backup
        temp_history = self.model.history[:]

        scale = 5  # fator de escala para visualização
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
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
        )
        print(f"GIF salvo como {gif_path}")

        self.model.data_matrix = temp_matrix
        self.model.history = temp_history
        self.model.layoutChanged.emit()

        # Removido: adição duplicada de widgets/layouts

    def handle_next_gen(self):
        self.model.next_generation()

    def handle_prev_gen(self):
        self.model.previous_generation()

    def handle_100_gens_gif(self):
        frames = []
        temp_matrix = [row[:] for row in self.model.data_matrix]  # backup
        temp_history = self.model.history[:]

        for i in range(20):
            # Criar imagem para GIF
            img = Image.new("RGB", (self.model.cols, self.model.rows), color="white")
            pixels = img.load()
            for c in range(self.model.rows):
                for r in range(self.model.cols):
                    if self.model.data_matrix[r][c]:
                        pixels[c, r] = (255, 255, 0)  # amarelo
            frames.append(img.copy())
            self.model.next_generation()

        # Salvar GIF
        frames[0].save(
            f"gifs/{randint(1000000,9999999)}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
        )
        print("GIF salvo como jogo_da_vida_20gens.gif")

        # Restaurar estado
        self.model.data_matrix = temp_matrix
        self.model.history = temp_history
        self.model.layoutChanged.emit()


# ============================================
# Executar o aplicativo
# ============================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
