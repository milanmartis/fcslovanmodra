--
-- PostgreSQL database dump
--

-- Dumped from database version 15.2
-- Dumped by pg_dump version 15.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: category; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.category (
    id integer NOT NULL,
    name character varying(200) NOT NULL
);


--
-- Name: category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.category_id_seq OWNED BY public.category.id;


--
-- Name: club; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.club (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    subdomain character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: club_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.club_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: club_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.club_id_seq OWNED BY public.club.id;


--
-- Name: event; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.event (
    id integer NOT NULL,
    title character varying(250) NOT NULL,
    start_event timestamp without time zone,
    end_event timestamp without time zone,
    user_id integer NOT NULL,
    event_category_id integer,
    event_team_id integer,
    address text,
    link text
);


--
-- Name: event_category; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.event_category (
    id integer NOT NULL,
    name character varying(200) NOT NULL
);


--
-- Name: event_category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.event_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: event_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.event_category_id_seq OWNED BY public.event_category.id;


--
-- Name: event_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.event_id_seq OWNED BY public.event.id;


--
-- Name: member; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.member (
    id integer NOT NULL,
    name character varying(250) NOT NULL,
    phone character varying(250) NOT NULL,
    address character varying(250) NOT NULL,
    psc character varying(250) NOT NULL,
    city character varying(250) NOT NULL,
    image_file character varying(20) NOT NULL,
    weight integer,
    height integer,
    user_id integer NOT NULL
);


--
-- Name: member_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.member_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: member_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.member_id_seq OWNED BY public.member.id;


--
-- Name: order; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."order" (
    id integer NOT NULL,
    produc_id integer NOT NULL,
    quantity integer,
    amount numeric(10,2) NOT NULL,
    user_id integer NOT NULL,
    is_paid boolean,
    order_date timestamp without time zone NOT NULL,
    storno boolean,
    variants text
);


--
-- Name: order_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.order_id_seq OWNED BY public."order".id;


--
-- Name: player; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.player (
    id integer NOT NULL,
    name character varying(250) NOT NULL,
    "position" integer,
    team character varying(250) NOT NULL,
    score integer,
    yellow_card integer,
    red_card integer,
    team_id integer NOT NULL,
    photo_url text
);


--
-- Name: player_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.player_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: player_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.player_id_seq OWNED BY public.player.id;


--
-- Name: position; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."position" (
    id integer NOT NULL,
    name character varying(180)
);


--
-- Name: position_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.position_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: position_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.position_id_seq OWNED BY public."position".id;


--
-- Name: positions_members; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.positions_members (
    member_id integer,
    position_id integer
);


--
-- Name: post; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    date_posted timestamp without time zone NOT NULL,
    content text NOT NULL,
    user_id integer NOT NULL,
    category_id integer NOT NULL
);


--
-- Name: post_gallery; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_gallery (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    image_file2 character varying(150) NOT NULL,
    orderz integer,
    post_id integer NOT NULL
);


--
-- Name: post_gallery_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.post_gallery_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: post_gallery_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.post_gallery_id_seq OWNED BY public.post_gallery.id;


--
-- Name: post_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.post_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: post_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.post_id_seq OWNED BY public.post.id;


--
-- Name: product; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    date_posted timestamp without time zone NOT NULL,
    content text NOT NULL,
    user_id integer NOT NULL,
    is_visible boolean,
    price numeric(10,2) NOT NULL,
    old_price numeric(10,2) NOT NULL,
    product_category_id integer NOT NULL,
    youtube_link character varying,
    stripe_link character varying(100)
);


--
-- Name: product_category; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_category (
    id integer NOT NULL,
    name character varying(200) NOT NULL
);


--
-- Name: product_category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.product_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: product_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.product_category_id_seq OWNED BY public.product_category.id;


--
-- Name: product_gallery; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_gallery (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    image_file2 character varying(150) NOT NULL,
    orderz integer,
    product_id integer NOT NULL
);


--
-- Name: product_gallery_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.product_gallery_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: product_gallery_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.product_gallery_id_seq OWNED BY public.product_gallery.id;


--
-- Name: product_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.product_id_seq OWNED BY public.product.id;


--
-- Name: product_variant; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_variant (
    id integer NOT NULL,
    name character varying(250) NOT NULL,
    type integer NOT NULL
);


--
-- Name: product_variant_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.product_variant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: product_variant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.product_variant_id_seq OWNED BY public.product_variant.id;


--
-- Name: product_variant_product; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_variant_product (
    product_variant_id integer,
    product_id integer
);


--
-- Name: role; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.role (
    id integer NOT NULL,
    name character varying(180),
    description character varying(250)
);


--
-- Name: role_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.role_id_seq OWNED BY public.role.id;


--
-- Name: roles_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles_users (
    user_id integer,
    role_id integer
);


--
-- Name: score_table; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.score_table (
    id integer NOT NULL,
    club character varying(250) NOT NULL,
    games integer,
    wins integer,
    draws integer,
    loses integer,
    score character varying(20) NOT NULL,
    points integer,
    team_id integer NOT NULL,
    logo text
);


--
-- Name: score_table_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.score_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: score_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.score_table_id_seq OWNED BY public.score_table.id;


--
-- Name: sponsors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sponsors (
    id integer NOT NULL,
    name character varying(128),
    url character varying(255),
    kind character varying(20) NOT NULL,
    image_file character varying(255) NOT NULL,
    orderz integer DEFAULT 0 NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    describe text
);


--
-- Name: sponsors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sponsors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sponsors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sponsors_id_seq OWNED BY public.sponsors.id;


--
-- Name: team; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.team (
    id integer NOT NULL,
    name character varying(250) NOT NULL,
    score_scrap character varying(250) NOT NULL,
    player_list_scrap character varying(250) NOT NULL,
    main_league character varying(300),
    events_results_scrap character varying(550),
    events_program_scrap character varying(550)
);


--
-- Name: team_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.team_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: team_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.team_id_seq OWNED BY public.team.id;


--
-- Name: teams_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.teams_events (
    team_id integer,
    event_id integer
);


--
-- Name: teams_members; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.teams_members (
    member_id integer,
    team_id integer
);


--
-- Name: type_product_variant; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.type_product_variant (
    id integer NOT NULL,
    name character varying(250) NOT NULL,
    operation character varying(450) NOT NULL
);


--
-- Name: type_product_variant_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.type_product_variant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: type_product_variant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.type_product_variant_id_seq OWNED BY public.type_product_variant.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    uuid text,
    username character varying(20) NOT NULL,
    email character varying(120) NOT NULL,
    image_file character varying(20) NOT NULL,
    password character varying(60) NOT NULL,
    confirm boolean DEFAULT false NOT NULL,
    active boolean DEFAULT true NOT NULL,
    confirmed_at timestamp with time zone,
    fs_uniquifier text
);


--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: variant_products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.variant_products (
    product_id integer,
    variant_id integer,
    variant_text character varying(100) NOT NULL,
    variant_image text,
    id integer NOT NULL
);


--
-- Name: variant_products_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.variant_products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: variant_products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.variant_products_id_seq OWNED BY public.variant_products.id;


--
-- Name: category id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category ALTER COLUMN id SET DEFAULT nextval('public.category_id_seq'::regclass);


--
-- Name: club id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.club ALTER COLUMN id SET DEFAULT nextval('public.club_id_seq'::regclass);


--
-- Name: event id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event ALTER COLUMN id SET DEFAULT nextval('public.event_id_seq'::regclass);


--
-- Name: event_category id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event_category ALTER COLUMN id SET DEFAULT nextval('public.event_category_id_seq'::regclass);


--
-- Name: member id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.member ALTER COLUMN id SET DEFAULT nextval('public.member_id_seq'::regclass);


--
-- Name: order id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."order" ALTER COLUMN id SET DEFAULT nextval('public.order_id_seq'::regclass);


--
-- Name: player id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.player ALTER COLUMN id SET DEFAULT nextval('public.player_id_seq'::regclass);


--
-- Name: position id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."position" ALTER COLUMN id SET DEFAULT nextval('public.position_id_seq'::regclass);


--
-- Name: post id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post ALTER COLUMN id SET DEFAULT nextval('public.post_id_seq'::regclass);


--
-- Name: post_gallery id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_gallery ALTER COLUMN id SET DEFAULT nextval('public.post_gallery_id_seq'::regclass);


--
-- Name: product id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product ALTER COLUMN id SET DEFAULT nextval('public.product_id_seq'::regclass);


--
-- Name: product_category id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_category ALTER COLUMN id SET DEFAULT nextval('public.product_category_id_seq'::regclass);


--
-- Name: product_gallery id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_gallery ALTER COLUMN id SET DEFAULT nextval('public.product_gallery_id_seq'::regclass);


--
-- Name: product_variant id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_variant ALTER COLUMN id SET DEFAULT nextval('public.product_variant_id_seq'::regclass);


--
-- Name: role id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role ALTER COLUMN id SET DEFAULT nextval('public.role_id_seq'::regclass);


--
-- Name: score_table id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.score_table ALTER COLUMN id SET DEFAULT nextval('public.score_table_id_seq'::regclass);


--
-- Name: sponsors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sponsors ALTER COLUMN id SET DEFAULT nextval('public.sponsors_id_seq'::regclass);


--
-- Name: team id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.team ALTER COLUMN id SET DEFAULT nextval('public.team_id_seq'::regclass);


