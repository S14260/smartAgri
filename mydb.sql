/*
 Navicat Premium Dump SQL

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80402 (8.4.2)
 Source Host           : localhost:3306
 Source Schema         : mydb

 Target Server Type    : MySQL
 Target Server Version : 80402 (8.4.2)
 File Encoding         : 65001

 Date: 13/09/2025 22:20:19
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admin
-- ----------------------------
DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `issuper` int NULL DEFAULT 0,
  `sex` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `age` int NULL DEFAULT NULL,
  `phone` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of admin
-- ----------------------------
INSERT INTO `admin` VALUES (1, 'admin', 'admin', 1, '男', 35, '76053434623');
INSERT INTO `admin` VALUES (2, 'Zitao', 'KpvUryXqtn', 0, '男', 34, '13053452364');
INSERT INTO `admin` VALUES (3, 'Jiehong', 'tMjH1JSLXP', 1, '男', 34, '7605545582');
INSERT INTO `admin` VALUES (4, 'Jiehong', 'XdLRLsdXBL', 1, '男', 41, '76968200986');
INSERT INTO `admin` VALUES (5, 'Anqi', 'qE6XS3MyfK', 1, '女', 29, '19352836014');
INSERT INTO `admin` VALUES (6, 'Jialun', 'RXaLVGpQos', 0, '男', 36, '19839538835');
INSERT INTO `admin` VALUES (7, 'Rui', 't2rl0uvbvR', 1, '男', 40, '13415516937');
INSERT INTO `admin` VALUES (8, 'Zitao', 'iVO4JUqfAJ', 0, '男', 41, '16503817627');
INSERT INTO `admin` VALUES (9, 'Lu', 'C3w0jO9jZp', 0, '女', 28, '15693589712');

-- ----------------------------
-- Table structure for admin_plots
-- ----------------------------
DROP TABLE IF EXISTS `admin_plots`;
CREATE TABLE `admin_plots`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '地块ID',
  `plot_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '地块名称',
  `last_crop` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '上季作物',
  `current_crop` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '本季作物',
  `contact_person` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '联系人',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '电话',
  `soil_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '土壤类型',
  `irrigation_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '灌溉条件',
  `land_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '土地类型',
  `shape_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '图形类型（polygon 或 circle）',
  `coordinates` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '坐标数据（JSON字符串）',
  `area` double NULL DEFAULT NULL COMMENT '面积（亩）',
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 46 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '地块信息表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of admin_plots
-- ----------------------------
INSERT INTO `admin_plots` VALUES (38, '张北一', '玉米', '玉米', 'sss', '17732218744', '砂质土', '滴灌', '流转', 'polygon', '{\"shapeType\":\"polygon\",\"latlngs\":[{\"lat\":41.27409741329659,\"lng\":114.88993406295778},{\"lat\":41.27229118891676,\"lng\":114.88716602325441},{\"lat\":41.272379888602266,\"lng\":114.88695144653322},{\"lat\":41.27169447880924,\"lng\":114.88579273223878},{\"lat\":41.27133967561908,\"lng\":114.88579273223878},{\"lat\":41.27079133962337,\"lng\":114.88489151000978},{\"lat\":41.270936487835144,\"lng\":114.88471984863283},{\"lat\":41.270759084421364,\"lng\":114.88439798355104},{\"lat\":41.270517169898426,\"lng\":114.8845160007477},{\"lat\":41.270501042231686,\"lng\":114.88419413566591},{\"lat\":41.27008978538383,\"lng\":114.88389372825624},{\"lat\":41.26902534386553,\"lng\":114.88226294517519},{\"lat\":41.268694718346495,\"lng\":114.88216638565065},{\"lat\":41.26842053981689,\"lng\":114.88135099411012},{\"lat\":41.26763025408357,\"lng\":114.88212347030641},{\"lat\":41.26779153766317,\"lng\":114.8824453353882},{\"lat\":41.26730768572921,\"lng\":114.88358259201051},{\"lat\":41.26990431576171,\"lng\":114.88742351531984},{\"lat\":41.271065508196905,\"lng\":114.88922595977785},{\"lat\":41.27261373264994,\"lng\":114.89182233810426}]}', 312.16, '河北省张家口市张北县郝家营乡郑家营');
INSERT INTO `admin_plots` VALUES (39, '张北二', '玉米', '玉米', 'sss', '17732218744', '黏质土', '渠灌', '承包', 'polygon', '{\"shapeType\":\"polygon\",\"latlngs\":[{\"lat\":41.27470732297565,\"lng\":114.87339019775392},{\"lat\":41.274159484501745,\"lng\":114.87233877182008},{\"lat\":41.27435283978222,\"lng\":114.87182378768922},{\"lat\":41.274159484501745,\"lng\":114.87139463424684},{\"lat\":41.273788885279934,\"lng\":114.87175941467287},{\"lat\":41.27259650829194,\"lng\":114.86980676651002},{\"lat\":41.2718391764632,\"lng\":114.87186670303345},{\"lat\":41.27377277222255,\"lng\":114.87499952316284},{\"lat\":41.274578420218944,\"lng\":114.87409830093385},{\"lat\":41.274433404313406,\"lng\":114.87377643585206}]}', 98.96, '河北省张家口市张北县郝家营乡207国道');
INSERT INTO `admin_plots` VALUES (40, '张北三', '水稻', '水稻', 'sss', '17732218744', '壤土', '渠灌', '开垦荒地', 'polygon', '{\"shapeType\":\"polygon\",\"latlngs\":[{\"lat\":41.2733057851047,\"lng\":114.84069943428041},{\"lat\":41.27169444775572,\"lng\":114.83833909034729},{\"lat\":41.27065511406588,\"lng\":114.84054923057558},{\"lat\":41.27087265039337,\"lng\":114.84075307846071},{\"lat\":41.27072762625559,\"lng\":114.84110713005067},{\"lat\":41.27205700212689,\"lng\":114.84239459037782}]}', 78.49, '河北省张家口市张北县郝家营乡张北龙鹏农机服务专业合作社');
INSERT INTO `admin_plots` VALUES (41, '张北四号地', '玉米', '水稻', 'ss', '17732218744', '黏质土', '渠灌', '开垦荒地', 'polygon', '{\"shapeType\":\"polygon\",\"latlngs\":[{\"lat\":41.26723786612363,\"lng\":114.87477302547634},{\"lat\":41.264445844101395,\"lng\":114.87043857570826},{\"lat\":41.26284804368873,\"lng\":114.87224102016627},{\"lat\":41.265898356005735,\"lng\":114.87676858898341}]}', 168.43, '河北省张家口市张北县郝家营乡');
INSERT INTO `admin_plots` VALUES (45, '天津工业大学', '甜菜', '甜菜', '张三', '17732218744', '壤土', '自然降水', '承包', 'polygon', '{\"shapeType\":\"polygon\",\"latlngs\":[{\"lat\":39.07084558555999,\"lng\":117.09863241492918},{\"lat\":39.07084558555999,\"lng\":117.11176352932698},{\"lat\":39.05805028838467,\"lng\":117.11184935360406},{\"lat\":39.058516824330056,\"lng\":117.09863241492918}]}', 2388.3, '天津市西青区精武镇西苑西路天开高教科创园西青园');

-- ----------------------------
-- Table structure for dormitory
-- ----------------------------
DROP TABLE IF EXISTS `dormitory`;
CREATE TABLE `dormitory`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `dormitoryid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `floor` int NULL DEFAULT NULL,
  `bed` int NULL DEFAULT NULL,
  `price` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 31 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of dormitory
-- ----------------------------
INSERT INTO `dormitory` VALUES (1, '@6#211', 2, 8, 651);
INSERT INTO `dormitory` VALUES (2, '@6#212', 2, 8, 651);
INSERT INTO `dormitory` VALUES (3, '@6#213', 2, 8, 651);
INSERT INTO `dormitory` VALUES (4, '@6#214', 2, 7, 651);
INSERT INTO `dormitory` VALUES (5, '@6#215', 2, 7, 651);
INSERT INTO `dormitory` VALUES (6, '@6#216', 2, 8, 651);
INSERT INTO `dormitory` VALUES (7, '6#217', 2, 7, 651);
INSERT INTO `dormitory` VALUES (8, '6#218', 2, 8, 651);
INSERT INTO `dormitory` VALUES (9, '6#219', 2, 8, 651);
INSERT INTO `dormitory` VALUES (10, '6#220', 2, 7, 651);
INSERT INTO `dormitory` VALUES (11, '6#311', 3, 8, 651);
INSERT INTO `dormitory` VALUES (12, '6#312', 3, 8, 651);
INSERT INTO `dormitory` VALUES (13, '6#313', 3, 8, 651);
INSERT INTO `dormitory` VALUES (14, '6#314', 3, 7, 651);
INSERT INTO `dormitory` VALUES (15, '6#315', 3, 7, 651);
INSERT INTO `dormitory` VALUES (16, '6#316', 3, 8, 651);
INSERT INTO `dormitory` VALUES (17, '6#317', 3, 7, 651);
INSERT INTO `dormitory` VALUES (18, '6#318', 3, 7, 651);
INSERT INTO `dormitory` VALUES (19, '6#319', 3, 8, 651);
INSERT INTO `dormitory` VALUES (20, '6#320', 3, 7, 651);
INSERT INTO `dormitory` VALUES (21, '附中#311', 3, 8, 651);
INSERT INTO `dormitory` VALUES (22, '附中#312', 3, 8, 651);
INSERT INTO `dormitory` VALUES (23, '附中#313', 3, 8, 651);
INSERT INTO `dormitory` VALUES (24, '附中#314', 3, 7, 651);
INSERT INTO `dormitory` VALUES (25, '附中#315', 3, 7, 651);
INSERT INTO `dormitory` VALUES (26, '附中#316', 3, 8, 651);
INSERT INTO `dormitory` VALUES (27, '附中#317', 3, 7, 651);
INSERT INTO `dormitory` VALUES (28, '附中#318', 3, 7, 651);
INSERT INTO `dormitory` VALUES (29, '附中#319', 3, 8, 651);
INSERT INTO `dormitory` VALUES (30, '附中#320', 3, 7, 651);

-- ----------------------------
-- Table structure for punch_record
-- ----------------------------
DROP TABLE IF EXISTS `punch_record`;
CREATE TABLE `punch_record`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `plot_id` bigint NULL DEFAULT NULL,
  `plot_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `longitude` double NULL DEFAULT NULL,
  `latitude` double NULL DEFAULT NULL,
  `punch_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` bigint NULL DEFAULT NULL,
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `status` int NULL DEFAULT NULL COMMENT '打卡状态：1有效 2无效',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 56 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of punch_record
-- ----------------------------
INSERT INTO `punch_record` VALUES (1, 14, '软件学院', 117.10337905505072, 39.07023657599896, '2025-05-27 07:54:51', NULL, NULL, NULL);
INSERT INTO `punch_record` VALUES (2, 14, '软件学院', 117.1033797567965, 39.07021913739897, '2025-05-27 08:00:22', NULL, NULL, NULL);
INSERT INTO `punch_record` VALUES (3, 14, '软件学院', 117.10335492574535, 39.070010456210206, '2025-05-27 08:33:57', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (4, 14, '软件学院', 117.10335492574535, 39.070010456210206, '2025-05-27 08:34:04', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (5, 14, '软件学院', 117.10339142470508, 39.07028639787185, '2025-05-27 08:36:03', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (6, 14, '软件学院', 117.10335492574535, 39.070010456210206, '2025-05-27 08:38:17', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (7, 14, '软件学院', 117.10334621404205, 39.06996269670587, '2025-05-27 08:41:54', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (8, 14, '软件学院', 117.103458, 39.069523, '2025-05-27 08:51:04', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (9, 14, '软件学院', 117.103435, 39.06955, '2025-05-28 05:07:57', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (10, 14, '软件学院', 117.10338837184885, 39.07021994340487, '2025-05-28 05:21:41', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (11, 14, '软件学院', 117.10339481848843, 39.07025459965426, '2025-05-28 05:41:03', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (12, 14, '软件学院', 117.10339481848843, 39.07025459965426, '2025-05-28 05:41:05', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (13, 14, '软件学院', 117.10339481848843, 39.07025459965426, '2025-05-28 05:41:07', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (14, 14, '软件学院', 117.10339481848843, 39.07025459965426, '2025-05-28 05:41:13', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (15, 14, '软件学院', 117.10339481848843, 39.07025459965426, '2025-05-28 05:41:19', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (16, 14, '软件学院', 117.10327831267331, 39.06950914479955, '2025-05-28 05:44:02', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (17, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:15', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (18, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:15', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (19, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:26', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (20, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:29', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (21, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:29', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (22, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:29', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (23, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:29', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (24, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:30', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (25, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:30', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (26, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:30', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (27, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:31', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (28, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:31', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (29, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:34', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (30, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:34', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (31, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:35', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (32, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:35', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (33, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:35', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (34, 14, '软件学院', 117.10335174038971, 39.0699528409489, '2025-05-28 05:44:45', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (35, 14, '软件学院', 117.10335492574535, 39.070010456210206, '2025-05-28 05:47:11', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (36, 14, '软件学院', 117.10333847232782, 39.06994927985801, '2025-05-28 05:49:44', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (37, 14, '软件学院', 117.10338639002887, 39.07027517008664, '2025-05-29 06:00:38', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (38, 14, '软件学院', 117.10338724603662, 39.070236669757875, '2025-05-29 06:06:03', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (39, 14, '软件学院', 117.10335689559072, 39.070037238009974, '2025-05-29 06:12:39', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (40, 14, '软件学院', 117.10334811189082, 39.06989365357469, '2025-05-29 06:16:32', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (41, 14, '软件学院', 117.10338987368631, 39.07026427405012, '2025-05-29 06:20:53', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (42, 14, '软件学院', 117.10338639002887, 39.07027517008664, '2025-05-29 08:13:04', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (43, 14, '软件学院', 117.10338639002887, 39.07027517008664, '2025-05-29 08:13:19', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (44, 14, '软件学院', 117.10339095290614, 39.07025564687748, '2025-05-29 08:33:15', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (45, 14, '软件学院', 117.10338705850364, 39.07025901260339, '2025-05-29 10:24:47', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (46, 14, '软件学院', 117.10338705850364, 39.07025901260339, '2025-05-29 10:25:09', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (47, 14, '软件学院', 117.103489, 39.069617, '2025-05-29 10:26:33', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (48, 14, '软件学院', 117.10339852748415, 39.07024412414015, '2025-05-29 13:12:20', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (49, 14, '软件学院', 117.10336354789061, 39.070062485589204, '2025-05-29 13:23:28', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (50, 14, '软件学院', 117.10336652351076, 39.07010490875837, '2025-05-31 05:08:11', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (51, 14, '软件学院', 117.10340164417191, 39.07025935774954, '2025-05-31 06:21:23', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (52, 14, '软件学院', 117.10341664294552, 39.06901065152333, '2025-06-08 07:53:02', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (53, 14, '软件学院', 117.10341664294552, 39.06901065152333, '2025-06-08 07:53:05', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (54, 14, '软件学院', 117.10336443017304, 39.06908159597515, '2025-06-08 08:28:07', NULL, NULL, 1);
INSERT INTO `punch_record` VALUES (55, 16, '福源小区', 117.10162342647278, 39.065760779802616, '2025-07-01 14:12:56', NULL, NULL, 1);

-- ----------------------------
-- Table structure for register
-- ----------------------------
DROP TABLE IF EXISTS `register`;
CREATE TABLE `register`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `studentid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `studentname` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `dormotoryid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `grade` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `comeout` int NULL DEFAULT NULL,
  `reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `runtime` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `phone` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `isout` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1001 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of register
-- ----------------------------
INSERT INTO `register` VALUES (1, '2020111114', '江詩涵', '6#223', '计科本201班', 0, '回家探亲', '2023-01-12', '14716562820', 0);
INSERT INTO `register` VALUES (2, '2020111118', '余子异', '6#223', '计科本202班', 1, '生病', '2023-01-06', '216488089', 1);
INSERT INTO `register` VALUES (3, '2020111119', '何子异', '6#216', '计科本202班', 0, '出去理由', '2023-02-03', '13744803282', 1);
INSERT INTO `register` VALUES (4, '2020111115', '马安琪', '6#213', '计科本201班', 1, '生病', '2023-01-06', '286436984', 1);
INSERT INTO `register` VALUES (5, '2020111112', '徐致远', '6#223', '大数据本201班', 0, '生病', '2023-01-02', '282132983', 0);
INSERT INTO `register` VALUES (6, '2020111116', '廖宇宁', '6#216', '计科本201班', 1, '出去理由', '2023-01-16', '17706830925', 0);
INSERT INTO `register` VALUES (7, '2020111117', '孟岚', '6#223', '计科本201班', 1, '回家探亲', '2023-02-13', '209602498', 0);
INSERT INTO `register` VALUES (8, '2020111116', '严岚', '6#213', '大数据本201班', 0, '生病', '2023-02-14', '15904099857', 1);
INSERT INTO `register` VALUES (9, '2020111114', '崔震南', '6#223', '计科本201班', 0, '回家探亲', '2023-01-21', '2081371238', 1);
INSERT INTO `register` VALUES (10, '2020111119', '莫璐', '6#211', '计科本202班', 1, '回家探亲', '2023-01-21', '76065149583', 0);
INSERT INTO `register` VALUES (11, '2020111112', '莫安琪', '6#213', '计科本202班', 1, '回家探亲', '2023-02-18', '101885768', 0);
INSERT INTO `register` VALUES (12, '2020111121', '孟秀英', '6#216', '计科本202班', 1, '出去理由', '2023-01-12', '18032355200', 1);
INSERT INTO `register` VALUES (13, '2020111117', '莫嘉伦', '6#215', '大数据本201班', 0, '回家探亲', '2023-01-01', '7608176508', 0);
INSERT INTO `register` VALUES (14, '2020111117', '袁杰宏', '6#213', '计科本202班', 1, '出去理由', '2023-01-24', '107378358', 1);
INSERT INTO `register` VALUES (15, '2020111116', '于秀英', '6#216', '计科本202班', 0, '出去理由', '2023-01-26', '14116221740', 0);
INSERT INTO `register` VALUES (16, '2020111112', '贾震南', '6#215', '大数据本201班', 0, '生病', '2023-01-16', '7604732806', 1);
INSERT INTO `register` VALUES (17, '2020111118', '陶宇宁', '6#223', '大数据本201班', 1, '回家探亲', '2023-02-12', '219568370', 0);
INSERT INTO `register` VALUES (18, '2020111117', '曾睿', '6#223', '计科本201班', 1, '回家探亲', '2023-01-10', '15622887783', 1);
INSERT INTO `register` VALUES (19, '2020111111', '徐詩涵', '6#215', '计科本201班', 1, '出去理由', '2023-01-10', '17043326461', 0);
INSERT INTO `register` VALUES (20, '2020111119', '黄子韬', '6#211', '计科本201班', 1, '生病', '2023-02-04', '2024492562', 1);
INSERT INTO `register` VALUES (21, '2020111113', '崔杰宏', '6#216', '计科本202班', 1, '生病', '2023-01-09', '214827124', 1);
INSERT INTO `register` VALUES (22, '2020111112', '宋嘉伦', '6#213', '计科本202班', 1, '出去理由', '2023-01-31', '7692872349', 0);
INSERT INTO `register` VALUES (23, '2020111114', '廖宇宁', '6#223', '计科本201班', 1, '回家探亲', '2023-01-01', '2875926657', 0);
INSERT INTO `register` VALUES (24, '2020111114', '许安琪', '6#211', '计科本202班', 0, '出去理由', '2023-02-14', '15451425354', 0);
INSERT INTO `register` VALUES (25, '2020111118', '胡致远', '6#211', '大数据本201班', 0, '生病', '2023-02-17', '17823060871', 0);
INSERT INTO `register` VALUES (26, '2020111116', '唐璐', '6#216', '计科本202班', 1, '生病', '2023-02-09', '1082271065', 1);
INSERT INTO `register` VALUES (27, '2020111113', '徐安琪', '6#213', '计科本201班', 0, '生病', '2023-01-27', '15843317822', 0);
INSERT INTO `register` VALUES (28, '2020111117', '蒋致远', '6#216', '计科本201班', 0, '出去理由', '2023-01-29', '18927855371', 0);
INSERT INTO `register` VALUES (29, '2020111112', '熊子异', '6#211', '大数据本201班', 1, '出去理由', '2023-01-02', '105638652', 1);
INSERT INTO `register` VALUES (30, '2020111112', '高嘉伦', '6#216', '大数据本201班', 0, '出去理由', '2023-02-15', '2092934778', 0);
INSERT INTO `register` VALUES (31, '2020111117', '金震南', '6#216', '计科本201班', 1, '生病', '2023-01-20', '13067890932', 1);
INSERT INTO `register` VALUES (32, '2020111120', '刘子韬', '6#223', '计科本201班', 1, '回家探亲', '2023-01-13', '205834144', 1);
INSERT INTO `register` VALUES (33, '2020111115', '邓詩涵', '6#223', '计科本202班', 0, '回家探亲', '2023-01-24', '14220731551', 0);
INSERT INTO `register` VALUES (34, '2020111115', '夏震南', '6#216', '计科本202班', 0, '回家探亲', '2023-01-02', '283338186', 1);
INSERT INTO `register` VALUES (35, '2020111118', '段岚', '6#211', '大数据本201班', 1, '出去理由', '2023-01-12', '13557326483', 0);
INSERT INTO `register` VALUES (36, '2020111121', '曾安琪', '6#223', '计科本202班', 1, '生病', '2023-01-06', '2150688674', 0);
INSERT INTO `register` VALUES (37, '2020111121', '孙子韬', '6#213', '计科本201班', 0, '回家探亲', '2023-02-08', '7600310987', 0);
INSERT INTO `register` VALUES (38, '2020111112', '曾詩涵', '6#223', '计科本202班', 1, '回家探亲', '2023-02-05', '1053930529', 1);
INSERT INTO `register` VALUES (39, '2020111112', '邓睿', '6#216', '大数据本201班', 0, '回家探亲', '2023-01-25', '18180310924', 0);
INSERT INTO `register` VALUES (40, '2020111114', '廖宇宁', '6#216', '计科本202班', 0, '生病', '2023-01-12', '75577547203', 0);
INSERT INTO `register` VALUES (41, '2020111115', '邹子异', '6#211', '计科本202班', 0, '回家探亲', '2023-02-01', '14917055167', 0);
INSERT INTO `register` VALUES (42, '2020111119', '曾璐', '6#213', '计科本202班', 1, '生病', '2023-01-25', '214972874', 1);
INSERT INTO `register` VALUES (43, '2020111116', '蔡睿', '6#223', '大数据本201班', 0, '出去理由', '2023-02-07', '17584270616', 0);
INSERT INTO `register` VALUES (44, '2020111111', '朱子异', '6#223', '计科本202班', 1, '出去理由', '2023-02-01', '7600187377', 0);
INSERT INTO `register` VALUES (45, '2020111118', '冯云熙', '6#211', '大数据本201班', 1, '生病', '2023-02-14', '19436648104', 1);
INSERT INTO `register` VALUES (46, '2020111113', '莫杰宏', '6#216', '计科本201班', 1, '生病', '2023-01-28', '19309451160', 1);
INSERT INTO `register` VALUES (47, '2020111118', '范嘉伦', '6#211', '计科本202班', 0, '生病', '2023-01-05', '14693783720', 0);
INSERT INTO `register` VALUES (48, '2020111119', '朱宇宁', '6#213', '计科本202班', 1, '回家探亲', '2023-01-26', '2119987808', 0);
INSERT INTO `register` VALUES (49, '2020111117', '朱宇宁', '6#223', '计科本202班', 1, '出去理由', '2023-02-06', '13764540417', 1);
INSERT INTO `register` VALUES (50, '2020111120', '袁安琪', '6#213', '计科本201班', 1, '回家探亲', '2023-01-01', '75570748463', 1);
INSERT INTO `register` VALUES (51, '2020111116', '高宇宁', '6#211', '计科本202班', 0, '出去理由', '2023-01-17', '76092305852', 1);
INSERT INTO `register` VALUES (52, '2020111118', '魏云熙', '6#215', '计科本202班', 1, '回家探亲', '2023-02-02', '17271075667', 0);
INSERT INTO `register` VALUES (53, '2020111111', '熊岚', '6#216', '计科本201班', 1, '回家探亲', '2023-01-17', '76962009025', 0);
INSERT INTO `register` VALUES (54, '2020111120', '钟睿', '6#223', '大数据本201班', 0, '回家探亲', '2023-01-29', '1078717626', 1);
INSERT INTO `register` VALUES (55, '2020111116', '郝云熙', '6#215', '计科本201班', 0, '出去理由', '2023-02-10', '2802741982', 0);
INSERT INTO `register` VALUES (56, '2020111119', '萧致远', '6#215', '大数据本201班', 1, '出去理由', '2023-01-12', '7556137459', 0);
INSERT INTO `register` VALUES (57, '2020111120', '严睿', '6#211', '大数据本201班', 0, '生病', '2023-01-14', '19672205421', 1);
INSERT INTO `register` VALUES (58, '2020111116', '宋安琪', '6#215', '计科本201班', 1, '出去理由', '2023-02-03', '19679959719', 1);
INSERT INTO `register` VALUES (59, '2020111113', '阎致远', '6#213', '大数据本201班', 1, '出去理由', '2023-01-17', '17592502056', 1);
INSERT INTO `register` VALUES (60, '2020111117', '蔡子韬', '6#213', '大数据本201班', 1, '出去理由', '2023-01-20', '13858937372', 0);
INSERT INTO `register` VALUES (61, '2020111116', '汤秀英', '6#215', '计科本201班', 0, '生病', '2023-02-10', '7694170309', 1);
INSERT INTO `register` VALUES (62, '2020111113', '宋子韬', '6#215', '大数据本201班', 0, '出去理由', '2023-02-16', '75500036413', 1);
INSERT INTO `register` VALUES (63, '2020111114', '黄宇宁', '6#215', '大数据本201班', 0, '生病', '2023-02-02', '14357626543', 1);
INSERT INTO `register` VALUES (64, '2020111117', '蒋子异', '6#211', '大数据本201班', 1, '生病', '2023-01-20', '17812753709', 0);
INSERT INTO `register` VALUES (65, '2020111120', '胡宇宁', '6#211', '计科本201班', 1, '回家探亲', '2023-02-13', '7555885270', 1);
INSERT INTO `register` VALUES (66, '2020111115', '刘杰宏', '6#213', '计科本201班', 1, '生病', '2023-01-25', '1086210017', 1);
INSERT INTO `register` VALUES (67, '2020111117', '丁震南', '6#215', '计科本202班', 0, '生病', '2023-02-10', '215775297', 1);
INSERT INTO `register` VALUES (68, '2020111119', '常杰宏', '6#213', '计科本201班', 0, '生病', '2023-02-06', '16331402845', 0);
INSERT INTO `register` VALUES (69, '2020111115', '黄秀英', '6#216', '计科本202班', 1, '生病', '2023-01-14', '13065032003', 0);
INSERT INTO `register` VALUES (70, '2020111119', '汤詩涵', '6#211', '计科本201班', 1, '出去理由', '2023-01-13', '17539700618', 0);
INSERT INTO `register` VALUES (71, '2020111112', '苏杰宏', '6#223', '大数据本201班', 0, '出去理由', '2023-01-05', '16337248135', 0);
INSERT INTO `register` VALUES (72, '2020111120', '薛詩涵', '6#216', '计科本202班', 1, '回家探亲', '2023-01-22', '2829184830', 1);
INSERT INTO `register` VALUES (73, '2020111116', '郑致远', '6#211', '计科本202班', 0, '生病', '2023-02-03', '19430913254', 0);
INSERT INTO `register` VALUES (74, '2020111121', '李安琪', '6#216', '计科本202班', 0, '生病', '2023-01-11', '7606752175', 1);
INSERT INTO `register` VALUES (75, '2020111117', '顾杰宏', '6#215', '计科本201班', 0, '出去理由', '2023-02-04', '15318418260', 1);
INSERT INTO `register` VALUES (76, '2020111116', '秦云熙', '6#216', '大数据本201班', 1, '回家探亲', '2023-02-17', '7690783050', 1);
INSERT INTO `register` VALUES (77, '2020111121', '魏致远', '6#223', '大数据本201班', 0, '生病', '2023-01-15', '13943034682', 1);
INSERT INTO `register` VALUES (78, '2020111119', '袁云熙', '6#216', '计科本202班', 0, '回家探亲', '2023-01-09', '1017653103', 0);
INSERT INTO `register` VALUES (79, '2020111115', '韩云熙', '6#215', '计科本202班', 0, '生病', '2023-01-11', '14847349300', 0);
INSERT INTO `register` VALUES (80, '2020111112', '沈震南', '6#213', '计科本202班', 0, '生病', '2023-02-13', '75583295073', 1);
INSERT INTO `register` VALUES (81, '2020111112', '廖杰宏', '6#215', '大数据本201班', 0, '出去理由', '2023-02-06', '2141333010', 1);
INSERT INTO `register` VALUES (82, '2020111113', '高安琪', '6#213', '大数据本201班', 0, '出去理由', '2023-02-04', '76955971819', 0);
INSERT INTO `register` VALUES (83, '2020111116', '龙宇宁', '6#215', '计科本202班', 1, '生病', '2023-01-25', '13937574636', 1);
INSERT INTO `register` VALUES (84, '2020111120', '戴杰宏', '6#213', '计科本202班', 1, '出去理由', '2023-01-19', '16253779486', 0);
INSERT INTO `register` VALUES (85, '2020111112', '董晓明', '6#223', '大数据本201班', 0, '出去理由', '2023-02-11', '14902485222', 1);
INSERT INTO `register` VALUES (86, '2020111111', '任詩涵', '6#213', '计科本201班', 0, '出去理由', '2023-02-15', '7605299598', 1);
INSERT INTO `register` VALUES (87, '2020111119', '谢安琪', '6#215', '计科本202班', 0, '回家探亲', '2023-01-21', '18803502219', 0);
INSERT INTO `register` VALUES (88, '2020111113', '王杰宏', '6#216', '计科本201班', 0, '生病', '2023-02-04', '16952345997', 1);
INSERT INTO `register` VALUES (89, '2020111113', '吴秀英', '6#216', '计科本202班', 0, '生病', '2023-01-10', '13094148151', 1);
INSERT INTO `register` VALUES (90, '2020111115', '谭璐', '6#211', '计科本201班', 0, '生病', '2023-01-14', '19319605760', 0);
INSERT INTO `register` VALUES (91, '2020111119', '丁致远', '6#215', '计科本202班', 0, '生病', '2023-02-01', '287835108', 0);
INSERT INTO `register` VALUES (92, '2020111112', '孟震南', '6#213', '计科本201班', 1, '回家探亲', '2023-02-08', '18902494796', 1);
INSERT INTO `register` VALUES (629, '2020111113', '段震南', '6#211', '计科本202班', 0, '回家探亲', '2023-02-05', '14161272915', 0);
INSERT INTO `register` VALUES (630, '2020111115', '廖睿', '6#215', '计科本201班', 0, '出去理由', '2023-01-30', '17912837484', 0);
INSERT INTO `register` VALUES (631, '2020111119', '江子韬', '6#223', '计科本202班', 1, '生病', '2023-01-17', '19272341442', 1);
INSERT INTO `register` VALUES (632, '2020111119', '郝岚', '6#211', '计科本202班', 1, '出去理由', '2023-01-30', '15808816090', 1);
INSERT INTO `register` VALUES (633, '2020111115', '廖睿', '6#215', '计科本202班', 0, '生病', '2023-01-10', '13521164715', 0);
INSERT INTO `register` VALUES (634, '2020111117', '尹云熙', '6#215', '大数据本201班', 0, '生病', '2023-02-15', '18293898221', 0);
INSERT INTO `register` VALUES (635, '2020111119', '萧宇宁', '6#215', '计科本202班', 1, '生病', '2023-01-08', '208549503', 1);
INSERT INTO `register` VALUES (636, '2020111116', '邱子异', '6#223', '计科本201班', 1, '出去理由', '2023-01-02', '1048539710', 0);
INSERT INTO `register` VALUES (637, '2020111121', '周晓明', '6#216', '大数据本201班', 0, '生病', '2023-01-23', '75532394194', 1);
INSERT INTO `register` VALUES (638, '2020111113', '周安琪', '6#213', '计科本201班', 0, '回家探亲', '2023-01-18', '75516418320', 0);
INSERT INTO `register` VALUES (639, '2020111114', '廖子韬', '6#216', '计科本202班', 0, '出去理由', '2023-02-03', '76029783957', 1);
INSERT INTO `register` VALUES (640, '2020111115', '谢璐', '6#215', '计科本201班', 1, '出去理由', '2023-01-11', '281461436', 1);
INSERT INTO `register` VALUES (641, '2020111120', '朱璐', '6#216', '大数据本201班', 0, '生病', '2023-02-01', '7606673834', 1);
INSERT INTO `register` VALUES (642, '2020111119', '严宇宁', '6#215', '大数据本201班', 1, '回家探亲', '2023-01-04', '17925626953', 0);
INSERT INTO `register` VALUES (643, '2020111113', '任震南', '6#223', '大数据本201班', 1, '回家探亲', '2023-01-19', '76039010783', 1);
INSERT INTO `register` VALUES (644, '2020111116', '魏詩涵', '6#213', '计科本202班', 1, '生病', '2023-02-13', '7601825806', 1);
INSERT INTO `register` VALUES (645, '2020111114', '袁杰宏', '6#223', '大数据本201班', 1, '回家探亲', '2023-01-19', '15161784876', 1);
INSERT INTO `register` VALUES (646, '2020111118', '石子韬', '6#211', '计科本201班', 0, '生病', '2023-01-20', '7698795026', 0);
INSERT INTO `register` VALUES (647, '2020111115', '唐璐', '6#211', '计科本202班', 1, '生病', '2023-01-25', '7609317962', 0);
INSERT INTO `register` VALUES (648, '2020111121', '程宇宁', '6#215', '计科本201班', 1, '回家探亲', '2023-01-28', '7608580706', 0);
INSERT INTO `register` VALUES (649, '2020111120', '唐震南', '6#223', '计科本202班', 1, '回家探亲', '2023-01-07', '18965348525', 0);
INSERT INTO `register` VALUES (650, '2020111114', '吴睿', '6#215', '计科本201班', 1, '出去理由', '2023-01-15', '7697151305', 0);
INSERT INTO `register` VALUES (651, '2020111115', '汤嘉伦', '6#211', '计科本202班', 1, '出去理由', '2023-01-17', '18290675055', 1);
INSERT INTO `register` VALUES (652, '2020111114', '郝子异', '6#223', '计科本202班', 1, '生病', '2023-01-30', '17301540332', 1);
INSERT INTO `register` VALUES (653, '2020111112', '王詩涵', '6#223', '计科本202班', 0, '生病', '2023-02-09', '286731416', 0);
INSERT INTO `register` VALUES (654, '2020111119', '吴嘉伦', '6#216', '计科本202班', 0, '回家探亲', '2023-02-12', '15346380916', 0);
INSERT INTO `register` VALUES (655, '2020111119', '孟杰宏', '6#211', '计科本202班', 0, '出去理由', '2023-02-15', '19685462525', 0);
INSERT INTO `register` VALUES (656, '2020111117', '黄晓明', '6#216', '计科本202班', 0, '回家探亲', '2023-01-27', '214453417', 0);
INSERT INTO `register` VALUES (657, '2020111118', '马安琪', '6#215', '大数据本201班', 0, '生病', '2023-01-02', '16589983094', 1);
INSERT INTO `register` VALUES (658, '2020111117', '高宇宁', '6#215', '计科本202班', 1, '出去理由', '2023-02-10', '7697320652', 1);
INSERT INTO `register` VALUES (659, '2020111113', '孙子异', '6#215', '计科本201班', 1, '回家探亲', '2023-01-28', '217138733', 1);
INSERT INTO `register` VALUES (660, '2020111113', '郑震南', '6#211', '计科本201班', 1, '回家探亲', '2023-01-29', '285735701', 1);
INSERT INTO `register` VALUES (661, '2020111114', '董致远', '6#215', '计科本202班', 0, '出去理由', '2023-01-19', '17438272743', 1);
INSERT INTO `register` VALUES (662, '2020111117', '宋璐', '6#216', '计科本201班', 1, '出去理由', '2023-01-08', '7699526861', 1);
INSERT INTO `register` VALUES (663, '2020111112', '周詩涵', '6#215', '计科本202班', 1, '回家探亲', '2023-01-25', '7698899822', 1);
INSERT INTO `register` VALUES (664, '2020111115', '卢致远', '6#215', '大数据本201班', 1, '回家探亲', '2023-02-13', '7693182622', 0);
INSERT INTO `register` VALUES (665, '2020111112', '董宇宁', '6#213', '大数据本201班', 0, '生病', '2023-01-30', '203737793', 1);
INSERT INTO `register` VALUES (666, '2020111118', '邱云熙', '6#223', '计科本201班', 1, '生病', '2023-02-06', '1086485845', 0);
INSERT INTO `register` VALUES (667, '2020111119', '范安琪', '6#213', '计科本201班', 1, '出去理由', '2023-01-12', '16308134810', 1);
INSERT INTO `register` VALUES (1000, '2020111114', '董岚', '6#216', '大数据本201班', 1, '出去理由', '2023-01-22', '282628939', 0);

-- ----------------------------
-- Table structure for student
-- ----------------------------
DROP TABLE IF EXISTS `student`;
CREATE TABLE `student`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `studentid` int NULL DEFAULT NULL,
  `studentname` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `sex` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `age` int NULL DEFAULT NULL,
  `department` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `grade` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `dormitory` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1003 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of student
-- ----------------------------
INSERT INTO `student` VALUES (1, 213, '3', '男', 1, '23', '123', '13', '153');
INSERT INTO `student` VALUES (2, 2020111186, '向安琪', '女', 23, '化学与工程学院', '计科本201班', '7601630587', '6#216');
INSERT INTO `student` VALUES (3, 2020111307, '林杰宏', '男', 20, '化学与工程学院', '计科本202班', '2850380967', '6#216');
INSERT INTO `student` VALUES (4, 2020111277, '方嘉伦', '男', 23, '信息工程学院', '化学本201班', '19372606959', '6#212');
INSERT INTO `student` VALUES (5, 2020111163, '钱詩涵', '女', 22, '信息工程学院', '大数据202班', '76002525018', '6#211');
INSERT INTO `student` VALUES (6, 2020111156, '程晓明', '男', 19, '信息工程学院', '大数据202班', '13737182016', '6#215');
INSERT INTO `student` VALUES (7, 2020111301, '梁震南', '男', 18, '信息工程学院', '化学本201班', '15882855764', '6#217');
INSERT INTO `student` VALUES (8, 2020111251, '周子韬', '男', 22, '信息工程学院', '计科本202班', '2166847033', '6#214');
INSERT INTO `student` VALUES (9, 2020111164, '韦睿', '男', 22, '预科教育学院', '大数据202班', '14512888556', '6#211');
INSERT INTO `student` VALUES (10, 2020111253, '范安琪', '女', 17, '化学与工程学院', '大数据202班', '14120930640', '6#212');
INSERT INTO `student` VALUES (11, 2020111129, '侯安琪', '女', 22, '化学与工程学院', '大数据201班', '14278262584', '6#212');
INSERT INTO `student` VALUES (12, 2020111160, '方睿', '男', 21, '信息工程学院', '大数据202班', '17718739273', '6#215');
INSERT INTO `student` VALUES (13, 2020111127, '侯睿', '男', 17, '信息工程学院', '计科本201班', '75510816291', '6#214');
INSERT INTO `student` VALUES (14, 2020111280, '尹云熙', '男', 20, '化学与工程学院', '化学本201班', '75584306190', '6#214');
INSERT INTO `student` VALUES (15, 2020111266, '龚宇宁', '男', 17, '预科教育学院', '化学本201班', '2135711355', '6#215');
INSERT INTO `student` VALUES (16, 2020111164, '何宇宁', '男', 17, '化学与工程学院', '计科本202班', '17285624313', '6#217');
INSERT INTO `student` VALUES (17, 2020111309, '蒋杰宏', '男', 23, '化学与工程学院', '计科本202班', '75572229617', '6#211');
INSERT INTO `student` VALUES (18, 2020111253, '顾杰宏', '男', 23, '信息工程学院', '大数据201班', '7553590869', '6#215');
INSERT INTO `student` VALUES (19, 2020111175, '江云熙', '男', 20, '化学与工程学院', '大数据201班', '76963292731', '6#216');
INSERT INTO `student` VALUES (20, 2020111116, '姚睿', '男', 17, '化学与工程学院', '大数据202班', '200093245', '6#214');
INSERT INTO `student` VALUES (21, 2020111211, '龙子异', '男', 19, '化学与工程学院', '大数据201班', '13743458837', '6#214');
INSERT INTO `student` VALUES (22, 2020111232, '沈子异', '男', 19, '预科教育学院', '大数据201班', '7557558244', '6#216');
INSERT INTO `student` VALUES (23, 2020111217, '潘嘉伦', '男', 21, '化学与工程学院', '计科本202班', '7696442902', '6#211');
INSERT INTO `student` VALUES (24, 2020111185, '尹璐', '女', 20, '预科教育学院', '化学本201班', '14619622992', '6#216');
INSERT INTO `student` VALUES (25, 2020111306, '曹震南', '男', 20, '化学与工程学院', '化学本201班', '76015793842', '6#217');
INSERT INTO `student` VALUES (26, 2020111233, '胡杰宏', '男', 18, '信息工程学院', '化学本201班', '2857650651', '6#211');
INSERT INTO `student` VALUES (27, 2020111179, '李子异', '男', 20, '信息工程学院', '化学本201班', '7559620430', '6#214');
INSERT INTO `student` VALUES (28, 2020111185, '黎安琪', '女', 21, '预科教育学院', '计科本201班', '17218411953', '6#214');
INSERT INTO `student` VALUES (29, 2020111157, '汪安琪', '女', 17, '信息工程学院', '计科本201班', '2807313451', '6#211');
INSERT INTO `student` VALUES (30, 2020111173, '田云熙', '男', 22, '化学与工程学院', '计科本202班', '1022682311', '6#214');
INSERT INTO `student` VALUES (31, 2020111171, '程杰宏', '男', 17, '信息工程学院', '计科本201班', '2198985313', '6#211');
INSERT INTO `student` VALUES (32, 2020111302, '李嘉伦', '男', 19, '信息工程学院', '计科本201班', '15957856366', '6#217');
INSERT INTO `student` VALUES (33, 2020111216, '任岚', '女', 20, '预科教育学院', '大数据201班', '2013369820', '6#214');
INSERT INTO `student` VALUES (34, 2020111267, '许震南', '男', 23, '信息工程学院', '计科本202班', '2084465145', '6#211');
INSERT INTO `student` VALUES (35, 2020111226, '傅晓明', '男', 17, '预科教育学院', '大数据201班', '213180457', '6#211');
INSERT INTO `student` VALUES (36, 2020111248, '傅杰宏', '男', 20, '信息工程学院', '计科本201班', '105395531', '6#216');
INSERT INTO `student` VALUES (37, 2020111187, '姜璐', '女', 20, '化学与工程学院', '大数据202班', '7692365305', '6#217');
INSERT INTO `student` VALUES (38, 2020111283, '钱璐', '女', 20, '信息工程学院', '化学本201班', '207963034', '6#217');
INSERT INTO `student` VALUES (39, 2020111278, '孙嘉伦', '男', 18, '预科教育学院', '化学本201班', '7605743524', '6#215');
INSERT INTO `student` VALUES (40, 2020111241, '唐嘉伦', '男', 20, '化学与工程学院', '化学本201班', '2139317169', '6#217');
INSERT INTO `student` VALUES (41, 2020111207, '邱子异', '男', 19, '信息工程学院', '计科本202班', '18870076753', '6#212');
INSERT INTO `student` VALUES (42, 2020111151, '范詩涵', '女', 19, '预科教育学院', '化学本201班', '17276749519', '6#214');
INSERT INTO `student` VALUES (43, 2020111177, '吕致远', '男', 19, '预科教育学院', '计科本201班', '218868993', '6#211');
INSERT INTO `student` VALUES (44, 2020111230, '孟秀英', '女', 21, '信息工程学院', '大数据201班', '7695110703', '6#211');
INSERT INTO `student` VALUES (45, 2020111167, '莫宇宁', '男', 23, '预科教育学院', '化学本201班', '13588340413', '6#217');
INSERT INTO `student` VALUES (46, 2020111180, '高云熙', '男', 19, '信息工程学院', '化学本201班', '2010440435', '6#214');
INSERT INTO `student` VALUES (47, 2020111131, '孟嘉伦', '男', 20, '信息工程学院', '化学本201班', '1026113135', '6#217');
INSERT INTO `student` VALUES (48, 2020111153, '蔡岚', '女', 21, '化学与工程学院', '化学本201班', '7699735326', '6#213');
INSERT INTO `student` VALUES (49, 2020111261, '方晓明', '男', 22, '化学与工程学院', '化学本201班', '2832830180', '6#211');
INSERT INTO `student` VALUES (50, 2020111133, '钱子韬', '男', 20, '预科教育学院', '化学本201班', '1047490777', '6#215');
INSERT INTO `student` VALUES (51, 2020111220, '汪子韬', '男', 18, '信息工程学院', '计科本201班', '7601045819', '6#213');
INSERT INTO `student` VALUES (52, 2020111112, '卢杰宏', '男', 20, '化学与工程学院', '大数据201班', '207314774', '6#217');
INSERT INTO `student` VALUES (53, 2020111153, '方云熙', '男', 19, '信息工程学院', '大数据201班', '75597385961', '6#214');
INSERT INTO `student` VALUES (54, 2020111190, '贺岚', '女', 18, '化学与工程学院', '大数据202班', '15438562042', '6#216');
INSERT INTO `student` VALUES (55, 2020111299, '莫嘉伦', '男', 21, '信息工程学院', '大数据201班', '15346995408', '6#212');
INSERT INTO `student` VALUES (56, 2020111130, '宋震南', '男', 18, '预科教育学院', '计科本201班', '13020941778', '6#215');
INSERT INTO `student` VALUES (57, 2020111247, '薛璐', '女', 21, '信息工程学院', '大数据201班', '15391582672', '6#215');
INSERT INTO `student` VALUES (58, 2020111191, '田杰宏', '男', 19, '预科教育学院', '大数据201班', '2102740922', '6#211');
INSERT INTO `student` VALUES (59, 2020111174, '梁震南', '男', 22, '预科教育学院', '计科本201班', '7554841450', '6#211');
INSERT INTO `student` VALUES (60, 2020111268, '姜宇宁', '男', 21, '预科教育学院', '大数据201班', '280172201', '6#215');
INSERT INTO `student` VALUES (61, 2020111201, '崔秀英', '女', 19, '化学与工程学院', '计科本201班', '212199715', '6#215');
INSERT INTO `student` VALUES (62, 2020111249, '吴子韬', '男', 19, '信息工程学院', '大数据202班', '13624374768', '6#217');
INSERT INTO `student` VALUES (63, 2020111257, '高岚', '女', 17, '信息工程学院', '计科本202班', '17150805700', '6#214');
INSERT INTO `student` VALUES (64, 2020111190, '范睿', '男', 19, '预科教育学院', '化学本201班', '14109517920', '6#213');
INSERT INTO `student` VALUES (65, 2020111281, '郝岚', '女', 18, '信息工程学院', '化学本201班', '17225082436', '6#216');
INSERT INTO `student` VALUES (66, 2020111269, '傅安琪', '女', 17, '化学与工程学院', '大数据201班', '217889523', '6#214');
INSERT INTO `student` VALUES (67, 2020111231, '郑子异', '男', 17, '信息工程学院', '大数据201班', '204815957', '6#211');
INSERT INTO `student` VALUES (68, 2020111221, '周晓明', '男', 23, '化学与工程学院', '大数据201班', '287339650', '6#216');
INSERT INTO `student` VALUES (69, 2020111210, '杜詩涵', '女', 22, '化学与工程学院', '大数据202班', '14851648559', '6#213');
INSERT INTO `student` VALUES (70, 2020111187, '许子异', '男', 20, '信息工程学院', '大数据202班', '15821645183', '6#211');
INSERT INTO `student` VALUES (71, 2020111238, '崔睿', '男', 23, '信息工程学院', '大数据202班', '13823623246', '6#214');
INSERT INTO `student` VALUES (72, 2020111253, '魏安琪', '女', 22, '化学与工程学院', '大数据201班', '75598409066', '6#216');
INSERT INTO `student` VALUES (73, 2020111138, '熊子异', '男', 20, '化学与工程学院', '大数据202班', '13089622163', '6#215');
INSERT INTO `student` VALUES (74, 2020111186, '沈云熙', '男', 22, '预科教育学院', '化学本201班', '15491826898', '6#217');
INSERT INTO `student` VALUES (75, 2020111116, '秦震南', '男', 21, '信息工程学院', '大数据202班', '14453615587', '6#215');
INSERT INTO `student` VALUES (76, 2020111192, '薛睿', '男', 18, '预科教育学院', '计科本202班', '17160288487', '6#213');
INSERT INTO `student` VALUES (77, 2020111131, '傅詩涵', '女', 22, '预科教育学院', '化学本201班', '13942047789', '6#213');
INSERT INTO `student` VALUES (78, 2020111235, '韦詩涵', '女', 22, '预科教育学院', '化学本201班', '18652597550', '6#213');
INSERT INTO `student` VALUES (79, 2020111250, '苏嘉伦', '男', 23, '化学与工程学院', '化学本201班', '17410022164', '6#211');
INSERT INTO `student` VALUES (80, 2020111248, '戴璐', '女', 19, '信息工程学院', '计科本202班', '75502721905', '6#214');
INSERT INTO `student` VALUES (81, 2020111180, '袁岚', '女', 20, '化学与工程学院', '大数据201班', '7550190902', '6#212');
INSERT INTO `student` VALUES (82, 2020111287, '黄子韬', '男', 20, '预科教育学院', '化学本201班', '7698883728', '6#212');
INSERT INTO `student` VALUES (83, 2020111161, '段安琪', '女', 20, '信息工程学院', '计科本202班', '14303901836', '6#214');
INSERT INTO `student` VALUES (84, 2020111232, '姜子异', '男', 19, '化学与工程学院', '化学本201班', '15668305319', '6#216');
INSERT INTO `student` VALUES (85, 2020111258, '陆震南', '男', 17, '化学与工程学院', '大数据201班', '19935106156', '6#217');
INSERT INTO `student` VALUES (86, 2020111127, '常璐', '女', 22, '信息工程学院', '大数据201班', '17181605392', '6#215');
INSERT INTO `student` VALUES (87, 2020111231, '赵子韬', '男', 21, '信息工程学院', '大数据202班', '1016860378', '6#216');
INSERT INTO `student` VALUES (88, 2020111165, '罗子异', '男', 20, '化学与工程学院', '计科本202班', '75576021040', '6#217');
INSERT INTO `student` VALUES (89, 2020111193, '严晓明', '男', 20, '预科教育学院', '大数据201班', '15616134944', '6#213');
INSERT INTO `student` VALUES (90, 2020111128, '范詩涵', '女', 17, '化学与工程学院', '计科本201班', '2053239612', '6#213');
INSERT INTO `student` VALUES (91, 2020111226, '刘致远', '男', 21, '信息工程学院', '计科本201班', '14808692224', '6#212');
INSERT INTO `student` VALUES (92, 2020111174, '萧子韬', '男', 18, '信息工程学院', '大数据202班', '19587290105', '6#217');
INSERT INTO `student` VALUES (93, 2020111275, '程杰宏', '男', 19, '化学与工程学院', '计科本202班', '19430734588', '6#214');
INSERT INTO `student` VALUES (94, 2020111299, '邹震南', '男', 18, '化学与工程学院', '大数据201班', '13858213036', '6#212');
INSERT INTO `student` VALUES (95, 2020111295, '黄杰宏', '男', 18, '化学与工程学院', '化学本201班', '75502738175', '6#213');
INSERT INTO `student` VALUES (96, 2020111289, '袁璐', '女', 20, '信息工程学院', '计科本202班', '19196144738', '6#212');
INSERT INTO `student` VALUES (97, 2020111234, '贺宇宁', '男', 20, '化学与工程学院', '化学本201班', '17930275866', '6#214');
INSERT INTO `student` VALUES (98, 2020111126, '陶睿', '男', 19, '信息工程学院', '大数据202班', '212894215', '6#211');
INSERT INTO `student` VALUES (99, 2020111223, '钟杰宏', '男', 22, '信息工程学院', '化学本201班', '15715539487', '6#214');
INSERT INTO `student` VALUES (100, 2020111140, '陈睿', '男', 22, '预科教育学院', '计科本202班', '15686637913', '6#215');
INSERT INTO `student` VALUES (101, 2020111191, '方震南', '男', 21, '化学与工程学院', '大数据201班', '289859226', '6#217');
INSERT INTO `student` VALUES (1000, 2020111137, '萧杰宏', '男', 21, '预科教育学院', '化学本201班', '14951349425', '6#216');
INSERT INTO `student` VALUES (1001, 2020111111, '韩运鹏', '男', 18, '软件', '24', '111', '111');
INSERT INTO `student` VALUES (1002, 32, '十大', '男', 21, 'fcgbv', 'dfg', 'dfg', 'dgf');

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `realname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `sex` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `age` int NULL DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, 'zhangsan', '123456', '张三', '男', 20, '17732222222');
INSERT INTO `user` VALUES (2, 'lisi', '123456', '李四', '男', 18, '17731111111');

-- ----------------------------
-- Table structure for user_plots
-- ----------------------------
DROP TABLE IF EXISTS `user_plots`;
CREATE TABLE `user_plots`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '地块ID',
  `user_id` bigint NOT NULL COMMENT '所属用户ID',
  `user_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户名称',
  `plot_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '地块名称',
  `last_crop` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '上季作物',
  `current_crop` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '本季作物',
  `contact_person` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '联系人',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '电话',
  `soil_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '土壤类型',
  `irrigation_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '灌溉条件',
  `land_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '土地类型',
  `shape_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '图形类型（polygon 或 circle）',
  `coordinates` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '坐标数据（JSON字符串）',
  `area` double NULL DEFAULT NULL COMMENT '面积（亩）',
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '地块地址',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户地块信息表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user_plots
-- ----------------------------
INSERT INTO `user_plots` VALUES (5, 1, 'zhangsan', '张北二号地', '水稻', '土豆', 'zhangsan', '17733333333', '壤土', '渠灌', '开垦荒地', 'polygon', '{\"shapeType\":\"polygon\",\"latlngs\":[{\"lat\":41.27686259429141,\"lng\":114.80395263863294},{\"lat\":41.27669314858158,\"lng\":114.80383463025191},{\"lat\":41.27645108251877,\"lng\":114.8036629816977},{\"lat\":41.27618480881282,\"lng\":114.80336259672781},{\"lat\":41.27578136173406,\"lng\":114.80321240424287},{\"lat\":41.27553929228984,\"lng\":114.80350206117811},{\"lat\":41.27553929228984,\"lng\":114.80371662187089},{\"lat\":41.27620901555823,\"lng\":114.80495034585434},{\"lat\":41.276289704644824,\"lng\":114.80468214498836},{\"lat\":41.27641073808769,\"lng\":114.80447831233022}]}', 15.48, '河北省张家口市张北县郝家营乡G1013海张高速', '2025-07-25 14:18:22', '2025-07-25 14:18:22');
INSERT INTO `user_plots` VALUES (6, 1, 'zhangsan', '张北一号地', '水稻', '玉米', '张三', '17733333333', '壤土', '自然降水', '承包', 'polygon', '{\"shapeType\":\"polygon\",\"latlngs\":[{\"lat\":41.278201578773334,\"lng\":114.80112065387196},{\"lat\":41.27815722711671,\"lng\":114.80100805919633},{\"lat\":41.277915166483616,\"lng\":114.80117434373324},{\"lat\":41.27793937258735,\"lng\":114.80106706338684},{\"lat\":41.277862719894785,\"lng\":114.80085250269406},{\"lat\":41.27772555169399,\"lng\":114.80100269517901},{\"lat\":41.27768117368495,\"lng\":114.80093832697118},{\"lat\":41.2779877847678,\"lng\":114.80045556541246},{\"lat\":41.27780623890584,\"lng\":114.80046629344707},{\"lat\":41.27756417697104,\"lng\":114.80063257798396},{\"lat\":41.277096188018234,\"lng\":114.80077204243428},{\"lat\":41.27659592025464,\"lng\":114.8010831554388},{\"lat\":41.2763094748896,\"lng\":114.80131380818354},{\"lat\":41.277128463226155,\"lng\":114.80250998404574},{\"lat\":41.27784658247435,\"lng\":114.80143718058189}]}', 24.73, '河北省张家口市张北县郝家营乡郝家营立交桥', '2025-07-25 14:30:10', '2025-07-25 14:30:22');
INSERT INTO `user_plots` VALUES (8, 1, 'zhangsan', '张北三号地', '玉米', '玉米', 's', '17345678911', '砂质土', '渠灌', '承包', 'polygon', '{\"shapeType\":\"polygon\",\"latlngs\":[{\"lat\":41.27986920430651,\"lng\":114.79412427916004},{\"lat\":41.27985308698105,\"lng\":114.7960980881357},{\"lat\":41.27838639370103,\"lng\":114.79592645257259},{\"lat\":41.27846698209963,\"lng\":114.7937380991431}]}', 41.89, '河北省张家口市张北县郝家营乡051乡道', '2025-09-11 10:56:41', '2025-09-11 10:56:41');
INSERT INTO `user_plots` VALUES (9, 1, 'zhangsan', '宁河一号地', '玉米', '水稻', 's', '17345678911', '黏质土', '渠灌', '开垦荒地', 'polygon', '{\"shapeType\":\"polygon\",\"latlngs\":[{\"lat\":39.30623494652515,\"lng\":117.82774578395168},{\"lat\":39.30582845143932,\"lng\":117.82745614893896},{\"lat\":39.30608562207409,\"lng\":117.82679106113197},{\"lat\":39.304426440070216,\"lng\":117.82558961219029},{\"lat\":39.303812532759785,\"lng\":117.82720942281703},{\"lat\":39.30582845143932,\"lng\":117.82871123399414}]}', 56.6, '天津市宁河区芦台街道芦台春生态园', '2025-09-11 10:57:21', '2025-09-11 10:57:21');

SET FOREIGN_KEY_CHECKS = 1;
