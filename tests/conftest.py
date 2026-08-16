import sys
from pathlib import Path

# verify.py mora na raiz do repo, nao num pacote instalavel. O pytest so
# acha modulos que estao no sys.path -- este arquivo roda antes de
# qualquer teste e resolve isso pra todos os test_*.py de uma vez.
sys.path.insert(0, str(Path(__file__).parent.parent))
