BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "user" (
	id SERIAL PRIMARY KEY,
	username VARCHAR(20) UNIQUE NOT NULL,
	email VARCHAR(120) UNIQUE NOT NULL,
	image_file VARCHAR(20) NOT NULL,
	password VARCHAR(60) NOT NULL
);
CREATE TABLE IF NOT EXISTS "post" (
	id SERIAL PRIMARY KEY,
	title	VARCHAR(100) NOT NULL,
	date_posted	TIMESTAMP NOT NULL,
	content	TEXT NOT NULL,
	user_id	INTEGER NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
INSERT INTO "user" VALUES (1,'milanmartis','milanmartis@gmail.com','9a2c801fc2fa84b2.jpg','$2b$12$zzO..m8udNa66ng0dcSeFunbKWtHJcNNYcX.7vriULz2eSPGzKd72');
INSERT INTO "user" VALUES (2,'Pišta','pista@dartsclub.sk','2e94a648bf283573.jpg','$2b$12$hMk0SBgWwrAevqGaOKwRf.ao2aav63eVn58wC1ZsVBmyptfAY0WCi');
INSERT INTO "post" VALUES (1,'Scott Parker: Club Bruges sack manager','2023-03-08 15:53:36.754860','The 42-year-old Englishman saw his side lose 5-1 to Benfica in their Champions League last 16 second leg on Tuesday, going out 7-1 on aggregate.



"Scott Parker is no longer head coach of Club Bruges," the club said in a short statement on Wednesday. ',1);
INSERT INTO "post" VALUES (3,'Too late for a comeback?','2023-03-08 21:24:22.720845','Great attacking build-up from Sarri. The energy she''s injected; she''s making things happen. Carter toe-pokes home but is it too late for them?',2);
INSERT INTO "post" VALUES (4,'GOAL - Chelsea 3-1 Brighton','2023-03-08 21:24:54.376528','The visitors do get a goal. Chelsea fail to clear the danger and substitute Danielle Carter reacts quickest to prod a finish past Zecira Musovic.',1);
INSERT INTO "post" VALUES (5,'Bianca Andreescu ''motivated and hungry'' after injury and mental health issues','2023-03-08 21:25:18.046739','A break from the sport in early 2022 included a retreat in Costa Rica, and 12 months on the now 22-year-old is able to say with a smile on her face that she "loves being back on tour, and loves the sport again".



"I definitely don''t feel like I have the perfect recipe," Andreescu says while preparing for the BNP Paribas Open at Indian Wells, which starts on Wednesday.



"I''m not sure anyone really does other than maybe Novak Djokovic and Roger Federer. But I''m striving to be as close to perfect as I can be, and I feel like right now I have a pretty good recipe as I feel really good about myself. ',1);
INSERT INTO "post" VALUES (6,'Red-S: Pippa Woolven''s experience and awareness activism','2023-03-08 21:25:53.923072','The condition affects both men and women, and can impact levels of oestrogen - an essential hormone for bone health. As a result of the condition, both Boniface and Clay developed osteoporosis.',2);
INSERT INTO "post" VALUES (7,'Abi Burton: ''I nearly died''','2023-03-08 21:26:17.863064','But Burton, 22, had no idea just how tough life was about to get.



One year on from losing to Fiji, she was wrongly sectioned for 26 days, spent 25 days in an induced coma, and contracted pneumonia twice.',2);
INSERT INTO "post" VALUES (8,'Rugby World Cup: The intrigue & inspiration behind first women''s tournament of 1991','2023-03-08 21:27:40.669033','One team was supposedly accompanied by KGB agents. Another had to sleep on the floor of a hotel conference room three days before the final. A young baby attended talks with rugby''s international governing body as one woman balanced motherhood with organising a major tournament.',1);
INSERT INTO "post" VALUES (9,'Syrian FA bans Ahmed Al-Saleh for life','2023-03-08 22:02:13.390687','The 33-year-old Al-Jaish defender lashed out at the official after being shown a red card in a top-flight game against Al-Wathba on Friday.



Al-Saleh had to be restrained by players from both sides.



The SFA disciplinary committee also fined Al-Saleh and Al-Jaish, who cannot appeal against the punishments.',2);
INSERT INTO "post" VALUES (10,'Liverpool v Manchester United','2023-03-08 22:02:48.921640','Football Focus pundit Stephen Warnock believes if Liverpool try to go "toe-to-toe" with Manchester United on Sunday, they could end up being "punished" by Erik ten Hag''s side.



Listen to Liverpool v Manchester United on Sunday, March 5 at 16.30 GMT on BBC Sounds.',2);
INSERT INTO "post" VALUES (12,'Jurgen Klopp: Liverpool manager ''really happy'' for Marcus Rashford''s return to form','2023-03-08 22:03:28.846950','Liverpool manager Jurgen Klopp says he is "really happy" to see Marcus Rashford return to form, although it is difficult for him to be positive for rivals Manchester United.



READ MORE: Klopp ''really happy'' for Rashford after ''difficult year''',1);
INSERT INTO "post" VALUES (13,'Cristian Stellini: Tottenham assistant manager does not regret starting Harry Kane on bench','2023-03-08 22:03:52.612826','Tottenham Hotspur assistant manager Cristian Stellini says he does not regret starting Harry Kane on the bench in Spurs'' defeat to Sheffield United in the FA Cup.',1);
INSERT INTO "post" VALUES (14,'My Latest Blog Post','2023-03-09 17:00:29.989466','Russia launched one of its biggest aerial assaults Thursday with 81 missiles targeted at Ukrainian infrastructure across the country. This included six Kinzhal ballistic missiles that eluded Kyiv''s air defenses, the Ukrainian military said. At least 11 people were killed.',1);
INSERT INTO "post" VALUES (15,' Chaim Topol, ‘Fiddler on the Roof’','2023-03-09 17:06:56.477663','“The story of Haim Topol’s life has been sealed but I am certain that his contribution to Israeli culture will live on for generations,” Netanyahu said in a statement. “He greatly loved the land of Israel, and the people of Israel loved him in return.” ',2);
COMMIT;
