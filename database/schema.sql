-- =====================================================
-- Schéma de base de données pour Veille Juridique RSS
-- Version 2.0 - Flask/SQLAlchemy
-- =====================================================

-- Création de la base de données
CREATE DATABASE IF NOT EXISTS dusselle_rss
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE dusselle_rss;

-- Table des flux RSS
CREATE TABLE IF NOT EXISTS rss_feeds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT 'Nom du flux RSS',
    url VARCHAR(500) NOT NULL UNIQUE COMMENT 'URL du flux RSS',
    category VARCHAR(100) DEFAULT 'Général' COMMENT 'Catégorie du flux',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Flux actif ou non',
    last_fetch DATETIME DEFAULT NULL COMMENT 'Date de dernière récupération',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de création',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Date de mise à jour',

    INDEX idx_category (category),
    INDEX idx_is_active (is_active),
    INDEX idx_last_fetch (last_fetch)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Flux RSS sources';

-- Table des articles
CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    feed_id INT NOT NULL COMMENT 'ID du flux RSS source',
    title VARCHAR(500) NOT NULL COMMENT 'Titre de l\'article',
    link VARCHAR(1000) NOT NULL COMMENT 'URL de l\'article',
    description TEXT COMMENT 'Description/résumé',
    content MEDIUMTEXT COMMENT 'Contenu complet',
    author VARCHAR(255) DEFAULT NULL COMMENT 'Auteur de l\'article',
    published_date DATETIME DEFAULT NULL COMMENT 'Date de publication',
    guid VARCHAR(500) UNIQUE COMMENT 'Identifiant unique de l\'article',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date d\'ajout dans la BDD',

    FOREIGN KEY (feed_id) REFERENCES rss_feeds(id) ON DELETE CASCADE,

    INDEX idx_feed_published (feed_id, published_date),
    INDEX idx_guid (guid),
    INDEX idx_created (created_at),
    INDEX idx_published (published_date),

    FULLTEXT INDEX ft_search (title, description, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Articles récupérés depuis les flux RSS';

-- Insertion de quelques flux RSS de démonstration (sources juridiques françaises)
INSERT IGNORE INTO rss_feeds (name, url, category, is_active) VALUES
    ('Legifrance - Actualités', 'https://www.legifrance.gouv.fr/rss/actualites.xml', 'Législation', TRUE),
    ('Journal Officiel (JORF)', 'https://www.legifrance.gouv.fr/rss/jorf.xml', 'Journal Officiel', TRUE),
    ('Dalloz Actualité', 'https://www.dalloz-actualite.fr/feed', 'Doctrine', TRUE);

-- Afficher les tables créées
SHOW TABLES;

-- Afficher les flux insérés
SELECT '✅ Flux RSS par défaut insérés:' AS status;
SELECT id, name, category FROM rss_feeds;
