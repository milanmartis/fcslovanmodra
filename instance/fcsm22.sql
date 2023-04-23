-- SELECT setval(pg_get_serial_sequence('public.score_table', 'id'), (SELECT MAX(id) FROM public.score_table)+ 1);
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
CREATE TABLE IF NOT EXISTS "event" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(250) NOT NULL,
	"start_event"	timestamp,
	"end_event"	timestamp,
	"user_id"	INTEGER NOT NULL,
	"event_category_id"	INTEGER,
	"event_team_id"	INTEGER,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "role" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(180),
	"description"	VARCHAR(250),
	PRIMARY KEY("id"),
	UNIQUE("name")
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
CREATE TABLE IF NOT EXISTS "team" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(250) NOT NULL,
	"score_scrap"	VARCHAR(250) NOT NULL,
	"player_list_scrap"	VARCHAR(250) NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "position" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(180),
	PRIMARY KEY("id"),
	UNIQUE("name")
);
CREATE TABLE IF NOT EXISTS "roles_users" (
	"user_id"	INTEGER,
	"role_id"	INTEGER,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	FOREIGN KEY("role_id") REFERENCES "role"("id")
);
CREATE TABLE IF NOT EXISTS "post" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(100) NOT NULL,
	"date_posted"	timestamp NOT NULL,
	"content"	TEXT NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	FOREIGN KEY("category_id") REFERENCES "category"("id"),
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
CREATE TABLE IF NOT EXISTS "member" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(250) NOT NULL,
	"phone"	VARCHAR(250) NOT NULL,
	"address"	VARCHAR(250) NOT NULL,
	"psc"	VARCHAR(250) NOT NULL,
	"city"	VARCHAR(250) NOT NULL,
	"image_file"	VARCHAR(20) NOT NULL,
	"weight"	INTEGER,
	"height"	INTEGER,
	"user_id"	INTEGER NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "teams_members" (
	"member_id"	INTEGER,
	"team_id"	INTEGER,
	FOREIGN KEY("member_id") REFERENCES "member"("id"),
	FOREIGN KEY("team_id") REFERENCES "team"("id")
);
CREATE TABLE IF NOT EXISTS "positions_members" (
	"member_id"	INTEGER,
	"position_id"	INTEGER,
	FOREIGN KEY("position_id") REFERENCES "position"("id"),
	FOREIGN KEY("member_id") REFERENCES "member"("id")
);
CREATE TABLE IF NOT EXISTS "post_gallery" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(100) NOT NULL,
	"image_file2"	VARCHAR(150) NOT NULL,
	"orderz"	INTEGER,
	"post_id"	INTEGER NOT NULL,
	FOREIGN KEY("post_id") REFERENCES "post"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "product_gallery" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(100) NOT NULL,
	"image_file2"	VARCHAR(150) NOT NULL,
	"orderz"	INTEGER,
	"product_id"	INTEGER NOT NULL,
	FOREIGN KEY("product_id") REFERENCES "product"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "teams_events" (
	"team_id"	INTEGER,
	"event_id"	INTEGER,
	FOREIGN KEY("event_id") REFERENCES "event"("id"),
	FOREIGN KEY("team_id") REFERENCES "team"("id")
);
CREATE TABLE IF NOT EXISTS "event_category" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(200) NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "score_table" (
	"id"	SERIAL NOT NULL,
	"club"	VARCHAR(250) NOT NULL,
	"games"	INTEGER,
	"wins"	INTEGER,
	"draws"	INTEGER,
	"loses"	INTEGER,
	"score"	VARCHAR(20) NOT NULL,
	"points"	INTEGER,
	"team_id"	INTEGER NOT NULL,
	FOREIGN KEY("team_id") REFERENCES "team"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "order" (
	"id"	SERIAL NOT NULL,
	"produc_id"	INTEGER NOT NULL,
	"quantity"	INTEGER,
	"amount"	NUMERIC(10, 2) NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"is_paid"	BOOLEAN,
	"order_date"	timestamp NOT NULL,
	"storno"	BOOLEAN,
	FOREIGN KEY("produc_id") REFERENCES "product"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "player" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(250) NOT NULL,
	"position"	INTEGER,
	"team"	VARCHAR(250) NOT NULL,
	"score"	INTEGER,
	"yellow_card"	INTEGER,
	"red_card"	INTEGER,
	"team_id"	INTEGER NOT NULL,
	FOREIGN KEY("team_id") REFERENCES "team"("id"),
	PRIMARY KEY("id")
);
INSERT INTO "user" VALUES (1,'be026d3b-cc56-41fa-97f7-8ee1f871e29d','admin','milanmartis@gmail.com','68cc54d8cc2d4dd9.png','$2b$12$uwA0hhVmdshdg9ri3lO5juc1aFD6Eiof9gQWKfW0k/eGjwG5dml42');
INSERT INTO "user" VALUES (2,'0bf2ec58-729c-4f98-9471-abd5fc514f30','fanusik','martis@gasparikmasovyroba.sk','default.jpg','$2b$12$WHFVKLe51mO2JNli/5mD0.t1Hvwsyq3FESCGUkCPpz8AJYdw9spRS');
INSERT INTO "user" VALUES (3,'ba4ed929-d4e6-46cf-9748-d8f5d5b8529c','messi','info@appdesign.sk','default.jpg','$2b$12$WuVeKYnAPagNsBLOUOr2zOWgFgopRlVYgUt7X1ORtXuCo25H9mWIC');
INSERT INTO "user" VALUES (4,'9c37ff6c-272f-480e-be39-8f7d88ab0a1f','stefanmatas','stefanmatas@fcsm.sk','default.jpg','$2b$12$dMj7R0YenqmdOlgNZ5lTDO7HmjGlBvig93L2xsFFY5SlBfxvX61CK');
INSERT INTO "user" VALUES (5,'1690736c-de05-4e35-beb8-d881151c4e40','noro','norosalis@fcsm.sk','default.jpg','$2b$12$nvDoXyqU1PMinTCk5MI0jO7BoPesa0qHulEtT4oB/NKdgbwmxfuMi');
INSERT INTO "user" VALUES (6,'76a15f81-3a3b-41d6-b3e2-8606428ff6c9','fero','ferodolutovsky@fcsm.sk','default.jpg','$2b$12$nlxNZej1pni89liBOEnwDObK3er3rCFVxtkzHY/glr27/EHbAJF5.');
INSERT INTO "user" VALUES (7,'2be0d46a-abf4-408f-8a6a-b13cdc6c9c91','jano','janvislocky@fcsm.sk','default.jpg','$2b$12$6iDtza/BgG8cBa227.MJm.HyA4vds4ImuzV7L4DePJFWr2bnWC/hS');
INSERT INTO "product_category" VALUES (1,'Merch');
INSERT INTO "product_category" VALUES (2,'Live Stream');
INSERT INTO "product_category" VALUES (3,'Členský poplatok');
INSERT INTO "product_category" VALUES (4,'Tréningy U9');
INSERT INTO "category" VALUES (1,'Aktuality');
INSERT INTO "category" VALUES (2,'A team');
INSERT INTO "team" VALUES (1,'A team','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/53930/tabulky/?partId=&sutaz=629b6e797163293609f9fa26','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/53930/hraci/?partId=&sutaz=629b6e797163293609f9fa26');
INSERT INTO "team" VALUES (2,'U19','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55092/tabulky/?partId=&sutaz=62a82e3e71632936092991de','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55092/hraci/?partId=&sutaz=62a82e3e71632936092991de');
INSERT INTO "team" VALUES (3,'U17','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55097/tabulky/?partId=&sutaz=629b6f437163293609faea9e','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55097/hraci/?partId=&sutaz=629b6f437163293609faea9e');
INSERT INTO "team" VALUES (4,'U15','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55099/tabulky/?partId=&sutaz=629b6f5d7163293609fb0ab7','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55099/hraci/?partId=&sutaz=629b6f5d7163293609fb0ab7');
INSERT INTO "team" VALUES (5,'U13','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55102/tabulky/?partId=&sutaz=629b6f827163293609fb32fe','https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55102/hraci/?partId=&sutaz=629b6f827163293609fb32fe');
INSERT INTO "team" VALUES (6,'U11','','');
INSERT INTO "team" VALUES (7,'U9','lppppp','lppl');
INSERT INTO "position" VALUES (1,'Brankár');
INSERT INTO "position" VALUES (2,'Obranca');
INSERT INTO "position" VALUES (3,'Záložník');
INSERT INTO "position" VALUES (4,'Útočník');
INSERT INTO "position" VALUES (5,'Tréner');
INSERT INTO "position" VALUES (6,'Asistent trénera');
-- INSERT INTO "roles_users" VALUES (1,1);
-- INSERT INTO "roles_users" VALUES (1,2);
-- INSERT INTO "roles_users" VALUES (6,3);
-- INSERT INTO "roles_users" VALUES (6,4);
-- INSERT INTO "roles_users" VALUES (4,3);
-- INSERT INTO "roles_users" VALUES (5,4);
-- INSERT INTO "roles_users" VALUES (3,4);
INSERT INTO "post" VALUES (2,'Villarreal’s Álex Baena says he has received','2023-04-11 17:11:21','It has been widely reported that the Madrid player in question is Federico Valverde. According to a Villarreal statement, the alleged fracas took place as Baena made his way to the team bus after a dramatic 3-2 victory over Los Blancos at the Santiago Bernabéu.



Villarreal said on Sunday that Baena had filed a report to the police, but the club’s statement didn’t mention Valverde by name.



CNN has reached out to Real Madrid, Valverde, Villarreal, Baena, the Madrid prosecutor and LaLiga for comment.



Multiple reports claimed the incident was sparked by comments Baena allegedly made about Valverde’s partner’s pregnancy, something the Villarreal player denies.



“Last Saturday I was assaulted by a colleague of this profession after the match against Real Madrid ended,” Baena said in a statement posted on Instagram.',1,2);
INSERT INTO "post" VALUES (3,'Haaland equalling Salah''s goal record makes Treble possible for Man City','2023-04-16 08:27:21','MANCHESTER, England -- Erling Haaland only played for 45 minutes against Leicester City on Saturday but it was still more than enough time for the Manchester City striker to equal another record.



Starting the game on 30 Premier League goals, he was on 32 by the time 25 minutes had elapsed at the Etihad Stadium, his first goal a penalty and the second a delicate clipped finish over Daniel Iversen in the Leicester goal. It was that one that tied Mohamed Salah''s record for most goals in a 38-game Premier League season, set in 2018.



Only Andy Cole and Alan Shearer have scored more goals in a single season (34), and they had 42 games to do it. Manchester City still have eight league games left this season, while progress in the Champions League and FA Cup would lift that number to 14.',1,2);
INSERT INTO "post" VALUES (4,'Manchester City seek assurances from Jude Bellingham','2023-04-16 08:43:28','The paper suggests that due to the £130 million valuation from Bellingham''s club, Borussia Dortmund, Liverpool have been forced to cut their interest in the 19-year-old, leaving rivals Man City in pole position to sign the England international. Earlier in the week, Reds manager Jurgen Klopp likened their interest in Bellingham to a child asking for a Ferrari at Christmas, indicating that a move for the Dortmund talisman looks unlikely.



Real Madrid are also believed to hold an interest in the youngster. However, the Spanish club will have to allow players to depart the Bernabeu first, before they make a move for the former Birmingham City midfielder.



Shrewd business from the Premier League champions in recent years, which has seen the likes of Raheem Sterling, Leroy Sane and Gabriel Jesus leave for hefty fees, leaves City in a promising financial position to acquire Bellingham in the summer.',1,1);
INSERT INTO "post" VALUES (5,'Lionel Messi, llkay Gundogan, Marcus Thuram among top free agents to sign this summer','2023-04-16 08:44:05','The list of high-profile players whose contracts expire this summer is impressive, but there are a number who look set to remain at their clubs. Real Madrid veterans Karim Benzema, Luka Modric and Toni Kroos are all reportedly close to agreeing another year, with forward Marco Asensio ready to sign up for another four, while the futures of Chelsea''s N''Golo Kante and Borussia Dortmund''s Marco Reus are likely to be resolved soon too.



Manchester United have an option to extend goalkeeper David de Gea by a year, though want him to accept a lower salary, so that could go either way. Meanwhile, a number of players have already agreed to move on including: Inter Milan centre-back Milan Skriniar, Eintracht Frankfurt attacking midfielder Daichi Kamada and RB Leipzig midfielder Konrad Laimer.





Yet there are several exceptionally talented players who are still to have their futures sorted just weeks before the end of the season. So here''s a rundown of the most coveted.',1,1);
INSERT INTO "post" VALUES (6,'What happened to Liverpool?','2023-04-16 08:44:53','Klopp has looked dumbfounded with what he is watching as his "heavy metal" football has seemed like an out of tune quartet at times. Barring a sensational upturn in form, Liverpool will not be in the lucrative Champions League next season. They might not play in Europe at all.



Such an absence would severely hit the club''s ability to attract the stars who might get this great club back chasing trophies and exciting fans again. Already, Liverpool have opted out of the race to sign England''s dynamic £130m-talent, Jude Bellingham of Borussia Dortmund, preferring to use whatever funds are available on more modest targets such as Chelsea''s Mason Mount or Brighton''s World Cup winner Alexis Mac Allister, if those deals can be done.',1,1);
INSERT INTO "post" VALUES (7,'Messi milestone tracker: 800 goals','2023-04-16 08:47:47','However, since making his senior debut in 2004, Messi has accumulated a truly vast number of honours and individual records. And, even at the age of 35, he''s still closing in on an array of significant landmark achievements.



Here we take a look at his trophy haul, his senior career stats and the impressive array of records he already holds, as well as a comprehensive rundown of the major career milestones he has in his sights with regular updates as he nears each of them.',1,2);
INSERT INTO "post" VALUES (8,'Konečne výhra','2023-04-19 18:48:18','However, since making his senior debut in 2004, Messi has accumulated a truly vast number of honours and individual records. And, even at the age of 35, he''s still closing in on an array of significant landmark achievements.



Here we take a look at his trophy haul, his senior career stats and the impressive array of records he already holds, as well as a comprehensive rundown of the major career milestones he has in his sights with regular updates as he nears each of them.',1,2);
INSERT INTO "product" VALUES (1,'Slovan - Budemrice','2023-04-12 12:11:47','Priateľský zápas',1,'false',5,5,2);
INSERT INTO "product" VALUES (2,'Jakubov - Modra','2023-04-12 12:11:55','FUTBALSERVIS V. liga BFZ ',1,'true',5,5,2);
INSERT INTO "member" VALUES (1,'Milan Martiš','+421917360277','Sládkovičova 22','90001','Modra','default.png',NULL,NULL,1);
INSERT INTO "member" VALUES (2,'Fanúšik','+421917360277','Sládkovičova 22','90001','Modra','default.png',NULL,NULL,2);
INSERT INTO "member" VALUES (3,'Slavomír Podubinský','+421917360277','Sládkovičova 22','90001','Modra','0341e28ea55de538.jpg',79,182,3);
INSERT INTO "member" VALUES (4,'Štefan Maťaš','+421917360277','Sládkovičova 22','90001','Modra','a2ebf1dd11ae608e.jpg',0,0,4);
INSERT INTO "member" VALUES (5,'Norbert Sališ','+421917360277','...','...','...','89345796b71a50b8.jpg',180,80,5);
INSERT INTO "member" VALUES (6,'František Dolutovský','+421917360277','...','...','...','5a4744e44fd40776.jpg',180,80,6);
INSERT INTO "member" VALUES (7,'Ján Vislocký','+421917360277','...','...','...','832506aff7f4c6d3.jpg',25,180,7);
INSERT INTO "teams_members" VALUES (6,1);
INSERT INTO "teams_members" VALUES (4,1);
INSERT INTO "teams_members" VALUES (5,1);
INSERT INTO "teams_members" VALUES (5,2);
INSERT INTO "teams_members" VALUES (7,1);
INSERT INTO "teams_members" VALUES (3,1);
INSERT INTO "positions_members" VALUES (6,2);
INSERT INTO "positions_members" VALUES (4,5);
INSERT INTO "positions_members" VALUES (5,2);
INSERT INTO "positions_members" VALUES (7,2);
INSERT INTO "positions_members" VALUES (3,2);
INSERT INTO "post_gallery" VALUES (1,'Villarreal’s Álex Baena says he has received death','230411114641-02-alex-baena-federico-valverde-confrontation-040823.webp',1,2);
INSERT INTO "post_gallery" VALUES (2,'Villarreal’s Álex Baena says he has received death','230411114641-02-alex-baena-federico-valverde-confrontation-040823.webp',0,2);
INSERT INTO "post_gallery" VALUES (3,'Haaland equalling Salah''s goal record makes Treble possible for Man City','haalamd.jpg',1,3);
INSERT INTO "post_gallery" VALUES (4,'Haaland equalling Salah''s goal record makes Treble possible for Man City','221219214614-pba-nacho-pkg.jpg',0,3);
INSERT INTO "post_gallery" VALUES (5,'Manchester City seek assurances from Jude Bellingham','230319111007-01-manchester-united-sale-explainer.webp',1,4);
INSERT INTO "post_gallery" VALUES (6,'Manchester City seek assurances from Jude Bellingham','230319111254-04-manchester-united-sale-explainer.webp',0,4);
INSERT INTO "post_gallery" VALUES (7,'Lionel Messi, llkay Gundogan, Marcus Thuram among top free agents to sign this summer','stream.jpg',1,5);
INSERT INTO "post_gallery" VALUES (8,'Lionel Messi, llkay Gundogan, Marcus Thuram among top free agents to sign this summer','230309070852-lionel-messi-munich-030823.jpg',0,5);
INSERT INTO "post_gallery" VALUES (9,'What happened to Liverpool?','230411114641-02-alex-baena-federico-valverde-confrontation-040823.webp',1,6);
INSERT INTO "post_gallery" VALUES (10,'What happened to Liverpool?','pic24.jpeg',0,6);
INSERT INTO "post_gallery" VALUES (11,'Messi milestone tracker: 800 goals','230305132620-01-liverpool-manchester-united-0305.jpg',1,7);
INSERT INTO "post_gallery" VALUES (12,'Messi milestone tracker: 800 goals','230317140215-01-wissa-premier-league-abuse.webp',0,7);
INSERT INTO "post_gallery" VALUES (13,'Konečne výhra','pic16.jpeg',1,8);
INSERT INTO "post_gallery" VALUES (14,'Konečne výhra','pic24.jpeg',1,8);
INSERT INTO "post_gallery" VALUES (15,'Konečne výhra','pic28.jpeg',1,8);
INSERT INTO "post_gallery" VALUES (16,'Konečne výhra','230319104020-01-zlatan-ibrahimovic-0318.webp',0,8);
INSERT INTO "product_gallery" VALUES (1,'Slovan - Budemrice','230411114641-02-alex-baena-federico-valverde-confrontation-040823.webp',1,2);
INSERT INTO "product_gallery" VALUES (2,'Slovan - Budmerice','corner-of-soccer-pitch-QFUKA5Z.jpg',0,2);
INSERT INTO "role" VALUES (1,'Admin','poiiii');
INSERT INTO "role" VALUES (2,'WebAdmin','poipoi');
INSERT INTO "role" VALUES (3,'Tréner',NULL);
INSERT INTO "role" VALUES (4,'Hráč',NULL);
INSERT INTO "event_category" VALUES (1,'Zápas');
INSERT INTO "event_category" VALUES (2,'Tréning');
INSERT INTO "event_category" VALUES (3,'Sústredenie');
INSERT INTO "event_category" VALUES (4,'Camp');
INSERT INTO "event_category" VALUES (5,'Iné');
INSERT INTO "event" VALUES (6,'iugigiugiug','2023-04-07 04:00:00.000000','2023-04-07 06:00:00.000000',1,3,7);
INSERT INTO "event" VALUES (7,'t87t8t7','2023-04-13 00:00:00.000000','2023-04-14 00:00:00.000000',1,4,3);
INSERT INTO "event" VALUES (8,'TJ Záhoran Jakubov - FC Slovan Modra','2023-04-23 17:00:00.000000','2023-04-23 19:00:00.000000',1,1,1);
INSERT INTO "score_table" VALUES (17,'MŠK Iskra Petržalka',11,10,0,1,'63:5',30,2);
INSERT INTO "score_table" VALUES (18,'MFK Záhorská Bystrica',10,8,0,2,'39:13',24,2);
INSERT INTO "score_table" VALUES (19,'FC Slovan Modra',10,6,0,4,'34:17',18,2);
INSERT INTO "score_table" VALUES (20,'FC Rohožník',11,6,0,5,'23:22',18,2);
INSERT INTO "score_table" VALUES (21,'Obecný športový klub Láb',10,3,0,7,'9:42',9,2);
INSERT INTO "score_table" VALUES (22,'FK Malé Leváre',10,2,1,7,'15:58',7,2);
INSERT INTO "score_table" VALUES (23,'ŠK Svätý Jur',10,0,1,9,'10:36',1,2);
INSERT INTO "score_table" VALUES (24,'ŠK Vrakuňa Bratislava (odstúpené)',0,0,0,0,'0:0',0,2);
INSERT INTO "score_table" VALUES (25,'PŠC Pezinok',13,11,0,2,'60:16',33,3);
INSERT INTO "score_table" VALUES (26,'FK Inter Bratislava B',12,10,2,0,'33:5',32,3);
INSERT INTO "score_table" VALUES (27,'MFK Záhorská Bystrica',14,9,2,3,'37:18',29,3);
INSERT INTO "score_table" VALUES (28,'FC Slovan Modra',13,7,2,4,'37:21',23,3);
INSERT INTO "score_table" VALUES (29,'FK Dúbravka',14,7,0,7,'40:36',21,3);
INSERT INTO "score_table" VALUES (30,'TJ Jarovce Bratislava',14,6,2,6,'37:31',20,3);
INSERT INTO "score_table" VALUES (31,'FKM Stupava',14,5,2,7,'33:29',17,3);
INSERT INTO "score_table" VALUES (32,'MŠK Iskra Petržalka',13,5,1,7,'20:30',16,3);
INSERT INTO "score_table" VALUES (33,'FK Rača Bratislava',14,3,3,8,'21:25',12,3);
INSERT INTO "score_table" VALUES (34,'FK Vajnory',13,3,0,10,'13:61',9,3);
INSERT INTO "score_table" VALUES (35,'Futbalová akadémia Lafranconi FTVŠ UK',14,1,0,13,'10:69',3,3);
INSERT INTO "score_table" VALUES (36,'FC IMAS (odstúpené)',0,0,0,0,'0:0',0,3);
INSERT INTO "score_table" VALUES (37,'MŠK Senec',16,15,1,0,'92:9',46,4);
INSERT INTO "score_table" VALUES (38,'FK Rača Bratislava',16,12,2,2,'57:14',38,4);
INSERT INTO "score_table" VALUES (39,'ŠK Slovan Bratislava C',17,10,4,3,'66:31',34,4);
INSERT INTO "score_table" VALUES (40,'FC - Žolík Malacky',16,10,4,2,'47:16',34,4);
INSERT INTO "score_table" VALUES (41,'PŠC Pezinok',17,11,0,6,'53:28',33,4);
INSERT INTO "score_table" VALUES (42,'FKP BRATISLAVA',16,10,2,4,'63:19',32,4);
INSERT INTO "score_table" VALUES (43,'FKM Stupava',16,6,2,8,'25:38',20,4);
INSERT INTO "score_table" VALUES (44,'NŠK 1922 Bratislava',16,5,3,8,'16:28',18,4);
INSERT INTO "score_table" VALUES (45,'TJ Jarovce Bratislava',16,5,1,10,'15:40',16,4);
INSERT INTO "score_table" VALUES (46,'FC Ružinov Bratislava',15,4,1,10,'29:64',13,4);
INSERT INTO "score_table" VALUES (47,'ŠK Bernolákovo',15,2,1,12,'12:71',7,4);
INSERT INTO "score_table" VALUES (48,'FC Slovan Modra',15,2,1,12,'9:54',7,4);
INSERT INTO "score_table" VALUES (49,'ŠK Vrakuňa Bratislava',17,1,0,16,'22:94',3,4);
INSERT INTO "score_table" VALUES (50,'FC IMAS (odstúpené)',0,0,0,0,'0:0',0,4);
INSERT INTO "score_table" VALUES (51,'ŠK Slovan Bratislava C',17,15,2,0,'150:12',47,5);
INSERT INTO "score_table" VALUES (52,'PŠC Pezinok',17,15,1,1,'56:11',46,5);
INSERT INTO "score_table" VALUES (53,'FK Rača Bratislava',16,12,1,3,'76:14',37,5);
INSERT INTO "score_table" VALUES (54,'NŠK 1922 Bratislava',16,10,1,5,'51:31',31,5);
INSERT INTO "score_table" VALUES (55,'ŠK Vrakuňa Bratislava',17,8,2,7,'32:32',26,5);
INSERT INTO "score_table" VALUES (56,'TJ Jarovce Bratislava',16,7,2,7,'34:54',23,5);
INSERT INTO "score_table" VALUES (57,'MŠK Senec',16,7,1,8,'41:25',22,5);
INSERT INTO "score_table" VALUES (58,'FKP BRATISLAVA',16,6,2,8,'24:38',20,5);
INSERT INTO "score_table" VALUES (59,'FKM Stupava',16,6,1,9,'37:56',19,5);
INSERT INTO "score_table" VALUES (60,'FC Ružinov Bratislava',15,5,1,9,'39:34',16,5);
INSERT INTO "score_table" VALUES (61,'FC - Žolík Malacky',16,3,3,10,'25:55',12,5);
INSERT INTO "score_table" VALUES (62,'ŠK Bernolákovo',15,1,0,14,'14:90',3,5);
INSERT INTO "score_table" VALUES (63,'FC Slovan Modra',15,0,1,14,'3:130',1,5);
INSERT INTO "score_table" VALUES (64,'FC IMAS (odstúpené)',0,0,0,0,'0:0',0,5);
INSERT INTO "score_table" VALUES (65,'FC Slovan Modra',20,15,4,1,'50:16',49,1);
INSERT INTO "score_table" VALUES (66,'TJ Záhoran Jakubov',19,12,4,3,'46:17',40,1);
INSERT INTO "score_table" VALUES (67,'Lokomotíva Devínska Nová Ves',19,11,4,4,'56:30',37,1);
INSERT INTO "score_table" VALUES (68,'FK Danubia Veľký Biel',19,8,9,2,'38:27',33,1);
INSERT INTO "score_table" VALUES (69,'TJ Slovan Vištuk',19,9,5,5,'45:31',32,1);
INSERT INTO "score_table" VALUES (70,'TJ Záhoran Kostolište',19,9,2,8,'66:58',29,1);
INSERT INTO "score_table" VALUES (71,'ŠK Závod',20,8,4,8,'39:42',28,1);
INSERT INTO "score_table" VALUES (72,'FKM Karlova Ves Bratislava',19,8,4,7,'52:34',28,1);
INSERT INTO "score_table" VALUES (73,'FK Karpaty Limbach',20,6,6,8,'31:31',24,1);
INSERT INTO "score_table" VALUES (74,'Obecný športový klub Láb',19,6,3,10,'24:44',21,1);
INSERT INTO "score_table" VALUES (75,'OŠK Slovenský Grob',19,6,3,10,'32:34',21,1);
INSERT INTO "score_table" VALUES (76,'TJ Čunovo',19,6,3,10,'31:48',21,1);
INSERT INTO "score_table" VALUES (77,'FK Vajnory',20,6,2,12,'21:38',20,1);
INSERT INTO "score_table" VALUES (78,'CFK Pezinok - Cajla',20,5,4,11,'28:54',19,1);
INSERT INTO "score_table" VALUES (79,'FK Lamač Bratislava',20,5,4,11,'27:41',19,1);
INSERT INTO "score_table" VALUES (80,'ŠK Svätý Jur',19,3,3,13,'30:71',12,1);
INSERT INTO "player" VALUES (31,'Richard Turinič',1,'3',1,0,0,3);
INSERT INTO "player" VALUES (32,'Jakub Vyskočil',1,'3',1,3,0,3);
INSERT INTO "player" VALUES (33,'Lukáš Tichý',1,'3',0,1,0,3);
INSERT INTO "player" VALUES (34,'Nicolas Pachinger',1,'3',2,0,1,3);
INSERT INTO "player" VALUES (35,'Oliver Kročka',1,'3',0,0,0,3);
INSERT INTO "player" VALUES (36,'Jakub Richter',1,'3',1,1,0,3);
INSERT INTO "player" VALUES (37,'Timotej Baričič',1,'3',1,0,0,3);
INSERT INTO "player" VALUES (38,'Matej Ďurian',1,'3',0,0,0,3);
INSERT INTO "player" VALUES (39,'Maťej Babača',1,'3',5,1,0,3);
INSERT INTO "player" VALUES (40,'Šimon Urbanec',1,'3',5,1,0,3);
INSERT INTO "player" VALUES (41,'Denis Michael Kintler',1,'3',5,4,0,3);
INSERT INTO "player" VALUES (42,'Adam Szerencés',1,'3',2,0,0,3);
INSERT INTO "player" VALUES (43,'Sebastián Sališ',1,'3',0,0,0,3);
INSERT INTO "player" VALUES (44,'Adam Jurčík',1,'3',4,1,0,3);
INSERT INTO "player" VALUES (45,'Anton Kenderessy',1,'3',0,0,0,3);
INSERT INTO "player" VALUES (46,'Martin Kulifaj',1,'3',9,0,0,3);
INSERT INTO "player" VALUES (47,'Juraj Nemčovič',1,'3',0,0,0,3);
INSERT INTO "player" VALUES (48,'Viktor Brichta',1,'4',0,0,0,4);
INSERT INTO "player" VALUES (49,'Jakub Richter',1,'4',0,1,0,4);
INSERT INTO "player" VALUES (50,'Matej Ďurian',1,'4',2,0,0,4);
INSERT INTO "player" VALUES (51,'Anton Kenderessy',1,'4',0,3,0,4);
INSERT INTO "player" VALUES (52,'Samuel Varga',1,'4',0,0,0,4);
INSERT INTO "player" VALUES (53,'Bernard Ličko',1,'4',0,0,0,4);
INSERT INTO "player" VALUES (54,'Daniel Duban',1,'4',1,0,0,4);
INSERT INTO "player" VALUES (55,'Peter Babača',1,'4',1,3,1,4);
INSERT INTO "player" VALUES (56,'Adam Oravec',1,'4',1,0,0,4);
INSERT INTO "player" VALUES (57,'Boris Kročka',1,'4',0,0,0,4);
INSERT INTO "player" VALUES (58,'Adam Trabalka',1,'4',0,0,0,4);
INSERT INTO "player" VALUES (59,'Jakub Hanic',1,'4',2,0,0,4);
INSERT INTO "player" VALUES (60,'Adem Useini',1,'4',0,1,0,4);
INSERT INTO "player" VALUES (61,'Viliam Fiala',1,'4',0,0,0,4);
INSERT INTO "player" VALUES (62,'David Darula',1,'4',1,0,0,4);
INSERT INTO "player" VALUES (63,'Peter Juran',1,'4',0,0,0,4);
INSERT INTO "player" VALUES (64,'Martin Tichý',1,'4',0,0,0,4);
INSERT INTO "player" VALUES (65,'Marko Fraňo',1,'4',0,1,0,4);
INSERT INTO "player" VALUES (66,'Boris Milan Valentšik',1,'4',0,0,0,4);
INSERT INTO "player" VALUES (67,'Lukáš Ochaba',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (68,'Pavel Antalec',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (69,'David Pilka',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (70,'Filip Pilka',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (71,'Daniel Škultéty',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (72,'Richard Somorovsky',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (73,'Nela Baxová',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (74,'Adrián Lederleitner',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (75,'Volodymyr Hodis',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (76,'Michal Polčič',1,'5',1,0,0,5);
INSERT INTO "player" VALUES (77,'Andrej Oman',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (78,'Martin Tichý',1,'5',1,0,0,5);
INSERT INTO "player" VALUES (79,'Adam Cíferský',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (80,'Bohuš Bišťan',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (81,'Patrik Jurčík',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (82,'Hugo Juskanič',1,'5',1,0,0,5);
INSERT INTO "player" VALUES (83,'Peter Juran',1,'5',0,0,0,5);
INSERT INTO "player" VALUES (84,'Marcel Kuľha',1,'1',0,0,0,1);
INSERT INTO "player" VALUES (85,'Ján Horáček',1,'1',0,0,0,1);
INSERT INTO "player" VALUES (86,'Ľubomír Lörincz',1,'1',0,0,0,1);
INSERT INTO "player" VALUES (87,'Milan Vinclér',1,'1',0,1,0,1);
INSERT INTO "player" VALUES (88,'Patrik Anguš',1,'1',0,0,0,1);
INSERT INTO "player" VALUES (89,'František Dolutovský',1,'1',0,6,0,1);
INSERT INTO "player" VALUES (90,'Martin Lehocký',1,'1',0,4,0,1);
INSERT INTO "player" VALUES (91,'Idris Ayodjii Lawal',1,'1',0,4,0,1);
INSERT INTO "player" VALUES (92,'Martin Kubín',1,'1',1,1,0,1);
INSERT INTO "player" VALUES (93,'Peter Vojtovič',1,'1',0,3,2,1);
INSERT INTO "player" VALUES (94,'Tomáš Plach',1,'1',0,0,0,1);
INSERT INTO "player" VALUES (95,'Daniel Čabala',1,'1',0,1,0,1);
INSERT INTO "player" VALUES (96,'Ruberth Alberto Garcia Quejada',1,'1',10,1,0,1);
INSERT INTO "player" VALUES (97,'Ján Vislocký',1,'1',3,1,0,1);
INSERT INTO "player" VALUES (98,'Štefan Maťaš',1,'1',0,0,0,1);
INSERT INTO "player" VALUES (99,'Martin Kovár',1,'1',2,1,0,1);
INSERT INTO "player" VALUES (100,'Slavomír Podubinský',1,'1',0,0,0,1);
INSERT INTO "player" VALUES (101,'Patrik Dvorák',1,'1',0,4,1,1);
INSERT INTO "player" VALUES (102,'Jhonatan Garcia Araque',1,'1',4,1,0,1);
INSERT INTO "player" VALUES (103,'David Peško',1,'1',3,0,0,1);
INSERT INTO "player" VALUES (104,'Mauricio Ospino Perez',1,'1',3,0,0,1);
INSERT INTO "player" VALUES (105,'Carlos Alberto Palacios Romaňa',1,'1',4,0,0,1);
INSERT INTO "player" VALUES (106,'Marek Heriban',1,'1',0,0,0,1);
INSERT INTO "player" VALUES (107,'Jakub Pavúk',1,'1',5,6,0,1);
INSERT INTO "player" VALUES (108,'Stanislav Haniš',1,'1',4,0,0,1);
INSERT INTO "player" VALUES (109,'Tomáš Tichý',1,'1',1,0,0,1);
INSERT INTO "player" VALUES (110,'Peter Bondra',1,'1',0,0,0,1);
INSERT INTO "player" VALUES (111,'Romuald Yvan Echeng Aguem',1,'1',5,4,1,1);
INSERT INTO "player" VALUES (112,'Norbert Sališ',1,'1',4,0,0,1);
INSERT INTO "player" VALUES (113,'Elias Ariel Argumedo Gutierrez',1,'1',1,1,0,1);
COMMIT;