--
-- Name: type_product_variant id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.type_product_variant ALTER COLUMN id SET DEFAULT nextval('public.type_product_variant_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: variant_products id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.variant_products ALTER COLUMN id SET DEFAULT nextval('public.variant_products_id_seq'::regclass);


--
-- Data for Name: category; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.category (id, name) FROM stdin;
1	Aktuality
2	A team
3	Mládež
8	Blog
\.


--
-- Data for Name: club; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.club (id, name, subdomain, created_at) FROM stdin;
\.


--
-- Data for Name: event; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.event (id, title, start_event, end_event, user_id, event_category_id, event_team_id, address, link) FROM stdin;
1037	NŠK 1922 Bratislava 4:0 FC Slovan Modra	2025-08-09 08:30:00	2025-08-09 10:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+N%C5%A0K+1922+Bratislava
1038	FC Slovan Modra 0:2 FK Slovan Ivanka pri Dunaji	2025-08-16 15:00:00	2025-08-16 17:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1039	FKM Karlova Ves Bratislava 5:1 FC Slovan Modra	2025-08-24 15:00:00	2025-08-24 17:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FKM+Karlova+Ves+Bratislava
1040	FC Slovan Modra 3:0 Lokomotíva Devínska Nová Ves	2025-08-30 14:30:00	2025-08-30 16:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1041	PŠC Pezinok 1:1 FC Slovan Modra	2025-09-06 14:30:00	2025-09-06 16:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+P%C5%A0C+Pezinok
1042	FC Slovan Modra 2:2 SFC Kalinkovo	2025-09-13 14:00:00	2025-09-13 16:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1043	FC Rohožník 6:0 FC Slovan Modra	2025-09-21 14:00:00	2025-09-21 16:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Roho%C5%BEn%C3%ADk
1044	FC Slovan Modra 2:1 MŠK Kráľová pri Senci	2025-09-27 13:30:00	2025-09-27 15:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1045	TJ Rovinka 1:0 FC Slovan Modra	2025-10-05 13:30:00	2025-10-05 15:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Rovinka
1046	TJ Záhoran Jakubov 0:0 FC Slovan Modra	2025-10-12 13:00:00	2025-10-12 15:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Z%C3%A1horan+Jakubov
1047	FC Slovan Modra 0:1 MFK Rusovce	2025-10-18 13:00:00	2025-10-18 15:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1048	ŠK Bernolákovo 2:0 FC Slovan Modra	2025-10-25 12:00:00	2025-10-25 14:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Bernol%C3%A1kovo
1049	FC Slovan Modra 1:1 OFK Dunajská Lužná	2025-11-01 12:30:00	2025-11-01 14:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1050	Športový klub Nová Dedinka 3:0 FC Slovan Modra	2025-11-09 12:30:00	2025-11-09 14:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0portov%C3%BD+klub+Nov%C3%A1+Dedinka
1051	FC Slovan Modra 0:3 ŠK Tomášov	2025-11-15 12:30:00	2025-11-15 14:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1052	FC Slovan Modra - NŠK 1922 Bratislava	2026-03-14 14:00:00	2026-03-14 16:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1053	FK Slovan Ivanka pri Dunaji - FC Slovan Modra	2026-03-22 14:00:00	2026-03-22 16:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+Slovan+Ivanka+pri+Dunaji
1054	FC Slovan Modra - FKM Karlova Ves Bratislava	2026-03-28 14:30:00	2026-03-28 16:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1055	Lokomotíva Devínska Nová Ves - FC Slovan Modra	2026-04-01 15:00:00	2026-04-01 17:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+Lokomot%C3%ADva+Dev%C3%ADnska+Nov%C3%A1+Ves
1056	FC Slovan Modra - PŠC Pezinok	2026-04-11 15:00:00	2026-04-11 17:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1057	SFC Kalinkovo - FC Slovan Modra	2026-04-19 15:00:00	2026-04-19 17:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+SFC+Kalinkovo
1058	FC Slovan Modra - FC Rohožník	2026-04-25 15:00:00	2026-04-25 17:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1059	MŠK Kráľová pri Senci - FC Slovan Modra	2026-04-29 15:30:00	2026-04-29 17:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+M%C5%A0K+Kr%C3%A1%C4%BEov%C3%A1+pri+Senci
1060	FC Slovan Modra - TJ Rovinka	2026-05-02 15:00:00	2026-05-02 17:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1061	FC Slovan Modra - TJ Záhoran Jakubov	2026-05-09 15:00:00	2026-05-09 17:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1062	MFK Rusovce - FC Slovan Modra	2026-05-17 15:00:00	2026-05-17 17:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+MFK+Rusovce
1063	FC Slovan Modra - ŠK Bernolákovo	2026-05-23 15:00:00	2026-05-23 17:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1064	OFK Dunajská Lužná - FC Slovan Modra	2026-05-31 15:30:00	2026-05-31 17:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+OFK+Dunajsk%C3%A1+Lu%C5%BEn%C3%A1
1065	FC Slovan Modra - Športový klub Nová Dedinka	2026-06-06 15:30:00	2026-06-06 17:30:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1066	ŠK Tomášov - FC Slovan Modra	2026-06-13 16:00:00	2026-06-13 18:00:00	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Tom%C3%A1%C5%A1ov
1098	FC Slovan Modra 1:5 TJ SLOVAN Vištuk	2025-09-20 09:00:00	2025-09-20 11:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1099	CFK Pezinok - Cajla 0:2 FC Slovan Modra	2025-09-27 08:30:00	2025-09-27 10:30:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+CFK+Pezinok+-+Cajla
1100	TJ Slovan Viničné 1:1 FC Slovan Modra	2025-10-12 10:30:00	2025-10-12 12:30:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Slovan+Vini%C4%8Dn%C3%A9
1101	FC Slovan Modra 2:2 TJ Záhoran Kostolište	2025-10-08 14:00:00	2025-10-08 16:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1102	Futbalový klub Dubová 5:0 FC Slovan Modra	2025-10-26 09:30:00	2025-10-26 11:30:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+Futbalov%C3%BD+klub+Dubov%C3%A1
1103	FC Slovan Modra 0:4 OŠK Slovenský Grob	2025-11-01 10:00:00	2025-11-01 12:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1067	FK Dúbravka B 4:1 FC Slovan Modra	2025-08-17 11:00:00	2025-08-17 13:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+D%C3%BAbravka+B
1068	FC Slovan Modra 1:2 TJ Slovan Viničné	2025-08-24 12:00:00	2025-08-24 14:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1069	ŠK Bernolákovo 3:4 FC Slovan Modra	2025-10-02 14:00:00	2025-10-02 16:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Bernol%C3%A1kovo
1070	FC Slovan Modra 2:1 FK Vajnory	2025-09-07 12:00:00	2025-09-07 14:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1071	ŠK Tomášov 5:2 FC Slovan Modra	2025-09-13 11:30:00	2025-09-13 13:30:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Tom%C3%A1%C5%A1ov
1072	FC Slovan Modra - FC Ružinov Bratislava	2025-09-20 11:30:00	2025-09-20 13:30:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1119	FC Slovan Modra 6:2 TJ Slovan Viničné	2025-08-24 09:00:00	2025-08-24 11:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1120	TJ Družstevník Jablonec 1:7 FC Slovan Modra	2025-08-31 12:00:00	2025-08-31 14:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Dru%C5%BEstevn%C3%ADk+Jablonec
1121	FC Slovan Modra 2:7 ŠK Igram	2025-09-07 09:00:00	2025-09-07 11:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1122	FC Slovan Modra 3:2 FKM Stupava B	2025-09-11 15:30:00	2025-09-11 17:30:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1123	Futbalový klub Budmerice 0:4 FC Slovan Modra	2025-09-14 08:00:00	2025-09-14 10:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+Futbalov%C3%BD+klub+Budmerice
1124	CFK Pezinok - Cajla 0:4 FC Slovan Modra	2025-09-16 15:00:00	2025-09-16 17:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+CFK+Pezinok+-+Cajla
1125	FC Slovan Modra 0:3 FK Karpaty Limbach	2025-09-21 09:00:00	2025-09-21 11:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1126	FC Slovan Modra 8:0 ŠK Báhoň	2025-09-28 09:00:00	2025-09-28 11:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1127	ŠK Bernolákovo B 3:0 FC Slovan Modra	2025-10-05 07:00:00	2025-10-05 09:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Bernol%C3%A1kovo+B
1128	FC Slovan Modra 10:2 FK CINEMAX Doľany	2025-10-12 09:00:00	2025-10-12 11:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1129	PŠC Pezinok B 2:5 FC Slovan Modra	2025-10-19 10:00:00	2025-10-19 12:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+P%C5%A0C+Pezinok+B
1130	FC Slovan Modra 0:5 OŠK Slovenský Grob	2025-10-26 10:00:00	2025-10-26 12:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1131	ŠK Šenkvice - FC Slovan Modra	2025-11-02 09:00:00	2025-11-02 11:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+%C5%A0enkvice
1132	FC Slovan Modra - ŠK Šenkvice	2026-03-22 10:00:00	2026-03-22 12:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1133	TJ Slovan Viničné - FC Slovan Modra	2026-03-28 12:30:00	2026-03-28 14:30:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Slovan+Vini%C4%8Dn%C3%A9
1134	FC Slovan Modra - TJ Družstevník Jablonec	2026-04-05 09:00:00	2026-04-05 11:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1135	ŠK Igram - FC Slovan Modra	2026-04-11 08:00:00	2026-04-11 10:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Igram
1136	FC Slovan Modra - Futbalový klub Budmerice	2026-04-19 09:00:00	2026-04-19 11:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1137	FK Karpaty Limbach - FC Slovan Modra	2026-04-26 09:30:00	2026-04-26 11:30:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+Karpaty+Limbach
1138	FKM Stupava B - FC Slovan Modra	2026-04-29 15:00:00	2026-04-29 17:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FKM+Stupava+B
1139	ŠK Báhoň - FC Slovan Modra	2026-05-02 08:00:00	2026-05-02 10:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+B%C3%A1ho%C5%88
1140	FC Slovan Modra - CFK Pezinok - Cajla	2026-05-06 15:00:00	2026-05-06 17:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1073	FKM Stupava 1:3 FC Slovan Modra	2025-10-04 08:00:00	2025-10-04 10:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FKM+Stupava
1074	FC Slovan Modra 2:0 Lokomotíva Devínska Nová Ves	2025-10-11 12:00:00	2025-10-11 14:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1075	Senec Football Academy 2:0 FC Slovan Modra	2025-10-18 13:00:00	2025-10-18 15:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+Senec+Football+Academy
1076	FC Slovan Modra 7:1 FC Zohor	2025-10-26 13:00:00	2025-10-26 15:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1077	ŠK Závod - FC Slovan Modra	2025-11-02 09:00:00	2025-11-02 11:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Z%C3%A1vod
1078	FC Slovan Modra 10:2 ŠK Lozorno, FO	2025-11-08 12:30:00	2025-11-08 14:30:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1079	TJ Slovan Viničné - FC Slovan Modra	2026-03-14 14:00:00	2026-03-14 16:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Slovan+Vini%C4%8Dn%C3%A9
1080	FC Slovan Modra - ŠK Bernolákovo	2026-03-22 13:00:00	2026-03-22 15:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1081	FK Vajnory - FC Slovan Modra	2026-03-28 11:30:00	2026-03-28 13:30:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+Vajnory
1141	FC Slovan Modra - ŠK Bernolákovo B	2026-05-10 09:00:00	2026-05-10 11:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1142	FK CINEMAX Doľany - FC Slovan Modra	2026-05-17 13:00:00	2026-05-17 15:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+CINEMAX+Do%C4%BEany
1082	FC Slovan Modra - ŠK Tomášov	2026-04-05 12:00:00	2026-04-05 14:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1143	FC Slovan Modra - PŠC Pezinok B	2026-05-24 09:00:00	2026-05-24 11:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1144	OŠK Slovenský Grob - FC Slovan Modra	2026-05-31 08:00:00	2026-05-31 10:00:00	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+O%C5%A0K+Slovensk%C3%BD+Grob
1083	FC Ružinov Bratislava - FC Slovan Modra	2026-04-11 11:00:00	2026-04-11 13:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Ru%C5%BEinov+Bratislava
1084	FC Slovan Modra - FKM Stupava	2026-04-26 12:00:00	2026-04-26 14:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1085	Lokomotíva Devínska Nová Ves - FC Slovan Modra	2026-05-02 11:30:00	2026-05-02 13:30:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+Lokomot%C3%ADva+Dev%C3%ADnska+Nov%C3%A1+Ves
1086	FC Slovan Modra - Senec Football Academy	2026-05-10 12:00:00	2026-05-10 14:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1087	FC Zohor - FC Slovan Modra	2026-05-17 12:30:00	2026-05-17 14:30:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Zohor
1088	FC Slovan Modra - ŠK Závod	2026-05-24 12:00:00	2026-05-24 14:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1089	ŠK Lozorno, FO - FC Slovan Modra	2026-05-30 13:00:00	2026-05-30 15:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Lozorno%2C+FO
1090	FC Slovan Modra - FK Dúbravka B	2026-06-07 12:00:00	2026-06-07 14:00:00	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1104	FKM Stupava B 1:1 FC Slovan Modra	2025-11-09 13:00:00	2025-11-09 15:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FKM+Stupava+B
1105	FC Slovan Modra - ŠK Lozorno, FO	2026-03-14 10:00:00	2026-03-14 12:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1106	PŠC Pezinok B - FC Slovan Modra	2026-03-22 08:00:00	2026-03-22 10:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+P%C5%A0C+Pezinok+B
1107	FC Slovan Modra - FC Zohor	2026-03-28 10:00:00	2026-03-28 12:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1108	FC Slovan Modra - FK Karpaty Limbach	2026-04-04 09:00:00	2026-04-04 11:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1109	TJ SLOVAN Vištuk - FC Slovan Modra	2026-04-12 12:30:00	2026-04-12 14:30:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+SLOVAN+Vi%C5%A1tuk
1110	FC Slovan Modra - CFK Pezinok - Cajla	2026-04-18 09:00:00	2026-04-18 11:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1111	FC Slovan Modra - TJ Záhoran Jakubov	2026-04-29 15:00:00	2026-04-29 17:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1112	FC Slovan Modra - TJ Slovan Viničné	2026-05-02 09:00:00	2026-05-02 11:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1113	ŠK Šenkvice - FC Slovan Modra	2026-05-06 15:00:00	2026-05-06 17:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+%C5%A0enkvice
1114	TJ Záhoran Kostolište - FC Slovan Modra	2026-05-10 08:30:00	2026-05-10 10:30:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Z%C3%A1horan+Kostoli%C5%A1te
1115	FC Slovan Modra - Futbalový klub Dubová	2026-05-16 09:00:00	2026-05-16 11:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1116	OŠK Slovenský Grob - FC Slovan Modra	2026-05-23 09:30:00	2026-05-23 11:30:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+O%C5%A0K+Slovensk%C3%BD+Grob
1117	FC Slovan Modra - FKM Stupava B	2026-05-30 09:00:00	2026-05-30 11:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1118	FC SLOVAN Častá - FC Slovan Modra	2026-06-07 13:00:00	2026-06-07 15:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+SLOVAN+%C4%8Cast%C3%A1
1091	FC Slovan Modra 7:1 FC SLOVAN Častá	2025-08-19 15:00:00	2025-08-19 17:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1092	ŠK Lozorno, FO 7:2 FC Slovan Modra	2025-08-24 08:30:00	2025-08-24 10:30:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Lozorno%2C+FO
1093	FC Slovan Modra 3:7 PŠC Pezinok B	2025-08-30 09:00:00	2025-08-30 11:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1094	FC Zohor 6:0 FC Slovan Modra	2025-10-01 14:30:00	2025-10-01 16:30:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Zohor
1095	TJ Záhoran Jakubov 2:4 FC Slovan Modra	2025-09-10 15:00:00	2025-09-10 17:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Z%C3%A1horan+Jakubov
1096	FK Karpaty Limbach 0:3 FC Slovan Modra	2025-09-13 09:00:00	2025-09-13 11:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+Karpaty+Limbach
1097	FC Slovan Modra 2:3 ŠK Šenkvice	2025-09-17 15:00:00	2025-09-17 17:00:00	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
\.


--
-- Data for Name: event_category; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.event_category (id, name) FROM stdin;
1	Zápas
2	Tréning
3	Sústredenie
4	Camp
5	Iné
\.


--
-- Data for Name: member; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.member (id, name, phone, address, psc, city, image_file, weight, height, user_id) FROM stdin;
1	Milan Martiš	+421917360277	Sládkovičova 22	90001	Modra	default.png	\N	\N	1
2	Fanúšik	+421917360277	Sládkovičova 22	90001	Modra	default.png	\N	\N	2
3	Slavomír Podubinský	+421917360277	Sládkovičova 22	90001	Modra	0341e28ea55de538.jpg	79	182	3
5	Norbert Sališ	+421917360277	...	...	...	89345796b71a50b8.jpg	180	80	5
7	Ján Vislocký	+421917360277	...	...	...	832506aff7f4c6d3.jpg	25	180	7
6	František Dolutovský	+421917360277	..	...	...	5a4744e44fd40776.jpg	180	80	6
4	Štefan Maťaš	+421905501402	Sládkovičova 22	90001	Modra	a2ebf1dd11ae608e.jpg	0	0	4
8	Milan Martiš	+421917360277	Sládkovičova 22	90001	Modra	default.png	\N	\N	15
10	Milan Martiš	+421917360277	Sládkovičova 22	90001	Modra	default.png	\N	\N	17
11	Milan Martiš	+421917360277	Sládkovičova 22	90001	Modra	default.png	\N	\N	18
13	Milan Martiš	+421917360277	Sládkovičova 22	90001	Modra	default.png	\N	\N	20
12	Milan Martiš	+421917360277	Sládkovičova 22	90001	Modra	d3bab7952ba8dcd0.png	20	14	19
14	Milan	+421917360277	kh	90001	oih	5ce91a4e141112c5.png	2	2	21
\.


--
-- Data for Name: order; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."order" (id, produc_id, quantity, amount, user_id, is_paid, order_date, storno, variants) FROM stdin;
\.


--
-- Data for Name: player; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.player (id, name, "position", team, score, yellow_card, red_card, team_id, photo_url) FROM stdin;
626	Sebastián Juran	1	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/64f88474f17aea9db522e358/formal-photo/0ac4e704-aadd-4f09-aa8f-12e31d3c53be
627	Oliver Miklušičák	2	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/68b549c494d10f7e9dd3ed59/formal-photo/f4d67d8a-7502-4761-ba73-62f0f3b79130
628	Tamara Siváčková	2	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/66e7e9dc5375b54b6fbc9b56/formal-photo/450cd035-d026-4deb-8db4-bb2788338606
629	Linda Marinič	2	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/67e66546ff066fbb4117349d/formal-photo/7a0f13e4-35b6-4750-b669-1ff67211a6e5
630	Lilien Nováková	2	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/66e2e59f5375b54b6fbc5e62/formal-photo/9ab4bb08-3289-432e-a5a3-04b6e79284d3
631	Marko Mišík	2	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/66e2e5dc5375b54b6fbc5e70/formal-photo/e85afb4e-cfc5-433e-915c-c44f77d3918b
632	Matej Trnovec	2	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/66e165eb5375b54b6fbc48ea/formal-photo/a6c4f9b6-7d27-41a9-99ba-ff6038944686
633	Mark Kostenko	2	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/663dae8e43f70463f1069f05/formal-photo/adb0f7bb-72d8-4314-a137-1b4ccb49361a
634	Adam Špaček	3	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/61443d99ebf3a384471afce9/formal-photo/a513f633-292e-4d63-bee5-e74edbacaac3
635	Oliver Salai	3	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/68b9afdd94d10f7e9dd485b4/formal-photo/cb6fe68d-6e5e-4f8a-bfc0-b2e47c42dbe4
636	Juraj Červenka	3	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/64f8848df17aea9db522e35d/formal-photo/0ed83dbe-54af-4b2e-9a18-f4a162a13acf
637	Victor Abeille	3	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/66e84afa5375b54b6fbca311/formal-photo/a29d64f4-c50d-4018-a381-260af9618d0f
638	Alex Špajdel	3	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/68bb37ff94d10f7e9dd4b86f/formal-photo/7b39cfce-0fc8-4326-87ee-1a475b835ce7
639	Oliver Fedor Malik	3	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f462a2ed2e2d501b526d9db/formal-photo/898a7bbe-440d-4c0c-9385-4c28be0bc240
640	Dávid Matula	3	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/633725783b9a3390f84f4330/formal-photo/f22c56c3-ecdc-47d0-8602-86da07112e6a
641	Tomáš Dvorský	4	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/631af088677da94122ab1db7/formal-photo/792e3cd6-3d7d-45cb-b7f3-849f081f478e
642	Filip Dostál	4	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/6516a750ee2d8d61ea692f82/formal-photo/c02f7430-e65a-4341-9756-afadcd271b04
643	Patrik Plávala	4	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/67e6656bff066fbb411734ae/formal-photo/70ed7f0a-f535-491a-a7cf-bec832295a77
644	Adam Obrtlík	4	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/66e2e5b35375b54b6fbc5e66/formal-photo/c26879e1-01cd-4745-915b-5ec2f9a992f0
645	Adam Vrška	4	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/67e66548ff066fbb411734a1/formal-photo/24a433e8-f840-45b7-88f3-f806f8d1e431
272	Richard Turinič	1	3	1	0	0	3	\N
273	Jakub Vyskočil	2	3	1	3	0	3	\N
274	Lukáš Tichý	2	3	0	1	0	3	\N
275	Nicolas Pachinger	2	3	2	0	1	3	\N
276	Oliver Kročka	2	3	0	0	0	3	\N
277	Jakub Richter	2	3	1	1	0	3	\N
278	Timotej Baričič	2	3	1	0	0	3	\N
279	Matej Ďurian	2	3	0	0	0	3	\N
280	Maťej Babača	3	3	5	1	0	3	\N
281	Šimon Urbanec	3	3	5	1	0	3	\N
282	Denis Michael Kintler	3	3	5	4	0	3	\N
283	Adam Szerencés	3	3	2	0	0	3	\N
284	Sebastián Sališ	3	3	0	0	0	3	\N
285	Adam Jurčík	3	3	4	1	0	3	\N
286	Anton Kenderessy	3	3	0	0	0	3	\N
287	Martin Kulifaj	4	3	9	0	0	3	\N
288	Juraj Nemčovič	4	3	0	0	0	3	\N
478	Sebastián Juran	1	U13	0	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/64f88474f17aea9db522e358/formal-photo/0ac4e704-aadd-4f09-aa8f-12e31d3c53be
479	Oliver Martiš	1	U13	0	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f462996d2e2d501b526d906/formal-photo/0177c2e1-2cb3-4845-82fc-2e78b86475ce
480	Michal Čurilla	2	U13	1	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/67e6655cff066fbb411734aa/formal-photo/56f2024b-f08e-48d7-af39-1809d3eea9df
646	Jakub Macinský	4	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/68c52a0c94d10f7e9dd57065/formal-photo/3d665a77-3c47-4973-820b-b0504fbd6e1b
647	Richard Volek	4	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/66e2e5ca5375b54b6fbc5e6a/formal-photo/e1deac22-3dd1-4b77-bcbf-ab9f32d97b34
648	Samuel Blahuta	4	U11	0	0	0	6	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/64f858aaf17aea9db522d429/formal-photo/4db954c9-557c-4e11-a1fa-94b85fdec0ad
481	Samuel Burnagiel	2	U13	0	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f4629c3d2e2d501b526d90e/formal-photo/c9ad59c6-8dd9-43cf-89fa-e67b81756b05
482	Tobias Pacalaj	2	U13	0	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/626507906b34eb652bd33977/formal-photo/efd34341-80c3-4715-865b-cdce8fd9987b
483	Boris Bartoš	2	U13	1	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/66e3e4fc5375b54b6fbc6eb8/formal-photo/05aa2859-4515-4b94-9f74-f4a3f1c5f27a
484	Adam Špaček	2	U13	0	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/61443d99ebf3a384471afce9/formal-photo/a513f633-292e-4d63-bee5-e74edbacaac3
525	Lukáš Tóth	2	U15	0	1	0	4	https://sportnet.sme.sk/futbalnet/img/avatar.svg
485	Filip Trnovec	3	U13	1	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/644cdaf348779bb601101477/formal-photo/ee360ca9-7ca5-4ac2-9c98-a6fae58f1dac
486	Oliver Fedor Malik	3	U13	5	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f462a2ed2e2d501b526d9db/formal-photo/898a7bbe-440d-4c0c-9385-4c28be0bc240
487	Michal Bartoš	3	U13	0	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/62e7a3760ae29819011a2ad9/formal-photo/c9103cb6-6513-46a5-a56c-cff663fb8089
488	Tomáš Dvorský	3	U13	3	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/631af088677da94122ab1db7/formal-photo/792e3cd6-3d7d-45cb-b7f3-849f081f478e
489	Daniel Baňas	4	U13	10	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f4b4c18d2e2d501b5286909/formal-photo/a7e6a07d-db0d-44c9-a04a-aec31a5e2771
490	Adam Šuvada	4	U13	2	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f475d36d2e2d501b5272b70/formal-photo/3b561646-a11c-42c9-8cea-d7fda23da284
491	Filip Kuchta	4	U13	21	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/628743c8596aecfaf8572184/formal-photo/13aa6ab9-d6c5-411f-9882-c3d0d1424713
492	Adam Kováč	4	U13	4	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/64f9f7aef17aea9db52317e3/formal-photo/424f8106-ec2c-413d-8115-502b106b4162
493	Juraj Červenka	4	U13	1	0	0	5	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/64f8848df17aea9db522e35d/formal-photo/0ed83dbe-54af-4b2e-9a18-f4a162a13acf
649	Viktor Brichta	1	U19	0	1	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658e5386dc8b723833f10e/formal-photo/8924a68d-26f6-41a3-8b75-308baf23fb2f
650	Samuel Milan Ružek	1	U19	0	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d6595f886dc8b7238350f0f/formal-photo/d5824f20-a34f-4a57-9897-7efe2490a2fe
651	Samuel Varga	2	U19	0	1	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658e4686dc8b723833ee4a/formal-photo/46a1af0e-f792-4540-89d3-97cf6aaa7538
652	Timotej Baričič	2	U19	0	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658c7a86dc8b7238339c6c/formal-photo/bdadd14e-2f51-4212-b248-752c35a40e27
653	Patrik Podskoč	2	U19	2	2	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658c8d86dc8b723833a0f4/formal-photo/16a60dc2-7d26-427a-84af-9b858109c573
654	Sebastián Sališ	2	U19	1	3	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d65947186dc8b723834de90/formal-photo/1967126c-f0e3-4ae6-abe6-46b5643e9da6
655	Ladislav Chovanec	2	U19	0	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d65912386dc8b7238346d75/formal-photo/28de15dd-2631-4f17-a0ba-3e6b3200d30a
656	Lukáš Tichý	2	U19	0	1	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658a5a86dc8b7238334048/formal-photo/60b91585-9387-483b-a139-98c5b2f61279
657	Michal Brunovský	2	U19	0	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/66d391a9792b1f6f9d75305d/formal-photo/be4e4dcb-6ea9-4e66-863e-df0544162fd0
658	Peter Juran	2	U19	0	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d6595e386dc8b7238350b6c/formal-photo/b8053c9f-bfdf-4d3f-89f8-c89edd3ab694
659	Samuel Vranovič	2	U19	0	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d6589dc86dc8b72383329c0/formal-photo/4f6891f2-3e06-46bd-bcfb-0f563f1aeeb2
660	David Darula	2	U19	0	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658e4886dc8b723833eeba/formal-photo/37d9e90a-1521-4360-844b-b1d60fcd903b
661	Šimon Urbanec	3	U19	4	2	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d65859186dc8b72383262a4/formal-photo/24791e79-cda7-498b-8dfc-7d7ddd1c171e
662	Matej Ďurian	3	U19	1	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658e4486dc8b723833edeb/formal-photo/39171457-7378-4e25-9752-1c59823ba2af
663	Denis Michael Kintler	3	U19	3	4	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658a5b86dc8b7238334121/formal-photo/2b3dbabe-a10f-4b37-bd67-b05d0207f9ce
664	Jakub Richter	3	U19	5	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658e4486dc8b723833edee/formal-photo/2aa6c22e-da0d-4c51-8478-895e419c9b84
665	Marc Michael Pretzelmayer	3	U19	0	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/65072a09ee2d8d61ea687082/formal-photo/f15240bc-21e7-4131-bfdd-8b9a32bee035
666	Daniel Duban	4	U19	1	2	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5e14d94d7ad8b85a6baf2684/formal-photo/d1ff16cf-fc2a-4a0b-bd71-cd0c6766fd8a
667	Anton Kenderessy	4	U19	7	4	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d6596c186dc8b72383529a6/formal-photo/4af9f1f8-e4ef-4e0c-8ef0-9a50ab5e5ad4
668	Bernard Ličko	4	U19	4	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/61430b74ebf3a384471aea0d/formal-photo/f2d352d4-e257-4247-8d9e-ec33d1cad5c1
669	Adem Useini	4	U19	2	1	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658db586dc8b723833d68f/formal-photo/e25d1b52-d812-4832-b8ac-f488ebc37c0c
516	Oliver Martiš	1	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f462996d2e2d501b526d906/formal-photo/0177c2e1-2cb3-4845-82fc-2e78b86475ce
517	Lukáš Gašparik	1	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/6871065abf40937d075da52f/formal-photo/159aba2b-7393-4919-b0c2-ac0a6ce0a6cf
518	Pavel Šebo	1	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/689ecf58b0d708955bbab03a/formal-photo/23f31afd-903b-4651-9ff8-e8a99ed26f06
519	Martin Tichý	2	U15	5	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5e14d8b87ad8b85a6baf1330/formal-photo/05770764-a9a0-4876-9f3e-55db890e3cf5
520	Arthur Abeille	2	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/688f974eb0d708955bb79398/formal-photo/9b1c20c1-2944-490a-8bea-8f41cef044e8
521	Jakub Poláček	2	U15	0	3	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/661699f025d3591224906fd8/formal-photo/075e2659-f275-404c-aeb9-d82717fb2294
522	Adam Šuvada	2	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f475d36d2e2d501b5272b70/formal-photo/3b561646-a11c-42c9-8cea-d7fda23da284
523	Nicolas Gašparovič	2	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/68a2f095b0d708955bbb4d54/formal-photo/e4cfa44e-f929-41fa-b873-2caaba583820
524	Marek Novák	2	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/60c08619492a2f634974aca9/formal-photo/cb11f963-c348-41e2-af56-b79ef0a237bb
526	Matej Liška	3	U15	1	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5e14d8c47ad8b85a6baf14fe/formal-photo/317ab387-89f1-4284-ac18-32ba2e2554ca
527	Bohuš Bišťan	3	U15	1	1	0	4	https://sportnet.sme.sk/futbalnet/img/avatar.svg
528	Adam Cíferský	3	U15	1	1	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f4629d5d2e2d501b526d91e/formal-photo/89e55d8e-8d22-460a-a154-5c545ca43561
529	Alex Hozlár	3	U15	1	1	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f3659e1f2140d7ecddcbd83/formal-photo/4acd7166-a551-4350-899b-c92e2c4c90ab
530	Daniel Škultéty	3	U15	1	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f4b3979d2e2d501b52864b2/formal-photo/acdf02df-2e8b-4c81-b474-16559aeb16a7
531	Michal Cehlárik	3	U15	0	1	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/68babc3794d10f7e9dd4a0e5/formal-photo/bd667b2f-593d-48c9-afe9-f295667e1694
532	Matúš Matovič	3	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/68c4716494d10f7e9dd568ac/formal-photo/5d31bb71-e94e-4569-a742-0b571227bb8c
533	Adam Kováč	3	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/64f9f7aef17aea9db52317e3/formal-photo/424f8106-ec2c-413d-8115-502b106b4162
534	Tomáš Vober	4	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d65974e86dc8b7238354063/formal-photo/4aaa1741-7930-4291-a9d5-4217cdbf9d5a
535	Patrik Jurčík	4	U15	2	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/605c1e2d3fba375e1079c346/formal-photo/5cb8b20e-76ef-4e99-80bd-b7e7a6fa5b34
536	Július Bittner	4	U15	14	1	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d6596d586dc8b7238352c3d/formal-photo/3bd6b085-49cb-4942-8ee9-cabeb60e9cd8
537	Ondrej Brezina	4	U15	0	0	0	4	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/68c4718094d10f7e9dd568b0/formal-photo/0d01eaa7-3b36-452f-9b07-d20ba80dc3c6
670	Juraj Šikula	4	U19	0	0	0	2	https://sportnet.sme.sk/futbalnet/img/avatar.svg
671	Jakub Hanic	4	U19	1	0	0	2	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d65949286dc8b723834e1ce/formal-photo/af522d57-3690-41e9-8d08-5429fdff984e
672	Juraj Nemčovič	1	A team	0	0	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d65880d86dc8b723832d487/formal-photo/a57a1cef-4ff4-48fd-8a83-a482aa26b322
673	Marcel Kuľha	1	A team	0	0	0	1	https://sportnet.sme.sk/futbalnet/img/avatar.svg
674	František Dolutovský	2	A team	0	5	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d656f1b86dc8b72382d6a36/formal-photo/8ee45cec-3360-4da0-8671-639d497922b7
675	Daniel Čabala	2	A team	2	1	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d6571af86dc8b72382dfa75/formal-photo/3ec643f7-d561-4385-912b-ffead7d6f53d
676	Patrik Dvorák	2	A team	1	3	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d657d8986dc8b723830d1cd/formal-photo/f0f22b86-6c59-4479-ba57-2121b6909766
677	Matúš Filin	2	A team	0	1	0	1	https://sportnet.sme.sk/futbalnet/img/avatar.svg
678	Jakub Vyskočil	2	A team	0	0	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d65859186dc8b723832628e/formal-photo/791b1185-c087-4d34-9246-a11f89ea84f3
679	Matej Ďurian	2	A team	0	0	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658e4486dc8b723833edeb/formal-photo/39171457-7378-4e25-9752-1c59823ba2af
680	René Feder	2	A team	2	0	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d65829086dc8b723831e374/formal-photo/6875502f-cef6-4efa-8840-5176fb0e5c13
681	Dávid Danko	2	A team	1	4	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d6569e286dc8b72382c5c23/formal-photo/78d2f221-0d25-4797-9ca2-2ada9eb843b0
682	Sebastián Sališ	2	A team	0	0	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d65947186dc8b723834de90/formal-photo/1967126c-f0e3-4ae6-abe6-46b5643e9da6
683	Lukáš Tichý	2	A team	0	0	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658a5a86dc8b7238334048/formal-photo/60b91585-9387-483b-a139-98c5b2f61279
684	Timotej Baričič	2	A team	0	0	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658c7a86dc8b7238339c6c/formal-photo/bdadd14e-2f51-4212-b248-752c35a40e27
685	Martin Lehocký	3	A team	3	3	0	1	https://sportnet.sme.sk/futbalnet/img/avatar.svg
686	Vasyl Demydenko	3	A team	0	4	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658ecf86dc8b72383407f8/formal-photo/61258f18-a797-442f-a9bf-fbfaca0b2911
687	Michal Fedoráš	3	A team	0	0	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d5696199a5ee058dc02b931/formal-photo/451fae46-6617-485d-9c1a-b027e02e708b
688	Jakub Pavúk	3	A team	0	4	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d656bbc86dc8b72382cb675/formal-photo/4c37b91c-af81-4633-b796-77122aacbed6
689	Jakub Richter	3	A team	0	2	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658e4486dc8b723833edee/formal-photo/2aa6c22e-da0d-4c51-8478-895e419c9b84
690	Denis Michael Kintler	3	A team	0	1	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658a5b86dc8b7238334121/formal-photo/2b3dbabe-a10f-4b37-bd67-b05d0207f9ce
691	Ján Vislocký	3	A team	1	2	0	1	https://sportnet.sme.sk/futbalnet/img/avatar.svg
692	Šimon Urbanec	3	A team	0	0	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d65859186dc8b72383262a4/formal-photo/24791e79-cda7-498b-8dfc-7d7ddd1c171e
693	Matúš Moravčík	3	A team	0	3	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5f44f3cac996a45b399fa676/formal-photo/411a01d5-ecbb-4b6c-89b5-263dc4c2a464
694	Patrik Podskoč	3	A team	0	0	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658c8d86dc8b723833a0f4/formal-photo/16a60dc2-7d26-427a-84af-9b858109c573
695	Maroš Borza	4	A team	0	1	0	1	https://api.sportnet.online/v1/ppo/futbalsfz.sk/users/5d658a5486dc8b7238333ec5/formal-photo/e0f8fbc4-57dd-4836-b091-b47efc0a5878
\.


--
-- Data for Name: position; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."position" (id, name) FROM stdin;
1	Brankár
2	Obranca
3	Záložník
4	Útočník
5	Tréner
6	Asistent trénera
\.


--
-- Data for Name: positions_members; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.positions_members (member_id, position_id) FROM stdin;
7	4
6	2
3	4
5	4
5	5
4	5
\.


--
-- Data for Name: post; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.post (id, title, date_posted, content, user_id, category_id) FROM stdin;
1	pojpoj	2023-04-20 09:01:55.199901	pojpoj	1	2
10	Finálový krok	2023-04-20 10:20:53.551281	Blíži sa finálový krok a s ním spojený bohatý program. Očakávame Vás v sobotu, 11. 6., už o 13:00 hod., kedy začne zápas Old Boys Artmedia Petržalka vs. Old boys FCSM. Po nich sa bude hrať o 15:00 hod. mini-turnaj prípraviek. O 16:30 sa budú konať rôzne súťaže a o 17:30 nastúpi naše Áčko proti OFK Vysoká pri Morave. Odohrá tak svoj posledný zápas sezóny. Tešíme sa aj na vystúpenie mažoretiek. Môžete sa tešiť na pestrý sprievodný program. My sa tešíme na Vás. 	1	2
11	Tak sme majstri, no a čo	2023-04-20 10:21:41.195984	Milí naši fanúšikovia a podporovatelia, sobota 11.6. sa zapísala do povedomia ľudí, ktorí s nami zdieľali moment víťazstva v V. lige. Vieme, že bez Vašej podpory na tribúnach a mimo nich by sa nám touto cestou k víťazstvu kráčalo o niečo horšie, predsa len nás to viac baví keď Vás je počuť. Veríme, že program a sprievodné akcie ste si užili a vidíme sa na ďalších oslavách, čo poviete? Prehľad sobotňajšieho zápasu FC Slovan Modra 6:0 OFK Vysoká pri Morave Góly posledného zápasu majú na konte Slavomír Podubinský (23', 57', 74') , Martin Lehocký (48'), Norbert Sališ (51'), Michal Habai (85'). 	1	2
12	Tak sme majstri, no a čo	2023-04-20 10:21:42.082175	Milí naši fanúšikovia a podporovatelia, sobota 11.6. sa zapísala do povedomia ľudí, ktorí s nami zdieľali moment víťazstva v V. lige. Vieme, že bez Vašej podpory na tribúnach a mimo nich by sa nám touto cestou k víťazstvu kráčalo o niečo horšie, predsa len nás to viac baví keď Vás je počuť. Veríme, že program a sprievodné akcie ste si užili a vidíme sa na ďalších oslavách, čo poviete? Prehľad sobotňajšieho zápasu FC Slovan Modra 6:0 OFK Vysoká pri Morave Góly posledného zápasu majú na konte Slavomír Podubinský (23', 57', 74') , Martin Lehocký (48'), Norbert Sališ (51'), Michal Habai (85'). 	1	2
13	Tak sme majstri, no a čo	2023-04-20 10:21:54.987294	Milí naši fanúšikovia a podporovatelia, sobota 11.6. sa zapísala do povedomia ľudí, ktorí s nami zdieľali moment víťazstva v V. lige. Vieme, že bez Vašej podpory na tribúnach a mimo nich by sa nám touto cestou k víťazstvu kráčalo o niečo horšie, predsa len nás to viac baví keď Vás je počuť. Veríme, že program a sprievodné akcie ste si užili a vidíme sa na ďalších oslavách, čo poviete? Prehľad sobotňajšieho zápasu FC Slovan Modra 6:0 OFK Vysoká pri Morave Góly posledného zápasu majú na konte Slavomír Podubinský (23', 57', 74') , Martin Lehocký (48'), Norbert Sališ (51'), Michal Habai (85'). 	1	2
14	Po festivale zahodených šancí vezieme domov predsa všetky body	2023-04-20 10:23:11.064893	Ďakujeme fanúšikom za podporu, ktorí prišli do Vajnôr v hojnom počte.\r\n\r\nFK Vajnory vs. FC Slovan Modra 0:1 (0:0).\r\nGól: 82' Pavúk. Zostava FCSM: Lörincz - Dolutovský, Vojtovič, Ayodeji, Lehocký - Araque - Haniš (70' Vislocký), Pavúk, Kovár (61' Peško), Quejada - Aguem (87' Kubín).\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „Ako som avizoval, prišlo k rotácii v zostave, máme široký káder. Lehocký po dlhšej dobe a problémoch s chrbtom nastúpil od začiatku a ako sme boli zvyknutí, podal veľmi spoľahlivý výkon. Taktiež Kovár začal od začiatku a nesklamal, Peško ako žolík opäť bavil divákov. Dnes sme vsak zlyhali v efektivite, Yvan nepremenil 3 tutovky, raz ho zastavil pri dorážke do prázdnej brány obranca nedovolene, ale penalta udelená nebola. Nakoniec nás spasil Pavúkov priamy kop, ktorý je rozdielový vo všetkých aspektoch. Je aj na mne, aby som z tohto mužstva vyťažil čo najviac. Každopádne, sme nováčik, dávame priestor 17-ročným odchovancom a hráme najatraktívnejší futbal v súťaži. Aj o týždeň sľubujem dobrý futbal."\r\n\r\nMartin Kovár, záložník: "Z môjho pohľadu sme boli jednoznačne lepším mužstvom. V prvom polčase sme si vytvorili množstvo šancí, ale zakončenie zlyhalo. V druhom polčase sme ďalej vytvárali na súpera tlak, ktorý sme pretavili víťazným gólom Kuba Pavúka z 83. minúty. Trojbodový cieľ sme si splnili a chceme sa poďakovať fanúšikom za neúnavnú podporu počas celého zápasu." 	1	2
15	Po výbornom výkone sme porazili Karlovu Ves rozdielom triedy	2023-04-20 10:24:11.789108	V zápase excelovali 17-roční odchovanci: David Peško strelil 2 góly a Martin Kovár si pripísal 3 asistencie.\r\n\r\nFC Slovan Modra vs. FKM Karlova Ves 4:1 (2:0)\r\nGóly: 32’ Aguem, 39’ Quejada, 69’ a 82’ Peško FCSM: Lörincz - Dolutovský, Lehocký, Ayodeji, Dvorák - Pavúk, Araque, Kovár (74’ Sališ) - Quejada (83’ Kubín), Aguem (57’ Peško), Vislocký. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: "Jeden z lepších výkonov proti súperovi, ktorý si myslel, že môže u nás hrať otvorenú partiu. S týmto scenárom som ale počítal, pretože Karlova Ves hra počas sezóny uvoľnene, bez tlaku, chcú hrať svoju hru, bez ohľadu na výsledky, a práve to im prináša vysoké výhry. Nám vyhovoval aj dážď, čo logicky napomáha útočiacemu mužstvu. Plán bol rozhodnúť do polčasu, čo by sa aj naplnilo, ak by sme premenili penaltu. Udivuje ma však množstvo hráčov v tejto súťaži, vrátane niektorých našich, ktorí sa do dažďa nevedia obuť. Celkovo bol náš výkon veľmi solídny, objavovalo sa viacero prvkov prenesených z tréningu, niektoré ukážkové akcie a aj keď nám chýbali niektorí hráči, všetci sa chytili šance. Opäť sme splnili sľub, keď som pred týždňom sľuboval dobrý zápas."\r\n\r\nDávid Peško, autor dvoch gólov: "V prvom rade by som chcel poďakovať divákom za to, že aj v nepriaznivom počasí si našli čas a došli nás podporiť. Z môjho pohľadu atraktívny zápas, v ktorom sme opäť trávili väčšinu času na súperovej polke. Mohlo byť rozhodnuté už v prvom polčase, no nepremenili sme šance a ani pokutový kop. V druhom polčase super znížil, no myslím si, že nás to nijak nerozhodilo, hrali sme stále svoju hru a naša aktivita bola odmenená dvoma ďalšími gólmi a bolo rozhodnuté. Ostávame naďalej bez prehry a ideme na plno ďalej." 	1	2
17	Domácu neporaziteľnosť sme si udržali aj v roku 2022!	2023-04-20 10:25:50.922355	V poslednom domácom zápase jesennej časti sme nasúkali súperovi 7 kúskov. Ďakujeme fanúšikom za podporu!\r\n\r\nFC Slovan Modra vs. TJ Záhoran Kostolište 7:2 (2:1)\r\nGóly: 25', 79' a 88' Araque, 47' a 68' Aguem, 12' Kovár, 84' Quejada\r\nFCSM: Lörincz - Dolutovský, Vislocký, Lehocký, Plach - Kovár, Dvorák (76' Ayodeji), Araque - Peško, Aguem (79' Kubín), Quejada. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „S Kostolišťom to bol zaujímavý a atraktívny zápas, hostia sa rýchlo po „štandardke“ ujali vedenia pekným gólom, ale zrejme si neuvedomili proti komu hrajú a povzbudení gólom chceli hrať ofenzívne. My sme nastúpili bez 4 hráčov základnej zostavy, čo bolo prvých 10 minút cítiť, no následne sme absolútne prebrali zápas do svojich rúk. Hráči sa momentálne bavia futbalom. Dnes bol ťažký terén, ale v našom podaní to bola v druhom polčase už exhibícia. Jeden krajší gól ako druhý a zároveň kopec zahodených tutoviek, kedy už chlapci vymýšľali. Teším sa z hattricku Jhonatana, je to veľmi dobrý chlapec, zaslúži si za svoje výkony absolutórium. Na druhej strane sú aj takí, ktorí ma dnes sklamali a nevážia si partiu. Vyvodím z toho dôsledky. Ešte raz sa chcem poďakovať všetkým chlapcom, ktorí dnes nastúpili. Posledný domáci zápas bol pre všetkých odmenou."\r\n\r\nJhonatan Garcia Araque, autor hetriku: „V dnešnom zápase bolo evidentné, že sme silný a kompaktný tím. Začali sme veľmi skoro prehrávať, ale máme silný charakter a za žiadneho stavu nedávame hlavy dole. Vždy ideme na 100 percent za každého stavu. Ďakujem Bohu za takýto výsledok a taktiež fanúšikom Modry, že nás celý zápas povzbudzovali. Vyhrali sme dôležitý zápas na teréne, ktorý bol pre obidva tímy náročný a využili sme príležitosti na skórovanie. VAMOS MODRA, sme skvelý tím a všetci sme spojení pre jeden cieľ. Po tomto zápase sme s istotou po jesennej časti na 1. mieste. Je to niečo veľmi pekné a ďakujem fanúšikom, že nás povzbudzujú a užívajú si s nami každý zápas.“ 	1	2
22	O pohár BFZ sme prehrali s PŠC Pezinok až na penalty	2023-04-20 10:30:00	V prvom kole o pohár BFZ sme prehrali až na pokutové kopy so štvrtoligovým PŠC Pezinok.\r\n\r\nFC Slovan Modra vs. PŠC Pezinok 2:3 (pokutové kopy)\r\nGóly: 85' Sališ, ŽK: 16' Pavúk, 31' Kovár\r\nFCSM: Nemčovič - Kubín, Vislocký, Ayodjii, Plach – Kovár - Pavúk (C), Araque, Peško – Tichý (79' Sališ), Ruberth. Viac nájdete tu\r\nHlasy po zápase:\r\nAndrej Janotka (asistent trénera): „Zápas sme brali ako rozlúčku s jesennou časťou, chceli sme dať priestor hráčom z lavičky a dorastencom. V základe nastúpili až 4 dorastenci, brankár Nemčovič si odbil premiéru v drese nášho áčka vo veku 16 rokov, ďalší traja hráči Kovár, Peško a Tichý sú vo veku 17 rokov už "ostrieľaní áčkari". Od začiatku sme boli lepším mužstvom, hostia hrozili výnimočne a to z rohových kopov, my sme v prvom polčase nepremenili 3 tutovky, postupne Tichý netrafil loptu z päťky, Pavúk vo vyloženej šanci trafil brankára a nakoniec Ruberth po krásnom sóle kedy obišiel aj brankára sa pri zakončení do prázdnej brány pošmykol. Druhý polčas bol opatrnejší, na posledných 10 minút som vytiahol žolíka - trénera na ihrisko a ten okamžite skóroval. Bohužiaľ sme v 90. minúte inkasovali gól čo sa nemôže stávať. Následne penalty boli už len lotéria.“\r\n\r\nNorbert Sališ (tréner a hráč): „Pred peknou diváckou kulisou sme ukázali, že aj hráči z druhého sledu majú svoju kvalitu a často sú práve oni rozdielom vo výsledkoch, keďže jedným z faktorov úspechu v dlhodobej súťaži je aj kvalita lavičky. U súpera som vnímal náznaky herných automatizmov, ktoré sú zrejme rukopisom nového trénera, avšak individuálna hráčska kvalita bola jasne na našej strane. Divácky bol zápas atraktívny, derby ma vždy svoj náboj, škoda nepremenených šancí v prvom polčase ale určite aj inkasovaného gólu na 2:2 v 90.minúte. To sa jednoducho nesmie stávať. Ja som nastúpil po "hecovaní" asistenta Janotku, ktorý veril, že môžem zápas rozhodnúť. Zdravotne momentálne neviem na čom som, čaká ma ešte kontrolná magnetická rezonancia, mal som veľký úlomok kosti v kolene. Futbal mám absolútne zakázaný, no riskli sme to. Vytiahli sme mercedes z garáže, aj keď má defekt, stále je to mercedes. O to viac ma mrzí, že po mojom peknom góle sme to nedotiahli do víťazného konca a inkasovali sme v 90. minúte na 2:2.“ 	1	2
62	Ďakujeme spoločnosti CNS EuroGrants	2020-04-23 09:53:00	Ďakujeme spoločnosti CNS EuroGrants za pomoc pri získaní finančného príspevku vo výške 11 000 EUR z dotačnej schémy Slovenského futbalového zväzu. Spoločnosť <a href="https://cns-e.eu/" target="_blank">CNS EuroGrants</a> poskytuje poradenské a konzultačné služby v oblasti čerpania nenávratnej finančnej pomoci pre oblasť súkromného aj verejného sektora. \r\n\r\n<b>kkkk</b>	1	1
7	Športovec roka 2021	2023-04-20 10:16:57.03803	\r\n\r\nAj tento rok mesto Modra spustilo súťaž o športovca mesta Modra za rok 2021. Mesto túto súťaž organizuje už niekoľko rokov a zapájajú sa do nej všetky športové kluby a ich členovia pôsobiace na území mesta. Náš futbalový klub do hlasovania prihlásil jednotlivcov aj družstvo žiakov U15. Hlasuje sa na web stránke mesta, hlasovanie trvá do 8.5.2022.\r\n\r\nOdkaz na web stránku : https://www.modra.sk/vismo/formulare2.asp?id_f=58 .\r\n\r\nV zozname nájdete takéto zastúpenie FC Slovan Modra.\r\n\r\nDenisa Michaela Kintlera – talentovaného mladého chlapca z Modry, medzi jeho dosiahnuté úspechu patrí 1. miesto BFZ Prípravka PK 2018/2019 hráč a kapitán prípravky, 1. miesto BFZ MZ 2019/2020 hráč a strelec rozhodujúceho gólu vo finále súťaže.\r\n\r\nFC Slovan Modra U15 – našu šikovnú mládež, ktorá už dva roky reprezentuje klub a mesto a drží sa v popredných miestach tabuľky 2.ligy BFZ. Spolu hrajú a trénujú už takmer 7 rokov. Trénerom U15 je náš nadaný hráč Ján Vislocký, ktorý vedie chlapcov tak aby boli na ihrisku úspešný.\r\n\r\nFrantiška Dolutovského – kapitána FC Slovan Modra, ktorý je vytrvalý športovec a reprezentuje náš klub a mesto na ihrisku aj mimo neho. František má výborný zmysel pre fair – play. V 2. lige  BFZ nastavil trend, ktorý nasmerováva sa prináša úspechy budúcich rokov v mládežníckych kategóriach.\r\n\r\nAk dáte hlas komukoľvek z tabuľky budeme Vám vďačný, keďže každý jeden hráč a každé jedno mužstvo klubu je pre nás nesmierne dôležité.\r\n	1	1
65	Nový fan shop	2023-04-09 05:07:47	Milí naši fanúšikovia, chceme Vám dať do pozornosti, že sa nám zmenil sprostredkovateľ fanshopu.\r\nNa konci článku nájdete odkaz na stránku FANZONE a po kliknutí Vás presmeruje do obchodu.\r\nObjednávanie je priamo cez ich stránku a nie cez náš klub ako doteraz. Veríme, že sa Vám bude nový\r\nsortiment páčiť. Nám sa páči:) V sobotu 11. 6., na akcii k ukončeniu sezóny a oslavám titulu (chýba nám už len krok), si môžete veci zakúpiť aj v stánku\r\nfanshopu, ktorý bude umiestnený pri vstupnej bráne. \r\n\r\n<a href="https://fanzone.sk/kategoria-produktu/futbal/fc-slovan-modra/" target="_blank">www.fanzone.sk</a>	1	1
64	Športovec roka 2021	2023-04-01 05:03:37	Aj tento rok mesto Modra spustilo súťaž o športovca mesta Modra za rok 2021. Mesto túto súťaž organizuje už niekoľko rokov a zapájajú sa do nej všetky športové kluby a ich členovia pôsobiace na území mesta. Náš futbalový klub do hlasovania prihlásil jednotlivcov aj družstvo žiakov U15. Hlasuje sa na web stránke mesta, hlasovanie trvá do 8.5.2022.\r\n\r\nOdkaz na web stránku <a href="https://www.modra.sk/vismo/formulare2.asp?id_f=58">www.modra.sk</a>.\r\n\r\nV zozname nájdete takéto zastúpenie FC Slovan Modra.\r\n\r\nDenisa Michaela Kintlera – talentovaného mladého chlapca z Modry, medzi jeho dosiahnuté úspechu patrí 1. miesto BFZ Prípravka PK 2018/2019 hráč a kapitán prípravky, 1. miesto BFZ MZ 2019/2020 hráč a strelec rozhodujúceho gólu vo finále súťaže.\r\n\r\nFC Slovan Modra U15 – našu šikovnú mládež, ktorá už dva roky reprezentuje klub a mesto a drží sa v popredných miestach tabuľky 2.ligy BFZ. Spolu hrajú a trénujú už takmer 7 rokov. Trénerom U15 je náš nadaný hráč Ján Vislocký, ktorý vedie chlapcov tak aby boli na ihrisku úspešný.\r\n\r\nFrantiška Dolutovského – kapitána FC Slovan Modra, ktorý je vytrvalý športovec a reprezentuje náš klub a mesto na ihrisku aj mimo neho. František má výborný zmysel pre fair – play. V 2. lige  BFZ nastavil trend, ktorý nasmerováva sa prináša úspechy budúcich rokov v mládežníckych kategóriach.\r\n\r\nAk dáte hlas komukoľvek z tabuľky budeme Vám vďačný, keďže každý jeden hráč a každé jedno mužstvo klubu je pre nás nesmierne dôležité.\r\n	1	1
16	V Lamači sme potvrdili našu skvelú jesennú formu	2023-04-20 10:24:58.658145	\r\nNáš náskok na čele tabuľky sa zvýšil už na 6 bodov.\r\n\r\nFK Lamač vs. FC Slovan Modra 0:3 (0:0)\r\nGóly: 57’ Quejada, 89’ Kubín, 90’ Araque.\r\nFCSM: Lörincz - Dolutovský, Vojtovič, Ayodeji, Lehocký - Pavúk, Dvorák (84’ Plach), Araque - Vislocký (73’ Haniš), Aguem (87’ Kubín), Quejada. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „V Lamači sme skúšali novú hernú variantu, ktorú hráči zvládli výborne. Nevyhli sme sa strate koncentrácie v záveroch polčasov, ale výborne nás podržal brankár Lörincz. Nie je jednoduché vyhrávať zápas za zápasom, v tomto kalendárnom roku sme v lige neprehrali, verím že sa to odzrkadli vo všetkých aspektoch, počnúc fanúšikmi až po partnerov a samotne mesto. Máme pred sebou posledný domáci zápas v tomto roku, následne ideme na posledné kolo jesene na derby do Vištuku. Hlavne doma by som bol rád, aby prišlo čo najviac ľudí.“\r\n\r\nMartin Lehocký, hráč: „V daždivom počasí a na ťažšom teréne sme opäť podali dominantný výkon, avšak chýbala nám väčšia presnosť a kľud vo finálnej fáze. To sa nám mohlo aj vypomstiť, keď súper z ojedinelých šanci mal možnosť skórovať, ale výbornými zákrokmi sa predviedol Ľubo Lörincz. Zo súperovho ihriska si odnášame 3 body a veríme, že ich potvrdíme v najbližšom domácom zápase pred našimi skvelými fanúšikmi“ 	1	2
19	V poslednom ligovom zápase jesennej časti sme prehrali	2023-04-20 10:28:56.527066	V poslednom ligovom zápase jesennej časti sme prehrali na pôde Vištuku. Ďakujeme fanúšikom za podporu!\r\n\r\nTJ Slovan Vištuk vs. FC Slovan Modra 2:0 (0:0)\r\nČK: 66' Dvorák (Po 2. ŽK), 90' Aguem\r\nFCSM: Lörincz - Lehocký, Vojtovič, Ayodeji, Plach (76' Peško) - Pavúk, Dvorák, Araque - Quejada, Aguem (76' Kovár), Vislocký. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „Zápas vnímam v dvoch rovinách, nakoľko išlo o derby a my sme boli jediné neporazené mužstvo v lige, už niekoľko kôl sa na nás každý super chystal a chcel vytiahnuť. Kvôli naším fanúšikom, ktorí boli aj v tomto zápase skvelí ma mrzí, že prehra prišla práve vo Vištuku. Domáci však boli veľmi nepríjemným súperom, hrali jednoducho, no veľmi poctivo a oduševnene. Nám trošku chýbala emócia, čo beriem na seba, pretože Vištuk nepovažujem za konkurenciu v boji o postup a preto som aj mužstvo nabádal že ide o bežný zápas a netreba sa nechať strhnúť a vyprovokovať. Z tohto pohľadu chcem pochváliť a poďakovať zároveň domácim za maximálne slušne a nekonfliktné prostredie a prístup. Zápas mal vysoké tempo a dobrý náboj. Ta druhá rovina je určitá pachuť, ktorá mi ostala po výkone rozhodcov. Vištuku výhru neberiem, my sme svoje šance nedali, Vištuk vyťažil z minima maximum, no na výkon rozhodcov nech si každý urobí svoj názor. Jedna prehra nás však naučí viac ako séria predchádzajúcich výhier. O týždeň máme ešte Bratislavský pohár, ďalšie derby s Pezinkom, beriem to skôr ako spestrenie a pekne ukončenie jesene. Ešte raz gratulujem domácim k výhre, nič sa však nedeje, zimovať budeme prví.“\r\n\r\nFoto zo zápasu: Dominika Jurčovičová 	1	2
18	Výsledkový sumár mládeže	2023-04-20 10:27:00	U17 Skupina "B" - 11. kolo, 29.10. o 10:00 FCSM – MŠK Iskra Petržalka 5-3. \r\nU15 II. liga SŽ - 11. kolo, 30.10. o 9:00 FCSM – NŠK 1922 Bratislava 1-1. \r\nU13 II. liga MŽ - 11. kolo, 30.10. o 9:00 FCSM – NŠK 1922 Bratislava 1-11.\r\n	1	3
20	V poslednom ligovom zápase jesennej časti sme prehrali	2023-04-20 10:28:57.408968	V poslednom ligovom zápase jesennej časti sme prehrali na pôde Vištuku. Ďakujeme fanúšikom za podporu!\r\n\r\nTJ Slovan Vištuk vs. FC Slovan Modra 2:0 (0:0)\r\nČK: 66' Dvorák (Po 2. ŽK), 90' Aguem\r\nFCSM: Lörincz - Lehocký, Vojtovič, Ayodeji, Plach (76' Peško) - Pavúk, Dvorák, Araque - Quejada, Aguem (76' Kovár), Vislocký. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „Zápas vnímam v dvoch rovinách, nakoľko išlo o derby a my sme boli jediné neporazené mužstvo v lige, už niekoľko kôl sa na nás každý super chystal a chcel vytiahnuť. Kvôli naším fanúšikom, ktorí boli aj v tomto zápase skvelí ma mrzí, že prehra prišla práve vo Vištuku. Domáci však boli veľmi nepríjemným súperom, hrali jednoducho, no veľmi poctivo a oduševnene. Nám trošku chýbala emócia, čo beriem na seba, pretože Vištuk nepovažujem za konkurenciu v boji o postup a preto som aj mužstvo nabádal že ide o bežný zápas a netreba sa nechať strhnúť a vyprovokovať. Z tohto pohľadu chcem pochváliť a poďakovať zároveň domácim za maximálne slušne a nekonfliktné prostredie a prístup. Zápas mal vysoké tempo a dobrý náboj. Ta druhá rovina je určitá pachuť, ktorá mi ostala po výkone rozhodcov. Vištuku výhru neberiem, my sme svoje šance nedali, Vištuk vyťažil z minima maximum, no na výkon rozhodcov nech si každý urobí svoj názor. Jedna prehra nás však naučí viac ako séria predchádzajúcich výhier. O týždeň máme ešte Bratislavský pohár, ďalšie derby s Pezinkom, beriem to skôr ako spestrenie a pekne ukončenie jesene. Ešte raz gratulujem domácim k výhre, nič sa však nedeje, zimovať budeme prví.“\r\n\r\nFoto zo zápasu: Dominika Jurčovičová 	1	2
24	Darujte 2% z daní	2023-04-20 10:33:00	Dobrý deň, touto cestou by som Vás všetkých priaznivcov nášho klubu FC Slovan Modra, požiadal o podporu a poukázanie 2% z daní nášmu OZ FC Slovan Modra. V prílohe Vám posielam tlačivo k vyplneniu a následne Vás požiadam, aby ste tlačivo a aj potvrdenie od zamestnávateľa doručili niektorému členovi VV FC Slovan Modra, počas tréningov/zápasov , alebo ho odovzdali svojmu trénerovi. Ďakujeme veľmi pekne, peniaze budú použité na mládežnícke mužstvá a pre naše detí. Tak isto by som Vás požiadal pokiaľ vlastníte firmu a podnikáte tak isto viete podporiť náš klub. No a v neposlednom rade ďakujem aj za šírenie a sharovanie na sociálnej sieti alebo v rámci vašej siete známych a vášho okolia.\r\n\r\nZa VV FC Slovan Modra Michal Kintler\r\n\r\n<a href="https://fcslovanmodra.sk/images/post/13/2_perc_SLOVAN_MODRA.pdf">>> Tu si stiahnite tlačivo <<</a>\r\n	1	1
84	FCSM na mesiac	2025-01-01 01:01:00	Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.	1	1
23	Privítali sme vzácnu návštevu	2023-04-20 10:31:00	Počas pohárového zápasu BFZ sme okrem PSČ Pezinka, jeho hráčov a fanúšikov privítali na našom štadióne aj vzácnu návštevu, futbalového agenta menom Sidy Fall.\r\n\r\nSidy Fall je medzinárodný agent FIFA senegalskej národnosti, žijúci v Miláne. Je zakladateľom akadémie s názvom Académia Angelo Africa sídliacej v Dakare. Každoročne sa zúčastňuje futbalového galavečera Zlatá Lopta, ktorého účastníkmi je len svetová futbalová špička. Na Slovensko zavítal na pozvanie nášho generálneho manažéra Norberta Sališa s ktorým nadviazali spoluprácu v oblasti scoutingu a manažmentu hráčov. Strávil tu 4 dni, počas ktorých sme ho previedli mestom Modra, ale hlavne si pozrel náš derby zápas s Pezinkom. Ocenil kolumbíjsku dvojicu Ruberth a Jhonathan ale aj prácu s mládežou, nakoľko v zápase nastúpili 4 hráči pod 18 rokov a zastali si svoje úlohy na výbornú. Po tomto zápase sa v sprievode nášho manažéra vydali na zápas Slovanu Bratislava s Ružomberkom.\r\n\r\n„Naša spolupráca bude prínosom aj pre modranský futbal, nakoľko náš klub bude partnerom Sidyho akadémie v Senegale. Takisto je to pre klub obrovská prezentácia, sme veľmi vďační za návštevu.“\r\n\r\nSenegalčan od nás cestoval priamo do Kataru na futbalové Majstrovstvá sveta kde bude fandiť svojmu národnému tímu, ktoré však pre zranenie na poslednú chvíľu nebude reprezentovať najväčšia hviezda Sadio Mané. Veríme, že sa Sidymu na Slovensku a špeciálne v Modre páčilo. 	1	1
21	V poslednom ligovom zápase jesennej časti sme prehrali	2023-04-20 10:29:00	V poslednom ligovom zápase jesennej časti sme prehrali na pôde Vištuku. Ďakujeme fanúšikom za podporu!\r\n\r\nTJ Slovan Vištuk vs. FC Slovan Modra 2:0 (0:0)\r\nČK: 66' Dvorák (Po 2. ŽK), 90' Aguem\r\nFCSM: Lörincz - Lehocký, Vojtovič, Ayodeji, Plach (76' Peško) - Pavúk, Dvorák, Araque - Quejada, Aguem (76' Kovár), Vislocký. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „Zápas vnímam v dvoch rovinách, nakoľko išlo o derby a my sme boli jediné neporazené mužstvo v lige, už niekoľko kôl sa na nás každý super chystal a chcel vytiahnuť. Kvôli naším fanúšikom, ktorí boli aj v tomto zápase skvelí ma mrzí, že prehra prišla práve vo Vištuku. Domáci však boli veľmi nepríjemným súperom, hrali jednoducho, no veľmi poctivo a oduševnene. Nám trošku chýbala emócia, čo beriem na seba, pretože Vištuk nepovažujem za konkurenciu v boji o postup a preto som aj mužstvo nabádal že ide o bežný zápas a netreba sa nechať strhnúť a vyprovokovať. Z tohto pohľadu chcem pochváliť a poďakovať zároveň domácim za maximálne slušne a nekonfliktné prostredie a prístup. Zápas mal vysoké tempo a dobrý náboj. Ta druhá rovina je určitá pachuť, ktorá mi ostala po výkone rozhodcov. Vištuku výhru neberiem, my sme svoje šance nedali, Vištuk vyťažil z minima maximum, no na výkon rozhodcov nech si každý urobí svoj názor. Jedna prehra nás však naučí viac ako séria predchádzajúcich výhier. O týždeň máme ešte Bratislavský pohár, ďalšie derby s Pezinkom, beriem to skôr ako spestrenie a pekne ukončenie jesene. Ešte raz gratulujem domácim k výhre, nič sa však nedeje, zimovať budeme prví.“\r\n\r\nFoto zo zápasu: Dominika Jurčovičová 	1	2
\.


