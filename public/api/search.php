<?php
/**
 * API - Rechercher des articles par mot-clé
 */

header('Content-Type: application/json');

require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../src/Database.php';
require_once __DIR__ . '/../../src/Article.php';

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Méthode non autorisée']);
    exit;
}

try {
    $keyword = $_GET['q'] ?? '';

    if (empty($keyword)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'Mot-clé requis (paramètre q)']);
        exit;
    }

    $articleModel = new Article();
    $articles = $articleModel->searchArticles($keyword);

    echo json_encode([
        'success' => true,
        'count' => count($articles),
        'articles' => $articles
    ]);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Erreur serveur : ' . $e->getMessage()
    ]);
}
