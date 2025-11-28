# multiple_curves_dynamic.py
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

app = QApplication(sys.argv)
win = pg.GraphicsLayoutWidget(show=True, title="Mise à jour dynamique")
plot = win.addPlot(title="Courbes dynamiques")
plot.addLegend()

x = np.linspace(0, 2 * np.pi, 500)
y1 = np.sin(x)
y2 = np.cos(x)

c1 = plot.plot(x, y1, pen=pg.mkPen('r', width=2), name="sin")
c2 = plot.plot(x, y2, pen=pg.mkPen('b', width=2), name="cos")

phase = 0.0

def update():
    global phase
    phase += 0.1
    c1.setData(x, np.sin(x + phase))
    c2.setData(x, 0.5 * np.cos(2*(x + phase)))
    # Pour limiter la charge, on ne met à jour que les données (pas de re-création des objets)

timer = QTimer()
timer.timeout.connect(update)
timer.start(50)  # 50 ms -> ~20 FPS

if __name__ == "__main__":
    sys.exit(app.exec())