--
-- Data for Name: post_gallery; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.post_gallery (id, title, image_file2, orderz, post_id) FROM stdin;
6	Finálový krok	title.jpg	1	10
7	Finálový krok	title.jpg	0	10
8	Tak sme majstri, no a čo	title.jpg	1	13
9	Tak sme majstri, no a čo	title.jpg	0	13
10	Po festivale zahodených šancí vezieme domov predsa všetky body	title.jpg	1	14
11	Po festivale zahodených šancí vezieme domov predsa všetky body	title.jpg	0	14
12	Po výbornom výkone sme porazili Karlovu Ves rozdielom triedy	title.jpg	1	15
13	Po výbornom výkone sme porazili Karlovu Ves rozdielom triedy	title.jpg	0	15
14	V Lamači sme potvrdili našu skvelú jesennú formu	title.jpg	1	16
15	V Lamači sme potvrdili našu skvelú jesennú formu	title.jpg	0	16
16	Domácu neporaziteľnosť sme si udržali aj v roku 2022!	title.jpg	1	17
17	Domácu neporaziteľnosť sme si udržali aj v roku 2022!	title.jpg	0	17
18	Výsledkový sumár mládeže	title.jpg	1	18
19	Výsledkový sumár mládeže	title.jpg	0	18
59	Športovec roka 2021	title_2.jpg	0	64
60	Nový fan shop	title_3.jpg	0	65
75		e3844e9804204088b4674bdedaf40d45_slide11.jpg	0	62
76		7c79a6891c904ddfbb9a1847f53ab1ef_title_1.jpg	0	24
77		e03ce17578674b19b1eac017a03bb330_230305132751-02-liverpool-manchester-united-0305.jpg	0	22
78		be43b29ba5f64b82ba14964ec3a46fc7_230305132838-03-liverpool-manchester-united-0305.jpg	1	22
79		a49bb1c209f44205bdfc168fe1e22680_230305132931-04-liverpool-manchester-united-0305.jpg	2	22
80		324bcaefd2a34a2fba60993fa221bce2_230306093450-01-manchester-liverpool-030523-restricted.jpg	0	23
87		7fac0060a3724eccab8c5eb20d36954a_e3844e9804204088b4674bdedaf40d45_slide11.jpg	0	21
85		c44ea999ff2d49a3a185987e6f82d8a9_link4.jpg	1	84
86		2fa9cf8ba69d40b1872548caf112f6aa_660ad3b2c3b0437f97f1d62dabe9bcd4_astrobotic-peregrine-pyld-ps-10_2.jpg	2	84
88		9bb0defbaa404b4ab2fb96907ba303c1_e3844e9804204088b4674bdedaf40d45_slide11.jpg	0	84
\.


