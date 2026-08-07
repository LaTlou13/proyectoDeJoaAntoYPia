-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: club_ciencias
-- ------------------------------------------------------
-- Server version	8.0.45

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
-- Dumping data for table `alumnos`
--

LOCK TABLES `alumnos` WRITE;
/*!40000 ALTER TABLE `alumnos` DISABLE KEYS */;
INSERT INTO `alumnos` VALUES (40123456,'Lucía','Gómez','5to'),(41987654,'Mateo','Rodríguez','6to');
/*!40000 ALTER TABLE `alumnos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `componentes`
--

LOCK TABLES `componentes` WRITE;
/*!40000 ALTER TABLE `componentes` DISABLE KEYS */;
INSERT INTO `componentes` VALUES (1,'Microcontrolador ESP32','Placa de desarrollo con WiFi y Bluetooth integrado',10),(2,'Motor Paso a Paso NEMA 17','Motor de alta precisión ideal para robótica',5),(3,'Sensor Ultrasónico HC-SR04','Módulo para medición de distancia',14),(4,'Kit de Robótica Completo','Incluye Arduino, chasis de auto, motores DC y sensores',5),(5,'Kit de Electrónica Avanzada','Breadboard, resistencias, condensadores, transistores y LEDs variados',7),(6,'Kit Sensores IoT','Módulos de temperatura, humedad, ultrasónico y Wi-Fi ESP8266',10),(7,'Kit Raspberry Pi 4','Placa Raspberry Pi 4 (4GB), fuente, tarjeta SD 32GB y carcasa',4),(8,'Resistencias','Set de resistencias varias',5),(9,'mi pititogrn','',1);
/*!40000 ALTER TABLE `componentes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `equipos_unicos`
--

LOCK TABLES `equipos_unicos` WRITE;
/*!40000 ALTER TABLE `equipos_unicos` DISABLE KEYS */;
INSERT INTO `equipos_unicos` VALUES (1,'PX-14','Nootebook negrita','Lab Informática (PX)','Disponible');
/*!40000 ALTER TABLE `equipos_unicos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `prestamos`
--

LOCK TABLES `prestamos` WRITE;
/*!40000 ALTER TABLE `prestamos` DISABLE KEYS */;
INSERT INTO `prestamos` VALUES (1,'Maria Pia Moreno','Alumno/a',NULL,1,'2026-07-29','2026-07-30','2026-07-29'),(2,'Maria Pia Moreno','Alumno/a',NULL,1,'2026-07-29','2026-07-31','2026-07-29'),(3,'joaquin rodriguez','Alumno/a',1,NULL,'2026-07-29','2026-07-31','2026-07-29'),(4,'joaquin rodriguez','Alumno/a',1,NULL,'2026-07-29','2026-07-31','2026-07-29'),(5,'joaquin rodriguez','Alumno/a',3,NULL,'2026-07-29','2026-07-31','2026-07-29');
/*!40000 ALTER TABLE `prestamos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-07 12:48:03
