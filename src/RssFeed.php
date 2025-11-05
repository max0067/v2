<?php
/**
 * Classe RssFeed - Gestion des flux RSS
 */

class RssFeed
{
    private $db;

    public function __construct()
    {
        $this->db = Database::getInstance()->getConnection();
    }

    /**
     * Récupérer tous les flux RSS
     *
     * @return array
     */
    public function getAllFeeds()
    {
        $stmt = $this->db->query("
            SELECT f.*, COUNT(a.id) as article_count
            FROM rss_feeds f
            LEFT JOIN articles a ON f.id = a.feed_id
            GROUP BY f.id
            ORDER BY f.name ASC
        ");
        return $stmt->fetchAll();
    }

    /**
     * Récupérer un flux RSS par ID
     *
     * @param int $id
     * @return array|false
     */
    public function getFeedById($id)
    {
        $stmt = $this->db->prepare("SELECT * FROM rss_feeds WHERE id = ?");
        $stmt->execute([$id]);
        return $stmt->fetch();
    }

    /**
     * Ajouter un nouveau flux RSS
     *
     * @param string $name
     * @param string $url
     * @param string $category
     * @return bool
     */
    public function addFeed($name, $url, $category = 'Général')
    {
        // Validation de l'URL
        if (!filter_var($url, FILTER_VALIDATE_URL)) {
            return false;
        }

        $stmt = $this->db->prepare("
            INSERT INTO rss_feeds (name, url, category)
            VALUES (?, ?, ?)
        ");
        return $stmt->execute([$name, $url, $category]);
    }

    /**
     * Mettre à jour un flux RSS
     *
     * @param int $id
     * @param string $name
     * @param string $url
     * @param string $category
     * @return bool
     */
    public function updateFeed($id, $name, $url, $category)
    {
        // Validation de l'URL
        if (!filter_var($url, FILTER_VALIDATE_URL)) {
            return false;
        }

        $stmt = $this->db->prepare("
            UPDATE rss_feeds
            SET name = ?, url = ?, category = ?
            WHERE id = ?
        ");
        return $stmt->execute([$name, $url, $category, $id]);
    }

    /**
     * Supprimer un flux RSS
     *
     * @param int $id
     * @return bool
     */
    public function deleteFeed($id)
    {
        $stmt = $this->db->prepare("DELETE FROM rss_feeds WHERE id = ?");
        return $stmt->execute([$id]);
    }

    /**
     * Récupérer les articles d'un flux RSS
     *
     * @param string $url
     * @return array
     */
    public function fetchFeedArticles($url)
    {
        $articles = [];

        // Configuration du contexte pour la récupération
        $context = stream_context_create([
            'http' => [
                'timeout' => RSS_TIMEOUT,
                'user_agent' => RSS_USER_AGENT
            ]
        ]);

        // Désactiver temporairement les erreurs libxml
        libxml_use_internal_errors(true);

        try {
            // Charger le flux RSS
            $xml = @file_get_contents($url, false, $context);

            if ($xml === false) {
                return ['error' => 'Impossible de récupérer le flux'];
            }

            $feed = simplexml_load_string($xml);

            if ($feed === false) {
                return ['error' => 'Format RSS invalide'];
            }

            // Détecter le type de flux (RSS ou Atom)
            if (isset($feed->channel->item)) {
                // Format RSS 2.0
                foreach ($feed->channel->item as $item) {
                    $articles[] = [
                        'title' => (string) $item->title,
                        'link' => (string) $item->link,
                        'description' => (string) ($item->description ?? ''),
                        'pub_date' => $this->parseDate((string) ($item->pubDate ?? '')),
                        'guid' => (string) ($item->guid ?? $item->link)
                    ];
                }
            } elseif (isset($feed->entry)) {
                // Format Atom
                foreach ($feed->entry as $entry) {
                    $articles[] = [
                        'title' => (string) $entry->title,
                        'link' => (string) ($entry->link['href'] ?? $entry->link),
                        'description' => (string) ($entry->summary ?? $entry->content),
                        'pub_date' => $this->parseDate((string) ($entry->published ?? $entry->updated)),
                        'guid' => (string) ($entry->id ?? $entry->link)
                    ];
                }
            }

            libxml_clear_errors();
            return $articles;

        } catch (Exception $e) {
            return ['error' => 'Erreur : ' . $e->getMessage()];
        }
    }

    /**
     * Parser une date RSS/Atom
     *
     * @param string $date
     * @return string|null
     */
    private function parseDate($date)
    {
        if (empty($date)) {
            return null;
        }

        try {
            $timestamp = strtotime($date);
            if ($timestamp === false) {
                return null;
            }
            return date('Y-m-d H:i:s', $timestamp);
        } catch (Exception $e) {
            return null;
        }
    }

    /**
     * Mettre à jour la date de dernière récupération
     *
     * @param int $feedId
     * @return bool
     */
    public function updateLastFetch($feedId)
    {
        $stmt = $this->db->prepare("
            UPDATE rss_feeds
            SET last_fetch = NOW()
            WHERE id = ?
        ");
        return $stmt->execute([$feedId]);
    }
}
