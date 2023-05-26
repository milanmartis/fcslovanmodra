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
CREATE TABLE IF NOT EXISTS "category" (
	"id"	SERIAL NOT NULL,
	"name"	VARCHAR(200) NOT NULL,
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
-- INSERT INTO "user" VALUES (1,'e5fe08f5-d128-48fa-820a-e309efc441ef','milanmartis','milanmartis@gmail.com','default.jpg','$2b$12$P7Vtn5YUrjrgwzt0hDEEPekcM3rXJfQ5RO0t.2vYLYNMUknEOjzVa');
-- INSERT INTO "category" VALUES (1,'Aktuality');
-- INSERT INTO "category" VALUES (2,'A TEAM');
-- INSERT INTO "post" VALUES (1,'lknlkn','2023-03-11 16:57:59','lknlknlknlkn',1,2);
COMMIT;
