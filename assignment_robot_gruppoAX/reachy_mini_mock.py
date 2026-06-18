"""
reachy_mini_mock.py
═══════════════════
Modulo mock di reachy_mini per testare lo script
senza il daemon del simulatore attivo.

 """

 

 
 
class ReachyMini:
    """
    Classe mock che replica l'interfaccia pubblica
    di reachy_mini.ReachyMini usata nello script principale.
    """
 
    def __init__(self, host: str = "localhost"):
        self.host = host
      
    def turn_on(self):
        print(f"    [ROBOT] → acceso (connesso a {self.host})")
 
    def turn_off(self):
        print("    [ROBOT] → spento")