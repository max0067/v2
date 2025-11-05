<?php
/**
 * API - Mettre à jour un flux RSS existant
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
    if (empty($data['id']) || empty($data['name']) || empty($data['url'])) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'ID, nom et URL requis']);
        exit;
    }

    $feedModel = new RssFeed();

    // Mettre à jour le flux
    $result = $feedModel->updateFeed(
        $data['id'],
        $data['name'],
        $data['url'],
        $data['category'] ?? 'Général'
    );

    if ($result) {
        echo json_encode([
            'success' => true,
            'message' => 'Flux mis à jour avec succès'
        ]);
    } else {
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'error' => 'URL invalide ou erreur lors de la mise à jour'
        ]);
    }

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Erreur serveur : ' . $e->getMessage()
    ]);
}
