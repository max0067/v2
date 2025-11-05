#!/usr/bin/env php
<?php
/**
 * Script CRON - Mise à jour automatique des flux RSS
 *
 * À ajouter dans la crontab pour exécution automatique :
 * 0 */6 * * * /usr/bin/php /chemin/vers/v2/cron/update-feeds.php >> /var/log/rss-update.log 2>&1
 *
 * Cette commande exécute le script toutes les 6 heures
 */

// Chemin absolu vers le fichier de configuration
$configPath = dirname(__DIR__) . '/config/config.php';

if (!file_exists($configPath)) {
    die("Erreur : Fichier de configuration introuvable.\n");
}

require_once $configPath;
require_once dirname(__DIR__) . '/src/Database.php';
require_once dirname(__DIR__) . '/src/RssFeed.php';
require_once dirname(__DIR__) . '/src/Article.php';

// Désactiver les limites de temps pour les longues opérations
set_time_limit(0);

echo "========================================\n";
echo "Début de la mise à jour des flux RSS\n";
echo "Date : " . date('Y-m-d H:i:s') . "\n";
echo "========================================\n\n";

try {
    $feedModel = new RssFeed();
    $articleModel = new Article();

    $feeds = $feedModel->getAllFeeds();
    $totalFeeds = count($feeds);
    $totalArticles = 0;
    $errors = [];

    echo "Nombre de flux à traiter : {$totalFeeds}\n\n";

    foreach ($feeds as $index => $feed) {
        $feedNumber = $index + 1;
        echo "[{$feedNumber}/{$totalFeeds}] Traitement du flux : {$feed['name']}\n";
        echo "  URL : {$feed['url']}\n";

        // Récupérer les articles du flux
        $articles = $feedModel->fetchFeedArticles($feed['url']);

        if (isset($articles['error'])) {
            $errorMsg = $articles['error'];
            $errors[] = [
                'feed' => $feed['name'],
                'error' => $errorMsg
            ];
            echo "  ❌ ERREUR : {$errorMsg}\n\n";
            continue;
        }

        // Ajouter chaque article à la base de données
        $addedCount = 0;
        foreach ($articles as $article) {
            if ($articleModel->addArticle($feed['id'], $article)) {
                $addedCount++;
            }
        }

        // Mettre à jour la date de dernière récupération
        $feedModel->updateLastFetch($feed['id']);

        $totalArticles += $addedCount;
        echo "  ✓ {$addedCount} article(s) ajouté(s)\n\n";
    }

    // Nettoyage des anciens articles (plus de 90 jours)
    echo "Nettoyage des anciens articles...\n";
    $deletedCount = $articleModel->deleteOldArticles(90);
    echo "✓ {$deletedCount} ancien(s) article(s) supprimé(s)\n\n";

    echo "========================================\n";
    echo "Résumé de la mise à jour\n";
    echo "========================================\n";
    echo "Flux traités : {$totalFeeds}\n";
    echo "Nouveaux articles : {$totalArticles}\n";
    echo "Articles supprimés : {$deletedCount}\n";

    if (count($errors) > 0) {
        echo "\nErreurs rencontrées :\n";
        foreach ($errors as $error) {
            echo "  - {$error['feed']} : {$error['error']}\n";
        }
    }

    echo "\nMise à jour terminée avec succès !\n";
    echo "Date de fin : " . date('Y-m-d H:i:s') . "\n";

    exit(0);

} catch (Exception $e) {
    echo "\n❌ ERREUR CRITIQUE : " . $e->getMessage() . "\n";
    echo "Trace :\n" . $e->getTraceAsString() . "\n";
    exit(1);
}
