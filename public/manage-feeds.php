<?php
/**
 * Page de gestion des flux RSS
 */

require_once __DIR__ . '/../config/config.php';
require_once __DIR__ . '/../src/Database.php';
require_once __DIR__ . '/../src/RssFeed.php';

$feedModel = new RssFeed();
$feeds = $feedModel->getAllFeeds();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo APP_NAME; ?> - Gestion des flux</title>

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-header">
            <i class="bi bi-newspaper"></i>
            <h4><?php echo APP_NAME; ?></h4>
        </div>
        <ul class="sidebar-menu">
            <li>
                <a href="index.php">
                    <i class="bi bi-house-door"></i>
                    <span>Accueil</span>
                </a>
            </li>
            <li class="active">
                <a href="manage-feeds.php">
                    <i class="bi bi-rss"></i>
                    <span>Gérer les flux</span>
                </a>
            </li>
        </ul>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <!-- Top Bar -->
        <div class="topbar">
            <h2>Gestion des flux RSS</h2>
            <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#addFeedModal">
                <i class="bi bi-plus-circle"></i>
                Ajouter un flux
            </button>
        </div>

        <!-- Feeds Table -->
        <div class="content-wrapper">
            <div class="card">
                <div class="card-body">
                    <?php if (empty($feeds)): ?>
                        <div class="alert alert-info">
                            <i class="bi bi-info-circle"></i>
                            Aucun flux RSS configuré. Cliquez sur "Ajouter un flux" pour commencer.
                        </div>
                    <?php else: ?>
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Nom</th>
                                        <th>URL</th>
                                        <th>Catégorie</th>
                                        <th>Articles</th>
                                        <th>Dernière màj</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php foreach ($feeds as $feed): ?>
                                        <tr>
                                            <td>
                                                <strong><?php echo htmlspecialchars($feed['name']); ?></strong>
                                            </td>
                                            <td>
                                                <a href="<?php echo htmlspecialchars($feed['url']); ?>" target="_blank" class="text-muted small">
                                                    <?php echo htmlspecialchars(substr($feed['url'], 0, 50)); ?>...
                                                </a>
                                            </td>
                                            <td>
                                                <span class="badge bg-primary">
                                                    <?php echo htmlspecialchars($feed['category']); ?>
                                                </span>
                                            </td>
                                            <td><?php echo $feed['article_count']; ?></td>
                                            <td>
                                                <?php
                                                if ($feed['last_fetch']) {
                                                    echo date('d/m/Y H:i', strtotime($feed['last_fetch']));
                                                } else {
                                                    echo '<span class="text-muted">Jamais</span>';
                                                }
                                                ?>
                                            </td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary edit-feed"
                                                        data-id="<?php echo $feed['id']; ?>"
                                                        data-name="<?php echo htmlspecialchars($feed['name']); ?>"
                                                        data-url="<?php echo htmlspecialchars($feed['url']); ?>"
                                                        data-category="<?php echo htmlspecialchars($feed['category']); ?>">
                                                    <i class="bi bi-pencil"></i>
                                                </button>
                                                <button class="btn btn-sm btn-outline-danger delete-feed"
                                                        data-id="<?php echo $feed['id']; ?>"
                                                        data-name="<?php echo htmlspecialchars($feed['name']); ?>">
                                                    <i class="bi bi-trash"></i>
                                                </button>
                                            </td>
                                        </tr>
                                    <?php endforeach; ?>
                                </tbody>
                            </table>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Feed Modal -->
    <div class="modal fade" id="addFeedModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Ajouter un flux RSS</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="addFeedForm">
                        <div class="mb-3">
                            <label for="feedName" class="form-label">Nom du flux</label>
                            <input type="text" class="form-control" id="feedName" required>
                        </div>
                        <div class="mb-3">
                            <label for="feedUrl" class="form-label">URL du flux RSS</label>
                            <input type="url" class="form-control" id="feedUrl" required
                                   placeholder="https://exemple.com/rss">
                        </div>
                        <div class="mb-3">
                            <label for="feedCategory" class="form-label">Catégorie</label>
                            <input type="text" class="form-control" id="feedCategory" value="Général">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annuler</button>
                    <button type="button" class="btn btn-primary" id="saveFeedBtn">Enregistrer</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Edit Feed Modal -->
    <div class="modal fade" id="editFeedModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Modifier un flux RSS</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="editFeedForm">
                        <input type="hidden" id="editFeedId">
                        <div class="mb-3">
                            <label for="editFeedName" class="form-label">Nom du flux</label>
                            <input type="text" class="form-control" id="editFeedName" required>
                        </div>
                        <div class="mb-3">
                            <label for="editFeedUrl" class="form-label">URL du flux RSS</label>
                            <input type="url" class="form-control" id="editFeedUrl" required>
                        </div>
                        <div class="mb-3">
                            <label for="editFeedCategory" class="form-label">Catégorie</label>
                            <input type="text" class="form-control" id="editFeedCategory">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annuler</button>
                    <button type="button" class="btn btn-primary" id="updateFeedBtn">Mettre à jour</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Alert Container -->
    <div id="alertContainer" style="position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 400px;"></div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="assets/js/app.js"></script>
</body>
</html>
