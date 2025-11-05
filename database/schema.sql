-- =====================================================
-- Schéma de base de données pour Veille Juridique RSS
-- =====================================================

-- Création de la base de données
CREATE DATABASE IF NOT EXISTS dusselle_rss
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE dusselle_rss;

-- Table des flux RSS
CREATE TABLE IF NOT EXISTS rss_feeds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'Général',
    is_active TINYINT(1) DEFAULT 1,
    last_fetch DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des articles
CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    feed_id INT NOT NULL,
    title VARCHAR(500) NOT NULL,
    link TEXT NOT NULL,
    description TEXT,
    pub_date DATETIME NULL,
    guid VARCHAR(500) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feed_id) REFERENCES rss_feeds(id) ON DELETE CASCADE,
    INDEX idx_feed_id (feed_id),
    INDEX idx_pub_date (pub_date),
    INDEX idx_created_at (created_at),
    UNIQUE KEY unique_guid (guid(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertion de quelques flux RSS de démonstration (sources juridiques françaises)
INSERT INTO rss_feeds (name, url, category) VALUES
    ('Legifrance - Actualités', 'https://www.legifrance.gouv.fr/rss/actualites.xml', 'Législation'),
    ('Journal Officiel - JORF', 'https://www.legifrance.gouv.fr/rss/jorf.xml', 'Journal Officiel'),
    ('Dalloz Actualité', 'https://www.dalloz-actualite.fr/feed', 'Doctrine'),
    ('Conseil d\'État', 'https://www.conseil-etat.fr/rss', 'Jurisprudence');

-- Afficher les tables créées
SHOW TABLES;
