import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout,
    QVBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPainter, QColor, QPainterPath

C = {
    'bg': '#000000', 'num': '#333333', 'num_p': '#737373',
    'fn':  '#a5a5a5', 'fn_t': '#000000', 'fn_p': '#d4d4d2',
    'op':  '#ff9f0a', 'op_p': '#ffd478', 'op_a': '#ffffff',
    'op_at': '#ff9f0a', 'txt': '#ffffff',
}
FONT = 'Helvetica Neue'


class CalculatorError(Exception):
    pass


class Calculator:
    OPS = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: (_ for _ in ()).throw(CalculatorError('0으로 나눌 수 없습니다'))
                          if b == 0 else a / b,
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self._cur = self._stored = 0.0
        self._op = ''; self._s = '0'; self._next = False

    def _fmt(self, v):
        if v == int(v) and abs(v) < 1e15: return str(int(v))
        if abs(v) >= 1e10 or (0 < abs(v) < 1e-4): return f'{v:.10g}'
        return f'{v:.10f}'.rstrip('0').rstrip('.')

    def input_digit(self, d):
        if self._next: self._s = d; self._next = False
        elif len(self._s.replace('-','').replace('.','')) < 15:
            self._s = d if self._s == '0' else self._s + d
        self._cur = float(self._s)

    def input_dot(self):
        if self._next: self._s = '0.'; self._next = False; return
        if '.' not in self._s: self._s += '.'

    def set_op(self, op):
        if self._op and not self._next: self.equal()
        self._stored = self._cur; self._op = op; self._next = True

    def equal(self):
        if not self._op: return self._s
        if self._op == '/' and self._cur == 0:
            raise CalculatorError('0으로 나눌 수 없습니다')
        r = self.OPS[self._op](self._stored, self._cur)
        if abs(r) > 1e308: raise CalculatorError('범위 초과')
        self._cur, self._s = r, self._fmt(r)
        self._stored = 0.0; self._op = ''; self._next = True
        return self._s

    def negative_positive(self):
        self._cur = -self._cur; self._s = self._fmt(self._cur)

    def percent(self):
        self._cur /= 100; self._s = self._fmt(self._cur)

    @property
    def display(self): return self._s


class CalcButton(QPushButton):
    COLORS = {
        'num':  ('#333333', '#737373', '#ffffff'),
        'func': ('#a5a5a5', '#d4d4d2', '#000000'),
        'op':   ('#ff9f0a', '#ffd478', '#ffffff'),
    }

    def __init__(self, text, kind, parent=None):
        super().__init__(text, parent)
        self._kind = kind; self._active = self._pressed = False
        self.setFlat(True); self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def set_active(self, v): self._active = v; self.update()

    def paintEvent(self, _):
        bg, bg_p, fg = self.COLORS[self._kind]
        if self._kind == 'op' and self._active:
            bg, fg = '#ffffff', '#ff9f0a'
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        path = QPainterPath(); path.addRoundedRect(0, 0, w, h, h/2, h/2)
        p.fillPath(path, QColor(bg_p if self._pressed else bg))
        p.setPen(QColor(fg)); p.setFont(self.font())
        if self.text() == '0' and w > h:
            p.drawText(self.rect().adjusted(int(h*.36),0,0,0), Qt.AlignLeft|Qt.AlignVCenter, '0')
        else:
            p.drawText(self.rect(), Qt.AlignCenter, self.text())

    def mousePressEvent(self, e):
        self._pressed = True; self.update(); super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._pressed = False; self.update(); super().mouseReleaseEvent(e)


