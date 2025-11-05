<?php
/**
 * API - Récupérer les articles depuis tous les flux RSS
 */

header('Content-Type: application/json');

require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../src/Database.php';
require_once __DIR__ . '/../../src/RssFeed.php';
require_once __DIR__ . '/../../src/Article.php';

try {
    $feedModel = new RssFeed();
    $articleModel = new Article();

    $feeds = $feedModel->getAllFeeds();
    $results = [
        'success' => true,
        'feeds_processed' => 0,
        'articles_added' => 0,
        'errors' => []
    ];

    foreach ($feeds as $feed) {
        // Récupérer les articles du flux
        $articles = $feedModel->fetchFeedArticles($feed['url']);

        if (isset($articles['error'])) {
            $results['errors'][] = [
                'feed' => $feed['name'],
                'error' => $articles['error']
            ];
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

        $results['feeds_processed']++;
        $results['articles_added'] += $addedCount;
    }

    $results['message'] = sprintf(
        '%d flux traité(s), %d nouvel(aux) article(s) ajouté(s)',
        $results['feeds_processed'],
        $results['articles_added']
    );

    echo json_encode($results);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Erreur serveur : ' . $e->getMessage()
    ]);
}