--
-- Data for Name: product; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product (id, title, date_posted, content, user_id, is_visible, price, old_price, product_category_id, youtube_link, stripe_link) FROM stdin;
17	pok	2025-11-06 15:53:33.187034	pokpok	1	f	25.00	6.00	1	kk	k
20	Champions T-Shirt	2025-12-12 19:04:55.25234	Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.\r\n\r\n	1	t	15.00	15.00	1		price_1Rt3NBKr9xveA3fnIv79kh3m
19	iuh	2025-11-06 17:00:51.368492	iuhiuh	1	t	20.00	6.00	1		hh
18	pok	2025-11-06 15:53:58.72836	pokpok	1	t	25.00	6.00	3		ooo
16	iou	2025-11-04 15:00:23.998235	oiu oiu 	1	t	2.00	2.00	2	g-GslMly3ho	iu
21	Zápas FC Slovan Modra vs. FC Húpacie Koníky	2025-12-12 21:10:49.206153	It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many	1	t	22.00	22.00	2	g-GslMly3ho	price_1Rt3NBKr9xveA3fnIv79kh3m
\.


--
-- Data for Name: product_category; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_category (id, name) FROM stdin;
1	Merch
2	Live Stream
3	Členský poplatok
4	Tréningy U9
\.


--
-- Data for Name: product_gallery; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_gallery (id, title, image_file2, orderz, product_id) FROM stdin;
26		7f1a6c48d871420db679afcb7030afd8_background-cv.png	0	19
29		ba1672dfa53946af9c0229748dcaebfa_660ad3b2c3b0437f97f1d62dabe9bcd4_astrobotic-peregrine-pyld-ps-10_2.jpg	0	18
30		b64c425a4c3e43fbaa6dfdf10090f4cb_background_cv.png	3	19
31		c8033416aa5b423aabf46fd2f74f938c_aplikacie-webstranky_grafika.jpg	3	19
34		a9e8fade31114347b707eeed36bad410_e03ce17578674b19b1eac017a03bb330_230305132751-02-liverpool-manchester-united-0305.jpg	0	16
35		517cf7664f984ca1adde840949f843be_e3844e9804204088b4674bdedaf40d45_slide11.jpg	0	21
37		7e32a7ec2f374ebb9e2f5b3033c5e25e_tricko-champions-modre.jpg	0	20
\.


