BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "user" (
	"id"	SERIAL NOT NULL,
	"uuid"	TEXT,
	"username"	VARCHAR(20) NOT NULL,
	"email"	VARCHAR(120) NOT NULL,
	"image_file"	VARCHAR(20) NOT NULL,
	"password"	VARCHAR(60) NOT NULL,
	PRIMARY KEY("id"),
	UNIQUE("username"),
	UNIQUE("email")
);
CREATE TABLE IF NOT EXISTS "category" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(200) NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "post" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(600) NOT NULL,
	"date_posted"	timestamp NOT NULL,
	"content"	TEXT NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("category_id") REFERENCES "category"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "post_gallery" (
	"id"	SERIAL NOT NULL,
	"title"	VARCHAR(600) NOT NULL,
	"image_file2"	VARCHAR(330) NOT NULL,
	"orderz"	INTEGER,
	"post_id"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("post_id") REFERENCES "post"("id")
);
INSERT INTO "user" VALUES (1,'ecdfbeef-5fca-4402-af98-e8bdd2ee2708','milanmartis','milanmartis@gmail.com','default.jpg','$2b$12$NbsltmAcIIv47eqa.b9wFeNiViOtS5g87wkOTUBZnj4atDCMumUHW');
INSERT INTO "user" VALUES (2,'f8f6f9ee-e1dd-456c-89d5-65ce94bb839a','mito','info@appdesign.sk','default.jpg','$2b$12$HSIj/D5EfTeHSuafO56NAOXJbLoFWxJsVXS8fDlooG/NLyGmWAXWG');
INSERT INTO "category" VALUES (1,'Aktuality');
INSERT INTO "category" VALUES (2,'A team');
INSERT INTO "category" VALUES (3,'jjjj');
INSERT INTO "post" VALUES (1,'Paris Saint-Germain: ‘Defeat is a culture’','2023-03-13 21:15:19','QSI doubled down by signing Messi and also Sergio Ramos – one of the Champions League’s most successful players of all time.



That strategy hasn’t worked as PSG were knocked out in the round of 16 last year by a Karim Benzema-inspired Real Madrid and this season by a functional, if not inspiring, Bayern.',1,1);
INSERT INTO "post" VALUES (2,'Erik ten Hag slams','2023-03-13 21:58:59','Braces from Cody Gakpo, Darwin Núñez and Mo Salah, plus Roberto Firmino’s late goal, secured the utterly dominant win and it’s no surprise that many of United’s traveling fans had left the stadium before the final whistle.



',1,2);
INSERT INTO "post" VALUES (3,'Cristiano Ronaldo Selling Former Manchester Mansion for £3.25M','2023-03-14 10:35:27','Images of the house reveal Mr. Ronaldo’s surprisingly Gothic taste in furnishings. The spartan decor left in the house is almost exclusively black, including a black shag and cowhide rugs, a plush charcoal-gray couch and even sheer black curtains.



',1,2);
INSERT INTO "post" VALUES (4,'Athletic Bilbao fans protest improper payment444','2023-03-14 10:37:00','Raphinha scored the only goal of the match as Barcelona won 1-0 and moved nine points clear at the top of La Liga, though the ongoing payment scandal has continued to engulf the club off the field with a number of former officials, including ex-president Josep Maria Bartomeu, also charged.



',1,2);
INSERT INTO "post" VALUES (13,'World Cup final: How Argentina won penalty shootout','2023-03-14 13:55:15','A soccer match lasts for 90 minutes, another 30 if there really needs to be a winner. But if it’s still level after that, then the game will be decided with a penalty shootout, arguably the most nerve-shredding experience in all of sports.



For the fans, it’s excruciating; at the World Cup in Qatar, one Argentina supporter sobbed uncontrollably as she watched the quarterfinal shootout against the Netherlands through her fingers. By the end, she looked distraught. All the emotion had been wrung out of her, and the tears that she cried were of relief, rather than joy.



For the players, such emotions are magnified tenfold. “Love hurts,” goes the anonymous quote, “but not as much as penalties.”



Success or failure could be career-defining, one simple kick from 12 yards is weighed down by teammates’ hopes and the expectation of potentially millions of fans. As the author Karl Wiggins put it, “It’s as if, for a few seconds, a player’s soul is laid bare for the entire world to see.”



',1,2);
INSERT INTO "post" VALUES (14,'Rampant Liverpool humiliates Manchester United with stunning 7-0 Premier League derby win','2023-03-14 16:27:02','This season has been one of trials and tribulations for Liverpool and its beleaguered fans, but there may still be light at the end of the tunnel as Jurgen Klopp’s men put in a truly scintillating performance to tear Manchester United apart at Anfield.



Braces from Cody Gakpo, Darwin Núñez and Mo Salah, plus Roberto Firmino’s late goal, secured an utterly dominant 7-0 win in this Premier League grudge match, marking the biggest win in the history of this storied fixture.



It was a sobering afternoon for Erik ten Hag’s side, which had been on a brilliant run of form since the season resumed following the World Cup and at one stage even looked as though it may begin to put pressure on Manchester City and Arsenal at the top of the table.



Klopp had called United a “results machine” in the build up to this match and even in his wildest dreams the German would surely not have envisaged a performance and result like this one.',1,2);
INSERT INTO "post" VALUES (15,'‘Muchachos’: How a 2003 hit became the unofficial anthem of Argentina’s World Cup success','2023-03-14 18:19:41','If you’ve had a catchy tune stuck in your head from the World Cup, it’s likely this one.



Heard in the streets of Doha, the stands of the Lusail Stadium and even in the Argentine dressing room, the 2003 hit ‘Muchachos’ by La Mosca has become the unofficial anthem of Argentina’s World Cup success.



Originally bearing the title “Muchachos, esta noche me emborracho” – “Boys, tonight I will get drunk” – the song was rewritten by a teacher, Fernando Romero, to mention Lionel Messi, Diego Maradona and “the kids of las Malvinas.”



Romero renamed the song “Muchachos, ahora nos volvimos a ilusionar” – “Boys, now we have hope again” – and such was its popularity, La Mosca rerecorded the tune with the new lyrics before the World Cup in Qatar, even featuring Romero in the new music video.



In an interview with Argentine outlet El Destape, Romero said the song has “changed my life.”',1,1);
INSERT INTO "post_gallery" VALUES (1,'Paris Saint-Germain: ‘Defeat is a culture’','230309071428-bayern-munich-goal-file-restricted-030823.jpg',0,1);
INSERT INTO "post_gallery" VALUES (2,'Erik ten Hag slams ‘unprofessional’ players','230309070852-lionel-messi-munich-030823.jpg',0,2);
INSERT INTO "post_gallery" VALUES (3,'Cristiano Ronaldo Selling Former Manchester Mansion for £3.25M','230306093450-01-manchester-liverpool-030523-restricted.jpg',0,3);
INSERT INTO "post_gallery" VALUES (4,'Athletic Bilbao fans protest improper payment444','230313114640-03-bilbao-fans-barcelona-031223.jpg',0,4);
INSERT INTO "post_gallery" VALUES (5,'World Cup final: How Argentina won penalty shootout','230301113421-05-penalty-shoot-outs.jpg',0,13);
INSERT INTO "post_gallery" VALUES (6,'Rampant Liverpool humiliates Manchester United with stunning 7-0 Premier League derby win','230305132620-01-liverpool-manchester-united-0305.jpg',1,14);
INSERT INTO "post_gallery" VALUES (7,'Rampant Liverpool humiliates Manchester United with stunning 7-0 Premier League derby win','230305132838-03-liverpool-manchester-united-0305.jpg',1,14);
INSERT INTO "post_gallery" VALUES (8,'Rampant Liverpool humiliates Manchester United with stunning 7-0 Premier League derby win','230305132931-04-liverpool-manchester-united-0305 (1).jpg',1,14);
INSERT INTO "post_gallery" VALUES (9,'Rampant Liverpool humiliates Manchester United with stunning 7-0 Premier League derby win','230305132751-02-liverpool-manchester-united-0305.jpg',0,14);
INSERT INTO "post_gallery" VALUES (10,'‘Muchachos’: How a 2003 hit became the unofficial anthem of Argentina’s World Cup success','221207114430-ronaldo-cheers-bench.jpg',1,15);
INSERT INTO "post_gallery" VALUES (11,'‘Muchachos’: How a 2003 hit became the unofficial anthem of Argentina’s World Cup success','230301113421-05-penalty-shoot-outs.jpg',1,15);
INSERT INTO "post_gallery" VALUES (12,'‘Muchachos’: How a 2003 hit became the unofficial anthem of Argentina’s World Cup success','230305132620-01-liverpool-manchester-united-0305.jpg',1,15);
INSERT INTO "post_gallery" VALUES (13,'‘Muchachos’: How a 2003 hit became the unofficial anthem of Argentina’s World Cup success','230306093450-01-manchester-liverpool-030523-restricted.jpg',1,15);
INSERT INTO "post_gallery" VALUES (14,'‘Muchachos’: How a 2003 hit became the unofficial anthem of Argentina’s World Cup success','230313114614-02-bilbao-fans-barcelona-031223.jpg',1,15);
INSERT INTO "post_gallery" VALUES (15,'‘Muchachos’: How a 2003 hit became the unofficial anthem of Argentina’s World Cup success','230313114640-03-bilbao-fans-barcelona-031223.jpg',1,15);
INSERT INTO "post_gallery" VALUES (16,'‘Muchachos’: How a 2003 hit became the unofficial anthem of Argentina’s World Cup success','221219214614-pba-nacho-pkg.jpg',0,15);
COMMIT;
