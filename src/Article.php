<?php
/**
 * Classe Article - Gestion des articles RSS
 */

class Article
{
    private $db;

    public function __construct()
    {
        $this->db = Database::getInstance()->getConnection();
    }

    /**
     * Récupérer tous les articles avec pagination
     *
     * @param int $limit
     * @param int $offset
     * @return array
     */
    public function getAllArticles($limit = 50, $offset = 0)
    {
        $stmt = $this->db->prepare("
            SELECT a.*, f.name as feed_name, f.category
            FROM articles a
            INNER JOIN rss_feeds f ON a.feed_id = f.id
            ORDER BY COALESCE(a.pub_date, a.created_at) DESC
            LIMIT ? OFFSET ?
        ");
        $stmt->execute([$limit, $offset]);
        return $stmt->fetchAll();
    }

    /**
     * Compter le nombre total d'articles
     *
     * @return int
     */
    public function countArticles()
    {
        $stmt = $this->db->query("SELECT COUNT(*) as total FROM articles");
        return (int) $stmt->fetch()['total'];
    }

    /**
     * Rechercher des articles par mot-clé
     *
     * @param string $keyword
     * @param int $limit
     * @return array
     */
    public function searchArticles($keyword, $limit = 100)
    {
        $searchTerm = '%' . $keyword . '%';

        $stmt = $this->db->prepare("
            SELECT a.*, f.name as feed_name, f.category
            FROM articles a
            INNER JOIN rss_feeds f ON a.feed_id = f.id
            WHERE a.title LIKE ?
               OR a.description LIKE ?
               OR f.name LIKE ?
            ORDER BY COALESCE(a.pub_date, a.created_at) DESC
            LIMIT ?
        ");

        $stmt->execute([$searchTerm, $searchTerm, $searchTerm, $limit]);
        return $stmt->fetchAll();
    }

    /**
     * Ajouter un article
     *
     * @param int $feedId
     * @param array $data
     * @return bool
     */
    public function addArticle($feedId, $data)
    {
        try {
            $stmt = $this->db->prepare("
                INSERT INTO articles (feed_id, title, link, description, pub_date, guid)
                VALUES (?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    description = VALUES(description)
            ");

            return $stmt->execute([
                $feedId,
                $data['title'] ?? '',
                $data['link'] ?? '',
                $data['description'] ?? '',
                $data['pub_date'] ?? null,
                $data['guid'] ?? null
            ]);
        } catch (PDOException $e) {
            // Ignorer les erreurs de doublons
            if ($e->getCode() == 23000) {
                return true;
            }
            return false;
        }
    }

    /**
     * Supprimer les anciens articles (plus de X jours)
     *
     * @param int $days
     * @return int Nombre d'articles supprimés
     */
    public function deleteOldArticles($days = 90)
    {
        $stmt = $this->db->prepare("
            DELETE FROM articles
            WHERE created_at < DATE_SUB(NOW(), INTERVAL ? DAY)
        ");
        $stmt->execute([$days]);
        return $stmt->rowCount();
    }

    /**
     * Récupérer les articles récents par catégorie
     *
     * @param string $category
     * @param int $limit
     * @return array
     */
    public function getArticlesByCategory($category, $limit = 20)
    {
        $stmt = $this->db->prepare("
            SELECT a.*, f.name as feed_name, f.category
            FROM articles a
            INNER JOIN rss_feeds f ON a.feed_id = f.id
            WHERE f.category = ?
            ORDER BY COALESCE(a.pub_date, a.created_at) DESC
            LIMIT ?
        ");
        $stmt->execute([$category, $limit]);
        return $stmt->fetchAll();
    }

    /**
     * Récupérer les statistiques des articles
     *
     * @return array
     */
    public function getStats()
    {
        $stmt = $this->db->query("
            SELECT
                COUNT(*) as total_articles,
                COUNT(DISTINCT feed_id) as total_feeds,
                MAX(created_at) as last_article_date
            FROM articles
        ");
        return $stmt->fetch();
    }
}