--
-- Data for Name: product_variant; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_variant (id, name, type) FROM stdin;
5	Size	2
6	Color	2
\.


--
-- Data for Name: product_variant_product; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_variant_product (product_variant_id, product_id) FROM stdin;
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.role (id, name, description) FROM stdin;
1	Admin	poiiii
2	WebAdmin	poipoi
3	Tréner	\N
4	Hráč	
\.


--
-- Data for Name: roles_users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.roles_users (user_id, role_id) FROM stdin;
1	1
1	2
6	4
3	4
5	4
4	3
\.


--
-- Data for Name: score_table; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.score_table (id, club, games, wins, draws, loses, score, points, team_id, logo) FROM stdin;
25	PŠC Pezinok	13	11	0	2	60:16	33	3	\N
26	FK Inter Bratislava B	12	10	2	0	33:5	32	3	\N
27	MFK Záhorská Bystrica	14	9	2	3	37:18	29	3	\N
28	FC Slovan Modra	13	7	2	4	37:21	23	3	\N
29	FK Dúbravka	14	7	0	7	40:36	21	3	\N
30	TJ Jarovce Bratislava	14	6	2	6	37:31	20	3	\N
31	FKM Stupava	14	5	2	7	33:29	17	3	\N
32	MŠK Iskra Petržalka	13	5	1	7	20:30	16	3	\N
33	FK Rača Bratislava	14	3	3	8	21:25	12	3	\N
34	FK Vajnory	13	3	0	10	13:61	9	3	\N
35	Futbalová akadémia Lafranconi FTVŠ UK	14	1	0	13	10:69	3	3	\N
656		0	0	0	0		0	6	\N
657		0	0	0	0		0	6	\N
658		0	0	0	0		0	6	\N
659		0	0	0	0		0	6	\N
660		0	0	0	0		0	6	\N
661		0	0	0	0		0	6	\N
662		0	0	0	0		0	6	\N
663		0	0	0	0		0	6	\N
664		0	0	0	0		0	6	\N
665		0	0	0	0		0	6	\N
666	ŠK Svätý Jur	10	0	10	0	0:0	10	6	\N
667	CFK Pezinok - Cajla	10	0	10	0	0:0	10	6	\N
668	TJ Slovan Viničné	10	0	10	0	0:0	10	6	\N
669	Obecný futbalový klub OFC 014 Vinosady	10	0	10	0	0:0	10	6	\N
670	PŠC Pezinok B	10	0	10	0	0:0	10	6	\N
671	FC Slovan Modra	10	0	10	0	0:0	10	6	\N
672	FK Karpaty Limbach	9	0	9	0	0:0	9	6	\N
673	FC SLOVAN Častá	9	0	9	0	0:0	9	6	\N
775		0	0	0	0		0	2	
776		0	0	0	0		0	2	
777		0	0	0	0		0	2	
778		0	0	0	0		0	2	
779		0	0	0	0		0	2	
780		0	0	0	0		0	2	
781		0	0	0	0		0	2	
782		0	0	0	0		0	2	
783		0	0	0	0		0	2	
784		0	0	0	0		0	2	
785	Senec Football Academy	10	9	1	0	43:12	28	2	https://api.sportnet.online/data/ppo/issf_club_10667/logo
786	ŠK Tomášov	10	8	1	1	39:13	25	2	https://api.sportnet.online/data/ppo/sk-tomasov.futbalnet.sk/logo
787	FKM Stupava	10	7	0	3	36:19	21	2	https://api.sportnet.online/data/ppo/issf_club_8623/logo
788	FK Dúbravka B	10	6	1	3	36:13	19	2	https://api.sportnet.online/data/ppo/fk-dubravka-bratislava.futbalnet.sk/logo
789	FC Slovan Modra	10	6	0	4	32:21	18	2	https://api.sportnet.online/data/ppo/fc-slovan-modra.futbalnet.sk/logo
790	TJ Slovan Viničné	10	5	1	4	41:26	16	2	https://api.sportnet.online/data/ppo/tj-slovan-vinicne.futbalnet.sk/logo
791	FK Vajnory	10	4	0	6	22:24	12	2	https://api.sportnet.online/data/ppo/fk-vajnory.futbalnet.sk/logo
792	Lokomotíva Devínska Nová Ves	10	3	0	7	29:35	9	2	https://api.sportnet.online/data/ppo/lokomotiva-devinska-nova-ves.futbalnet.sk/logo
793	ŠK Bernolákovo	10	3	0	7	23:35	9	2	https://api.sportnet.online/data/ppo/sk-bernolakovo.futbalnet.sk/logo
794	ŠK Lozorno, FO	10	2	0	8	10:53	6	2	https://api.sportnet.online/data/ppo/sk-lozorno-fo.futbalnet.sk/logo
795	FC Zohor	10	0	0	10	7:67	0	2	https://api.sportnet.online/data/ppo/fc-zohor.futbalnet.sk/logo
796	FC Ružinov Bratislava	0	0	0	0	0:0	0	2	https://api.sportnet.online/data/ppo/fc-ruzinov-bratislava.futbalnet.sk/logo
797	ŠK Závod	0	0	0	0	0:0	0	2	https://api.sportnet.online/data/ppo/sk-zavod.futbalnet.sk/logo
590	ŠK Igram	12	12	0	0	122:11	36	5	\N
591	FK Karpaty Limbach	12	10	0	2	66:20	30	5	\N
592	OŠK Slovenský Grob	12	10	0	2	69:16	30	5	\N
593	FC Slovan Modra	12	8	0	4	49:27	24	5	\N
594	FKM Stupava B	12	7	0	5	56:29	21	5	\N
595	ŠK Bernolákovo B	12	6	0	6	39:25	18	5	\N
596	TJ Slovan Viničné	12	6	0	6	53:44	18	5	\N
597	Futbalový klub Budmerice	12	5	1	6	36:42	16	5	\N
598	PŠC Pezinok B	12	4	0	8	19:63	12	5	\N
599	FK CINEMAX Doľany	12	3	2	7	20:76	11	5	\N
600	CFK Pezinok - Cajla	12	3	1	8	22:55	10	5	\N
601	ŠK Báhoň	12	1	2	9	15:65	5	5	\N
602	TJ Družstevník Jablonec	12	0	0	12	5:98	0	5	\N
848		0	0	0	0		0	4	
849		0	0	0	0		0	4	
850		0	0	0	0		0	4	
851		0	0	0	0		0	4	
852		0	0	0	0		0	4	
853		0	0	0	0		0	4	
854		0	0	0	0		0	4	
855		0	0	0	0		0	4	
856		0	0	0	0		0	4	
857		0	0	0	0		0	4	
858	Futbalový klub Dubová	14	14	0	0	106:10	42	4	https://api.sportnet.online/data/ppo/tj-dubova.futbalnet.sk/logo
859	OŠK Slovenský Grob	14	10	3	1	55:15	33	4	https://api.sportnet.online/data/ppo/osk-slovensky-grob.futbalnet.sk/logo
860	TJ SLOVAN Vištuk	14	9	1	4	83:36	28	4	https://api.sportnet.online/data/ppo/tj-slovan-vistuk.futbalnet.sk/logo
861	ŠK Lozorno, FO	14	8	4	2	56:31	28	4	https://api.sportnet.online/data/ppo/sk-lozorno-fo.futbalnet.sk/logo
862	PŠC Pezinok B	14	8	3	3	50:26	27	4	https://api.sportnet.online/data/ppo/psc-pezinok.futbalnet.sk/logo
863	FC Zohor	14	7	1	6	68:34	22	4	https://api.sportnet.online/data/ppo/fc-zohor.futbalnet.sk/logo
864	ŠK Šenkvice	14	7	1	6	38:54	22	4	https://api.sportnet.online/data/ppo/sk-senkvice.futbalnet.sk/logo
865	TJ Záhoran Jakubov	14	6	2	6	40:50	20	4	https://api.sportnet.online/data/ppo/tj-zahoran-jakubov.futbalnet.sk/logo
866	FKM Stupava B	14	6	1	7	35:51	19	4	https://api.sportnet.online/data/ppo/issf_club_8623/logo
867	FC Slovan Modra	14	4	3	7	28:44	15	4	https://api.sportnet.online/data/ppo/fc-slovan-modra.futbalnet.sk/logo
868	FK Karpaty Limbach	14	5	0	9	36:68	15	4	https://api.sportnet.online/data/ppo/fk-karpaty-limbach.futbalnet.sk/logo
869	TJ Záhoran Kostolište	14	4	1	9	23:59	13	4	https://api.sportnet.online/data/ppo/tj-zahoran-kostoliste.futbalnet.sk/logo
870	FC SLOVAN Častá	14	2	3	9	23:72	9	4	https://api.sportnet.online/data/ppo/fc-slovan-casta.futbalnet.sk/logo
871	TJ Slovan Viničné	14	2	2	10	13:37	8	4	https://api.sportnet.online/data/ppo/tj-slovan-vinicne.futbalnet.sk/logo
872	CFK Pezinok - Cajla	14	0	1	13	7:74	1	4	https://api.sportnet.online/data/ppo/cfk-pezinok-cajla.futbalnet.sk/logo
1185		0	0	0	0		0	1	
1186		0	0	0	0		0	1	
1187		0	0	0	0		0	1	
1188		0	0	0	0		0	1	
1189		0	0	0	0		0	1	
1190		0	0	0	0		0	1	
1191		0	0	0	0		0	1	
1192		0	0	0	0		0	1	
1193		0	0	0	0		0	1	
1194		0	0	0	0		0	1	
1195	MFK Rusovce	15	10	2	3	34:17	32	1	https://api.sportnet.online/data/ppo/mfk-rusovce.futbalnet.sk/logo
1196	ŠK Bernolákovo	15	10	2	3	28:11	32	1	https://api.sportnet.online/data/ppo/sk-bernolakovo.futbalnet.sk/logo
1197	FK Slovan Ivanka pri Dunaji	15	10	1	4	26:9	31	1	https://api.sportnet.online/data/ppo/fk-slovan-ivanka-pri-dunaji.futbalnet.sk/logo
1198	OFK Dunajská Lužná	15	8	5	2	24:11	29	1	https://api.sportnet.online/data/ppo/ofk-dunajska-luzna.futbalnet.sk/logo
1199	Športový klub Nová Dedinka	15	8	5	2	22:10	29	1	https://api.sportnet.online/data/ppo/sk-nova-dedinka.futbalnet.sk/logo
1200	TJ Rovinka	15	9	1	5	24:21	28	1	https://api.sportnet.online/data/ppo/tj-rovinka.futbalnet.sk/logo
1201	ŠK Tomášov	15	6	4	5	23:16	22	1	https://api.sportnet.online/data/ppo/sk-tomasov.futbalnet.sk/logo
1202	FC Rohožník	15	6	2	7	26:27	20	1	https://api.sportnet.online/data/ppo/fc-rohoznik.futbalnet.sk/logo
1203	SFC Kalinkovo	15	4	5	6	15:21	17	1	https://api.sportnet.online/data/ppo/sfc-kalinkovo.futbalnet.sk/logo
1204	Lokomotíva Devínska Nová Ves	15	5	1	9	13:24	16	1	https://api.sportnet.online/data/ppo/lokomotiva-devinska-nova-ves.futbalnet.sk/logo
1205	TJ Záhoran Jakubov	15	3	6	6	12:25	15	1	https://api.sportnet.online/data/ppo/tj-zahoran-jakubov.futbalnet.sk/logo
1206	NŠK 1922 Bratislava	15	3	5	7	15:18	14	1	https://api.sportnet.online/data/ppo/nmsk-1922-bratislava.futbalnet.sk/logo
1207	PŠC Pezinok	15	3	5	7	19:23	14	1	https://api.sportnet.online/data/ppo/psc-pezinok.futbalnet.sk/logo
1208	FKM Karlova Ves Bratislava	15	3	4	8	21:32	13	1	https://api.sportnet.online/data/ppo/fkm-karlova-ves-bratislava.futbalnet.sk/logo
1209	MŠK Kráľová pri Senci	15	3	2	10	15:30	11	1	https://api.sportnet.online/data/ppo/msk-kralova-pri-senci.futbalnet.sk/logo
1210	FC Slovan Modra	15	2	4	9	10:32	10	1	https://api.sportnet.online/data/ppo/fc-slovan-modra.futbalnet.sk/logo
\.


