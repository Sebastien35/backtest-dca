import subprocess
import sys
import os

INSTALL_FLAG_FILE = "install_done.txt"

def install_requirements():
    try:
        print("Installation des dépendances...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        with open(INSTALL_FLAG_FILE, "w") as f:
            f.write("installed")
        print("Dépendances installées.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'installation : {e}")
        sys.exit(1)

def run_scripts():
    try:
        print("Exécution de getData.py...")
        subprocess.check_call([sys.executable, "getData.py"])

        print("J'essaye de trouver les meilleurs paramètres...")
        subprocess.check_call([sys.executable, "opti.py"])

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution des scripts : {e}")
        sys.exit(1)

def main():
    if not os.path.exists(INSTALL_FLAG_FILE):
        install_requirements()
    else:
        print("Dépendances déjà installées, on va pas recommencer quand même !")

    run_scripts()

if __name__ == "__main__":
    main()
