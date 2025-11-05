<?php
/**
 * API - Ajouter un nouveau flux RSS
 */

header('Content-Type: application/json');

require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../src/Database.php';
require_once __DIR__ . '/../../src/RssFeed.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Méthode non autorisée']);
    exit;
}

try {
    $data = json_decode(file_get_contents('php://input'), true);

    // Validation des données
    if (empty($data['name']) || empty($data['url'])) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'Nom et URL requis']);
        exit;
    }

    $feedModel = new RssFeed();

    // Ajouter le flux
    $result = $feedModel->addFeed(
        $data['name'],
        $data['url'],
        $data['category'] ?? 'Général'
    );

    if ($result) {
        echo json_encode([
            'success' => true,
            'message' => 'Flux ajouté avec succès'
        ]);
    } else {
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'error' => 'URL invalide ou erreur lors de l\'ajout'
        ]);
    }

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Erreur serveur : ' . $e->getMessage()
    ]);
}