--
-- Data for Name: sponsors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sponsors (id, name, url, kind, image_file, orderz, created_at, describe) FROM stdin;
2	Atops	https://www.atops.sk/	main	22a72b46742e47bdb19960b0cc865c2f_6899787f88ce49524333717a_527342095_18062660111253929_4574921588219728515_n.jpg	1	2025-12-08 16:08:15.586614	\N
5			partner	86a1a293ca8942c4a2622a83355c7cbe_68de6cd45a1e3c74ca1d15e5_fadfasdf.jpg	2	2025-12-08 17:53:57.447142	\N
4		https://modra.sk	partner	21865833a7b047cca4aa42826802bbf1_6899787f1b78152212dea850_527318661_1319202123547717_4382761230831107370_n.jpg	1	2025-12-08 17:53:50.062062	
8		https://appdesign.sk	partner	60a140d455284a0581261577d8f90a8e_app_logo.jpg	3	2025-12-10 17:18:12.569668	
\.


--
-- Data for Name: team; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.team (id, name, score_scrap, player_list_scrap, main_league, events_results_scrap, events_program_scrap) FROM stdin;
7	U9				\N	\N
6	U11	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/u11-m-a/tabulky/#/?competitionId=684c50cbe7ee690eb42219bc	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/u11-m-a/hraci/	BFZ - PRÍPRAVKA U11 - PK (PRPK)	\N	\N
3	U17	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55097/tabulky/?partId=&sutaz=629b6f437163293609faea9e	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55097/hraci/?partId=&sutaz=629b6f437163293609faea9e	III. liga MD	\N	\N
4	U15	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55099/tabulky/?partId=&sutaz=629b6f5d7163293609fb0ab7	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55099/hraci/?partId=&sutaz=629b6f5d7163293609fb0ab7	II. liga SŽ	https://sutaze.api.sportnet.online/api/v2/futbalnet/matches?playerAppSpace=fc-slovan-modra.futbalnet.sk&teamId=68610c035a52cdc943f78f99	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/u15-m-a/program/
2	U19	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55092/tabulky/?partId=&sutaz=62a82e3e71632936092991de	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55092/hraci/?partId=&sutaz=62a82e3e71632936092991de	IV. liga dorast (SD4V)	https://sutaze.api.sportnet.online/api/v2/futbalnet/matches?playerAppSpace=fc-slovan-modra.futbalnet.sk&teamId=685cca695a52cdc943e28360	\N
5	U13	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55102/tabulky/?partId=&sutaz=629b6f827163293609fb32fe	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55102/hraci/?partId=&sutaz=629b6f827163293609fb32fe	II. liga MŽ	https://sutaze.api.sportnet.online/api/v2/futbalnet/matches?playerAppSpace=fc-slovan-modra.futbalnet.sk&teamId=685cca7a5a52cdc943e29d3f	\N
1	A team	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/53930/tabulky/?partId=&sutaz=629b6e797163293609f9fa26	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/53930/hraci/?partId=&sutaz=629b6e797163293609f9fa26	FUTBALSERVIS V. liga BFZ	https://sutaze.api.sportnet.online/api/v2/futbalnet/matches?playerAppSpace=fc-slovan-modra.futbalnet.sk&teamId=685bb1705a52cdc94319e046	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/dospeli-m-a/program/
\.


