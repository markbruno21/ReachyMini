"""
reachy_mini_mock.py
═══════════════════
Modulo mock di reachy_mini per testare lo script
senza il daemon del simulatore attivo.
 
USO:  rinominare questo file in  reachy_mini.py
      nella stessa cartella di interazione_reachy.py,
      oppure aggiungerlo al PYTHONPATH per i test locali.
"""
 
import time
 
 
class _Head:
    def look_forward(self):
        print("    [HEAD] → guarda dritto avanti")
        time.sleep(0.1)
 
    def nod(self):
        print("    [HEAD] → annuisce")
        time.sleep(0.15)
 
    def turn_left(self, deg: int = 10):
        print(f"    [HEAD] → ruota a sinistra di {deg}°")
        time.sleep(0.1)
 
    def turn_right(self, deg: int = 10):
        print(f"    [HEAD] → ruota a destra di {deg}°")
        time.sleep(0.1)
 
    def look_at(self, x: float, y: float):
        print(f"    [HEAD] → sguardo verso ({x}, {y})")
        time.sleep(0.1)
 
 
class _Arm:
    def __init__(self, side: str):
        self._side = side.upper()
 
    def raise_up(self, deg: int = 30):
        print(f"    [{self._side} ARM] → alza di {deg}°")
        time.sleep(0.15)
 
    def lower(self):
        print(f"    [{self._side} ARM] → abbassa")
        time.sleep(0.1)
 
    def wave(self):
        print(f"    [{self._side} ARM] → saluta con la mano 👋")
        time.sleep(0.3)
 
 
class _Eye:
    def look_at(self, x: float, y: float):
        print(f"    [EYE] → pupilla verso ({x}, {y})")
        time.sleep(0.05)
 
 
class ReachyMini:
    """
    Classe mock che replica l'interfaccia pubblica
    di reachy_mini.ReachyMini usata nello script principale.
    """
 
    def __init__(self, host: str = "localhost"):
        self.host = host
        self.head = _Head()
        self.left_arm  = _Arm("left")
        self.right_arm = _Arm("right")
        self.left_eye  = _Eye()
        self.right_eye = _Eye()
 
    def turn_on(self):
        print(f"    [ROBOT] → acceso (connesso a {self.host})")
 
    def turn_off(self):
        print("    [ROBOT] → spento")