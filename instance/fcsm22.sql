BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "user" (
	"id"	SERIAL NOT NULL,
	"uuid"	TEXT,
	"username"	VARCHAR(20) NOT NULL,
	"email"	VARCHAR(120) NOT NULL,
	"image_file"	VARCHAR(20) NOT NULL,
	"password"	VARCHAR(60) NOT NULL,
	PRIMARY KEY("id"),
	UNIQUE("email"),
	UNIQUE("username")
);
CREATE TABLE IF NOT EXISTS "product_category" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(200) NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "category" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(200) NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "role" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(80),
	UNIQUE("name"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "post" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(100) NOT NULL,
	"date_posted"	timestamp NOT NULL,
	"content"	TEXT NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	FOREIGN KEY("category_id") REFERENCES "category"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "events" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(250) NOT NULL,
	"start_event"	timestamp,
	"end_event"	timestamp,
	"user_id"	INTEGER NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "post_gallery" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(100) NOT NULL,
	"image_file2"	VARCHAR(100) NOT NULL,
	"orderz"	INTEGER,
	"post_id"	INTEGER NOT NULL,
	FOREIGN KEY("post_id") REFERENCES "post"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "product" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(100) NOT NULL,
	"date_posted"	timestamp NOT NULL,
	"content"	TEXT NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"is_visible"	BOOLEAN,
	"price"	DECIMAL(10, 2) NOT NULL,
	"old_price"	DECIMAL(10, 2) NOT NULL,
	"product_category_id"	INTEGER NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	FOREIGN KEY("product_category_id") REFERENCES "product_category"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "team" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(250) NOT NULL,
	"score_scrap"	VARCHAR(250),
	"player_list_scrap"	VARCHAR(250),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "position" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(180),
	UNIQUE("name"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "member" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(250) NOT NULL,
	"phone"	VARCHAR(250) NOT NULL,
	"address"	VARCHAR(250) NOT NULL,
	"psc"	VARCHAR(250) NOT NULL,
	"city"	VARCHAR(250) NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"image_file"	VARCHAR(250) DEFAULT 'default.png',
	"weight"	INTEGER,
	"height"	INTEGER,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "positions_members" (
	"member_id"	INTEGER,
	"position_id"	INTEGER,
	FOREIGN KEY("position_id") REFERENCES "position"("id"),
	FOREIGN KEY("member_id") REFERENCES "member"("id")
);
CREATE TABLE IF NOT EXISTS "teams_members" (
	"member_id"	INTEGER,
	"team_id"	INTEGER,
	FOREIGN KEY("member_id") REFERENCES "member"("id"),
	FOREIGN KEY("team_id") REFERENCES "team"("id")
);
CREATE TABLE IF NOT EXISTS "roles_members" (
	"member_id"	INTEGER,
	"role_id"	INTEGER,
	FOREIGN KEY("role_id") REFERENCES "role"("id"),
	FOREIGN KEY("member_id") REFERENCES "member"("id")
);
CREATE TABLE IF NOT EXISTS "product_gallery" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(100) NOT NULL,
	"image_file2"	VARCHAR(30) NOT NULL,
	"orderz"	INTEGER,
	"product_id"	INTEGER NOT NULL,
	FOREIGN KEY("product_id") REFERENCES "product"("id"),
	PRIMARY KEY("id")
);
INSERT INTO "user" VALUES (1,'1a3e4be1-fd21-41f7-833e-6cca7e666fd8','milanmartis','milanmartis@gmail.com','55ceab7e6619e11e.jpg','$2b$12$V7MBiE4MQZMhFUCF8RE4tuj/f0p22ZOBnMox2sg0r7nw4A/DbM0/e');
-- INSERT INTO "user" VALUES (5,'e2ac49a3-a17b-4812-859d-b9ef4979dbe5','Ronaldo','info@appdesign.sk','default.jpg','$2b$12$wiHkosu3JZW4/B3mPw/SEuOmG6sKM4R9B091zz88SLNJpkZUDll16');
-- INSERT INTO "user" VALUES (6,'7deab31c-c941-4fd8-be35-61460aa0b6a6','Messi','martis@gasparikmasovyroba.sk','7a89e109d637ec33.jpg','$2b$12$Ly2mIHM67PEfo9M4t8LVeu6DHjzq/tgs9d0VtXo9NK7.tnkXzx/Iu');
-- INSERT INTO "user" VALUES (7,'e0619cbc-2c44-4b20-87be-ed9bebaec9c8','lklk','milanmuhuhartis@gmail.com','default.jpg','$2b$12$DDNkPIbN.YFxW66t4G0J6OJMfClm53T8tq0U9PNnF3k/nM7IQLpFe');
-- INSERT INTO "user" VALUES (8,'5cbe9d89-81de-4d44-883c-03cd996a8999','u9uu','oo@oo.oo','default.jpg','$2b$12$jq2E2Sy4caPDUNkLss2oy.OxCeUYGe9hME2qQA87S4WsnKOZxBNce');
-- INSERT INTO "user" VALUES (9,'0c313dcc-a7bd-43bb-ba8f-c2a76d8af364','hfg','eee@eee.eee','default.jpg','$2b$12$/2v1A47vozN6eMJsT3sX/.Fmy0JxGFQtnD86maiNgzvG00FY1leZC');
-- INSERT INTO "user" VALUES (10,'62411db0-6ab8-4c4b-977c-17e23fc154ce','fanusik','fanusik@gmail.com','default.jpg','$2b$12$ViYs9esXq96.oTjRo68WY.hNnWgwS8kcwnrfib/o8OkqHVH3psXeq');
-- INSERT INTO "category" VALUES (2,'A team');
-- INSERT INTO "category" VALUES (3,'Mládež');
-- INSERT INTO "category" VALUES (4,'Aktuality');
-- INSERT INTO "category" VALUES (5,'Fan Shop');
-- INSERT INTO "category" VALUES (6,'oihoih');
INSERT INTO "role" VALUES (1,'Admin');
INSERT INTO "role" VALUES (2,'Tréner');
INSERT INTO "role" VALUES (3,'Hráč');
INSERT INTO "role" VALUES (4,'Správca ihriska');
INSERT INTO "role" VALUES (5,'Asistent trénera');
INSERT INTO "role" VALUES (6,'Kondičný tréner');
INSERT INTO "role" VALUES (7,'Rodič');
-- INSERT INTO "post" VALUES (3,'Zlatan Ibrahimović becomes oldest ever goalscorer in Serie A','2023-03-20 12:49:05','After Milan’s Scudetto success last season, Ibrahimović revealed on social media that he played the last six months of the 2021/2022 season without an ACL in his left knee – the strong band of tissue that connects the thigh bone to the shin bone and the knee joint.



-- But, despite his age and career-threatening injury, Ibrahimović seems determined to continue playing soccer.



-- “As long as I can produce results, I will still play,” he told CNN last November. “The day I slow down, I want the people around me to be honest and say he’s slowing down and then I’ll be realistic.”



-- Milan remain fourth in the table after its defeat, and will next take to the field on April 2 to face league leader Napoli.



-- Meanwhile in Saudi Arabia, Cristiano Ronaldo – another legendary forward – rolled back the years to score a glorious long-range free kick as Al Nassr defeated Abha 2-1 in the Saudi Pro League on Saturday.



-- He then allowed his teammate Anderson Talisca to convert the winning penalty eight minutes later as a mark of respect. Brazilian Talisca has just come back from injury.',1,2);
-- INSERT INTO "post" VALUES (4,'World Cup final: How Argentina won penalty shootout','2023-03-21 13:21:24','(CNN)A soccer match lasts for 90 minutes, another 30 if there really needs to be a winner. But if it''s still level after that, then the game will be decided with a penalty shootout, arguably the most nerve-shredding experience in all of sports. For the fans, it''s excruciating; at the World Cup in Qatar, one Argentina supporter sobbed uncontrollably as she watched the quarterfinal shootout against the Netherlands through her fingers. By the end, she looked distraught. All the emotion had been wrung out of her, and the tears that she cried were of relief, rather than joy.

-- For the players, such emotions are magnified tenfold. "Love hurts," goes the anonymous quote, "but not as much as penalties."

-- Success or failure could be career-defining, one simple kick from 12 yards is weighed down by teammates'' hopes and the expectation of potentially millions of fans. As the author Karl Wiggins put it, "It''s as if, for a few seconds, a player''s soul is laid bare for the entire world to see."',1,2);
-- INSERT INTO "post" VALUES (5,'Social media can be ‘dangerous’ for soccer players','2023-03-21 13:27:22','“It’s like this, when people get frustrated they just post in that moment. But when it gets personal, it gets personal for a long time so it’s important to restrict it.”



-- His comments come amid a landmark ruling in which a 24-year-old man was banned from every UK stadium for three years after he racially abused Wissa’s Brentford teammate Ivan Toney on Instagram in October 2022.



-- Wissa, who plays for DR Congo and has been a vital part of Brentford’s impressive season, says his club teammates have tried to support Toney as much as possible as the 27-year-old continues to be targeted with racist abuse online.',1,4);
-- INSERT INTO "post" VALUES (6,'Tričko','2023-03-31 19:48:45','XXL',1,5);
-- INSERT INTO "post" VALUES (7,'Tričko','2023-03-31 19:50:20','XXL',1,5);
INSERT INTO "member" VALUES (2,'Christiano Ronaldo','+421917360277','Sládkovičova 22','90001','Modra',5,'288149ebe5b09638.jpg',NULL,NULL);
-- INSERT INTO "member" VALUES (3,'Milan Martiš','+421917360277','Sládkovičova 22','90001','Modra',6,'0751291063f521be.jpg',NULL,NULL);
-- INSERT INTO "member" VALUES (4,'Milan Martiš','+421917360277','Sládkovičova 22','90001','Modra',8,'default.png',NULL,NULL);
-- INSERT INTO "member" VALUES (5,'Janko Hraško','+421917360277','Sládkovičova 22','90001','Modra',9,'default.png',NULL,NULL);
-- INSERT INTO "member" VALUES (6,'fanusik','+421917360277','21','21222','21',10,'default.png',NULL,NULL);
-- INSERT INTO "events" VALUES (1,'okok555','2023-03-21 14:44:36','2023-03-21 14:44:36',1);
-- INSERT INTO "events" VALUES (2,'nun1','2023-03-21 15:08:41','2023-03-21 15:08:41',1);
-- INSERT INTO "events" VALUES (3,'6565','2023-03-01 00:00:00.000000','2023-03-02 00:00:00.000000',1);
-- INSERT INTO "events" VALUES (4,'kkkk','2023-03-29 18:29:21','2023-03-29 18:29:21',1);
-- INSERT INTO "events" VALUES (5,'kkllklkkl;lm;lm;lm','2023-03-29 18:36:35','2023-03-29 18:36:35',1);
-- INSERT INTO "events" VALUES (6,'kkkkk122','2023-03-29 18:30:20','2023-03-29 18:30:20',1);
-- INSERT INTO "events" VALUES (7,'22121;','2023-03-30 10:30:57','2023-03-30 10:30:57',1);
-- INSERT INTO "events" VALUES (9,'2121221.','2023-03-30 10:30:53','2023-03-30 10:30:53',1);
-- INSERT INTO "events" VALUES (10,'211opjpojpojpojpj p jp ojpoj poj pj poj','2023-03-03 00:00:00.000000','2023-03-04 00:00:00.000000',1);
-- INSERT INTO "events" VALUES (11,' pojpjp jpoj ','2023-03-04 00:00:00.000000','2023-03-05 00:00:00.000000',1);
-- INSERT INTO "events" VALUES (12,' poj pojpj ','2023-03-04 00:00:00.000000','2023-03-05 00:00:00.000000',1);
-- INSERT INTO "events" VALUES (13,'','2023-04-13 00:00:00.000000','2023-04-14 00:00:00.000000',1);
-- INSERT INTO "events" VALUES (14,'kjkvhikvuikvkj','2023-04-17 00:00:00.000000','2023-04-29 00:00:00.000000',1);
-- INSERT INTO "events" VALUES (15,'vjhjhv','2023-06-14 00:00:00.000000','2023-06-23 00:00:00.000000',1);
-- INSERT INTO "events" VALUES (16,'','2023-06-09 00:00:00.000000','2023-06-10 00:00:00.000000',1);
-- INSERT INTO "post_gallery" VALUES (8,'Zlatan Ibrahimović becomes oldest ever goalscorer in Serie A','230319104020-01-zlatan-ibrahimovic-0318.webp',1,3);
-- INSERT INTO "post_gallery" VALUES (9,'Zlatan Ibrahimović becomes oldest ever goalscorer in Serie A','230319104020-01-zlatan-ibrahimovic-0318.webp',0,3);
-- INSERT INTO "post_gallery" VALUES (10,'World Cup final: How Argentina won penalty shootout','221219214614-pba-nacho-pkg.jpg',1,4);
-- INSERT INTO "post_gallery" VALUES (11,'World Cup final: How Argentina won penalty shootout','230301113421-05-penalty-shoot-outs.jpg',1,4);
-- INSERT INTO "post_gallery" VALUES (12,'World Cup final: How Argentina won penalty shootout','230309070852-lionel-messi-munich-030823.jpg',1,4);
-- INSERT INTO "post_gallery" VALUES (13,'World Cup final: How Argentina won penalty shootout','221219214614-pba-nacho-pkg.jpg',0,4);
-- INSERT INTO "post_gallery" VALUES (14,'Social media can be ‘dangerous’ for soccer players','230317140215-01-wissa-premier-league-abuse.webp',1,5);
-- INSERT INTO "post_gallery" VALUES (15,'Social media can be ‘dangerous’ for soccer players','230317140320-02-wissa-premier-league-abuse.webp',1,5);
-- INSERT INTO "post_gallery" VALUES (16,'Social media can be ‘dangerous’ for soccer players','230317140320-02-wissa-premier-league-abuse.webp',0,5);
-- INSERT INTO "roles_members" VALUES (3,2);
-- INSERT INTO "roles_members" VALUES (3,3);
-- INSERT INTO "roles_members" VALUES (3,4);
-- INSERT INTO "roles_members" VALUES (3,5);
-- INSERT INTO "roles_members" VALUES (3,6);
-- INSERT INTO "roles_members" VALUES (5,6);
-- INSERT INTO "roles_members" VALUES (2,3);
-- INSERT INTO "roles_members" VALUES (2,5);
-- INSERT INTO "team" VALUES (1,'A team','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/53930/tabulky/?partId=&sutaz=629b6e797163293609f9fa26','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/53930/hraci/?partId=&sutaz=629b6e797163293609f9fa26');
-- INSERT INTO "team" VALUES (2,'U19','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55092/tabulky/?partId=&sutaz=62a82e3e71632936092991de','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55092/hraci/?partId=&sutaz=62a82e3e71632936092991de');
-- INSERT INTO "team" VALUES (3,'U17','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55097/tabulky/?partId=&sutaz=629b6f437163293609faea9e','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55097/hraci/?partId=&sutaz=629b6f437163293609faea9e');
-- INSERT INTO "team" VALUES (4,'U15','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55099/tabulky/?partId=&sutaz=629b6f5d7163293609fb0ab7','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55099/hraci/?partId=&sutaz=629b6f5d7163293609fb0ab7');
-- INSERT INTO "team" VALUES (5,'U13','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55102/tabulky/?partId=&sutaz=629b6f827163293609fb32fe','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55102/hraci/?partId=&sutaz=629b6f827163293609fb32fe');
-- INSERT INTO "team" VALUES (6,'U11','','');
-- INSERT INTO "team" VALUES (7,'U9','','');
-- INSERT INTO "teams_members" VALUES (3,1);
-- INSERT INTO "teams_members" VALUES (3,2);
-- INSERT INTO "teams_members" VALUES (3,3);
-- INSERT INTO "teams_members" VALUES (3,4);
-- INSERT INTO "teams_members" VALUES (3,5);
-- INSERT INTO "teams_members" VALUES (3,6);
-- INSERT INTO "teams_members" VALUES (3,7);
-- INSERT INTO "teams_members" VALUES (5,3);
-- INSERT INTO "teams_members" VALUES (5,4);
-- INSERT INTO "teams_members" VALUES (5,5);
-- INSERT INTO "teams_members" VALUES (2,4);
-- INSERT INTO "position" VALUES (1,'Brankár');
-- INSERT INTO "position" VALUES (2,'Obranca');
-- INSERT INTO "position" VALUES (3,'Záložník');
-- INSERT INTO "position" VALUES (4,'Útočník');
-- INSERT INTO "positions_members" VALUES (2,1);
-- INSERT INTO "product_category" VALUES (1,'Merch');
-- INSERT INTO "product_category" VALUES (2,'Live Stream');
-- INSERT INTO "product_category" VALUES (3,'Členský poplatok');
-- INSERT INTO "product_category" VALUES (4,'Tréningy U9');
-- INSERT INTO "product" VALUES (6,'Slovan vs. Budmerice','2023-04-01 17:39:11','Priateľský zápas',1,true,5,5,2);
-- INSERT INTO "product" VALUES (7,'Tričko','2023-04-01 17:41:06','XXL',1,true,16,16,1);
-- INSERT INTO "product" VALUES (8,'Mikina','2023-04-01 17:43:18','Bavlnená klokanka s potlačou',1,true,35,35,1);
-- INSERT INTO "product" VALUES (9,'Šál látkový','2023-04-01 20:26:53','Šál obojstranný látkový',1,true,12,12,1);
-- INSERT INTO "product" VALUES (10,'Tréning U9','2023-04-02 08:59:30','Mesačný poplatok',1,true,15,15,3);
-- INSERT INTO "product_gallery" VALUES (3,'Slovan vs. Budmerice','stream.jpg',1,6);
-- INSERT INTO "product_gallery" VALUES (4,'Slovan vs. Budmerice','stream.jpg',0,6);
-- INSERT INTO "product_gallery" VALUES (5,'Tričko','tricko.jpg',1,7);
-- INSERT INTO "product_gallery" VALUES (6,'Tričko','tricko.jpg',0,7);
-- INSERT INTO "product_gallery" VALUES (7,'Mikina','mikina.jpg',1,8);
-- INSERT INTO "product_gallery" VALUES (8,'Mikina','mikina.jpg',0,8);
-- INSERT INTO "product_gallery" VALUES (9,'Šál látkový','sal.jpg',1,9);
-- INSERT INTO "product_gallery" VALUES (10,'Šál látkový','sal.jpg',0,9);
-- INSERT INTO "product_gallery" VALUES (11,'Trening U9','training.jpg',1,10);
-- INSERT INTO "product_gallery" VALUES (12,'Trening U9','training.jpg',0,10);
COMMIT;