--
-- Data for Name: teams_events; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.teams_events (team_id, event_id) FROM stdin;
\.


--
-- Data for Name: teams_members; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.teams_members (member_id, team_id) FROM stdin;
7	1
6	1
3	1
5	1
5	2
4	1
4	2
\.


--
-- Data for Name: type_product_variant; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.type_product_variant (id, name, operation) FROM stdin;
2	default	select
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."user" (id, uuid, username, email, image_file, password, confirm, active, confirmed_at, fs_uniquifier) FROM stdin;
3	ba4ed929-d4e6-46cf-9748-d8f5d5b8529c	messi	info@appdesign.sk	default.jpg	$2b$12$WuVeKYnAPagNsBLOUOr2zOWgFgopRlVYgUt7X1ORtXuCo25H9mWIC	f	t	\N	ba4ed929-d4e6-46cf-9748-d8f5d5b8529c
4	9c37ff6c-272f-480e-be39-8f7d88ab0a1f	stefanmatas	stefanmatas@fcsm.sk	default.jpg	$2b$12$dMj7R0YenqmdOlgNZ5lTDO7HmjGlBvig93L2xsFFY5SlBfxvX61CK	f	t	\N	9c37ff6c-272f-480e-be39-8f7d88ab0a1f
5	1690736c-de05-4e35-beb8-d881151c4e40	noro	norosalis@fcsm.sk	default.jpg	$2b$12$nvDoXyqU1PMinTCk5MI0jO7BoPesa0qHulEtT4oB/NKdgbwmxfuMi	f	t	\N	1690736c-de05-4e35-beb8-d881151c4e40
6	76a15f81-3a3b-41d6-b3e2-8606428ff6c9	fero	ferodolutovsky@fcsm.sk	default.jpg	$2b$12$nlxNZej1pni89liBOEnwDObK3er3rCFVxtkzHY/glr27/EHbAJF5.	f	t	\N	76a15f81-3a3b-41d6-b3e2-8606428ff6c9
7	2be0d46a-abf4-408f-8a6a-b13cdc6c9c91	jano	janvislocky@fcsm.sk	default.jpg	$2b$12$6iDtza/BgG8cBa227.MJm.HyA4vds4ImuzV7L4DePJFWr2bnWC/hS	f	t	\N	2be0d46a-abf4-408f-8a6a-b13cdc6c9c91
8	98e41192-874a-4dc3-b397-b203eecf9dff	Mito	office@appdesign.sk	default.jpg	$2b$12$QIl0miaTdXyz/WcHkOEp/u8dq1XvU53rrRKNfAEkq/7u9WS4r9Dr6	f	t	\N	98e41192-874a-4dc3-b397-b203eecf9dff
9	89f1f056-6799-46eb-bbd2-639f206a720d	pokus	milanmartispokus@gmail.com	default.jpg	$2b$12$lSw6RQLg/h2FtFdjF1AhMe2263i1aiipej0L57rLFq40q9mymD6xe	f	t	\N	89f1f056-6799-46eb-bbd2-639f206a720d
10	4fc78207-937f-45d2-aa36-7e3975c8ae76	mmm	milanmartis2@gmail.com	default.jpg	$2b$12$eV8GYGaACd.VGu8/1TTDtuBlbbO2/3MZhSFbjFOpq/3J3UuV/GCh.	f	t	\N	4fc78207-937f-45d2-aa36-7e3975c8ae76
11	5514b11a-f361-4aea-bd61-445968dc3ee7	mmm2	milanmartis22@gmail.com	default.jpg	$2b$12$t1YDiNCRZCpI7179U7iN6uAERsz.Yfy.IxdWa3LT5b.VQALQ4vfHS	f	t	\N	5514b11a-f361-4aea-bd61-445968dc3ee7
12	3cd45551-2fe6-421f-9548-d5158bc73a89	m3	milanmartis3@gmail.com	default.jpg	$2b$12$0IwWfQKqTRrWYsWdpLwSm.bmNebqPz4rlbuusGRWOi1gvzR9dLO6C	f	t	\N	3cd45551-2fe6-421f-9548-d5158bc73a89
13	f95f0bae-483b-487b-a3de-3dad582f3267	m4	milanmartis4@gmail.com	default.jpg	$2b$12$plx6qw50FyoI9ihP1WxjCehwZa6et1aOs51G4rvBKcHlgPdyKpIxK	f	t	\N	f95f0bae-483b-487b-a3de-3dad582f3267
14	cf7194c6-5e7c-4ff4-872b-5d8a16f571b4	mm5	milanmartis5@gmail.com	default.jpg	$2b$12$kice669vAJ9cY3eU.hHUMOgVpJ1VPwyYj/BeRd4Sn39FIH99qC5fW	f	t	\N	cf7194c6-5e7c-4ff4-872b-5d8a16f571b4
15	99e7a33a-120f-47df-af1a-d4716d5891a0	mm6	milanmartis6@gmail.com	default.jpg	$2b$12$UCWfEoHYIhjNpO1rvByCl.zei7lgYFoRxxVsUu36w1nvkn1I2.T6G	f	t	\N	99e7a33a-120f-47df-af1a-d4716d5891a0
2	0bf2ec58-729c-4f98-9471-abd5fc514f30	fanusik	martis55@ddd.sk	default.jpg	$2b$12$WHFVKLe51mO2JNli/5mD0.t1Hvwsyq3FESCGUkCPpz8AJYdw9spRS	f	t	\N	0bf2ec58-729c-4f98-9471-abd5fc514f30
17	79a06094-ae5e-476c-941b-46846fb03178	mm	martis5opjpoj5@ddd.sk	default.jpg	$2b$12$qv1487203XG4ubet.eF17uMUh62xq2dBhDgfDPUJQQOl3/zD1TLDm	f	t	\N	79a06094-ae5e-476c-941b-46846fb03178
18	14a17e5d-843d-4233-a577-995a6f1edd98	mitko	martisvvvvv55@ddd.sk	default.jpg	$2b$12$BZse8zU333ulFg6/tSgRquuY8RGLJuvlmsdEK9X4/q0i8X322tPAq	f	t	\N	14a17e5d-843d-4233-a577-995a6f1edd98
19	5aa72ff2-bea8-497c-a0c1-aa622f2683fe	mmmm	martis5opjpoj5@dsssdd.sk	default.jpg	$2b$12$dTubhghEJs/q2ZD99MQcruUiktOlzwwBpsQWzckhw0waNkDv9w4Iy	f	t	\N	5aa72ff2-bea8-497c-a0c1-aa622f2683fe
20	3375cd78-b758-4ab0-9fc0-368f68eb51b0	milanmartis	martisvv45655@ddd.sk	default.jpg	$2b$12$nj80qbJ4Hx.IDuYLfYFAnOPq8YkYBUabLjRWBbULO7M3ec/W.yn1a	t	t	\N	3375cd78-b758-4ab0-9fc0-368f68eb51b0
21	0526d01d-3e1d-41e3-bf7e-29d3a0c98913	fanusik2	martis@gasparikmasovyroba.sk	default.jpg	$2b$12$.feQka7ZW04qkgTwQY4smOL1EImDfQPPvNZIAntG69f7AteS/6ozC	t	t	\N	0526d01d-3e1d-41e3-bf7e-29d3a0c98913
1	be026d3b-cc56-41fa-97f7-8ee1f871e29d	admin	milanmartis@gmail.com	758a11ec7ca3396e.png	$2b$12$5IxmS6.KlVy4wcZ3c3GPXe2ffJvuEqoGLWPv88dYgIOr/TPDYx.mO	t	t	2025-12-09 21:42:27.944414+01	be026d3b-cc56-41fa-97f7-8ee1f871e29d
\.


