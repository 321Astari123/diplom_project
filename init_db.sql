-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: online_library
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `book_genres`
--

DROP TABLE IF EXISTS `book_genres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book_genres` (
  `book_id` int NOT NULL,
  `genre_id` int NOT NULL,
  PRIMARY KEY (`book_id`,`genre_id`),
  KEY `genre_id` (`genre_id`),
  CONSTRAINT `book_genres_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE,
  CONSTRAINT `book_genres_ibfk_2` FOREIGN KEY (`genre_id`) REFERENCES `genres` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book_genres`
--

LOCK TABLES `book_genres` WRITE;
/*!40000 ALTER TABLE `book_genres` DISABLE KEYS */;
INSERT INTO `book_genres` VALUES (208,9),(235,9),(231,10),(219,25),(231,25),(211,26),(198,33),(205,33),(198,34),(201,36),(232,36),(199,37),(212,37),(237,37),(202,38),(232,38),(202,40),(216,40),(221,40),(208,41),(211,41),(223,41),(230,41),(235,41),(236,41),(201,42),(210,42),(217,42),(199,44),(212,44),(214,44),(230,44),(236,44),(237,44),(199,46),(212,46),(237,46),(202,47),(221,47),(210,48),(217,48),(205,49),(209,51),(218,51),(225,51),(227,51),(209,52),(224,52),(203,53),(204,53),(209,53),(218,53),(224,53),(225,53),(226,53),(227,53),(209,54),(218,54),(224,54),(225,54),(203,59),(204,59),(224,59),(227,59),(216,68),(219,68),(221,68),(211,69),(216,69),(231,69),(211,70),(212,70),(214,70),(237,70),(203,85),(224,85),(227,95),(227,99),(233,106),(233,108),(231,110),(234,112),(221,166),(226,317);
/*!40000 ALTER TABLE `book_genres` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `books` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `author` varchar(512) DEFAULT NULL,
  `file_path` varchar(255) NOT NULL,
  `cover_path` varchar(255) DEFAULT NULL,
  `file_format` varchar(10) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `average_rating` float DEFAULT '0',
  `total_ratings` int DEFAULT '0',
  `publication_year` varchar(20) DEFAULT NULL,
  `isbn` varchar(40) DEFAULT NULL,
  `language` varchar(20) DEFAULT NULL,
  `pages` int DEFAULT NULL,
  `added_by` int DEFAULT NULL,
  `is_approved` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_books_title` (`title`),
  KEY `idx_books_author` (`author`),
  KEY `added_by` (`added_by`),
  CONSTRAINT `books_ibfk_1` FOREIGN KEY (`added_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=238 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES (198,'Вы меня слышите? Встречи с жизнью и смертью фельдшера скорой помощи','Джейк  Джонс','80110140.epub',NULL,'epub','2025-05-14 16:57:52','2025-05-14 16:57:52',0,0,'2020','bca073c7-11f2-11eb-9deb-441ea152441c','ru',28,1,1),(199,'Снежная слепота','Рагнар  Йонассон','91690648.epub',NULL,'epub','2025-05-14 16:57:52','2025-05-14 16:57:52',0,0,'2010','d1dd6d82-7540-11ec-a9b2-441ea1508474','ru',55,1,1),(201,'Все закончится на нас','Колин  Гувер','98542708.epub',NULL,'epub','2025-05-14 16:57:52','2025-05-14 16:57:52',0,0,'2016','8b35f140-973d-11ea-8695-0cc47a545a1e','ru',87,1,1),(202,'Невинность с секретом','Ольга  Коротаева','93989133.epub',NULL,'epub','2025-05-14 16:57:52','2025-05-14 16:57:52',0,0,'2020','c7ce7b18-f0d4-11ec-876c-0cc47af30fe4','ru',47,1,1),(203,'Зоопарк в твоей голове. 25 психологических синдромов, которые мешают нам жить','Ирина  Тева Кумар, Сергей  Грабовский, Виктория  Ахмедянова, Майя И. Богданова, Анастасия  Афанасьева, Елена Дмитриевна Садова, Татьяна Владимировна Мужицкая, Антон  Нефедов, Игорь  Романов, Артем  Толоконин, Андрей  Кузнецов, Роман  Доронин, Юлия Леонидовна Булгакова, Сона  Лэнд, Анна  Лебедева, Марина  Гогуева, Ольга Федоровна Берг, Галина  Петракова, Ольга Викторовна Примаченко, Юлия  Пирумова, Ольга Александровна Савельева, Михаил  Лабковский, Юрий  Мурадян','99728404.epub',NULL,'epub','2025-05-14 16:57:53','2025-05-14 16:57:53',0,0,'2023','0504ea54-06ef-11ee-8496-0cc47af30fe4','ru',22,1,1),(204,'К себе нежно. Книга о том, как ценить и беречь себя','Ольга Викторовна Примаченко','109249576.epub',NULL,'epub','2025-05-14 16:58:12','2025-05-14 16:58:12',0,0,'2020','19bc1bab-11fb-11eb-b47e-0cc47a5f137d','ru',41,1,1),(205,'Слово пацана. Криминальный Татарстан 1970–2010-х. Дополненное издание','Роберт Наилевич Гараев','106451953.epub',NULL,'epub','2025-05-14 16:58:12','2025-05-14 16:58:12',0,0,'2024','09b9d56d-4958-11ed-9637-ac1f6b0b3464','ru',47,1,1),(208,'Пищеблок','Алексей Викторович Иванов','100468222.epub',NULL,'epub','2025-05-14 16:58:12','2025-05-14 16:58:12',0,0,'2018','df2cf807-f21b-11e8-8d7d-0cc47a545a1e','ru',80,1,1),(209,'Мужские правила. Отношения, секс, психология','Марк  Мэнсон','109249441.epub',NULL,'epub','2025-05-14 16:58:13','2025-05-14 16:58:12',0,0,'2016','8daafe04-459d-11ea-aa86-0cc47a5453d6','ru',60,1,1),(210,'Наша вина','Мерседес  Рон','102461743.epub',NULL,'epub','2025-05-14 16:58:13','2025-05-14 16:58:12',0,0,'2018','2dd2b9d0-32b0-11ee-8496-0cc47af30fe4','ru',109,1,1),(211,'Позже','Стивен  Кинг','109249675.epub',NULL,'epub','2025-05-14 16:58:28','2025-05-14 16:58:27',0,0,'2021','0580e80e-f9b1-11eb-8116-0cc47a5f137d','ru',59,1,1),(212,'Скрытые намерения','Майк  Омер','109251649.epub',NULL,'epub','2025-05-14 16:58:28','2025-05-14 16:58:27',0,0,'2022','0a754e52-fe29-11ed-8496-0cc47af30fe4','ru',98,1,1),(214,'Хороших девочек не убивают','Холли  Джексон','109249711.epub',NULL,'epub','2025-05-14 16:58:28','2025-05-14 16:58:27',0,0,'2018','d1b81cc5-510a-11ec-ab26-441ea1508474','ru',80,1,1),(216,'Школа чернокнижников. Железная корона','Матильда  Старр','109251196.epub',NULL,'epub','2025-05-14 16:58:28','2025-05-14 16:58:28',0,0,'2022-12-08','570ef5e5-76ff-11ed-9637-ac1f6b0b3464','ru',60,1,1),(217,'Твоя вина','Мерседес  Рон','109250935.epub',NULL,'epub','2025-05-14 16:58:28','2025-05-14 16:58:28',0,0,'2017','09fe321d-0d2d-11ed-b16e-ac1f6b0b3464','ru',103,1,1),(218,'Тонкое искусство пофигизма. Парадоксальный способ жить счастливо','Марк  Мэнсон','109355860.epub',NULL,'epub','2025-05-14 16:58:39','2025-05-14 16:58:39',0,0,'2016','3a075c14-1864-4c0f-a516-ead47cc9fac7','ru',17,1,1),(219,'Легкий заказ','Андрей Александрович Васильев','109251805.epub',NULL,'epub','2025-05-14 16:58:39','2025-05-14 16:58:39',0,0,'2023-06','91cb7e42-1b0e-11ee-8496-0cc47af30fe4','ru',83,1,1),(221,'Академия мертвых душ. Неправильная студентка','Матильда  Старр','109307017.epub',NULL,'epub','2025-05-14 16:58:39','2025-05-14 16:58:39',0,0,'2021','8bd5e1f3-c2bb-11eb-bab6-0cc47a5f137d','ru',53,1,1),(223,'Марь','Татьяна Владимировна Корсакова','109252663.epub',NULL,'epub','2025-05-14 16:58:40','2025-05-14 16:58:40',0,0,'2024','bf41d5c0-c009-11ee-8496-0cc47af30fe4','ru',83,1,1),(224,'Хочу и буду: Принять себя, полюбить жизнь и стать счастливым','Михаил  Лабковский','109355845.epub',NULL,'epub','2025-05-14 16:58:40','2025-05-14 16:58:40',0,0,'2017','2e1eb700-8896-11e7-87a0-00259059d1c2','ru',48,1,1),(225,'Тонкое искусство пофигизма. Парадоксальный способ жить счастливо','Марк  Мэнсон','109355860.epub',NULL,'epub','2025-05-14 16:58:49','2025-05-14 16:58:48',0,0,'2016','3a075c14-1864-4c0f-a516-ead47cc9fac7','ru',17,1,1),(226,'Трансерфинг себя','Вадим  Зеланд','115605964.epub',NULL,'epub','2025-05-14 16:58:49','2025-05-14 16:58:48',0,0,'2024','5ee3cb38-a728-11ef-8ce3-0cc47af30fe4','ru',7,1,1),(227,'НИ СЫ. Будь уверен в своих силах и не позволяй сомнениям мешать тебе двигаться вперед','Джен  Синсеро','111249328.epub',NULL,'epub','2025-05-14 16:58:49','2025-05-14 16:58:48',0,0,'2013','ea05aa02-f3ea-11e7-aa38-0cc47a520424','ru',51,1,1),(230,'Тихие шаги','Елена Александровна Обухова','114467095.epub',NULL,'epub','2025-05-14 16:58:49','2025-05-14 16:58:48',0,0,'2024-11-06','83d74385-9b67-11ef-8ce3-0cc47af30fe4','ru',76,1,1),(231,'Тайна мертвого ректора. Книга 2','Виктор  Дашкевич','115702111.epub',NULL,'epub','2025-05-14 16:58:49','2025-05-14 16:58:48',0,0,'2025','5bff4335-e23e-11ef-8ce3-0cc47af30fe4','ru',87,1,1),(232,'Игрок','Селина  Аллен','116282197.epub',NULL,'epub','2025-05-14 16:58:49','2025-05-14 16:58:48',0,0,'2024-09-30','43716437-df44-41a3-bd04-38b02c778d85','ru',116,1,1),(233,'Коктейли: лучшие рецепты','Сальвадор  Зимний','117029653.epub',NULL,'epub','2025-05-14 16:58:49','2025-05-14 16:58:48',0,0,NULL,'8c83131a-81fd-41ac-9b9b-2f2787c1716e','ru',35,1,1),(234,'Пустые зеркала','Елена Александровна Обухова','117637192.epub',NULL,'epub','2025-05-14 16:58:49','2025-05-14 16:58:48',0,0,'2025-02-11','41beb9aa-e797-11ef-8ce3-0cc47af30fe4','ru',69,1,1),(235,'Отель Перекресток','Андрей Александрович Васильев','118403008.epub',NULL,'epub','2025-05-14 16:58:49','2025-05-14 16:58:48',0,0,'2025-01-22','8e72b156-d3e1-11ef-8ce3-0cc47af30fe4','ru',68,1,1),(236,'Джутовая маска','Елена Александровна Обухова','114881467.epub',NULL,'epub','2025-05-14 16:58:49','2025-05-14 16:58:49',0,0,'2024-06-13','0fe17ba3-2963-11ef-8496-0cc47af30fe4','ru',70,1,1),(237,'Внутри убийцы','Майк  Омер','110695348.epub','uploads/covers/book_237.jpg','epub','2025-05-14 16:58:49','2025-05-15 18:08:24',0,0,'2018','56f128fc-f020-11e9-82ee-0cc47a5203ba','ru',79,1,1);
/*!40000 ALTER TABLE `books` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `book_id` int NOT NULL,
  `user_id` int NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `book_id` (`book_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE,
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `favorites`
--

DROP TABLE IF EXISTS `favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `favorites` (
  `id` int NOT NULL AUTO_INCREMENT,
  `book_id` int NOT NULL,
  `user_id` int NOT NULL,
  `added_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_favorite` (`book_id`,`user_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE,
  CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `favorites`
--

LOCK TABLES `favorites` WRITE;
/*!40000 ALTER TABLE `favorites` DISABLE KEYS */;
INSERT INTO `favorites` VALUES (7,237,1,'2025-05-14 21:29:52');
/*!40000 ALTER TABLE `favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genres`
--

DROP TABLE IF EXISTS `genres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genres` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=348 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genres`
--

LOCK TABLES `genres` WRITE;
/*!40000 ALTER TABLE `genres` DISABLE KEYS */;
INSERT INTO `genres` VALUES (33,'Биографии и Мемуары'),(13,'Боевая фантастика'),(11,'Боевое фэнтези'),(10,'Героическая фантастика'),(25,'Городское фэнтези'),(69,'Детективная фантастика'),(49,'Документальная литература'),(51,'Зарубежная психология'),(26,'Зарубежное фэнтези'),(46,'Зарубежные детективы'),(42,'Зарубежные любовные романы'),(110,'Историческое фэнтези'),(27,'Книги для детей: прочее'),(68,'Книги про волшебников'),(12,'Космическая фантастика'),(106,'Кулинария'),(53,'Личностный рост'),(166,'Любовно-фантастические романы'),(40,'Любовное фэнтези'),(34,'Медицина'),(14,'Научная фантастика'),(85,'Общая психология'),(48,'Остросюжетные любовные романы'),(112,'Очерки'),(37,'Полицейские детективы'),(47,'Попаданцы'),(59,'Психотерапия и консультирование'),(108,'Руководства'),(99,'Самосовершенствование'),(52,'Секс и семейная психология'),(9,'Современная русская литература'),(44,'Современные детективы'),(36,'Современные любовные романы'),(54,'Социальная психология'),(70,'Триллеры'),(41,'Ужасы и Мистика'),(95,'Управление, подбор персонала'),(317,'Эзотерика'),(38,'Эротическая литература');
/*!40000 ALTER TABLE `genres` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `progress`
--

DROP TABLE IF EXISTS `progress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `progress` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `book_id` int NOT NULL,
  `progress` float DEFAULT '0',
  `last_read` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_book` (`user_id`,`book_id`),
  KEY `book_id` (`book_id`),
  CONSTRAINT `progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `progress_ibfk_2` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `progress`
--

LOCK TABLES `progress` WRITE;
/*!40000 ALTER TABLE `progress` DISABLE KEYS */;
INSERT INTO `progress` VALUES (49,1,203,85.6753,'2025-05-14 18:29:44'),(50,1,236,1.3073,'2025-05-14 18:28:15'),(51,1,221,1.0989,'2025-05-15 16:50:56'),(52,1,237,0.714286,'2025-05-15 16:50:59'),(53,1,232,1.15628,'2025-05-15 17:03:26');
/*!40000 ALTER TABLE `progress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratings`
--

DROP TABLE IF EXISTS `ratings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ratings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `book_id` int NOT NULL,
  `rating` int NOT NULL,
  `review` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_book` (`user_id`,`book_id`),
  KEY `book_id` (`book_id`),
  CONSTRAINT `ratings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ratings_ibfk_2` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ratings_chk_1` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratings`
--

LOCK TABLES `ratings` WRITE;
/*!40000 ALTER TABLE `ratings` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reset_passwords`
--

DROP TABLE IF EXISTS `reset_passwords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reset_passwords` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `password` varchar(255) NOT NULL,
  `reset_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `reset_passwords_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reset_passwords`
--

LOCK TABLES `reset_passwords` WRITE;
/*!40000 ALTER TABLE `reset_passwords` DISABLE KEYS */;
/*!40000 ALTER TABLE `reset_passwords` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_admin` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `avatar_path` varchar(255) DEFAULT NULL,
  `bio` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin@library.com','$2b$12$H5eIQ7cGJi.OAwfzBxsWNeGiPat1g2abPSgFuw4AhRVHBfAFJN/zu',1,'2025-05-04 10:24:26','avatars/avatar_1_cxwc5fjtwkA.jpg','супер мега ультра скуфчанский'),(8,'Admin2','admin2@library.com','$2b$12$FyKJz0wXj9mjHFmQFHRAC..qgVgKZClkwRVrbE7hmIftWCUMy0Rh6',1,'2025-05-14 12:50:36',NULL,NULL),(12,'Astariik','user1@book.ly','$2b$12$ubS9KnRCzY/rUd7pMQKZueuRRxPiEcAf0ZwrZS2TZzYNjBlmIFdV2',0,'2025-05-15 18:11:01',NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `views`
--

DROP TABLE IF EXISTS `views`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `views` (
  `id` int NOT NULL AUTO_INCREMENT,
  `book_id` int NOT NULL,
  `user_id` int NOT NULL,
  `viewed_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_view` (`book_id`,`user_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `views_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE,
  CONSTRAINT `views_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `views`
--

LOCK TABLES `views` WRITE;
/*!40000 ALTER TABLE `views` DISABLE KEYS */;
INSERT INTO `views` VALUES (52,203,1,'2025-05-14 19:59:17'),(55,221,1,'2025-05-15 19:50:52'),(56,237,1,'2025-05-15 21:10:13'),(58,237,8,'2025-05-14 21:30:15'),(63,237,12,'2025-05-15 21:11:07');
/*!40000 ALTER TABLE `views` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-15 21:12:21
