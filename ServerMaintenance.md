# 1. Démarrer le service
Pour démarrer ton service Gunicorn (ton application Flask), utilise la commande suivante :
```
sudo systemctl start TLwebsite.service
```

Cela démarre le service TLwebsite.service qui lance Gunicorn et ton application Flask.

# 2. Arrêter le service
Si tu veux arrêter ton application, utilise la commande :
```
sudo systemctl stop TLwebsite.service
```

Cela arrête le service Gunicorn, et donc ton application Flask.

# 3. Redémarrer le service
Si tu veux redémarrer le service, par exemple après avoir modifié des fichiers ou effectué des mises à jour, utilise la commande suivante :
```
sudo systemctl restart TLwebsite.service
```

Cela arrête puis redémarre le service Gunicorn.

# 4. Activer le service au démarrage
Si tu veux que ton service Gunicorn se lance automatiquement lors du démarrage de ton serveur, active le service avec la commande suivante :
```
sudo systemctl enable TLwebsite.service
```

Cela configure systemd pour démarrer automatiquement ton application Flask à chaque démarrage du serveur.

# 5. Désactiver le service au démarrage
Si tu veux désactiver le démarrage automatique du service au démarrage de ton serveur, utilise la commande :
```
sudo systemctl disable TLwebsite.service
```

Cela empêche systemd de démarrer ton application Flask au démarrage du serveur.

6. Vérifier le statut du service
Pour vérifier si ton service est en cours d'exécution ou obtenir des informations supplémentaires sur son état, utilise la commande suivante :
```
sudo systemctl status TLwebsite.service
```

Cela te montrera si ton service est actif, inactif, ou si une erreur est survenue. Par exemple, tu pourrais voir des informations comme ceci :

```
● TLwebsite.service - Gunicorn instance pour Flask
   Loaded: loaded (/etc/systemd/system/TLwebsite.service; enabled; preset: enabled)
   Active: active (running) since ... (date/heure)
   Main PID: 1234 (gunicorn)
   ...
```

# 7. Consulter les logs du service
Si tu rencontres des problèmes ou des erreurs avec ton service, tu peux consulter les journaux pour obtenir plus de détails sur ce qui se passe avec la commande suivante :

```
journalctl -u TLwebsite.service -xe
```

Cela t'affichera les logs détaillés liés au service TLwebsite.service, ce qui peut être utile pour diagnostiquer les erreurs.

# 8. Recharger systemd après modification du service
Si tu apportes des modifications à ton fichier de service (par exemple, changement de la commande ExecStart), tu dois recharger systemd pour qu'il prenne en compte les changements :
```
sudo systemctl daemon-reload
```

Cela recharge les fichiers de configuration des services systemd après des modifications.

Résumé des commandes
Voici un résumé des commandes à utiliser pour gérer ton service Gunicorn sous systemd :

Action	Commande
Démarrer le service	sudo systemctl start TLwebsite.service
Arrêter le service	sudo systemctl stop TLwebsite.service
Redémarrer le service	sudo systemctl restart TLwebsite.service
Activer le service au démarrage	sudo systemctl enable TLwebsite.service
Désactiver le service au démarrage	sudo systemctl disable TLwebsite.service
Vérifier le statut du service	sudo systemctl status TLwebsite.service
Consulter les logs du service	journalctl -u TLwebsite.service -xe
Recharger systemd après modification	sudo systemctl daemon-reload