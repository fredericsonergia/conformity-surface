# Surface Estimator

## API

Comment installer les dépendances et lancer l'API

### "A la main"

#### Installation des dépendances

```bash
pip3 install -r requirements.txt
```

#### Lancer le serveur

Le seveur utilise par défaut le port 8000
Tenez à vérifier que le fichier de configuration `surface.config` avec les valeurs désirées avant de lancer le serveur

```bash
uvicorn main:app --reload
```

Pour modifier le port du serveur il suffit de rajouter ces quelque lignes à la fin du fichier `main.py`situé à la racine

```python=
if __name__ == "__main__":
    uvicorn.run(app, host=0.0.0.0, port=8000)
```

Puis lancer

```bash
cd src
python3 main.py
```

### En utilisant Docker

Pour build et lancer l'image docker :

```bash
docker-compose up --build
```

### Documentation de l'API

Le swagger de l'API se trouve à l'adresse suivante

<${baseURL}/docs#/>
Ou est accessible sur le répository à la racine sur le fichier `swagger.json`

## CLI

### Lancer les tests

Pour lancer les tests sur la CLI, veuillez lancer :

```bash
python3 -m unittest src/test/cli/test_cli.py
```

Pour lancer les tests sur l'API, veuillez lancer :

```bash
python3 -m unittest src/test/app/test_app.py
```


### Lancer un calcul par batch

Il est possible d'utiliser le module pour effectuer un calcul par batch de coordinnées enregistrées dans un fichier `.csv`. Il s'agit alors d'indiquer les chemins d'accès aux fichier d'entrée et de sortie dans la section `[Batch]` du fichier de configuration (indiqué en paramètre)

```bash
cd src
python3 batchs.py -c path/to/config/file.config -m True
```

Le paramètre `-m` est facultatif et permet de forcer la mise à jour des données d'urbanisme

Le fichier d'entrée doit être de la forme suivante :

```csv
Latitude1;Longitude1
Latitide2;Longitude2
...;...
```

Pour en savoir plus sur le format de la sortie, veuillez vous référer à l'objet `SolutionCombiner` (en particulier sa méthode `str`) dans le fichier `combine_solutions.py`

### Réentrainer l'indice de confiance

```bash=
cd src/cli
python3 confidence.py --config_file=path/to/app.config train max_depth min_sample_size method save output_file

# exemple
python3 confidence.py --config_file=../app/app.config train 10 5 binary
```

plus de précisions dans le fichier `src/cli/confidence.py`

### Tester l'indice de confiance

```bash=
python3 confidence.py --config_file=path/to/app.config test save output_file

# exemple
python3 confidence.py --config_file=../app/app.config test True ../test/test_data/result.csv
```

plus de précisions dans le fichier `src/cli/confidence.py`
Les fichiers de test et d'entrainements doivent être au format de celui donné sur la dropbox (`201216_Fichier Cadastre surface.csv`). Si ce n'est pas le cas, veuillez modifier la méthode privée `_get_infos()`
