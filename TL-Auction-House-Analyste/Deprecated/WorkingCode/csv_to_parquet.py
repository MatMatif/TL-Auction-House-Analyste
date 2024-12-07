import os
import pandas as pd
import chardet

def detect_encoding(file_path):
    """
    Detecte l'encodage du fichier CSV.
    """
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']

def clean_dataframe(df):
    """
    Nettoie le DataFrame en supprimant certains caractères problematiques dans chaque cellule.
    """
    def clean_column(column):
        # Supprimer plusieurs caractères problematiques specifiques
        return column.apply(
            lambda x: str(x).replace('→', '').replace('©', '').replace('®', '') if isinstance(x, str) else x
        )

    # Appliquer le nettoyage à chaque colonne du DataFrame
    for col in df.columns:
        df[col] = clean_column(df[col])
    return df

def convert_csv_to_parquet(directory, archive_csv=False):
    """
    Convertit tous les fichiers CSV dans un repertoire donne en fichiers Parquet.
    :param directory: Chemin du repertoire contenant les fichiers CSV.
    :param archive_csv: Si True, les fichiers CSV originaux seront deplaces dans un sous-dossier 'archive'.
    """
    # Creer un sous-dossier 'archive' si l'archivage est active
    if archive_csv:
        archive_dir = os.path.join(directory, "archive")
        os.makedirs(archive_dir, exist_ok=True)

    csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]

    if not csv_files:
        print("Aucun fichier CSV trouve dans le repertoire.")
        return  # Fin de la fonction si aucun fichier CSV n'est trouve

    for csv_file in csv_files:
        csv_path = os.path.join(directory, csv_file)
        
        parquet_file = csv_file.replace(".csv", ".parquet")
        parquet_path = os.path.join(directory, parquet_file)
        
        try:
            # Lire le fichier CSV avec l'encodage detecte
            encoding = detect_encoding(csv_path)
            try:
                encoding = "utf-8"
                df = pd.read_csv(csv_path, encoding=encoding)
            except UnicodeDecodeError:
                df = pd.read_csv(csv_path, encoding='ISO-8859-1')  # Utilise un encodage plus tolerant

            # Nettoyer les donnees dans tout le DataFrame
            df = clean_dataframe(df)

            # Sauvegarder au format Parquet
            df.to_parquet(parquet_path, index=False, engine="pyarrow")
            print(f"Converti : {csv_file} en {parquet_file}")
            
            # Archiver ou supprimer le fichier CSV original
            if archive_csv:
                os.rename(csv_path, os.path.join(archive_dir, csv_file))
            else:
                os.remove(csv_path)
        
        except UnicodeEncodeError as e:
            print(f"Erreur d'encodage dans {csv_file} : {e}")
        except Exception as e:
            print(f"Erreur lors de la conversion de {csv_file} : {e}")

    print("Tous les fichiers CSV ont ete traites.")

if __name__ == "__main__":
    # Chemin du repertoire contenant les fichiers CSV
    data_directory = "./data"
    
    # Convertir les CSV en Parquet et archiver les originaux
    convert_csv_to_parquet(data_directory, archive_csv=True)
