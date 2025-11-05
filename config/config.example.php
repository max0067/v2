<?php
/**
 * Exemple de configuration
 *
 * Copiez ce fichier en config.php et modifiez les valeurs
 * Commande : cp config.example.php config.php
 */

// Configuration de la base de données
define('DB_HOST', 'localhost');
define('DB_NAME', 'dusselle_rss');
define('DB_USER', 'votre_utilisateur');
define('DB_PASS', 'votre_mot_de_passe');
define('DB_CHARSET', 'utf8mb4');

// Configuration de l'application
define('APP_NAME', 'Veille Juridique RSS');
define('APP_URL', 'https://dusselle.fr');
define('TIMEZONE', 'Europe/Paris');

// Paramètres RSS
define('RSS_TIMEOUT', 10);
define('RSS_USER_AGENT', 'Mozilla/5.0 (compatible; RSS Reader)');

// Sécurité
define('SESSION_LIFETIME', 7200);

// Configuration du fuseau horaire
date_default_timezone_set(TIMEZONE);

// Gestion des erreurs (à désactiver en production)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Démarrage de la session
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}