class CalcWindow(QMainWindow):
    W, H, B, G, M = 393, 700, 80, 12, 16

    BTNS = [
        ('AC','fn',0,0,1),  ('+/-','fn',0,1,1), ('%','fn',0,2,1), ('÷','op',0,3,1),
        ('7','num',1,0,1),  ('8','num',1,1,1),  ('9','num',1,2,1),('×','op',1,3,1),
        ('4','num',2,0,1),  ('5','num',2,1,1),  ('6','num',2,2,1),('−','op',2,3,1),
        ('1','num',3,0,1),  ('2','num',3,1,1),  ('3','num',3,2,1),('+','op',3,3,1),
        ('0','num',4,0,2),  ('.','num',4,2,1),  ('=','op',4,3,1),
    ]
    SYM = {'÷':'/','×':'*','−':'-','+':'+'}
    ACT = {'AC':'_ac','+/-':'_neg','%':'_pct','=':'_eq',
           '÷':'/', '×':'*','−':'-','+':'+','.':'_dot'}

    def __init__(self):
        super().__init__()
        self._calc = Calculator(); self._op_btns = {}
        self._build()

    def _build(self):
        self.setWindowTitle('계산기')
        self.setFixedSize(self.W, self.H)
        self.setStyleSheet(f'QMainWindow{{background:{C["bg"]};}}')
        cw = QWidget(); cw.setStyleSheet(f'background:{C["bg"]};')
        self.setCentralWidget(cw)

        root = QVBoxLayout(cw); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        root.addStretch(1)

        self._lbl = QLabel('0')
        self._lbl.setAlignment(Qt.AlignRight|Qt.AlignBottom)
        self._lbl.setStyleSheet(f'color:{C["txt"]};background:transparent;')
        self._lbl.setContentsMargins(self.M,0,self.M,4)
        self._lbl.setMinimumHeight(110)
        self._fit('0'); root.addWidget(self._lbl)

        gw = QWidget(); gw.setStyleSheet('background:transparent;')
        g = QGridLayout(gw)
        g.setContentsMargins(self.M,self.G,self.M,self.M)
        g.setHorizontalSpacing(self.G); g.setVerticalSpacing(self.G)
        root.addWidget(gw)

        FSIZES = {'fn':(20,QFont.Normal),'op':(36,QFont.Light),'num':(26,QFont.Normal)}

        for lbl, kind, row, col, span in self.BTNS:
            k = {'fn':'func','num':'num','op':'op'}[kind]
            btn = CalcButton(lbl, k)
            sz, wt = FSIZES[kind]; f = QFont(FONT, sz); f.setWeight(wt); btn.setFont(f)
            btn.setFixedSize(self.B if span==1 else self.B*2+self.G, self.B)
            btn.clicked.connect(self._make_cb(lbl))
            g.addWidget(btn, row, col, 1, span, Qt.AlignCenter)
            if lbl in self.SYM: self._op_btns[self.SYM[lbl]] = btn

    def _make_cb(self, lbl):
        a = self.ACT.get(lbl, lbl)
        if a in ('_ac','_neg','_pct','_dot','_eq'):
            return getattr(self, a)
        if a in '/+*-':
            return lambda checked=False, s=a: self._op(s)
        return lambda checked=False, d=lbl: self._d(d)

    def _fit(self, t):
        f = QFont(FONT, 80); f.setWeight(QFont.Light)
        self._lbl.setFont(f)

    def _refresh(self):
        t = self._calc.display; self._fit(t); self._lbl.setText(t)

    def _off(self):
        for b in self._op_btns.values(): b.set_active(False)

    def _d(self, n):   self._off(); self._calc.input_digit(n); self._refresh()
    def _dot(self):    self._off(); self._calc.input_dot();     self._refresh()
    def _ac(self):     self._calc.reset(); self._off();         self._refresh()
    def _neg(self):    self._calc.negative_positive();          self._refresh()
    def _pct(self):    self._calc.percent();                    self._refresh()

    def _op(self, sym):
        self._calc.set_op(sym); self._off()
        if sym in self._op_btns: self._op_btns[sym].set_active(True)
        self._refresh()

    def _eq(self):
        self._off()
        try:
            r = self._calc.equal(); self._fit(r); self._lbl.setText(r)
        except CalculatorError as e:
            t = str(e); self._fit(t); self._lbl.setText(t); self._calc.reset()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    CalcWindow().show()
    sys.exit(app.exec_())
