from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication, QTableView, QHeaderView,
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout
)
import sys

# ============================================
# Modelo da Matriz (dados + cores + histórico)
# ============================================
class MatrizModel(QAbstractTableModel):
    def __init__(self, rows=300, cols=300):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.data_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
        self.history = []  # Guarda gerações anteriores

    def rowCount(self, parent=None):
        return self.rows

    def columnCount(self, parent=None):
        return self.cols

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        value = self.data_matrix[index.row()][index.column()]
        if role == Qt.BackgroundRole:
            return QColor("yellow") if value == 1 else QColor("white")
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        self.data_matrix[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    # --------------------------------------------
    # Próxima geração
    # --------------------------------------------
    def next_generation(self):
        # Salvar a geração atual no histórico
        self.history.append([row[:] for row in self.data_matrix])

        new_matrix = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                alive = self.data_matrix[r][c]
                neighbors = 0
                # Verifica os 8 vizinhos
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        rr = r + dr
                        cc = c + dc
                        if 0 <= rr < self.rows and 0 <= cc < self.cols:
                            neighbors += self.data_matrix[rr][cc]

                # Regras do Conway
                if alive:
                    new_matrix[r][c] = 1 if neighbors in (2, 3) else 0
                else:
                    new_matrix[r][c] = 1 if neighbors == 3 else 0

        self.data_matrix = new_matrix
        self.layoutChanged.emit()

    # --------------------------------------------
    # Voltar geração
    # --------------------------------------------
    def previous_generation(self):
        if self.history:
            self.data_matrix = self.history.pop()
            self.layoutChanged.emit()


# ============================================
# View da Matriz (visual)
# ============================================
class MatrizView(QTableView):
    def __init__(self, model, tamanho_px=600):
        super().__init__()
        self.setModel(model)
        self.tamanho_px = tamanho_px
        self.setFixedSize(tamanho_px, tamanho_px)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.clicked.connect(self.handle_click)
        self.adjust_cell_sizes()

    def adjust_cell_sizes(self):
        cols = self.model().columnCount()
        cell_size = self.tamanho_px // cols

        for c in range(cols):
            self.setColumnWidth(c, cell_size)

        for r in range(self.model().rowCount()):
            self.setRowHeight(r, cell_size)

    def handle_click(self, index):
        r = index.row()
        c = index.column()
        atual = self.model().data_matrix[r][c]
        self.model().setData(index, 1 - atual)


# ============================================
# Janela principal com botões
# ============================================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.model = MatrizModel()
        self.view = MatrizView(self.model, tamanho_px=600)

        # Layout horizontal para botões
        h_layout = QHBoxLayout()

        btn_prev = QPushButton("Voltar Geração")
        btn_prev.clicked.connect(self.handle_prev_gen)

        btn_next = QPushButton("Próxima Geração")
        btn_next.clicked.connect(self.handle_next_gen)

        h_layout.addWidget(btn_prev)
        h_layout.addWidget(btn_next)

        layout.addWidget(self.view)
        layout.addLayout(h_layout)

        self.setWindowTitle("Jogo da Vida - Matriz 300×300")
        self.setFixedSize(650, 700)
    
    def handle_prev_gen(self):
        self.model.previous_generation()

    def handle_next_gen(self):
        self.model.next_generation()



# ============================================
# Executar o aplicativo
# ============================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
