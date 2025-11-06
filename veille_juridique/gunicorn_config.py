"""
Configuration Gunicorn pour l'application de veille juridique
"""
import multiprocessing

# Adresse et port d'écoute
bind = "0.0.0.0:8000"

# Nombre de workers (processus)
# Formule recommandée : (2 x CPU cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Type de worker
worker_class = "sync"

# Timeout pour les requêtes (en secondes)
timeout = 120

# Nombre maximum de requêtes par worker avant redémarrage
max_requests = 1000
max_requests_jitter = 50

# Fichiers de logs
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"

# Nom du processus
proc_name = "veille_juridique"

# Activer le rechargement automatique en développement
reload = False

# Préchargement de l'application (économie de mémoire)
preload_app = True

# Limite de taille des requêtes (10 MB)
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