--
-- Data for Name: variant_products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.variant_products (product_id, variant_id, variant_text, variant_image, id) FROM stdin;
19	5	140		1
19	5	141		2
19	5	149		3
19	6	Black	C:\\fakepath\\660ad3b2c3b0437f97f1d62dabe9bcd4_astrobotic-peregrine-pyld-ps-10 (2).jpg	9
19	6	White	C:\\fakepath\\660ad3b2c3b0437f97f1d62dabe9bcd4_astrobotic-peregrine-pyld-ps-10 (2).jpg	10
19	6	Yellow	C:\\fakepath\\660ad3b2c3b0437f97f1d62dabe9bcd4_astrobotic-peregrine-pyld-ps-10 (2).jpg	11
20	5	138		18
20	5	140		19
20	6	Blue		20
\.


--
-- Name: category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.category_id_seq', 10, true);


--
-- Name: club_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.club_id_seq', 1, false);


--
-- Name: event_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.event_category_id_seq', 1, false);


--
-- Name: event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.event_id_seq', 1144, true);


--
-- Name: member_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.member_id_seq', 14, true);


--
-- Name: order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.order_id_seq', 2, true);


--
-- Name: player_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.player_id_seq', 695, true);


--
-- Name: position_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.position_id_seq', 1, false);


--
-- Name: post_gallery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.post_gallery_id_seq', 88, true);


--
-- Name: post_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.post_id_seq', 85, true);


--
-- Name: product_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.product_category_id_seq', 1, false);


--
-- Name: product_gallery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.product_gallery_id_seq', 37, true);


--
-- Name: product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.product_id_seq', 21, true);


--
-- Name: product_variant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.product_variant_id_seq', 7, true);


--
-- Name: role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.role_id_seq', 3, true);


--
-- Name: score_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.score_table_id_seq', 1210, true);


--
-- Name: sponsors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sponsors_id_seq', 8, true);


--
-- Name: team_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.team_id_seq', 9, true);


--
-- Name: type_product_variant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.type_product_variant_id_seq', 2, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_id_seq', 21, true);


--
-- Name: variant_products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.variant_products_id_seq', 20, true);


--
-- Name: category category_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_pkey PRIMARY KEY (id);


--
-- Name: club club_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.club
    ADD CONSTRAINT club_pkey PRIMARY KEY (id);


--
-- Name: club club_subdomain_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.club
    ADD CONSTRAINT club_subdomain_key UNIQUE (subdomain);


--
-- Name: event_category event_category_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event_category
    ADD CONSTRAINT event_category_pkey PRIMARY KEY (id);


--
-- Name: event event_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id);


--
-- Name: member member_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.member
    ADD CONSTRAINT member_pkey PRIMARY KEY (id);


--
-- Name: order order_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pkey PRIMARY KEY (id);


--
-- Name: player player_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.player
    ADD CONSTRAINT player_pkey PRIMARY KEY (id);


--
-- Name: position position_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."position"
    ADD CONSTRAINT position_name_key UNIQUE (name);


--
-- Name: position position_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."position"
    ADD CONSTRAINT position_pkey PRIMARY KEY (id);


--
-- Name: post_gallery post_gallery_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_gallery
    ADD CONSTRAINT post_gallery_pkey PRIMARY KEY (id);


--
-- Name: post post_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post
    ADD CONSTRAINT post_pkey PRIMARY KEY (id);


--
-- Name: product_category product_category_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_category
    ADD CONSTRAINT product_category_pkey PRIMARY KEY (id);


--
-- Name: product_gallery product_gallery_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_gallery
    ADD CONSTRAINT product_gallery_pkey PRIMARY KEY (id);


--
-- Name: product product_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pkey PRIMARY KEY (id);


--
-- Name: product_variant product_variant_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_variant
    ADD CONSTRAINT product_variant_pkey PRIMARY KEY (id);


--
-- Name: role role_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_name_key UNIQUE (name);


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: score_table score_table_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.score_table
    ADD CONSTRAINT score_table_pkey PRIMARY KEY (id);


--
-- Name: sponsors sponsors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sponsors
    ADD CONSTRAINT sponsors_pkey PRIMARY KEY (id);


--
-- Name: team team_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.team
    ADD CONSTRAINT team_pkey PRIMARY KEY (id);


--
-- Name: type_product_variant type_product_variant_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.type_product_variant
    ADD CONSTRAINT type_product_variant_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- Name: variant_products variant_products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.variant_products
    ADD CONSTRAINT variant_products_pkey PRIMARY KEY (id);


--
-- Name: idx_sponsors_kind; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sponsors_kind ON public.sponsors USING btree (kind);


--
-- Name: idx_sponsors_kind_orderz; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sponsors_kind_orderz ON public.sponsors USING btree (kind, orderz);


--
-- Name: idx_sponsors_orderz; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sponsors_orderz ON public.sponsors USING btree (orderz);


--
-- Name: event event_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: member member_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.member
    ADD CONSTRAINT member_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: order order_produc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_produc_id_fkey FOREIGN KEY (produc_id) REFERENCES public.product(id);


--
-- Name: order order_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: player player_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.player
    ADD CONSTRAINT player_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.team(id);


--
-- Name: positions_members positions_members_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.positions_members
    ADD CONSTRAINT positions_members_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.member(id);


--
-- Name: positions_members positions_members_position_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.positions_members
    ADD CONSTRAINT positions_members_position_id_fkey FOREIGN KEY (position_id) REFERENCES public."position"(id);


--
-- Name: post post_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post
    ADD CONSTRAINT post_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.category(id);


--
-- Name: post_gallery post_gallery_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_gallery
    ADD CONSTRAINT post_gallery_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.post(id);


--
-- Name: post post_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post
    ADD CONSTRAINT post_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: product_gallery product_gallery_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_gallery
    ADD CONSTRAINT product_gallery_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: product product_product_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_product_category_id_fkey FOREIGN KEY (product_category_id) REFERENCES public.product_category(id);


--
-- Name: product product_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: product_variant_product product_variant_product_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_variant_product
    ADD CONSTRAINT product_variant_product_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: product_variant_product product_variant_product_product_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_variant_product
    ADD CONSTRAINT product_variant_product_product_variant_id_fkey FOREIGN KEY (product_variant_id) REFERENCES public.product_variant(id);


--
-- Name: product_variant product_variant_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_variant
    ADD CONSTRAINT product_variant_type_fkey FOREIGN KEY (type) REFERENCES public.type_product_variant(id);


--
-- Name: roles_users roles_users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles_users
    ADD CONSTRAINT roles_users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(id);


--
-- Name: roles_users roles_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles_users
    ADD CONSTRAINT roles_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: score_table score_table_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.score_table
    ADD CONSTRAINT score_table_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.team(id);


--
-- Name: teams_events teams_events_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams_events
    ADD CONSTRAINT teams_events_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.event(id);


--
-- Name: teams_events teams_events_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams_events
    ADD CONSTRAINT teams_events_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.team(id);


--
-- Name: teams_members teams_members_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams_members
    ADD CONSTRAINT teams_members_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.member(id);


--
-- Name: teams_members teams_members_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams_members
    ADD CONSTRAINT teams_members_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.team(id);


--
-- Name: variant_products variant_products_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.variant_products
    ADD CONSTRAINT variant_products_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: variant_products variant_products_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.variant_products
    ADD CONSTRAINT variant_products_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES public.product_variant(id);


--
-- PostgreSQL database dump complete
--

