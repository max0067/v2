<?php
/**
 * Page d'accueil - Affichage des articles RSS
 */

require_once __DIR__ . '/../config/config.php';
require_once __DIR__ . '/../src/Database.php';
require_once __DIR__ . '/../src/Article.php';

$articleModel = new Article();
$stats = $articleModel->getStats();
$articles = $articleModel->getAllArticles(100);
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo APP_NAME; ?> - Accueil</title>

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
            <li class="active">
                <a href="index.php">
                    <i class="bi bi-house-door"></i>
                    <span>Accueil</span>
                </a>
            </li>
            <li>
                <a href="manage-feeds.php">
                    <i class="bi bi-rss"></i>
                    <span>Gérer les flux</span>
                </a>
            </li>
        </ul>
        <div class="sidebar-footer">
            <div class="stats">
                <div class="stat-item">
                    <i class="bi bi-file-text"></i>
                    <span><?php echo number_format($stats['total_articles']); ?> articles</span>
                </div>
                <div class="stat-item">
                    <i class="bi bi-rss-fill"></i>
                    <span><?php echo $stats['total_feeds']; ?> flux</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <!-- Top Bar -->
        <div class="topbar">
            <div class="search-box">
                <i class="bi bi-search"></i>
                <input type="text" id="searchInput" placeholder="Rechercher des articles...">
            </div>
            <button class="btn btn-primary" id="refreshBtn">
                <i class="bi bi-arrow-clockwise"></i>
                Actualiser les flux
            </button>
        </div>

        <!-- Articles Grid -->
        <div class="content-wrapper">
            <div class="content-header">
                <h2>Derniers articles</h2>
                <p class="text-muted">
                    <?php echo count($articles); ?> article(s) affiché(s)
                    <?php if ($stats['last_article_date']): ?>
                        · Dernier article : <?php echo date('d/m/Y à H:i', strtotime($stats['last_article_date'])); ?>
                    <?php endif; ?>
                </p>
            </div>

            <div id="articlesContainer" class="articles-grid">
                <?php if (empty($articles)): ?>
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle"></i>
                        Aucun article disponible. Cliquez sur "Actualiser les flux" pour récupérer les derniers articles.
                    </div>
                <?php else: ?>
                    <?php foreach ($articles as $article): ?>
                        <div class="article-card" data-category="<?php echo htmlspecialchars($article['category']); ?>">
                            <div class="article-header">
                                <span class="badge bg-primary"><?php echo htmlspecialchars($article['category']); ?></span>
                                <span class="article-date">
                                    <i class="bi bi-clock"></i>
                                    <?php
                                    $date = $article['pub_date'] ?? $article['created_at'];
                                    echo date('d/m/Y', strtotime($date));
                                    ?>
                                </span>
                            </div>
                            <h3 class="article-title">
                                <a href="<?php echo htmlspecialchars($article['link']); ?>" target="_blank">
                                    <?php echo htmlspecialchars($article['title']); ?>
                                </a>
                            </h3>
                            <?php if (!empty($article['description'])): ?>
                                <p class="article-description">
                                    <?php echo htmlspecialchars(substr(strip_tags($article['description']), 0, 200)); ?>...
                                </p>
                            <?php endif; ?>
                            <div class="article-footer">
                                <span class="article-source">
                                    <i class="bi bi-rss"></i>
                                    <?php echo htmlspecialchars($article['feed_name']); ?>
                                </span>
                                <a href="<?php echo htmlspecialchars($article['link']); ?>" target="_blank" class="btn btn-sm btn-outline-primary">
                                    Lire l'article <i class="bi bi-arrow-right"></i>
                                </a>
                            </div>
                        </div>
                    <?php endforeach; ?>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <!-- Loading Overlay -->
    <div id="loadingOverlay" class="loading-overlay" style="display: none;">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Chargement...</span>
        </div>
        <p class="mt-3">Récupération des flux RSS en cours...</p>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="assets/js/app.js"></script>
</body>
</html>
