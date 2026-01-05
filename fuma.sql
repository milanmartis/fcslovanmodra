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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO fuma_user;

--
-- Name: category; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.category (
    id integer NOT NULL,
    name character varying(200) NOT NULL
);


ALTER TABLE public.category OWNER TO fuma_user;

--
-- Name: category_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.category_id_seq OWNER TO fuma_user;

--
-- Name: category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.category_id_seq OWNED BY public.category.id;


--
-- Name: club; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.club (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    subdomain character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.club OWNER TO fuma_user;

--
-- Name: club_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.club_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.club_id_seq OWNER TO fuma_user;

--
-- Name: club_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.club_id_seq OWNED BY public.club.id;


--
-- Name: event; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.event (
    id integer NOT NULL,
    title character varying(250) NOT NULL,
    start_event timestamp with time zone,
    end_event timestamp with time zone,
    user_id integer NOT NULL,
    event_category_id integer NOT NULL,
    event_team_id integer NOT NULL,
    address character varying(250) NOT NULL,
    link text NOT NULL
);


ALTER TABLE public.event OWNER TO fuma_user;

--
-- Name: event_category; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.event_category (
    id integer NOT NULL,
    name character varying(200) NOT NULL
);


ALTER TABLE public.event_category OWNER TO fuma_user;

--
-- Name: event_category_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.event_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.event_category_id_seq OWNER TO fuma_user;

--
-- Name: event_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.event_category_id_seq OWNED BY public.event_category.id;


--
-- Name: event_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.event_id_seq OWNER TO fuma_user;

--
-- Name: event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.event_id_seq OWNED BY public.event.id;


--
-- Name: member; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.member (
    id integer NOT NULL,
    name character varying(250) NOT NULL,
    phone character varying(250) NOT NULL,
    address character varying(250) NOT NULL,
    psc character varying(250) NOT NULL,
    city character varying(250) NOT NULL,
    image_file character varying(255),
    weight integer,
    height integer,
    user_id integer NOT NULL
);


ALTER TABLE public.member OWNER TO fuma_user;

--
-- Name: member_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.member_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.member_id_seq OWNER TO fuma_user;

--
-- Name: member_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.member_id_seq OWNED BY public.member.id;


--
-- Name: order; Type: TABLE; Schema: public; Owner: fuma_user
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
    variants character varying(200) NOT NULL
);


ALTER TABLE public."order" OWNER TO fuma_user;

--
-- Name: order_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.order_id_seq OWNER TO fuma_user;

--
-- Name: order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.order_id_seq OWNED BY public."order".id;


--
-- Name: player; Type: TABLE; Schema: public; Owner: fuma_user
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
    photo_url character varying(600)
);


ALTER TABLE public.player OWNER TO fuma_user;

--
-- Name: player_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.player_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.player_id_seq OWNER TO fuma_user;

--
-- Name: player_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.player_id_seq OWNED BY public.player.id;


--
-- Name: position; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public."position" (
    id integer NOT NULL,
    name character varying(180)
);


ALTER TABLE public."position" OWNER TO fuma_user;

--
-- Name: position_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.position_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.position_id_seq OWNER TO fuma_user;

--
-- Name: position_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.position_id_seq OWNED BY public."position".id;


--
-- Name: positions_members; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.positions_members (
    member_id integer,
    position_id integer
);


ALTER TABLE public.positions_members OWNER TO fuma_user;

--
-- Name: post; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.post (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    date_posted timestamp with time zone NOT NULL,
    content text NOT NULL,
    user_id integer NOT NULL,
    category_id integer NOT NULL,
    slug character varying(255) NOT NULL,
    views integer DEFAULT 0 NOT NULL,
    is_featured boolean DEFAULT false NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    published_at timestamp with time zone
);


ALTER TABLE public.post OWNER TO fuma_user;

--
-- Name: post_gallery; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.post_gallery (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    image_file2 character varying(250) NOT NULL,
    orderz integer,
    post_id integer NOT NULL
);


ALTER TABLE public.post_gallery OWNER TO fuma_user;

--
-- Name: post_gallery_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.post_gallery_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.post_gallery_id_seq OWNER TO fuma_user;

--
-- Name: post_gallery_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.post_gallery_id_seq OWNED BY public.post_gallery.id;


--
-- Name: post_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.post_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.post_id_seq OWNER TO fuma_user;

--
-- Name: post_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.post_id_seq OWNED BY public.post.id;


--
-- Name: product; Type: TABLE; Schema: public; Owner: fuma_user
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
    youtube_link character varying NOT NULL,
    stripe_link character varying(100) NOT NULL
);


ALTER TABLE public.product OWNER TO fuma_user;

--
-- Name: product_category; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.product_category (
    id integer NOT NULL,
    name character varying(200) NOT NULL
);


ALTER TABLE public.product_category OWNER TO fuma_user;

--
-- Name: product_category_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.product_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.product_category_id_seq OWNER TO fuma_user;

--
-- Name: product_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.product_category_id_seq OWNED BY public.product_category.id;


--
-- Name: product_gallery; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.product_gallery (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    image_file2 character varying(250) NOT NULL,
    orderz integer,
    product_id integer NOT NULL
);


ALTER TABLE public.product_gallery OWNER TO fuma_user;

--
-- Name: product_gallery_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.product_gallery_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.product_gallery_id_seq OWNER TO fuma_user;

--
-- Name: product_gallery_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.product_gallery_id_seq OWNED BY public.product_gallery.id;


--
-- Name: product_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.product_id_seq OWNER TO fuma_user;

--
-- Name: product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.product_id_seq OWNED BY public.product.id;


--
-- Name: product_variant; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.product_variant (
    id integer NOT NULL,
    name character varying(100),
    type integer NOT NULL
);


ALTER TABLE public.product_variant OWNER TO fuma_user;

--
-- Name: product_variant_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.product_variant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.product_variant_id_seq OWNER TO fuma_user;

--
-- Name: product_variant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.product_variant_id_seq OWNED BY public.product_variant.id;


--
-- Name: product_variant_product; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.product_variant_product (
    product_variant_id integer,
    product_id integer
);


ALTER TABLE public.product_variant_product OWNER TO fuma_user;

--
-- Name: push_token; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.push_token (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying(512) NOT NULL,
    platform character varying(50),
    device character varying(200),
    last_seen_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.push_token OWNER TO fuma_user;

--
-- Name: push_token_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.push_token_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.push_token_id_seq OWNER TO fuma_user;

--
-- Name: push_token_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.push_token_id_seq OWNED BY public.push_token.id;


--
-- Name: role; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.role (
    id integer NOT NULL,
    name character varying(80) NOT NULL,
    description character varying(255)
);


ALTER TABLE public.role OWNER TO fuma_user;

--
-- Name: role_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.role_id_seq OWNER TO fuma_user;

--
-- Name: role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.role_id_seq OWNED BY public.role.id;


--
-- Name: roles_users; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.roles_users (
    user_id integer,
    role_id integer
);


ALTER TABLE public.roles_users OWNER TO fuma_user;

--
-- Name: score_table; Type: TABLE; Schema: public; Owner: fuma_user
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


ALTER TABLE public.score_table OWNER TO fuma_user;

--
-- Name: score_table_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.score_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.score_table_id_seq OWNER TO fuma_user;

--
-- Name: score_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.score_table_id_seq OWNED BY public.score_table.id;


--
-- Name: sponsors; Type: TABLE; Schema: public; Owner: fuma_user
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


ALTER TABLE public.sponsors OWNER TO fuma_user;

--
-- Name: sponsors_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.sponsors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sponsors_id_seq OWNER TO fuma_user;

--
-- Name: sponsors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.sponsors_id_seq OWNED BY public.sponsors.id;


--
-- Name: talk_message; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.talk_message (
    id integer NOT NULL,
    room_id integer NOT NULL,
    user_id integer NOT NULL,
    text text,
    created_at timestamp with time zone DEFAULT now(),
    msg_type character varying(20) DEFAULT 'text'::character varying NOT NULL,
    payload_json text,
    attachment_url character varying(900),
    attachment_mime character varying(120),
    attachment_size integer
);


ALTER TABLE public.talk_message OWNER TO fuma_user;

--
-- Name: talk_message_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.talk_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.talk_message_id_seq OWNER TO fuma_user;

--
-- Name: talk_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.talk_message_id_seq OWNED BY public.talk_message.id;


--
-- Name: talk_poll; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.talk_poll (
    id integer NOT NULL,
    message_id integer NOT NULL,
    question character varying(300) NOT NULL,
    allow_multi boolean DEFAULT false NOT NULL,
    expires_at timestamp with time zone
);


ALTER TABLE public.talk_poll OWNER TO fuma_user;

--
-- Name: talk_poll_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.talk_poll_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.talk_poll_id_seq OWNER TO fuma_user;

--
-- Name: talk_poll_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.talk_poll_id_seq OWNED BY public.talk_poll.id;


--
-- Name: talk_poll_option; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.talk_poll_option (
    id integer NOT NULL,
    poll_id integer NOT NULL,
    text character varying(250) NOT NULL,
    order_index integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.talk_poll_option OWNER TO fuma_user;

--
-- Name: talk_poll_option_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.talk_poll_option_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.talk_poll_option_id_seq OWNER TO fuma_user;

--
-- Name: talk_poll_option_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.talk_poll_option_id_seq OWNED BY public.talk_poll_option.id;


--
-- Name: talk_poll_vote; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.talk_poll_vote (
    id integer NOT NULL,
    poll_id integer NOT NULL,
    option_id integer NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.talk_poll_vote OWNER TO fuma_user;

--
-- Name: talk_poll_vote_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.talk_poll_vote_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.talk_poll_vote_id_seq OWNER TO fuma_user;

--
-- Name: talk_poll_vote_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.talk_poll_vote_id_seq OWNED BY public.talk_poll_vote.id;


--
-- Name: talk_room; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.talk_room (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    team_id integer,
    created_by_user_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.talk_room OWNER TO fuma_user;

--
-- Name: talk_room_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.talk_room_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.talk_room_id_seq OWNER TO fuma_user;

--
-- Name: talk_room_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.talk_room_id_seq OWNED BY public.talk_room.id;


--
-- Name: talk_room_members; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.talk_room_members (
    room_id integer NOT NULL,
    user_id integer NOT NULL,
    is_admin boolean DEFAULT false NOT NULL,
    joined_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.talk_room_members OWNER TO fuma_user;

--
-- Name: talk_room_read_state; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.talk_room_read_state (
    id integer NOT NULL,
    user_id integer NOT NULL,
    room_id integer NOT NULL,
    last_read_message_id integer,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.talk_room_read_state OWNER TO fuma_user;

--
-- Name: talk_room_read_state_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.talk_room_read_state_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.talk_room_read_state_id_seq OWNER TO fuma_user;

--
-- Name: talk_room_read_state_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.talk_room_read_state_id_seq OWNED BY public.talk_room_read_state.id;


--
-- Name: team; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.team (
    id integer NOT NULL,
    name character varying(250) NOT NULL,
    score_scrap character varying(250) NOT NULL,
    player_list_scrap character varying(250) NOT NULL,
    main_league character varying(300) NOT NULL,
    events_results_scrap character varying(550),
    events_program_scrap character varying(550)
);


ALTER TABLE public.team OWNER TO fuma_user;

--
-- Name: team_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.team_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.team_id_seq OWNER TO fuma_user;

--
-- Name: team_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.team_id_seq OWNED BY public.team.id;


--
-- Name: team_lineup_slots; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.team_lineup_slots (
    id integer NOT NULL,
    lineup_id integer NOT NULL,
    player_id integer NOT NULL,
    is_starter boolean NOT NULL,
    order_index integer NOT NULL,
    "position" integer NOT NULL
);


ALTER TABLE public.team_lineup_slots OWNER TO fuma_user;

--
-- Name: team_lineup_slots_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.team_lineup_slots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.team_lineup_slots_id_seq OWNER TO fuma_user;

--
-- Name: team_lineup_slots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.team_lineup_slots_id_seq OWNED BY public.team_lineup_slots.id;


--
-- Name: team_lineups; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.team_lineups (
    id integer NOT NULL,
    team_id integer NOT NULL,
    formation character varying(16) NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.team_lineups OWNER TO fuma_user;

--
-- Name: team_lineups_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.team_lineups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.team_lineups_id_seq OWNER TO fuma_user;

--
-- Name: team_lineups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.team_lineups_id_seq OWNED BY public.team_lineups.id;


--
-- Name: teams_members; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.teams_members (
    member_id integer,
    team_id integer
);


ALTER TABLE public.teams_members OWNER TO fuma_user;

--
-- Name: type_product_variant; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.type_product_variant (
    id integer NOT NULL,
    name character varying(250) NOT NULL,
    operation character varying(450) NOT NULL
);


ALTER TABLE public.type_product_variant OWNER TO fuma_user;

--
-- Name: type_product_variant_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.type_product_variant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.type_product_variant_id_seq OWNER TO fuma_user;

--
-- Name: type_product_variant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.type_product_variant_id_seq OWNED BY public.type_product_variant.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    uuid character varying(36),
    username character varying(20) NOT NULL,
    email character varying(120) NOT NULL,
    image_file character varying(255) NOT NULL,
    password character varying(60) NOT NULL,
    confirm boolean DEFAULT false,
    active boolean DEFAULT true,
    confirmed_at timestamp without time zone,
    fs_uniquifier character varying(64)
);


ALTER TABLE public."user" OWNER TO fuma_user;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO fuma_user;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: variant_products; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.variant_products (
    product_id integer,
    variant_id integer,
    variant_text character varying(100) NOT NULL,
    variant_image text
);


ALTER TABLE public.variant_products OWNER TO fuma_user;

--
-- Name: webpush_subscription; Type: TABLE; Schema: public; Owner: fuma_user
--

CREATE TABLE public.webpush_subscription (
    id integer NOT NULL,
    user_id integer NOT NULL,
    endpoint text NOT NULL,
    p256dh character varying(256) NOT NULL,
    auth character varying(128) NOT NULL,
    device character varying(200),
    platform character varying(50),
    created_at timestamp with time zone DEFAULT now(),
    last_seen_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.webpush_subscription OWNER TO fuma_user;

--
-- Name: webpush_subscription_id_seq; Type: SEQUENCE; Schema: public; Owner: fuma_user
--

CREATE SEQUENCE public.webpush_subscription_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.webpush_subscription_id_seq OWNER TO fuma_user;

--
-- Name: webpush_subscription_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fuma_user
--

ALTER SEQUENCE public.webpush_subscription_id_seq OWNED BY public.webpush_subscription.id;


--
-- Name: category id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.category ALTER COLUMN id SET DEFAULT nextval('public.category_id_seq'::regclass);


--
-- Name: club id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.club ALTER COLUMN id SET DEFAULT nextval('public.club_id_seq'::regclass);


--
-- Name: event id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.event ALTER COLUMN id SET DEFAULT nextval('public.event_id_seq'::regclass);


--
-- Name: event_category id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.event_category ALTER COLUMN id SET DEFAULT nextval('public.event_category_id_seq'::regclass);


--
-- Name: member id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.member ALTER COLUMN id SET DEFAULT nextval('public.member_id_seq'::regclass);


--
-- Name: order id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."order" ALTER COLUMN id SET DEFAULT nextval('public.order_id_seq'::regclass);


--
-- Name: player id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.player ALTER COLUMN id SET DEFAULT nextval('public.player_id_seq'::regclass);


--
-- Name: position id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."position" ALTER COLUMN id SET DEFAULT nextval('public.position_id_seq'::regclass);


--
-- Name: post id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.post ALTER COLUMN id SET DEFAULT nextval('public.post_id_seq'::regclass);


--
-- Name: post_gallery id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.post_gallery ALTER COLUMN id SET DEFAULT nextval('public.post_gallery_id_seq'::regclass);


--
-- Name: product id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product ALTER COLUMN id SET DEFAULT nextval('public.product_id_seq'::regclass);


--
-- Name: product_category id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product_category ALTER COLUMN id SET DEFAULT nextval('public.product_category_id_seq'::regclass);


--
-- Name: product_gallery id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product_gallery ALTER COLUMN id SET DEFAULT nextval('public.product_gallery_id_seq'::regclass);


--
-- Name: product_variant id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product_variant ALTER COLUMN id SET DEFAULT nextval('public.product_variant_id_seq'::regclass);


--
-- Name: push_token id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.push_token ALTER COLUMN id SET DEFAULT nextval('public.push_token_id_seq'::regclass);


--
-- Name: role id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.role ALTER COLUMN id SET DEFAULT nextval('public.role_id_seq'::regclass);


--
-- Name: score_table id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.score_table ALTER COLUMN id SET DEFAULT nextval('public.score_table_id_seq'::regclass);


--
-- Name: sponsors id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.sponsors ALTER COLUMN id SET DEFAULT nextval('public.sponsors_id_seq'::regclass);


--
-- Name: talk_message id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_message ALTER COLUMN id SET DEFAULT nextval('public.talk_message_id_seq'::regclass);


--
-- Name: talk_poll id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll ALTER COLUMN id SET DEFAULT nextval('public.talk_poll_id_seq'::regclass);


--
-- Name: talk_poll_option id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll_option ALTER COLUMN id SET DEFAULT nextval('public.talk_poll_option_id_seq'::regclass);


--
-- Name: talk_poll_vote id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll_vote ALTER COLUMN id SET DEFAULT nextval('public.talk_poll_vote_id_seq'::regclass);


--
-- Name: talk_room id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room ALTER COLUMN id SET DEFAULT nextval('public.talk_room_id_seq'::regclass);


--
-- Name: talk_room_read_state id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room_read_state ALTER COLUMN id SET DEFAULT nextval('public.talk_room_read_state_id_seq'::regclass);


--
-- Name: team id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.team ALTER COLUMN id SET DEFAULT nextval('public.team_id_seq'::regclass);


--
-- Name: team_lineup_slots id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.team_lineup_slots ALTER COLUMN id SET DEFAULT nextval('public.team_lineup_slots_id_seq'::regclass);


--
-- Name: team_lineups id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.team_lineups ALTER COLUMN id SET DEFAULT nextval('public.team_lineups_id_seq'::regclass);


--
-- Name: type_product_variant id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.type_product_variant ALTER COLUMN id SET DEFAULT nextval('public.type_product_variant_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: webpush_subscription id; Type: DEFAULT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.webpush_subscription ALTER COLUMN id SET DEFAULT nextval('public.webpush_subscription_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.alembic_version (version_num) FROM stdin;
3e1efed09a19
\.


--
-- Data for Name: category; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.category (id, name) FROM stdin;
1	Aktuality
2	A team
3	Mládež
8	Blog
\.


--
-- Data for Name: club; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.club (id, name, subdomain, created_at) FROM stdin;
\.


--
-- Data for Name: event; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.event (id, title, start_event, end_event, user_id, event_category_id, event_team_id, address, link) FROM stdin;
1423	FC Slovan Modra - FK Záhoran Jakubov	2026-01-23 10:00:00+01	2026-01-23 11:00:00+01	1	1	1	ii	ii
1098	FC Slovan Modra 1:5 TJ SLOVAN Vištuk	2025-09-20 09:00:00+02	2025-09-20 11:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1099	CFK Pezinok - Cajla 0:2 FC Slovan Modra	2025-09-27 08:30:00+02	2025-09-27 10:30:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+CFK+Pezinok+-+Cajla
1100	TJ Slovan Viničné 1:1 FC Slovan Modra	2025-10-12 10:30:00+02	2025-10-12 12:30:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Slovan+Vini%C4%8Dn%C3%A9
1101	FC Slovan Modra 2:2 TJ Záhoran Kostolište	2025-10-08 14:00:00+02	2025-10-08 16:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1102	Futbalový klub Dubová 5:0 FC Slovan Modra	2025-10-26 09:30:00+01	2025-10-26 11:30:00+01	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+Futbalov%C3%BD+klub+Dubov%C3%A1
1103	FC Slovan Modra 0:4 OŠK Slovenský Grob	2025-11-01 10:00:00+01	2025-11-01 12:00:00+01	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1067	FK Dúbravka B 4:1 FC Slovan Modra	2025-08-17 11:00:00+02	2025-08-17 13:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+D%C3%BAbravka+B
1068	FC Slovan Modra 1:2 TJ Slovan Viničné	2025-08-24 12:00:00+02	2025-08-24 14:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1069	ŠK Bernolákovo 3:4 FC Slovan Modra	2025-10-02 14:00:00+02	2025-10-02 16:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Bernol%C3%A1kovo
1070	FC Slovan Modra 2:1 FK Vajnory	2025-09-07 12:00:00+02	2025-09-07 14:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1071	ŠK Tomášov 5:2 FC Slovan Modra	2025-09-13 11:30:00+02	2025-09-13 13:30:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Tom%C3%A1%C5%A1ov
1072	FC Slovan Modra - FC Ružinov Bratislava	2025-09-20 11:30:00+02	2025-09-20 13:30:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1119	FC Slovan Modra 6:2 TJ Slovan Viničné	2025-08-24 09:00:00+02	2025-08-24 11:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1120	TJ Družstevník Jablonec 1:7 FC Slovan Modra	2025-08-31 12:00:00+02	2025-08-31 14:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Dru%C5%BEstevn%C3%ADk+Jablonec
1121	FC Slovan Modra 2:7 ŠK Igram	2025-09-07 09:00:00+02	2025-09-07 11:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1122	FC Slovan Modra 3:2 FKM Stupava B	2025-09-11 15:30:00+02	2025-09-11 17:30:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1123	Futbalový klub Budmerice 0:4 FC Slovan Modra	2025-09-14 08:00:00+02	2025-09-14 10:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+Futbalov%C3%BD+klub+Budmerice
1124	CFK Pezinok - Cajla 0:4 FC Slovan Modra	2025-09-16 15:00:00+02	2025-09-16 17:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+CFK+Pezinok+-+Cajla
1125	FC Slovan Modra 0:3 FK Karpaty Limbach	2025-09-21 09:00:00+02	2025-09-21 11:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1126	FC Slovan Modra 8:0 ŠK Báhoň	2025-09-28 09:00:00+02	2025-09-28 11:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1127	ŠK Bernolákovo B 3:0 FC Slovan Modra	2025-10-05 07:00:00+02	2025-10-05 09:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Bernol%C3%A1kovo+B
1128	FC Slovan Modra 10:2 FK CINEMAX Doľany	2025-10-12 09:00:00+02	2025-10-12 11:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1129	PŠC Pezinok B 2:5 FC Slovan Modra	2025-10-19 10:00:00+02	2025-10-19 12:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+P%C5%A0C+Pezinok+B
1130	FC Slovan Modra 0:5 OŠK Slovenský Grob	2025-10-26 10:00:00+01	2025-10-26 12:00:00+01	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1131	ŠK Šenkvice - FC Slovan Modra	2025-11-02 09:00:00+01	2025-11-02 11:00:00+01	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+%C5%A0enkvice
1132	FC Slovan Modra - ŠK Šenkvice	2026-03-22 10:00:00+01	2026-03-22 12:00:00+01	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1133	TJ Slovan Viničné - FC Slovan Modra	2026-03-28 12:30:00+01	2026-03-28 14:30:00+01	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Slovan+Vini%C4%8Dn%C3%A9
1134	FC Slovan Modra - TJ Družstevník Jablonec	2026-04-05 09:00:00+02	2026-04-05 11:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1135	ŠK Igram - FC Slovan Modra	2026-04-11 08:00:00+02	2026-04-11 10:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Igram
1136	FC Slovan Modra - Futbalový klub Budmerice	2026-04-19 09:00:00+02	2026-04-19 11:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1137	FK Karpaty Limbach - FC Slovan Modra	2026-04-26 09:30:00+02	2026-04-26 11:30:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+Karpaty+Limbach
1138	FKM Stupava B - FC Slovan Modra	2026-04-29 15:00:00+02	2026-04-29 17:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FKM+Stupava+B
1139	ŠK Báhoň - FC Slovan Modra	2026-05-02 08:00:00+02	2026-05-02 10:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+B%C3%A1ho%C5%88
1140	FC Slovan Modra - CFK Pezinok - Cajla	2026-05-06 15:00:00+02	2026-05-06 17:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1073	FKM Stupava 1:3 FC Slovan Modra	2025-10-04 08:00:00+02	2025-10-04 10:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FKM+Stupava
1074	FC Slovan Modra 2:0 Lokomotíva Devínska Nová Ves	2025-10-11 12:00:00+02	2025-10-11 14:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1075	Senec Football Academy 2:0 FC Slovan Modra	2025-10-18 13:00:00+02	2025-10-18 15:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+Senec+Football+Academy
1076	FC Slovan Modra 7:1 FC Zohor	2025-10-26 13:00:00+01	2025-10-26 15:00:00+01	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1077	ŠK Závod - FC Slovan Modra	2025-11-02 09:00:00+01	2025-11-02 11:00:00+01	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Z%C3%A1vod
1078	FC Slovan Modra 10:2 ŠK Lozorno, FO	2025-11-08 12:30:00+01	2025-11-08 14:30:00+01	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1079	TJ Slovan Viničné - FC Slovan Modra	2026-03-14 14:00:00+01	2026-03-14 16:00:00+01	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Slovan+Vini%C4%8Dn%C3%A9
1080	FC Slovan Modra - ŠK Bernolákovo	2026-03-22 13:00:00+01	2026-03-22 15:00:00+01	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1081	FK Vajnory - FC Slovan Modra	2026-03-28 11:30:00+01	2026-03-28 13:30:00+01	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+Vajnory
1141	FC Slovan Modra - ŠK Bernolákovo B	2026-05-10 09:00:00+02	2026-05-10 11:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1142	FK CINEMAX Doľany - FC Slovan Modra	2026-05-17 13:00:00+02	2026-05-17 15:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+CINEMAX+Do%C4%BEany
1082	FC Slovan Modra - ŠK Tomášov	2026-04-05 12:00:00+02	2026-04-05 14:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1143	FC Slovan Modra - PŠC Pezinok B	2026-05-24 09:00:00+02	2026-05-24 11:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1144	OŠK Slovenský Grob - FC Slovan Modra	2026-05-31 08:00:00+02	2026-05-31 10:00:00+02	1	1	5	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+O%C5%A0K+Slovensk%C3%BD+Grob
1083	FC Ružinov Bratislava - FC Slovan Modra	2026-04-11 11:00:00+02	2026-04-11 13:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Ru%C5%BEinov+Bratislava
1084	FC Slovan Modra - FKM Stupava	2026-04-26 12:00:00+02	2026-04-26 14:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1085	Lokomotíva Devínska Nová Ves - FC Slovan Modra	2026-05-02 11:30:00+02	2026-05-02 13:30:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+Lokomot%C3%ADva+Dev%C3%ADnska+Nov%C3%A1+Ves
1086	FC Slovan Modra - Senec Football Academy	2026-05-10 12:00:00+02	2026-05-10 14:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1087	FC Zohor - FC Slovan Modra	2026-05-17 12:30:00+02	2026-05-17 14:30:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Zohor
1088	FC Slovan Modra - ŠK Závod	2026-05-24 12:00:00+02	2026-05-24 14:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1089	ŠK Lozorno, FO - FC Slovan Modra	2026-05-30 13:00:00+02	2026-05-30 15:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Lozorno%2C+FO
1090	FC Slovan Modra - FK Dúbravka B	2026-06-07 12:00:00+02	2026-06-07 14:00:00+02	1	1	2	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1104	FKM Stupava B 1:1 FC Slovan Modra	2025-11-09 13:00:00+01	2025-11-09 15:00:00+01	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FKM+Stupava+B
1106	PŠC Pezinok B - FC Slovan Modra	2026-03-22 08:00:00+01	2026-03-22 10:00:00+01	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+P%C5%A0C+Pezinok+B
1107	FC Slovan Modra - FC Zohor	2026-03-28 10:00:00+01	2026-03-28 12:00:00+01	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1108	FC Slovan Modra - FK Karpaty Limbach	2026-04-04 09:00:00+02	2026-04-04 11:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1109	TJ SLOVAN Vištuk - FC Slovan Modra	2026-04-12 12:30:00+02	2026-04-12 14:30:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+SLOVAN+Vi%C5%A1tuk
1110	FC Slovan Modra - CFK Pezinok - Cajla	2026-04-18 09:00:00+02	2026-04-18 11:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1111	FC Slovan Modra - TJ Záhoran Jakubov	2026-04-29 15:00:00+02	2026-04-29 17:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1112	FC Slovan Modra - TJ Slovan Viničné	2026-05-02 09:00:00+02	2026-05-02 11:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1113	ŠK Šenkvice - FC Slovan Modra	2026-05-06 15:00:00+02	2026-05-06 17:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+%C5%A0enkvice
1114	TJ Záhoran Kostolište - FC Slovan Modra	2026-05-10 08:30:00+02	2026-05-10 10:30:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Z%C3%A1horan+Kostoli%C5%A1te
1115	FC Slovan Modra - Futbalový klub Dubová	2026-05-16 09:00:00+02	2026-05-16 11:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1116	OŠK Slovenský Grob - FC Slovan Modra	2026-05-23 09:30:00+02	2026-05-23 11:30:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+O%C5%A0K+Slovensk%C3%BD+Grob
1117	FC Slovan Modra - FKM Stupava B	2026-05-30 09:00:00+02	2026-05-30 11:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1118	FC SLOVAN Častá - FC Slovan Modra	2026-06-07 13:00:00+02	2026-06-07 15:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+SLOVAN+%C4%8Cast%C3%A1
1091	FC Slovan Modra 7:1 FC SLOVAN Častá	2025-08-19 15:00:00+02	2025-08-19 17:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1092	ŠK Lozorno, FO 7:2 FC Slovan Modra	2025-08-24 08:30:00+02	2025-08-24 10:30:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Lozorno%2C+FO
1093	FC Slovan Modra 3:7 PŠC Pezinok B	2025-08-30 09:00:00+02	2025-08-30 11:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1094	FC Zohor 6:0 FC Slovan Modra	2025-10-01 14:30:00+02	2025-10-01 16:30:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Zohor
1095	TJ Záhoran Jakubov 2:4 FC Slovan Modra	2025-09-10 15:00:00+02	2025-09-10 17:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Z%C3%A1horan+Jakubov
1096	FK Karpaty Limbach 0:3 FC Slovan Modra	2025-09-13 09:00:00+02	2025-09-13 11:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+Karpaty+Limbach
1097	FC Slovan Modra 2:3 ŠK Šenkvice	2025-09-17 15:00:00+02	2025-09-17 17:00:00+02	1	1	4	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1385	NŠK 1922 Bratislava 4:0 FC Slovan Modra	2025-08-09 08:30:00+02	2025-08-09 10:30:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+N%C5%A0K+1922+Bratislava
1386	FC Slovan Modra 0:2 FK Slovan Ivanka pri Dunaji	2025-08-16 15:00:00+02	2025-08-16 17:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1421	jlklj	2025-12-26 00:00:00+01	2025-12-27 00:00:00+01	1	2	7	j	j
1387	FKM Karlova Ves Bratislava 5:1 FC Slovan Modra	2025-08-24 15:00:00+02	2025-08-24 17:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FKM+Karlova+Ves+Bratislava
1388	FC Slovan Modra 3:0 Lokomotíva Devínska Nová Ves	2025-08-30 14:30:00+02	2025-08-30 16:30:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1389	PŠC Pezinok 1:1 FC Slovan Modra	2025-09-06 14:30:00+02	2025-09-06 16:30:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+P%C5%A0C+Pezinok
1390	FC Slovan Modra 2:2 SFC Kalinkovo	2025-09-13 14:00:00+02	2025-09-13 16:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1391	FC Rohožník 6:0 FC Slovan Modra	2025-09-21 14:00:00+02	2025-09-21 16:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Roho%C5%BEn%C3%ADk
1392	FC Slovan Modra 2:1 MŠK Kráľová pri Senci	2025-09-27 13:30:00+02	2025-09-27 15:30:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1393	TJ Rovinka 1:0 FC Slovan Modra	2025-10-05 13:30:00+02	2025-10-05 15:30:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Rovinka
1394	TJ Záhoran Jakubov 0:0 FC Slovan Modra	2025-10-12 13:00:00+02	2025-10-12 15:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+TJ+Z%C3%A1horan+Jakubov
1395	FC Slovan Modra 0:1 MFK Rusovce	2025-10-18 13:00:00+02	2025-10-18 15:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1396	ŠK Bernolákovo 2:0 FC Slovan Modra	2025-10-25 12:00:00+02	2025-10-25 14:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Bernol%C3%A1kovo
1397	FC Slovan Modra 1:1 OFK Dunajská Lužná	2025-11-01 12:30:00+01	2025-11-01 14:30:00+01	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1398	Športový klub Nová Dedinka 3:0 FC Slovan Modra	2025-11-09 12:30:00+01	2025-11-09 14:30:00+01	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0portov%C3%BD+klub+Nov%C3%A1+Dedinka
1399	FC Slovan Modra 0:3 ŠK Tomášov	2025-11-15 12:30:00+01	2025-11-15 14:30:00+01	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1400	FC Slovan Modra - NŠK 1922 Bratislava	2026-03-14 14:00:00+01	2026-03-14 16:00:00+01	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1401	FK Slovan Ivanka pri Dunaji - FC Slovan Modra	2026-03-22 14:00:00+01	2026-03-22 16:00:00+01	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FK+Slovan+Ivanka+pri+Dunaji
1402	FC Slovan Modra - FKM Karlova Ves Bratislava	2026-03-28 14:30:00+01	2026-03-28 16:30:00+01	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1403	Lokomotíva Devínska Nová Ves - FC Slovan Modra	2026-04-01 15:00:00+02	2026-04-01 17:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+Lokomot%C3%ADva+Dev%C3%ADnska+Nov%C3%A1+Ves
1404	FC Slovan Modra - PŠC Pezinok	2026-04-11 15:00:00+02	2026-04-11 17:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1405	SFC Kalinkovo - FC Slovan Modra	2026-04-19 15:00:00+02	2026-04-19 17:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+SFC+Kalinkovo
1406	FC Slovan Modra - FC Rohožník	2026-04-25 15:00:00+02	2026-04-25 17:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1407	MŠK Kráľová pri Senci - FC Slovan Modra	2026-04-29 15:30:00+02	2026-04-29 17:30:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+M%C5%A0K+Kr%C3%A1%C4%BEov%C3%A1+pri+Senci
1408	FC Slovan Modra - TJ Rovinka	2026-05-02 15:00:00+02	2026-05-02 17:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1409	FC Slovan Modra - TJ Záhoran Jakubov	2026-05-09 15:00:00+02	2026-05-09 17:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1410	MFK Rusovce - FC Slovan Modra	2026-05-17 15:00:00+02	2026-05-17 17:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+MFK+Rusovce
1411	FC Slovan Modra - ŠK Bernolákovo	2026-05-23 15:00:00+02	2026-05-23 17:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1412	OFK Dunajská Lužná - FC Slovan Modra	2026-05-31 15:30:00+02	2026-05-31 17:30:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+OFK+Dunajsk%C3%A1+Lu%C5%BEn%C3%A1
1413	FC Slovan Modra - Športový klub Nová Dedinka	2026-06-06 15:30:00+02	2026-06-06 17:30:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+FC+Slovan+Modra
1414	ŠK Tomášov - FC Slovan Modra	2026-06-13 16:00:00+02	2026-06-13 18:00:00+02	1	1	1	Navigácia na štadión	https://www.google.com/maps/dir/?api=1&destination=%C5%A0tadi%C3%B3n+%C5%A0K+Tom%C3%A1%C5%A1ov
\.


--
-- Data for Name: event_category; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.event_category (id, name) FROM stdin;
1	Zápas
2	Tréning
5	Iné
4	Kemp
\.


--
-- Data for Name: member; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.member (id, name, phone, address, psc, city, image_file, weight, height, user_id) FROM stdin;
1	Milan Martiš	+421917360277	Sládkovičova 22	90001	Modra	default.png	\N	\N	1
2	Fanúšik	+421917360277	Sládkovičova 22	90001	Modra	default.png	\N	\N	2
3	Slavomír Podubinský	+421917360277	Sládkovičova 22	90001	Modra	0341e28ea55de538.jpg	79	182	3
7	Ján Vislocký	+421917360277	...	...	...	832506aff7f4c6d3.jpg	25	180	7
6	František Dolutovský	+421917360277	..	...	...	5a4744e44fd40776.jpg	180	80	6
4	Štefan Maťaš	+421905501402	Sládkovičova 22	90001	Modra	a2ebf1dd11ae608e.jpg	0	0	4
8	Milan Martiš	+421917360277	Sládkovičova 22	90001	Modra	default.png	\N	\N	15
10	Milan Martiš	+421917360277	Sládkovičova 22	90001	Modra	default.png	\N	\N	17
14	Milan	+421917360277	kh	90001	oih	5fc7d6b9f58c4085.png	23	2	21
15	Marco Van Basten	+421917360277	Sládkovičova 22	90001	Modra	2a5d67c181a84564.jpg	3	3	22
11	Jakub Pavúk	+421917360277	Sládkovičova 22	90001	Modra	4482ceace8a04b53.jpg	15	12	18
\.


--
-- Data for Name: order; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public."order" (id, produc_id, quantity, amount, user_id, is_paid, order_date, storno, variants) FROM stdin;
\.


--
-- Data for Name: player; Type: TABLE DATA; Schema: public; Owner: fuma_user
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
-- Data for Name: position; Type: TABLE DATA; Schema: public; Owner: fuma_user
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
-- Data for Name: positions_members; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.positions_members (member_id, position_id) FROM stdin;
7	4
6	2
4	5
3	4
11	3
11	6
\.


--
-- Data for Name: post; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.post (id, title, date_posted, content, user_id, category_id, slug, views, is_featured, priority, published_at) FROM stdin;
23	Privítali sme vzácnu návštevu	2023-04-20 10:31:00+02	Počas pohárového zápasu BFZ sme okrem PSČ Pezinka, jeho hráčov a fanúšikov privítali na našom štadióne aj vzácnu návštevu, futbalového agenta menom Sidy Fall.\r\n\r\nSidy Fall je medzinárodný agent FIFA senegalskej národnosti, žijúci v Miláne. Je zakladateľom akadémie s názvom Académia Angelo Africa sídliacej v Dakare. Každoročne sa zúčastňuje futbalového galavečera Zlatá Lopta, ktorého účastníkmi je len svetová futbalová špička. Na Slovensko zavítal na pozvanie nášho generálneho manažéra Norberta Sališa s ktorým nadviazali spoluprácu v oblasti scoutingu a manažmentu hráčov. Strávil tu 4 dni, počas ktorých sme ho previedli mestom Modra, ale hlavne si pozrel náš derby zápas s Pezinkom. Ocenil kolumbíjsku dvojicu Ruberth a Jhonathan ale aj prácu s mládežou, nakoľko v zápase nastúpili 4 hráči pod 18 rokov a zastali si svoje úlohy na výbornú. Po tomto zápase sa v sprievode nášho manažéra vydali na zápas Slovanu Bratislava s Ružomberkom.\r\n\r\n„Naša spolupráca bude prínosom aj pre modranský futbal, nakoľko náš klub bude partnerom Sidyho akadémie v Senegale. Takisto je to pre klub obrovská prezentácia, sme veľmi vďační za návštevu.“\r\n\r\nSenegalčan od nás cestoval priamo do Kataru na futbalové Majstrovstvá sveta kde bude fandiť svojmu národnému tímu, ktoré však pre zranenie na poslednú chvíľu nebude reprezentovať najväčšia hviezda Sadio Mané. Veríme, že sa Sidymu na Slovensku a špeciálne v Modre páčilo. 	1	1	post-23	11	f	0	\N
1	pojpoj	2023-04-20 09:01:55.199901+02	pojpoj	1	2	post-1	0	f	0	\N
10	Finálový krok	2023-04-20 10:20:53.551281+02	Blíži sa finálový krok a s ním spojený bohatý program. Očakávame Vás v sobotu, 11. 6., už o 13:00 hod., kedy začne zápas Old Boys Artmedia Petržalka vs. Old boys FCSM. Po nich sa bude hrať o 15:00 hod. mini-turnaj prípraviek. O 16:30 sa budú konať rôzne súťaže a o 17:30 nastúpi naše Áčko proti OFK Vysoká pri Morave. Odohrá tak svoj posledný zápas sezóny. Tešíme sa aj na vystúpenie mažoretiek. Môžete sa tešiť na pestrý sprievodný program. My sa tešíme na Vás. 	1	2	post-10	0	f	0	\N
17	Domácu neporaziteľnosť sme si udržali aj v roku 2022!	2023-04-20 10:25:50.922355+02	V poslednom domácom zápase jesennej časti sme nasúkali súperovi 7 kúskov. Ďakujeme fanúšikom za podporu!\r\n\r\nFC Slovan Modra vs. TJ Záhoran Kostolište 7:2 (2:1)\r\nGóly: 25', 79' a 88' Araque, 47' a 68' Aguem, 12' Kovár, 84' Quejada\r\nFCSM: Lörincz - Dolutovský, Vislocký, Lehocký, Plach - Kovár, Dvorák (76' Ayodeji), Araque - Peško, Aguem (79' Kubín), Quejada. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „S Kostolišťom to bol zaujímavý a atraktívny zápas, hostia sa rýchlo po „štandardke“ ujali vedenia pekným gólom, ale zrejme si neuvedomili proti komu hrajú a povzbudení gólom chceli hrať ofenzívne. My sme nastúpili bez 4 hráčov základnej zostavy, čo bolo prvých 10 minút cítiť, no následne sme absolútne prebrali zápas do svojich rúk. Hráči sa momentálne bavia futbalom. Dnes bol ťažký terén, ale v našom podaní to bola v druhom polčase už exhibícia. Jeden krajší gól ako druhý a zároveň kopec zahodených tutoviek, kedy už chlapci vymýšľali. Teším sa z hattricku Jhonatana, je to veľmi dobrý chlapec, zaslúži si za svoje výkony absolutórium. Na druhej strane sú aj takí, ktorí ma dnes sklamali a nevážia si partiu. Vyvodím z toho dôsledky. Ešte raz sa chcem poďakovať všetkým chlapcom, ktorí dnes nastúpili. Posledný domáci zápas bol pre všetkých odmenou."\r\n\r\nJhonatan Garcia Araque, autor hetriku: „V dnešnom zápase bolo evidentné, že sme silný a kompaktný tím. Začali sme veľmi skoro prehrávať, ale máme silný charakter a za žiadneho stavu nedávame hlavy dole. Vždy ideme na 100 percent za každého stavu. Ďakujem Bohu za takýto výsledok a taktiež fanúšikom Modry, že nás celý zápas povzbudzovali. Vyhrali sme dôležitý zápas na teréne, ktorý bol pre obidva tímy náročný a využili sme príležitosti na skórovanie. VAMOS MODRA, sme skvelý tím a všetci sme spojení pre jeden cieľ. Po tomto zápase sme s istotou po jesennej časti na 1. mieste. Je to niečo veľmi pekné a ďakujem fanúšikom, že nás povzbudzujú a užívajú si s nami každý zápas.“ 	1	2	post-17	0	f	0	\N
18	Výsledkový sumár mládeže	2023-04-20 10:27:00+02	U17 Skupina "B" - 11. kolo, 29.10. o 10:00 FCSM – MŠK Iskra Petržalka 5-3. \r\nU15 II. liga SŽ - 11. kolo, 30.10. o 9:00 FCSM – NŠK 1922 Bratislava 1-1. \r\nU13 II. liga MŽ - 11. kolo, 30.10. o 9:00 FCSM – NŠK 1922 Bratislava 1-11.\r\n	1	3	post-18	6	f	0	\N
19	V poslednom ligovom zápase jesennej časti sme prehrali	2023-04-20 10:28:56.527066+02	V poslednom ligovom zápase jesennej časti sme prehrali na pôde Vištuku. Ďakujeme fanúšikom za podporu!\r\n\r\nTJ Slovan Vištuk vs. FC Slovan Modra 2:0 (0:0)\r\nČK: 66' Dvorák (Po 2. ŽK), 90' Aguem\r\nFCSM: Lörincz - Lehocký, Vojtovič, Ayodeji, Plach (76' Peško) - Pavúk, Dvorák, Araque - Quejada, Aguem (76' Kovár), Vislocký. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „Zápas vnímam v dvoch rovinách, nakoľko išlo o derby a my sme boli jediné neporazené mužstvo v lige, už niekoľko kôl sa na nás každý super chystal a chcel vytiahnuť. Kvôli naším fanúšikom, ktorí boli aj v tomto zápase skvelí ma mrzí, že prehra prišla práve vo Vištuku. Domáci však boli veľmi nepríjemným súperom, hrali jednoducho, no veľmi poctivo a oduševnene. Nám trošku chýbala emócia, čo beriem na seba, pretože Vištuk nepovažujem za konkurenciu v boji o postup a preto som aj mužstvo nabádal že ide o bežný zápas a netreba sa nechať strhnúť a vyprovokovať. Z tohto pohľadu chcem pochváliť a poďakovať zároveň domácim za maximálne slušne a nekonfliktné prostredie a prístup. Zápas mal vysoké tempo a dobrý náboj. Ta druhá rovina je určitá pachuť, ktorá mi ostala po výkone rozhodcov. Vištuku výhru neberiem, my sme svoje šance nedali, Vištuk vyťažil z minima maximum, no na výkon rozhodcov nech si každý urobí svoj názor. Jedna prehra nás však naučí viac ako séria predchádzajúcich výhier. O týždeň máme ešte Bratislavský pohár, ďalšie derby s Pezinkom, beriem to skôr ako spestrenie a pekne ukončenie jesene. Ešte raz gratulujem domácim k výhre, nič sa však nedeje, zimovať budeme prví.“\r\n\r\nFoto zo zápasu: Dominika Jurčovičová 	1	2	post-19	2	f	0	\N
62	Ďakujeme spoločnosti CNS EuroGrants	2020-04-23 09:53:00+02	Ďakujeme spoločnosti CNS EuroGrants za pomoc pri získaní finančného príspevku vo výške 11 000 EUR z dotačnej schémy Slovenského futbalového zväzu. Spoločnosť <a href="https://cns-e.eu/" target="_blank">CNS EuroGrants</a> poskytuje poradenské a konzultačné služby v oblasti čerpania nenávratnej finančnej pomoci pre oblasť súkromného aj verejného sektora. \r\n\r\n<b>kkkk</b>	1	1	post-62	0	f	0	\N
7	Športovec roka 2021	2023-04-20 10:16:57.03803+02	\r\n\r\nAj tento rok mesto Modra spustilo súťaž o športovca mesta Modra za rok 2021. Mesto túto súťaž organizuje už niekoľko rokov a zapájajú sa do nej všetky športové kluby a ich členovia pôsobiace na území mesta. Náš futbalový klub do hlasovania prihlásil jednotlivcov aj družstvo žiakov U15. Hlasuje sa na web stránke mesta, hlasovanie trvá do 8.5.2022.\r\n\r\nOdkaz na web stránku : https://www.modra.sk/vismo/formulare2.asp?id_f=58 .\r\n\r\nV zozname nájdete takéto zastúpenie FC Slovan Modra.\r\n\r\nDenisa Michaela Kintlera – talentovaného mladého chlapca z Modry, medzi jeho dosiahnuté úspechu patrí 1. miesto BFZ Prípravka PK 2018/2019 hráč a kapitán prípravky, 1. miesto BFZ MZ 2019/2020 hráč a strelec rozhodujúceho gólu vo finále súťaže.\r\n\r\nFC Slovan Modra U15 – našu šikovnú mládež, ktorá už dva roky reprezentuje klub a mesto a drží sa v popredných miestach tabuľky 2.ligy BFZ. Spolu hrajú a trénujú už takmer 7 rokov. Trénerom U15 je náš nadaný hráč Ján Vislocký, ktorý vedie chlapcov tak aby boli na ihrisku úspešný.\r\n\r\nFrantiška Dolutovského – kapitána FC Slovan Modra, ktorý je vytrvalý športovec a reprezentuje náš klub a mesto na ihrisku aj mimo neho. František má výborný zmysel pre fair – play. V 2. lige  BFZ nastavil trend, ktorý nasmerováva sa prináša úspechy budúcich rokov v mládežníckych kategóriach.\r\n\r\nAk dáte hlas komukoľvek z tabuľky budeme Vám vďačný, keďže každý jeden hráč a každé jedno mužstvo klubu je pre nás nesmierne dôležité.\r\n	1	1	post-7	0	f	0	\N
22	O pohár BFZ sme prehrali s PŠC Pezinok až na penalty	2023-04-20 10:30:00+02	V prvom kole o pohár BFZ sme prehrali až na pokutové kopy so štvrtoligovým PŠC Pezinok.\r\n\r\nFC Slovan Modra vs. PŠC Pezinok 2:3 (pokutové kopy)\r\nGóly: 85' Sališ, ŽK: 16' Pavúk, 31' Kovár\r\nFCSM: Nemčovič - Kubín, Vislocký, Ayodjii, Plach – Kovár - Pavúk (C), Araque, Peško – Tichý (79' Sališ), Ruberth. Viac nájdete tu\r\nHlasy po zápase:\r\nAndrej Janotka (asistent trénera): „Zápas sme brali ako rozlúčku s jesennou časťou, chceli sme dať priestor hráčom z lavičky a dorastencom. V základe nastúpili až 4 dorastenci, brankár Nemčovič si odbil premiéru v drese nášho áčka vo veku 16 rokov, ďalší traja hráči Kovár, Peško a Tichý sú vo veku 17 rokov už "ostrieľaní áčkari". Od začiatku sme boli lepším mužstvom, hostia hrozili výnimočne a to z rohových kopov, my sme v prvom polčase nepremenili 3 tutovky, postupne Tichý netrafil loptu z päťky, Pavúk vo vyloženej šanci trafil brankára a nakoniec Ruberth po krásnom sóle kedy obišiel aj brankára sa pri zakončení do prázdnej brány pošmykol. Druhý polčas bol opatrnejší, na posledných 10 minút som vytiahol žolíka - trénera na ihrisko a ten okamžite skóroval. Bohužiaľ sme v 90. minúte inkasovali gól čo sa nemôže stávať. Následne penalty boli už len lotéria.“\r\n\r\nNorbert Sališ (tréner a hráč): „Pred peknou diváckou kulisou sme ukázali, že aj hráči z druhého sledu majú svoju kvalitu a často sú práve oni rozdielom vo výsledkoch, keďže jedným z faktorov úspechu v dlhodobej súťaži je aj kvalita lavičky. U súpera som vnímal náznaky herných automatizmov, ktoré sú zrejme rukopisom nového trénera, avšak individuálna hráčska kvalita bola jasne na našej strane. Divácky bol zápas atraktívny, derby ma vždy svoj náboj, škoda nepremenených šancí v prvom polčase ale určite aj inkasovaného gólu na 2:2 v 90.minúte. To sa jednoducho nesmie stávať. Ja som nastúpil po "hecovaní" asistenta Janotku, ktorý veril, že môžem zápas rozhodnúť. Zdravotne momentálne neviem na čom som, čaká ma ešte kontrolná magnetická rezonancia, mal som veľký úlomok kosti v kolene. Futbal mám absolútne zakázaný, no riskli sme to. Vytiahli sme mercedes z garáže, aj keď má defekt, stále je to mercedes. O to viac ma mrzí, že po mojom peknom góle sme to nedotiahli do víťazného konca a inkasovali sme v 90. minúte na 2:2.“ 	1	2	post-22	20	f	0	\N
11	Tak sme majstri, no a čo	2023-04-20 10:21:41.195984+02	Milí naši fanúšikovia a podporovatelia, sobota 11.6. sa zapísala do povedomia ľudí, ktorí s nami zdieľali moment víťazstva v V. lige. Vieme, že bez Vašej podpory na tribúnach a mimo nich by sa nám touto cestou k víťazstvu kráčalo o niečo horšie, predsa len nás to viac baví keď Vás je počuť. Veríme, že program a sprievodné akcie ste si užili a vidíme sa na ďalších oslavách, čo poviete? Prehľad sobotňajšieho zápasu FC Slovan Modra 6:0 OFK Vysoká pri Morave Góly posledného zápasu majú na konte Slavomír Podubinský (23', 57', 74') , Martin Lehocký (48'), Norbert Sališ (51'), Michal Habai (85'). 	1	2	post-11	0	f	0	\N
12	Tak sme majstri, no a čo	2023-04-20 10:21:42.082175+02	Milí naši fanúšikovia a podporovatelia, sobota 11.6. sa zapísala do povedomia ľudí, ktorí s nami zdieľali moment víťazstva v V. lige. Vieme, že bez Vašej podpory na tribúnach a mimo nich by sa nám touto cestou k víťazstvu kráčalo o niečo horšie, predsa len nás to viac baví keď Vás je počuť. Veríme, že program a sprievodné akcie ste si užili a vidíme sa na ďalších oslavách, čo poviete? Prehľad sobotňajšieho zápasu FC Slovan Modra 6:0 OFK Vysoká pri Morave Góly posledného zápasu majú na konte Slavomír Podubinský (23', 57', 74') , Martin Lehocký (48'), Norbert Sališ (51'), Michal Habai (85'). 	1	2	post-12	0	f	0	\N
13	Tak sme majstri, no a čo	2023-04-20 10:21:54.987294+02	Milí naši fanúšikovia a podporovatelia, sobota 11.6. sa zapísala do povedomia ľudí, ktorí s nami zdieľali moment víťazstva v V. lige. Vieme, že bez Vašej podpory na tribúnach a mimo nich by sa nám touto cestou k víťazstvu kráčalo o niečo horšie, predsa len nás to viac baví keď Vás je počuť. Veríme, že program a sprievodné akcie ste si užili a vidíme sa na ďalších oslavách, čo poviete? Prehľad sobotňajšieho zápasu FC Slovan Modra 6:0 OFK Vysoká pri Morave Góly posledného zápasu majú na konte Slavomír Podubinský (23', 57', 74') , Martin Lehocký (48'), Norbert Sališ (51'), Michal Habai (85'). 	1	2	post-13	0	f	0	\N
14	Po festivale zahodených šancí vezieme domov predsa všetky body	2023-04-20 10:23:11.064893+02	Ďakujeme fanúšikom za podporu, ktorí prišli do Vajnôr v hojnom počte.\r\n\r\nFK Vajnory vs. FC Slovan Modra 0:1 (0:0).\r\nGól: 82' Pavúk. Zostava FCSM: Lörincz - Dolutovský, Vojtovič, Ayodeji, Lehocký - Araque - Haniš (70' Vislocký), Pavúk, Kovár (61' Peško), Quejada - Aguem (87' Kubín).\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „Ako som avizoval, prišlo k rotácii v zostave, máme široký káder. Lehocký po dlhšej dobe a problémoch s chrbtom nastúpil od začiatku a ako sme boli zvyknutí, podal veľmi spoľahlivý výkon. Taktiež Kovár začal od začiatku a nesklamal, Peško ako žolík opäť bavil divákov. Dnes sme vsak zlyhali v efektivite, Yvan nepremenil 3 tutovky, raz ho zastavil pri dorážke do prázdnej brány obranca nedovolene, ale penalta udelená nebola. Nakoniec nás spasil Pavúkov priamy kop, ktorý je rozdielový vo všetkých aspektoch. Je aj na mne, aby som z tohto mužstva vyťažil čo najviac. Každopádne, sme nováčik, dávame priestor 17-ročným odchovancom a hráme najatraktívnejší futbal v súťaži. Aj o týždeň sľubujem dobrý futbal."\r\n\r\nMartin Kovár, záložník: "Z môjho pohľadu sme boli jednoznačne lepším mužstvom. V prvom polčase sme si vytvorili množstvo šancí, ale zakončenie zlyhalo. V druhom polčase sme ďalej vytvárali na súpera tlak, ktorý sme pretavili víťazným gólom Kuba Pavúka z 83. minúty. Trojbodový cieľ sme si splnili a chceme sa poďakovať fanúšikom za neúnavnú podporu počas celého zápasu." 	1	2	post-14	0	f	0	\N
65	Nový fan shop	2023-04-09 05:07:47+02	Milí naši fanúšikovia, chceme Vám dať do pozornosti, že sa nám zmenil sprostredkovateľ fanshopu.\r\nNa konci článku nájdete odkaz na stránku FANZONE a po kliknutí Vás presmeruje do obchodu.\r\nObjednávanie je priamo cez ich stránku a nie cez náš klub ako doteraz. Veríme, že sa Vám bude nový\r\nsortiment páčiť. Nám sa páči:) V sobotu 11. 6., na akcii k ukončeniu sezóny a oslavám titulu (chýba nám už len krok), si môžete veci zakúpiť aj v stánku\r\nfanshopu, ktorý bude umiestnený pri vstupnej bráne. \r\n\r\n<a href="https://fanzone.sk/kategoria-produktu/futbal/fc-slovan-modra/" target="_blank">www.fanzone.sk</a>	1	1	post-65	0	f	0	\N
64	Športovec roka 2021	2023-04-01 05:03:37+02	Aj tento rok mesto Modra spustilo súťaž o športovca mesta Modra za rok 2021. Mesto túto súťaž organizuje už niekoľko rokov a zapájajú sa do nej všetky športové kluby a ich členovia pôsobiace na území mesta. Náš futbalový klub do hlasovania prihlásil jednotlivcov aj družstvo žiakov U15. Hlasuje sa na web stránke mesta, hlasovanie trvá do 8.5.2022.\r\n\r\nOdkaz na web stránku <a href="https://www.modra.sk/vismo/formulare2.asp?id_f=58">www.modra.sk</a>.\r\n\r\nV zozname nájdete takéto zastúpenie FC Slovan Modra.\r\n\r\nDenisa Michaela Kintlera – talentovaného mladého chlapca z Modry, medzi jeho dosiahnuté úspechu patrí 1. miesto BFZ Prípravka PK 2018/2019 hráč a kapitán prípravky, 1. miesto BFZ MZ 2019/2020 hráč a strelec rozhodujúceho gólu vo finále súťaže.\r\n\r\nFC Slovan Modra U15 – našu šikovnú mládež, ktorá už dva roky reprezentuje klub a mesto a drží sa v popredných miestach tabuľky 2.ligy BFZ. Spolu hrajú a trénujú už takmer 7 rokov. Trénerom U15 je náš nadaný hráč Ján Vislocký, ktorý vedie chlapcov tak aby boli na ihrisku úspešný.\r\n\r\nFrantiška Dolutovského – kapitána FC Slovan Modra, ktorý je vytrvalý športovec a reprezentuje náš klub a mesto na ihrisku aj mimo neho. František má výborný zmysel pre fair – play. V 2. lige  BFZ nastavil trend, ktorý nasmerováva sa prináša úspechy budúcich rokov v mládežníckych kategóriach.\r\n\r\nAk dáte hlas komukoľvek z tabuľky budeme Vám vďačný, keďže každý jeden hráč a každé jedno mužstvo klubu je pre nás nesmierne dôležité.\r\n	1	1	post-64	0	f	0	\N
16	V Lamači sme potvrdili našu skvelú jesennú formu	2023-04-20 10:24:58.658145+02	\r\nNáš náskok na čele tabuľky sa zvýšil už na 6 bodov.\r\n\r\nFK Lamač vs. FC Slovan Modra 0:3 (0:0)\r\nGóly: 57’ Quejada, 89’ Kubín, 90’ Araque.\r\nFCSM: Lörincz - Dolutovský, Vojtovič, Ayodeji, Lehocký - Pavúk, Dvorák (84’ Plach), Araque - Vislocký (73’ Haniš), Aguem (87’ Kubín), Quejada. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „V Lamači sme skúšali novú hernú variantu, ktorú hráči zvládli výborne. Nevyhli sme sa strate koncentrácie v záveroch polčasov, ale výborne nás podržal brankár Lörincz. Nie je jednoduché vyhrávať zápas za zápasom, v tomto kalendárnom roku sme v lige neprehrali, verím že sa to odzrkadli vo všetkých aspektoch, počnúc fanúšikmi až po partnerov a samotne mesto. Máme pred sebou posledný domáci zápas v tomto roku, následne ideme na posledné kolo jesene na derby do Vištuku. Hlavne doma by som bol rád, aby prišlo čo najviac ľudí.“\r\n\r\nMartin Lehocký, hráč: „V daždivom počasí a na ťažšom teréne sme opäť podali dominantný výkon, avšak chýbala nám väčšia presnosť a kľud vo finálnej fáze. To sa nám mohlo aj vypomstiť, keď súper z ojedinelých šanci mal možnosť skórovať, ale výbornými zákrokmi sa predviedol Ľubo Lörincz. Zo súperovho ihriska si odnášame 3 body a veríme, že ich potvrdíme v najbližšom domácom zápase pred našimi skvelými fanúšikmi“ 	1	2	post-16	0	f	0	\N
24	Darujte 2% z daní	2023-04-20 10:33:00+02	Dobrý deň, touto cestou by som Vás všetkých priaznivcov nášho klubu FC Slovan Modra, požiadal o podporu a poukázanie 2% z daní nášmu OZ FC Slovan Modra. V prílohe Vám posielam tlačivo k vyplneniu a následne Vás požiadam, aby ste tlačivo a aj potvrdenie od zamestnávateľa doručili niektorému členovi VV FC Slovan Modra, počas tréningov/zápasov , alebo ho odovzdali svojmu trénerovi. Ďakujeme veľmi pekne, peniaze budú použité na mládežnícke mužstvá a pre naše detí. Tak isto by som Vás požiadal pokiaľ vlastníte firmu a podnikáte tak isto viete podporiť náš klub. No a v neposlednom rade ďakujem aj za šírenie a sharovanie na sociálnej sieti alebo v rámci vašej siete známych a vášho okolia.\r\n\r\nZa VV FC Slovan Modra Michal Kintler\r\n\r\n<a href="https://fcslovanmodra.sk/images/post/13/2_perc_SLOVAN_MODRA.pdf">>> Tu si stiahnite tlačivo <<</a>\r\n	1	1	post-24	7	f	0	\N
84	FCSM na nový mesiac	2025-01-01 01:01:00+01	Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.j	1	1	post-84	89	f	0	\N
20	V poslednom ligovom zápase jesennej časti sme prehrali	2023-04-20 10:28:00+02	V poslednom ligovom zápase jesennej časti sme prehrali na pôde Vištuku. Ďakujeme fanúšikom za podporu!\r\n\r\nTJ Slovan Vištuk vs. FC Slovan Modra 2:0 (0:0)\r\nČK: 66' Dvorák (Po 2. ŽK), 90' Aguem\r\nFCSM: Lörincz - Lehocký, Vojtovič, Ayodeji, Plach (76' Peško) - Pavúk, Dvorák, Araque - Quejada, Aguem (76' Kovár), Vislocký. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „Zápas vnímam v dvoch rovinách, nakoľko išlo o derby a my sme boli jediné neporazené mužstvo v lige, už niekoľko kôl sa na nás každý super chystal a chcel vytiahnuť. Kvôli naším fanúšikom, ktorí boli aj v tomto zápase skvelí ma mrzí, že prehra prišla práve vo Vištuku. Domáci však boli veľmi nepríjemným súperom, hrali jednoducho, no veľmi poctivo a oduševnene. Nám trošku chýbala emócia, čo beriem na seba, pretože Vištuk nepovažujem za konkurenciu v boji o postup a preto som aj mužstvo nabádal že ide o bežný zápas a netreba sa nechať strhnúť a vyprovokovať. Z tohto pohľadu chcem pochváliť a poďakovať zároveň domácim za maximálne slušne a nekonfliktné prostredie a prístup. Zápas mal vysoké tempo a dobrý náboj. Ta druhá rovina je určitá pachuť, ktorá mi ostala po výkone rozhodcov. Vištuku výhru neberiem, my sme svoje šance nedali, Vištuk vyťažil z minima maximum, no na výkon rozhodcov nech si každý urobí svoj názor. Jedna prehra nás však naučí viac ako séria predchádzajúcich výhier. O týždeň máme ešte Bratislavský pohár, ďalšie derby s Pezinkom, beriem to skôr ako spestrenie a pekne ukončenie jesene. Ešte raz gratulujem domácim k výhre, nič sa však nedeje, zimovať budeme prví.“\r\n\r\nFoto zo zápasu: Dominika Jurčovičová 	1	2	post-20	2	f	0	\N
15	Po výbornom výkone sme porazili Karlovu Ves rozdielom triedy	2023-04-20 10:24:11.789108+02	V zápase excelovali 17-roční odchovanci: David Peško strelil 2 góly a Martin Kovár si pripísal 3 asistencie.\r\n\r\nFC Slovan Modra vs. FKM Karlova Ves 4:1 (2:0)\r\nGóly: 32’ Aguem, 39’ Quejada, 69’ a 82’ Peško FCSM: Lörincz - Dolutovský, Lehocký, Ayodeji, Dvorák - Pavúk, Araque, Kovár (74’ Sališ) - Quejada (83’ Kubín), Aguem (57’ Peško), Vislocký. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: "Jeden z lepších výkonov proti súperovi, ktorý si myslel, že môže u nás hrať otvorenú partiu. S týmto scenárom som ale počítal, pretože Karlova Ves hra počas sezóny uvoľnene, bez tlaku, chcú hrať svoju hru, bez ohľadu na výsledky, a práve to im prináša vysoké výhry. Nám vyhovoval aj dážď, čo logicky napomáha útočiacemu mužstvu. Plán bol rozhodnúť do polčasu, čo by sa aj naplnilo, ak by sme premenili penaltu. Udivuje ma však množstvo hráčov v tejto súťaži, vrátane niektorých našich, ktorí sa do dažďa nevedia obuť. Celkovo bol náš výkon veľmi solídny, objavovalo sa viacero prvkov prenesených z tréningu, niektoré ukážkové akcie a aj keď nám chýbali niektorí hráči, všetci sa chytili šance. Opäť sme splnili sľub, keď som pred týždňom sľuboval dobrý zápas."\r\n\r\nDávid Peško, autor dvoch gólov: "V prvom rade by som chcel poďakovať divákom za to, že aj v nepriaznivom počasí si našli čas a došli nás podporiť. Z môjho pohľadu atraktívny zápas, v ktorom sme opäť trávili väčšinu času na súperovej polke. Mohlo byť rozhodnuté už v prvom polčase, no nepremenili sme šance a ani pokutový kop. V druhom polčase super znížil, no myslím si, že nás to nijak nerozhodilo, hrali sme stále svoju hru a naša aktivita bola odmenená dvoma ďalšími gólmi a bolo rozhodnuté. Ostávame naďalej bez prehry a ideme na plno ďalej." 	1	2	post-15	1	f	0	\N
21	V poslednom ligovom zápase jesennej časti sme prehrali	2023-04-20 10:29:00+02	V poslednom ligovom zápase jesennej časti sme prehrali na pôde Vištuku. Ďakujeme fanúšikom za podporu!\r\n\r\nTJ Slovan Vištuk vs. FC Slovan Modra 2:0 (0:0)\r\nČK: 66' Dvorák (Po 2. ŽK), 90' Aguem\r\nFCSM: Lörincz - Lehocký, Vojtovič, Ayodeji, Plach (76' Peško) - Pavúk, Dvorák, Araque - Quejada, Aguem (76' Kovár), Vislocký. Viac nájdete tu\r\nHlasy po zápase:\r\nNorbert Sališ, tréner: „Zápas vnímam v dvoch rovinách, nakoľko išlo o derby a my sme boli jediné neporazené mužstvo v lige, už niekoľko kôl sa na nás každý super chystal a chcel vytiahnuť. Kvôli naším fanúšikom, ktorí boli aj v tomto zápase skvelí ma mrzí, že prehra prišla práve vo Vištuku. Domáci však boli veľmi nepríjemným súperom, hrali jednoducho, no veľmi poctivo a oduševnene. Nám trošku chýbala emócia, čo beriem na seba, pretože Vištuk nepovažujem za konkurenciu v boji o postup a preto som aj mužstvo nabádal že ide o bežný zápas a netreba sa nechať strhnúť a vyprovokovať. Z tohto pohľadu chcem pochváliť a poďakovať zároveň domácim za maximálne slušne a nekonfliktné prostredie a prístup. Zápas mal vysoké tempo a dobrý náboj. Ta druhá rovina je určitá pachuť, ktorá mi ostala po výkone rozhodcov. Vištuku výhru neberiem, my sme svoje šance nedali, Vištuk vyťažil z minima maximum, no na výkon rozhodcov nech si každý urobí svoj názor. Jedna prehra nás však naučí viac ako séria predchádzajúcich výhier. O týždeň máme ešte Bratislavský pohár, ďalšie derby s Pezinkom, beriem to skôr ako spestrenie a pekne ukončenie jesene. Ešte raz gratulujem domácim k výhre, nič sa však nedeje, zimovať budeme prví.“\r\n\r\nFoto zo zápasu: Dominika Jurčovičová 	1	2	post-21	18	f	0	\N
\.


--
-- Data for Name: post_gallery; Type: TABLE DATA; Schema: public; Owner: fuma_user
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
90		933036c842294fdeb396ef5583b49cbf_tricko-sipkaren.webp	0	20
104		d1b6ef47d7004f66badb62540d972cf9_610a609f661b486881bc04ee28cdf291_68410e495ca39e6b8af76b53_e3a59815-3966-449e-8e52-8bca91d4b6f8.webp	4	84
105		e4377047e8524d288e5b9a966328c086_67a26c9c229ed5f715f79762_475119095_18044824346253929_6053121050512387495_n.webp	5	84
85		c44ea999ff2d49a3a185987e6f82d8a9_link4.jpg	2	84
86		2fa9cf8ba69d40b1872548caf112f6aa_660ad3b2c3b0437f97f1d62dabe9bcd4_astrobotic-peregrine-pyld-ps-10_2.jpg	3	84
88		9bb0defbaa404b4ab2fb96907ba303c1_e3844e9804204088b4674bdedaf40d45_slide11.jpg	1	84
100		8fed08259aec43cb8b7c29e36d0fa0da_66d6d971fb673f142012ef49_68410bc6617e7ac784c6995a_c5fe08ca-7270-4a84-844a-6367c5035dec-transcode.mp4	0	84
\.


--
-- Data for Name: product; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.product (id, title, date_posted, content, user_id, is_visible, price, old_price, product_category_id, youtube_link, stripe_link) FROM stdin;
17	pok	2025-11-06 15:53:33.187034	pokpok	1	f	25.00	6.00	1	kk	k
20	Champions T-Shirt	2025-12-12 19:04:55.25234	Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.\r\n\r\n	1	t	15.00	15.00	1		price_1Rt3NBKr9xveA3fnIv79kh3m
21	Zápas FC Slovan Modra vs. FC Húpacie Koníkyj	2025-12-12 21:10:49.206153	It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many	1	t	22.00	22.00	2	g-GslMly3ho	price_1Rt3NBKr9xveA3fnIv79kh3m
19	Best Paradise	2025-11-06 17:00:51.368492	The "Best Paradise" is subjective, but travelers often name tropical islands like Fiji, Seychelles, Palawan (Philippines), Boracay (Philippines), and St. Lucia as top contenders for stunning beaches, clear waters, marine life, and relaxation. 	1	t	20.00	6.00	1		hh
18	pok	2025-11-06 15:53:58.72836	pokpok	1	t	25.00	6.00	3		ooo
16	iou	2025-11-04 15:00:23.998235	oiu oiu 	1	t	2.00	2.00	2	g-GslMly3ho	iu
\.


--
-- Data for Name: product_category; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.product_category (id, name) FROM stdin;
1	Merch
2	Live Stream
3	Členský poplatok
4	Tréningy U9
\.


--
-- Data for Name: product_gallery; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.product_gallery (id, title, image_file2, orderz, product_id) FROM stdin;
26		7f1a6c48d871420db679afcb7030afd8_background-cv.png	0	19
29		ba1672dfa53946af9c0229748dcaebfa_660ad3b2c3b0437f97f1d62dabe9bcd4_astrobotic-peregrine-pyld-ps-10_2.jpg	0	18
30		b64c425a4c3e43fbaa6dfdf10090f4cb_background_cv.png	3	19
31		c8033416aa5b423aabf46fd2f74f938c_aplikacie-webstranky_grafika.jpg	3	19
34		a9e8fade31114347b707eeed36bad410_e03ce17578674b19b1eac017a03bb330_230305132751-02-liverpool-manchester-united-0305.jpg	0	16
35		517cf7664f984ca1adde840949f843be_e3844e9804204088b4674bdedaf40d45_slide11.jpg	0	21
37		7e32a7ec2f374ebb9e2f5b3033c5e25e_tricko-champions-modre.jpg	0	20
41		896a438c3d984dc58f20015520d7465c_20230430_181404.webp	3	19
42		48f2d039183e4e54b082bef818b5717f_7b7a15a18a9c401e98c9f5b5341267d6_tricko-sipkaren.webp	0	17
\.


--
-- Data for Name: product_variant; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.product_variant (id, name, type) FROM stdin;
5	Size	2
6	Color	2
\.


--
-- Data for Name: product_variant_product; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.product_variant_product (product_variant_id, product_id) FROM stdin;
\.


--
-- Data for Name: push_token; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.push_token (id, user_id, token, platform, device, last_seen_at) FROM stdin;
26	1	chFfwqfrRJ0raq0ACFwmhM:APA91bEHLbB4mhdkxBJ9kt_lScY4ble2vIK8H2wAFxrsZdZXZJux73YBDE0IhWRj75lsq9L_gI3P6vMfvTS_8C9GzWG8Ai6_y04WDEsd6iy5TjBfhqfgksI	web	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	2025-12-19 12:30:37.712897+01
35	1	efBA7JBdINRlAL3B57hmac:APA91bFBxvRZF571CVHh7s758dv8xeHS5aPWj3LQhmWobA3sOOjkYUD-wRfRdr0vZaMeTPM473xOoZCuK-2JrwjyQOwTNrVtBmw3LV8YqFPzE2QFZUIBeDM	web	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0	2025-12-22 21:36:07.218237+01
36	1	dkIW2qn0gl6VggGVFYyjib:APA91bFEIieH-gziTCnBr2_ObtCQeIyfUkHspY2otui-UfKdDyu448VZQhpb8ESrKf99B0pkCkKQ-R85ftLbmi5P8-Nq-KBOUq37PdhT7nJziJoJ2NtXRa4	web	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0	2025-12-22 21:37:13.967254+01
38	1	es6UTkAyq0Kex4YhQ9evhG:APA91bHeUodtI6TaTldMm-iFVLcRkQDir3eMFa0EjnVvPLw-wUdDGXEgv4eKOCf7Sy5EAAU_pYQZTpu9t-RAWq46W3Xo1l6ZGWHLCR6UKJ4xzxP1vls4xm4	web	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0	2025-12-26 11:56:10.655989+01
39	1	d4DF8bLZ-H1QztzGmKTu8l:APA91bFovsnr4QVndnRklP5rq365W3eGT1cH7L4G0UunMshR7m0HgkMn_x5OS2WJemyBqasEvF6BVIhxNxN891_yqzK5mHahHr0S-jDqjXGWNp7Ha7Svc6s	web	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0	2025-12-26 17:56:55.923841+01
40	1	chFfwqfrRJ0raq0ACFwmhM:APA91bG40MJ_y07OwEQOVoPOFnrDOs8QpNCweYK5wGw1RJXNyIaqAlnNVTdRDqXE9s-gOyYH7czdVysPdBLFvxcJ9TcRM5RhLmUhnYtzeiHoVbKgUtjyAF4	web	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	2025-12-26 19:52:19.752018+01
41	1	cO8Jk0r98apyGIfgEyx5El:APA91bHumLRvb9sg1NgaZe3fv8mnzVCfGcjHp0ygseker0GlZsuoeoIFBAaG7FQb2dVfCXlo_tQCOuo93_rr3dz995FvoVha7rUtntpLq0EF6WdArEStIx8	web	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0	2026-01-02 20:33:59.536618+01
42	1	cO8Jk0r98apyGIfgEyx5El:APA91bGKRSOtsJqTZZqDMEYNeOrNYwLegZQmQtnq5xLHORvQV1ms6zY9tqokxY6Z0Y7-uf5zSQf4oL7tqxX3TWpyJZn06jh59OCxYwy-gkS1rliR3ll9Ulo	web	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0	2026-01-03 12:39:01.721747+01
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.role (id, name, description) FROM stdin;
1	Admin	poiiii
2	WebAdmin	poipoi
3	Coach	\N
4	Player	
5	Parent	\N
\.


--
-- Data for Name: roles_users; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.roles_users (user_id, role_id) FROM stdin;
1	1
1	2
6	4
4	3
22	4
3	4
18	3
\.


--
-- Data for Name: score_table; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.score_table (id, club, games, wins, draws, loses, score, points, team_id, logo) FROM stdin;
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
-- Data for Name: sponsors; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.sponsors (id, name, url, kind, image_file, orderz, created_at, describe) FROM stdin;
8		https://appdesign.sk	partner	60a140d455284a0581261577d8f90a8e_app_logo.jpg	2	2025-12-10 17:18:12.569668	
2	Atops	https://www.atops.sk/	main	22a72b46742e47bdb19960b0cc865c2f_6899787f88ce49524333717a_527342095_18062660111253929_4574921588219728515_n.jpg	0	2025-12-08 16:08:15.586614	
4		https://modra.sk	partner	21865833a7b047cca4aa42826802bbf1_6899787f1b78152212dea850_527318661_1319202123547717_4382761230831107370_n.jpg	1	2025-12-08 17:53:50.062062	
5			partner	86a1a293ca8942c4a2622a83355c7cbe_68de6cd45a1e3c74ca1d15e5_fadfasdf.jpg	0	2025-12-08 17:53:57.447142	
\.


--
-- Data for Name: talk_message; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.talk_message (id, room_id, user_id, text, created_at, msg_type, payload_json, attachment_url, attachment_mime, attachment_size) FROM stdin;
1	2	1	kkkkkkk	2025-12-14 17:33:18.161256+01	text	\N	\N	\N	\N
2	2	1	hjbjhjbhjhb	2025-12-14 17:33:23.584586+01	text	\N	\N	\N	\N
3	2	1	6544586áýžáýžáýž	2025-12-14 17:33:44.041306+01	text	\N	\N	\N	\N
4	2	1	lklklk	2025-12-14 17:34:38.256219+01	text	\N	\N	\N	\N
5	2	1	poi poip oi	2025-12-14 17:42:16.730564+01	text	\N	\N	\N	\N
6	2	1	asdjf OSIJF OISDFJ	2025-12-14 17:46:14.854468+01	text	\N	\N	\N	\N
7	2	1	LKNALSNALKNAS	2025-12-14 17:46:17.03866+01	text	\N	\N	\N	\N
8	2	1	oiuoiuoiu	2025-12-14 17:47:08.052166+01	text	\N	\N	\N	\N
9	2	1	oiuoiuiou	2025-12-14 17:47:10.536589+01	text	\N	\N	\N	\N
10	2	1	zxc\\zc\\zc\\zc	2025-12-14 17:47:12.356827+01	text	\N	\N	\N	\N
11	2	1	\\z\\zc\\c\\zc	2025-12-14 17:47:13.498527+01	text	\N	\N	\N	\N
12	2	1	\\z\\zc\\c\\	2025-12-14 17:47:14.5104+01	text	\N	\N	\N	\N
13	2	1	zc\\	2025-12-14 17:47:14.732364+01	text	\N	\N	\N	\N
14	2	1	zc\\zc	2025-12-14 17:47:15.233801+01	text	\N	\N	\N	\N
15	2	1	\\	2025-12-14 17:47:15.408151+01	text	\N	\N	\N	\N
16	2	1	c\\	2025-12-14 17:47:15.560535+01	text	\N	\N	\N	\N
17	2	1	c	2025-12-14 17:47:15.733478+01	text	\N	\N	\N	\N
18	2	1	\\z	2025-12-14 17:47:15.8637+01	text	\N	\N	\N	\N
19	2	1	c\\z	2025-12-14 17:47:16.162614+01	text	\N	\N	\N	\N
20	2	1	c\\z	2025-12-14 17:47:16.376421+01	text	\N	\N	\N	\N
21	2	1	c	2025-12-14 17:47:16.489502+01	text	\N	\N	\N	\N
22	2	1	\\z	2025-12-14 17:47:16.653546+01	text	\N	\N	\N	\N
23	2	1	c	2025-12-14 17:47:16.811999+01	text	\N	\N	\N	\N
24	2	1	\\c	2025-12-14 17:47:16.952729+01	text	\N	\N	\N	\N
25	2	1	z	2025-12-14 17:47:17.112174+01	text	\N	\N	\N	\N
26	2	1	c	2025-12-14 17:47:17.264945+01	text	\N	\N	\N	\N
27	2	1	zc	2025-12-14 17:47:17.44174+01	text	\N	\N	\N	\N
28	2	1	\\z	2025-12-14 17:47:17.592969+01	text	\N	\N	\N	\N
29	2	1	c\\	2025-12-14 17:47:17.750867+01	text	\N	\N	\N	\N
30	2	1	zc	2025-12-14 17:47:17.907177+01	text	\N	\N	\N	\N
31	2	1	\\	2025-12-14 17:47:18.063357+01	text	\N	\N	\N	\N
32	2	1	c\\	2025-12-14 17:47:18.208045+01	text	\N	\N	\N	\N
33	2	1	zc	2025-12-14 17:47:18.362925+01	text	\N	\N	\N	\N
34	2	1	\\zc	2025-12-14 17:47:18.531136+01	text	\N	\N	\N	\N
35	2	1	\\	2025-12-14 17:47:18.676032+01	text	\N	\N	\N	\N
36	2	1	zc\\z	2025-12-14 17:47:18.801993+01	text	\N	\N	\N	\N
37	2	1	ijojioij	2025-12-14 20:29:28.150036+01	text	\N	\N	\N	\N
38	3	1	oiuoiuiou	2025-12-14 20:47:01.325395+01	text	\N	\N	\N	\N
39	2	1	uoiuoiuoiu	2025-12-14 21:04:09.139094+01	text	\N	\N	\N	\N
40	3	1	oiuoiuiu	2025-12-14 21:04:39.811616+01	text	\N	\N	\N	\N
41	3	1	uuuuu	2025-12-14 21:05:13.094434+01	text	\N	\N	\N	\N
42	3	1	pojpoj	2025-12-14 21:13:06.925549+01	text	\N	\N	\N	\N
43	3	1	ppoipoiopi	2025-12-14 21:15:23.972854+01	text	\N	\N	\N	\N
44	2	1	oiuoioiu	2025-12-14 21:18:21.059555+01	text	\N	\N	\N	\N
45	2	1	iiiii	2025-12-14 21:18:26.95719+01	text	\N	\N	\N	\N
46	2	1	aaaaaaaaaaaaaaa	2025-12-14 21:18:32.347139+01	text	\N	\N	\N	\N
47	2	3	lkjkjlkj	2025-12-14 21:20:07.570939+01	text	\N	\N	\N	\N
48	2	3	lkjlkjlkj	2025-12-14 21:20:31.953947+01	text	\N	\N	\N	\N
49	3	1	kjkj	2025-12-14 21:20:41.155405+01	text	\N	\N	\N	\N
50	2	3	lkjlkjlj	2025-12-14 21:21:02.389759+01	text	\N	\N	\N	\N
51	3	1	jkpo pjpojpo jopj	2025-12-14 21:22:33.298721+01	text	\N	\N	\N	\N
52	2	1	pojpjpoj	2025-12-14 22:39:15.948252+01	text	\N	\N	\N	\N
53	2	1	hihiuhiuh	2025-12-14 22:39:51.85229+01	text	\N	\N	\N	\N
54	2	3	pokpokpok	2025-12-14 22:40:30.007462+01	text	\N	\N	\N	\N
55	2	3	pokpokpok	2025-12-14 22:40:38.50799+01	text	\N	\N	\N	\N
56	2	3	pokpokpok	2025-12-14 22:40:43.815729+01	text	\N	\N	\N	\N
57	2	1	pokpkpok	2025-12-14 22:55:49.518459+01	text	\N	\N	\N	\N
58	2	1	pojpoj	2025-12-14 23:16:19.349014+01	text	\N	\N	\N	\N
59	2	1	pjpojpjpoj	2025-12-15 06:56:16.437449+01	text	\N	\N	\N	\N
60	2	1	ojpjpojpojo	2025-12-15 06:56:23.573254+01	text	\N	\N	\N	\N
61	2	1	jjjjjjjjjjjjjjjjjjjjjjj	2025-12-15 06:56:26.807916+01	text	\N	\N	\N	\N
62	2	1	jjjjjjjjjjjjjjjj	2025-12-15 06:56:30.166069+01	text	\N	\N	\N	\N
63	2	1	oiuouoiuoiu	2025-12-15 06:59:32.26908+01	text	\N	\N	\N	\N
64	2	1	oiuoioiu	2025-12-15 06:59:39.491479+01	text	\N	\N	\N	\N
65	2	1	po kpokopk pokpo	2025-12-15 07:05:24.590446+01	text	\N	\N	\N	\N
66	2	1	p[l[pl	2025-12-15 07:06:50.2396+01	text	\N	\N	\N	\N
67	2	1	ioj oij oij	2025-12-15 07:07:44.910754+01	text	\N	\N	\N	\N
68	2	1	pokpk pkpo po k	2025-12-15 08:19:40.522422+01	text	\N	\N	\N	\N
69	2	1	pokpokp okpo k	2025-12-15 08:19:50.459601+01	text	\N	\N	\N	\N
70	2	1	pokpkok	2025-12-15 08:19:57.481107+01	text	\N	\N	\N	\N
71	2	3	;lk;lk;lk	2025-12-15 08:21:03.262152+01	text	\N	\N	\N	\N
72	2	3	kl;k;lk	2025-12-15 08:21:12.293926+01	text	\N	\N	\N	\N
73	2	3	ioj ojo iji	2025-12-15 08:30:02.580106+01	text	\N	\N	\N	\N
74	2	3	oi joij oijioj oij	2025-12-15 08:30:07.780845+01	text	\N	\N	\N	\N
75	2	3	ijijoij oijoij oij oij	2025-12-15 08:30:13.55669+01	text	\N	\N	\N	\N
76	2	3	oijoij oij	2025-12-15 08:30:19.031323+01	text	\N	\N	\N	\N
77	2	1	oij oij oij oij oij oij  oij oij oij	2025-12-15 08:30:37.878774+01	text	\N	\N	\N	\N
78	2	1	oi joijioj ij iojj oij oij	2025-12-15 08:31:40.863529+01	text	\N	\N	\N	\N
79	2	1	900909i09i09i	2025-12-15 08:46:03.31495+01	text	\N	\N	\N	\N
80	2	1	oijoijoij	2025-12-15 08:47:16.541992+01	text	\N	\N	\N	\N
81	2	1	oij oij oij oij	2025-12-15 08:47:21.032832+01	text	\N	\N	\N	\N
82	2	1	pokpokpok	2025-12-15 08:53:59.32984+01	text	\N	\N	\N	\N
83	2	3	pok pk pok	2025-12-15 08:59:20.176906+01	text	\N	\N	\N	\N
84	2	3	oijh oij oij oij	2025-12-15 08:59:23.051146+01	text	\N	\N	\N	\N
85	2	3	hoihoihoih	2025-12-15 09:34:48.447024+01	text	\N	\N	\N	\N
86	2	1	oijoijoij	2025-12-15 10:11:31.414946+01	text	\N	\N	\N	\N
87	2	1	oijioj	2025-12-15 10:11:59.451728+01	text	\N	\N	\N	\N
88	2	3	iojoijoij	2025-12-15 10:22:38.670103+01	text	\N	\N	\N	\N
89	2	3	oijoijoij	2025-12-15 10:24:10.955121+01	text	\N	\N	\N	\N
90	2	1	pkpokpokpo	2025-12-15 10:24:20.652446+01	text	\N	\N	\N	\N
91	2	1	oijoijoi jo joij	2025-12-15 10:47:04.715728+01	text	\N	\N	\N	\N
92	2	1	oi ui oiu oiuiou	2025-12-15 10:58:05.892806+01	text	\N	\N	\N	\N
93	2	1	popopo	2025-12-15 10:58:56.544124+01	text	\N	\N	\N	\N
94	2	1	oi uoiu	2025-12-15 11:08:55.973379+01	text	\N	\N	\N	\N
95	2	1	oiu oiu i u	2025-12-15 11:09:08.196399+01	text	\N	\N	\N	\N
96	2	1	90u0u09u	2025-12-15 11:09:24.366743+01	text	\N	\N	\N	\N
97	2	1	9i900u09u09u09u09u	2025-12-15 11:09:28.677208+01	text	\N	\N	\N	\N
98	2	1	iuyiuy	2025-12-15 11:09:45.881048+01	text	\N	\N	\N	\N
99	2	1	iuyiuyiuyiuy	2025-12-15 11:09:57.817656+01	text	\N	\N	\N	\N
100	2	1	oijoijoij	2025-12-15 11:10:13.043368+01	text	\N	\N	\N	\N
101	2	1	oijoijoijioj oijoi joijoijoij	2025-12-15 11:10:55.440738+01	text	\N	\N	\N	\N
102	2	1	09un0 u09u09 u	2025-12-15 11:11:10.793266+01	text	\N	\N	\N	\N
103	2	1	oiuoi uoi uo u	2025-12-15 11:12:49.880806+01	text	\N	\N	\N	\N
104	2	1	jjpojo	2025-12-15 11:12:56.582911+01	text	\N	\N	\N	\N
105	2	1	09u09u09u	2025-12-15 11:19:02.826649+01	text	\N	\N	\N	\N
106	2	1	oijoijoij	2025-12-15 11:19:20.27136+01	text	\N	\N	\N	\N
107	2	1	oi oijij ioj	2025-12-15 11:19:29.416526+01	text	\N	\N	\N	\N
108	2	3	k[p k[k [p	2025-12-15 11:19:42.650131+01	text	\N	\N	\N	\N
109	2	3	[pk [p k[k[pk	2025-12-15 11:19:45.96181+01	text	\N	\N	\N	\N
110	2	1	oijojoij	2025-12-15 11:51:39.021923+01	text	\N	\N	\N	\N
111	3	1	hoihoihioh	2025-12-15 11:52:35.078417+01	text	\N	\N	\N	\N
112	2	3	jojoijoij	2025-12-15 11:57:43.772529+01	text	\N	\N	\N	\N
113	3	1	oijoijoij	2025-12-15 11:57:51.360243+01	text	\N	\N	\N	\N
114	3	1	jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj	2025-12-15 11:57:55.807663+01	text	\N	\N	\N	\N
115	2	1	jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj	2025-12-15 11:58:08.298221+01	text	\N	\N	\N	\N
116	2	1	loijijoij oij	2025-12-15 12:34:57.094838+01	text	\N	\N	\N	\N
117	2	3	joijoij oij	2025-12-15 15:08:31.561966+01	text	\N	\N	\N	\N
118	2	3	poi pipio	2025-12-15 15:10:47.725386+01	text	\N	\N	\N	\N
119	2	3	poipi pi	2025-12-15 15:10:51.829714+01	text	\N	\N	\N	\N
120	2	3	poi pipoi oi	2025-12-15 15:11:09.109146+01	text	\N	\N	\N	\N
121	2	3	jjjjj	2025-12-15 15:11:49.360962+01	text	\N	\N	\N	\N
122	2	1	i poipoipoi	2025-12-15 15:18:09.647048+01	text	\N	\N	\N	\N
123	2	3	oiu oiuoiu oiu	2025-12-15 15:51:19.668185+01	text	\N	\N	\N	\N
124	2	3	pop okpok	2025-12-15 16:00:05.345189+01	text	\N	\N	\N	\N
125	2	3	jo ijoijoij oij	2025-12-15 16:09:08.982931+01	text	\N	\N	\N	\N
126	2	3	oij oijoij o j	2025-12-15 16:09:22.494595+01	text	\N	\N	\N	\N
127	2	1	oij oij oij	2025-12-15 16:09:50.453773+01	text	\N	\N	\N	\N
128	2	1	oij oj oj	2025-12-15 16:10:04.06988+01	text	\N	\N	\N	\N
129	2	3	oi jij oij oij	2025-12-15 16:11:47.071818+01	text	\N	\N	\N	\N
130	2	1	oij oijoij	2025-12-15 16:11:53.048533+01	text	\N	\N	\N	\N
131	2	1	oij oij	2025-12-15 16:12:14.857023+01	text	\N	\N	\N	\N
132	2	3	oij oj oij	2025-12-15 16:12:18.871027+01	text	\N	\N	\N	\N
133	2	1	pok pok pokopk	2025-12-15 16:52:33.279645+01	text	\N	\N	\N	\N
134	3	1	pko pok	2025-12-15 16:52:47.408074+01	text	\N	\N	\N	\N
135	2	3	pok pokpo k	2025-12-15 16:53:16.967585+01	text	\N	\N	\N	\N
136	2	1	pok pokpo k	2025-12-15 16:53:22.393278+01	text	\N	\N	\N	\N
137	2	1	oijoij oij	2025-12-15 16:54:14.746047+01	text	\N	\N	\N	\N
138	2	1	oij oijoi joij	2025-12-15 16:54:17.909968+01	text	\N	\N	\N	\N
139	2	1	iiiiiiiiiiiiiiiiiiiiii	2025-12-15 16:54:20.424333+01	text	\N	\N	\N	\N
140	2	3	poi poipoi	2025-12-15 16:55:02.135762+01	text	\N	\N	\N	\N
141	2	1	poi poipoi	2025-12-15 16:55:15.366264+01	text	\N	\N	\N	\N
142	2	3	poi poipoi po i	2025-12-15 16:55:22.246611+01	text	\N	\N	\N	\N
143	2	1	poi poi po i	2025-12-15 16:55:43.191357+01	text	\N	\N	\N	\N
144	2	1	poip oipo i	2025-12-15 16:57:24.937203+01	text	\N	\N	\N	\N
145	2	3	poi poi	2025-12-15 16:57:39.001791+01	text	\N	\N	\N	\N
146	2	3	jjjjjjjjjjjjjjjjj	2025-12-15 16:57:45.261796+01	text	\N	\N	\N	\N
147	2	3	poipoipioipo	2025-12-15 19:56:31.537682+01	text	\N	\N	\N	\N
148	2	1	kjhkjhkjh	2025-12-15 19:57:18.225977+01	text	\N	\N	\N	\N
149	2	3	kjhkjhkjh	2025-12-15 19:57:33.00994+01	text	\N	\N	\N	\N
150	2	3	kjhkjhkjh	2025-12-15 19:57:41.340953+01	text	\N	\N	\N	\N
151	2	3	kjhkjhkjhjhkjkjhk	2025-12-15 19:57:45.301121+01	text	\N	\N	\N	\N
152	2	3	oioijoijoij	2025-12-15 19:57:49.892559+01	text	\N	\N	\N	\N
153	2	1	oijoijoijij	2025-12-15 19:57:53.786661+01	text	\N	\N	\N	\N
154	2	3	joijoij	2025-12-15 19:58:33.982416+01	text	\N	\N	\N	\N
155	2	1	oijoijoij	2025-12-15 19:58:52.218172+01	text	\N	\N	\N	\N
156	2	3	lklkjlkjlkjlkjlk	2025-12-15 20:03:03.24261+01	text	\N	\N	\N	\N
157	2	3	lkjlkj	2025-12-15 20:03:18.847913+01	text	\N	\N	\N	\N
158	2	3	kjhkjh	2025-12-15 20:03:35.908561+01	text	\N	\N	\N	\N
159	2	3	jjjjjjjjjjjjjjjjjjjjj	2025-12-15 20:03:41.433771+01	text	\N	\N	\N	\N
160	2	1	kjbkjbkjb	2025-12-15 20:03:59.89894+01	text	\N	\N	\N	\N
161	2	1	pojpj pojp oj	2025-12-15 20:09:08.468655+01	text	\N	\N	\N	\N
162	2	3	poj pojpjo	2025-12-15 20:09:39.995815+01	text	\N	\N	\N	\N
163	2	1	oijoijoij	2025-12-15 20:10:25.71488+01	text	\N	\N	\N	\N
164	2	1	lkjlkj lkj lj	2025-12-15 21:39:28.923768+01	text	\N	\N	\N	\N
165	2	1	lkj lj lj j	2025-12-15 21:39:47.537798+01	text	\N	\N	\N	\N
166	2	3	pokpkpok	2025-12-15 21:40:30.797223+01	text	\N	\N	\N	\N
167	2	3	pokpokopk	2025-12-15 21:40:52.403451+01	text	\N	\N	\N	\N
168	2	3	kkkkkkkkkkkkkkkkkk	2025-12-15 21:40:59.634286+01	text	\N	\N	\N	\N
169	2	1	pokpokpok	2025-12-15 21:41:02.706223+01	text	\N	\N	\N	\N
170	2	1	pokpokpok	2025-12-15 21:41:20.13853+01	text	\N	\N	\N	\N
171	2	3	pokpok	2025-12-15 21:41:41.57855+01	text	\N	\N	\N	\N
172	2	3	pokpok	2025-12-15 21:41:50.609874+01	text	\N	\N	\N	\N
173	2	1	[opo[po[po	2025-12-15 22:26:21.174924+01	text	\N	\N	\N	\N
174	2	1	poi poipoi po	2025-12-15 23:07:05.542003+01	text	\N	\N	\N	\N
175	2	3	lkjljjklkj	2025-12-15 23:13:35.442358+01	text	\N	\N	\N	\N
176	2	3	lkjlklkj	2025-12-15 23:13:53.246152+01	text	\N	\N	\N	\N
177	2	3	lkmlkm	2025-12-15 23:14:07.623541+01	text	\N	\N	\N	\N
178	2	3	lkmlkmkm	2025-12-15 23:14:31.519041+01	text	\N	\N	\N	\N
179	2	3	;lk;lklk	2025-12-15 23:14:43.754279+01	text	\N	\N	\N	\N
180	2	1	lkjpoipoipoi	2025-12-15 23:16:23.591682+01	text	\N	\N	\N	\N
181	2	1	;;lk;lkl;k	2025-12-15 23:17:19.784885+01	text	\N	\N	\N	\N
182	2	3	;lk;lk;lk	2025-12-15 23:18:00.166963+01	text	\N	\N	\N	\N
183	2	3	;lk;lk;lk;lk	2025-12-15 23:18:08.806719+01	text	\N	\N	\N	\N
184	2	1	;lk;lkl;k	2025-12-15 23:18:15.246378+01	text	\N	\N	\N	\N
185	2	1	oijoioijioj	2025-12-15 23:34:18.343+01	text	\N	\N	\N	\N
186	2	1	pokpokopk	2025-12-15 23:34:23.744705+01	text	\N	\N	\N	\N
187	2	3	jnkjnkjnkjn	2025-12-15 23:34:46.685875+01	text	\N	\N	\N	\N
188	2	3	fbbxbxcb	2025-12-15 23:34:51.579825+01	text	\N	\N	\N	\N
189	2	3	xbxcb	2025-12-15 23:34:52.199096+01	text	\N	\N	\N	\N
190	2	3	xb	2025-12-15 23:34:52.415923+01	text	\N	\N	\N	\N
191	2	3	xc	2025-12-15 23:34:52.601043+01	text	\N	\N	\N	\N
192	2	3	bx	2025-12-15 23:34:52.787836+01	text	\N	\N	\N	\N
193	2	3	cb	2025-12-15 23:34:52.964446+01	text	\N	\N	\N	\N
194	2	3	xc	2025-12-15 23:34:53.130363+01	text	\N	\N	\N	\N
195	2	3	bx	2025-12-15 23:34:53.274894+01	text	\N	\N	\N	\N
196	2	3	c	2025-12-15 23:34:53.465264+01	text	\N	\N	\N	\N
197	2	3	xcb	2025-12-15 23:34:53.618768+01	text	\N	\N	\N	\N
198	2	3	x	2025-12-15 23:34:53.775364+01	text	\N	\N	\N	\N
199	2	3	cb	2025-12-15 23:34:53.947779+01	text	\N	\N	\N	\N
200	2	3	xcb	2025-12-15 23:34:54.111213+01	text	\N	\N	\N	\N
201	2	3	x	2025-12-15 23:34:54.276055+01	text	\N	\N	\N	\N
202	2	3	cb	2025-12-15 23:34:54.433269+01	text	\N	\N	\N	\N
203	2	3	xcb	2025-12-15 23:34:54.603751+01	text	\N	\N	\N	\N
204	2	3	xc	2025-12-15 23:34:54.782687+01	text	\N	\N	\N	\N
205	2	3	bx	2025-12-15 23:34:54.917398+01	text	\N	\N	\N	\N
206	2	3	cb	2025-12-15 23:34:55.084977+01	text	\N	\N	\N	\N
207	2	3	xcb	2025-12-15 23:34:55.239535+01	text	\N	\N	\N	\N
208	2	3	xc	2025-12-15 23:34:55.398048+01	text	\N	\N	\N	\N
209	2	1	pppokpok	2025-12-15 23:51:34.386041+01	text	\N	\N	\N	\N
210	2	3	bpokpokpok	2025-12-15 23:51:45.617734+01	text	\N	\N	\N	\N
211	2	3	okpkpopok	2025-12-15 23:51:51.795979+01	text	\N	\N	\N	\N
212	2	3	pokpokpokpokopk	2025-12-15 23:51:56.087241+01	text	\N	\N	\N	\N
213	2	1	okokpk	2025-12-15 23:52:04.05541+01	text	\N	\N	\N	\N
214	2	1	[p[l[pl	2025-12-16 10:41:19.31652+01	text	\N	\N	\N	\N
215	2	3	oijoi joij oij oi joioiioioio	2025-12-16 10:42:11.868497+01	text	\N	\N	\N	\N
216	2	3	oijoijoij	2025-12-16 10:42:29.890438+01	text	\N	\N	\N	\N
217	2	3	oijoijoij	2025-12-16 10:42:40.992328+01	text	\N	\N	\N	\N
218	2	3	oijoijoijij	2025-12-16 10:42:49.874189+01	text	\N	\N	\N	\N
219	2	1	jjjj	2025-12-16 10:42:56.608806+01	text	\N	\N	\N	\N
220	2	3	jjjjj	2025-12-16 10:43:05.498921+01	text	\N	\N	\N	\N
221	2	3	pokpokpok	2025-12-16 10:44:37.36864+01	text	\N	\N	\N	\N
222	2	3	pokpkpok	2025-12-16 10:44:46.821688+01	text	\N	\N	\N	\N
223	2	3	pokpokpok	2025-12-16 10:44:52.559926+01	text	\N	\N	\N	\N
224	2	3	poooooooooooooooooooooooooooo	2025-12-16 10:45:00.22198+01	text	\N	\N	\N	\N
225	2	1	oijoijoij	2025-12-16 10:45:18.426759+01	text	\N	\N	\N	\N
226	3	1	pjoojpoj poj	2025-12-16 13:00:04.941583+01	text	\N	\N	\N	\N
227	3	1	[po[p o[o[p o	2025-12-16 13:00:45.11742+01	text	\N	\N	\N	\N
228	3	1	hiuhiuhih i	2025-12-16 13:04:18.816826+01	text	\N	\N	\N	\N
229	3	1	ih ihiuh ih	2025-12-16 13:04:24.856864+01	text	\N	\N	\N	\N
230	3	1	poj pojp ojpo	2025-12-16 15:22:17.96581+01	text	\N	\N	\N	\N
231	3	1	jjjjjjjjjjjjjjjj	2025-12-16 15:22:20.967823+01	text	\N	\N	\N	\N
232	2	1	kjhkjhkjh	2025-12-16 15:24:15.131391+01	text	\N	\N	\N	\N
233	2	1	kjhkjkjh	2025-12-16 15:24:18.552857+01	text	\N	\N	\N	\N
234	2	3	oijoij oij	2025-12-16 15:24:52.997501+01	text	\N	\N	\N	\N
235	2	3	oij oijoij	2025-12-16 15:25:01.176217+01	text	\N	\N	\N	\N
236	2	3	oij oij	2025-12-16 15:25:19.90068+01	text	\N	\N	\N	\N
237	6	22	pokpokok	2025-12-16 21:19:18.653052+01	text	\N	\N	\N	\N
238	2	1	oioiuoiu	2025-12-18 10:11:22.774299+01	text	\N	\N	\N	\N
240	2	3	090 i09i 09i	2025-12-19 09:02:40.833578+01	text	\N	\N	\N	\N
241	2	1	000000909	2025-12-19 09:02:58.148791+01	text	\N	\N	\N	\N
242	2	3	yyyyyy	2025-12-19 09:03:07.949363+01	text	\N	\N	\N	\N
243	2	3	op[o[po [po	2025-12-19 09:13:59.742538+01	text	\N	\N	\N	\N
244	2	1	p poipoi poi poi	2025-12-19 09:18:37.155771+01	text	\N	\N	\N	\N
245	2	1	ppoipoi	2025-12-19 09:18:54.522586+01	text	\N	\N	\N	\N
246	2	3	oiu oiuo uoi u	2025-12-19 09:19:18.644272+01	text	\N	\N	\N	\N
247	2	1	poi poi pio	2025-12-19 09:22:49.093549+01	text	\N	\N	\N	\N
248	2	3	kkkkkk	2025-12-19 09:24:56.377659+01	text	\N	\N	\N	\N
249	2	3	[pk[pk[pk[pk	2025-12-19 09:25:07.4487+01	text	\N	\N	\N	\N
250	2	3	kopkpok	2025-12-19 09:27:13.223789+01	text	\N	\N	\N	\N
251	2	1	pppppp	2025-12-19 09:28:42.954779+01	text	\N	\N	\N	\N
252	2	1	kuku	2025-12-19 09:31:09.71328+01	text	\N	\N	\N	\N
253	2	3	ljlkjlj lj lj	2025-12-19 12:16:15.700106+01	text	\N	\N	\N	\N
254	2	3	ljk lj lj	2025-12-19 12:16:23.733859+01	text	\N	\N	\N	\N
255	2	3	kkkkk	2025-12-19 12:16:36.531657+01	text	\N	\N	\N	\N
256	2	1	ippoipoipi	2025-12-19 12:22:36.923027+01	text	\N	\N	\N	\N
257	2	1	iojoijoij	2025-12-19 12:28:15.152555+01	text	\N	\N	\N	\N
258	2	3	pi pipoi pi	2025-12-19 12:29:30.500243+01	text	\N	\N	\N	\N
259	2	1	po ipi pi	2025-12-19 12:29:37.734124+01	text	\N	\N	\N	\N
260	2	1	-----	2025-12-19 12:29:51.021383+01	text	\N	\N	\N	\N
261	2	1	pokpkopokpok	2025-12-19 12:30:45.164024+01	text	\N	\N	\N	\N
262	2	3	pok pkp kp ok	2025-12-19 12:30:56.451317+01	text	\N	\N	\N	\N
263	2	3	ppppp	2025-12-19 12:31:06.091558+01	text	\N	\N	\N	\N
264	2	1	k;lk;lk ;k	2025-12-19 12:31:58.179509+01	text	\N	\N	\N	\N
265	2	1	ghhhh kkh	2025-12-19 12:39:07.438177+01	text	\N	\N	\N	\N
266	2	1	iuh iuh iuh	2025-12-19 13:04:15.612234+01	text	\N	\N	\N	\N
267	2	3	oijoi joi j	2025-12-19 13:04:43.675425+01	text	\N	\N	\N	\N
268	2	3	iiiii	2025-12-19 13:04:50.563474+01	text	\N	\N	\N	\N
269	2	3	oij oijoij	2025-12-19 13:05:01.461847+01	text	\N	\N	\N	\N
270	2	1	oij oijoi j	2025-12-19 13:05:07.324909+01	text	\N	\N	\N	\N
271	2	3	oij oij oij oij	2025-12-19 13:05:23.261708+01	text	\N	\N	\N	\N
272	2	3	jjjjjjjjjjjj	2025-12-20 11:18:07.766159+01	text	\N	\N	\N	\N
273	2	3	oijo ij io	2025-12-20 11:18:35.052348+01	text	\N	\N	\N	\N
274	2	3	joi joi oi j	2025-12-20 11:19:02.671022+01	text	\N	\N	\N	\N
275	2	3	kpokpok	2025-12-20 17:08:24.679658+01	text	\N	\N	\N	\N
276	2	3	pokpko	2025-12-20 17:08:37.680345+01	text	\N	\N	\N	\N
277	6	1	pok pokpok	2025-12-20 23:24:05.711483+01	text	\N	\N	\N	\N
278	6	1	po pk okpok	2025-12-20 23:24:43.532036+01	text	\N	\N	\N	\N
279	2	3	pok poko	2025-12-20 23:24:56.34624+01	text	\N	\N	\N	\N
280	2	1	j oij ojo ji	2025-12-20 23:34:41.277779+01	text	\N	\N	\N	\N
281	2	1	ioj oijoj	2025-12-20 23:35:02.277142+01	text	\N	\N	\N	\N
282	6	1	po opkpokopk	2025-12-20 23:37:44.005792+01	text	\N	\N	\N	\N
283	2	1	kpkpokkkkkkkkkkk	2025-12-20 23:38:22.781881+01	text	\N	\N	\N	\N
284	3	1	pojp poj p j	2025-12-20 23:48:34.506255+01	text	\N	\N	\N	\N
285	8	1	oijoij oij oij	2025-12-20 23:48:58.891722+01	text	\N	\N	\N	\N
286	2	1	popo kpkpok po	2025-12-20 23:55:35.755683+01	text	\N	\N	\N	\N
287	2	1	pok pokpok pok pok	2025-12-20 23:55:44.171402+01	text	\N	\N	\N	\N
288	2	1	poipoipoi	2025-12-21 00:00:12.61918+01	text	\N	\N	\N	\N
289	2	3	poi pipoip i	2025-12-21 00:00:29.459813+01	text	\N	\N	\N	\N
290	2	3	pok pop ok	2025-12-21 00:01:29.739066+01	text	\N	\N	\N	\N
291	2	1	pok po k	2025-12-21 00:01:53.761085+01	text	\N	\N	\N	\N
292	2	1	pokpo kopk	2025-12-21 00:02:03.418643+01	text	\N	\N	\N	\N
293	8	1	pok pokpok	2025-12-21 12:50:51.45937+01	text	\N	\N	\N	\N
294	8	1	pokp okp ok	2025-12-21 12:51:02.466833+01	text	\N	\N	\N	\N
295	2	1	pokpokpok	2025-12-22 13:13:48.060003+01	text	\N	\N	\N	\N
296	2	3	po kpo kopk	2025-12-22 13:15:36.33182+01	text	\N	\N	\N	\N
297	2	1	lkjlkj	2025-12-22 13:16:18.536587+01	text	\N	\N	\N	\N
298	2	1	;l,;l,	2025-12-22 13:16:43.704258+01	text	\N	\N	\N	\N
299	2	3	lkjljlkj	2025-12-22 13:56:14.490012+01	text	\N	\N	\N	\N
300	2	3	ioj oij oij	2025-12-22 13:56:45.630376+01	text	\N	\N	\N	\N
301	2	3	pokpokpok	2025-12-22 13:58:35.245149+01	text	\N	\N	\N	\N
302	2	3	pojoppoj	2025-12-22 14:06:08.111553+01	text	\N	\N	\N	\N
303	2	3	[k[pk[pk	2025-12-22 14:12:11.922722+01	text	\N	\N	\N	\N
304	2	3	lknlkn	2025-12-22 14:13:00.796813+01	text	\N	\N	\N	\N
305	2	3	poi poipoi	2025-12-22 14:29:20.805411+01	text	\N	\N	\N	\N
306	2	3	poi poi pio	2025-12-22 14:29:29.594371+01	text	\N	\N	\N	\N
307	5	3	oij oij oij oij i	2025-12-22 14:30:31.654101+01	text	\N	\N	\N	\N
308	5	1	pok pok pok	2025-12-22 14:32:51.917621+01	text	\N	\N	\N	\N
309	5	1	pok pokpok	2025-12-22 14:34:38.184303+01	text	\N	\N	\N	\N
310	5	1	pok pokpo k	2025-12-22 14:34:47.441358+01	text	\N	\N	\N	\N
311	5	3	oij oijoij oijo ij	2025-12-22 14:37:29.726691+01	text	\N	\N	\N	\N
312	2	1	lkjlkjlkj	2025-12-22 14:42:07.330442+01	text	\N	\N	\N	\N
313	5	1	pok pokpok po	2025-12-22 14:51:38.508752+01	text	\N	\N	\N	\N
314	5	1	kpokpokpokpok	2025-12-22 14:54:57.43669+01	text	\N	\N	\N	\N
315	5	1	pok pokpo k	2025-12-22 14:56:15.546549+01	text	\N	\N	\N	\N
316	5	1	iuh iuhi uh	2025-12-22 14:56:56.883701+01	text	\N	\N	\N	\N
317	5	1	[pk[p[kp	2025-12-22 14:58:22.879393+01	text	\N	\N	\N	\N
318	5	1	oijoijoijoijoij	2025-12-22 14:58:34.470424+01	text	\N	\N	\N	\N
319	2	1	[po[po	2025-12-22 19:27:40.460149+01	text	\N	\N	\N	\N
320	2	3	poi poi poi	2025-12-22 19:30:35.551329+01	text	\N	\N	\N	\N
321	2	1	oijoijoij	2025-12-22 19:31:31.711426+01	text	\N	\N	\N	\N
322	2	1	oijoij	2025-12-22 19:31:40.324458+01	text	\N	\N	\N	\N
323	2	3	oij oij	2025-12-22 19:41:45.386809+01	text	\N	\N	\N	\N
324	2	3	ooooooooooooo	2025-12-22 19:41:54.523306+01	text	\N	\N	\N	\N
325	2	3	oij oij oij	2025-12-22 19:42:41.933834+01	text	\N	\N	\N	\N
326	2	3	oi joij	2025-12-22 19:43:00.268074+01	text	\N	\N	\N	\N
327	2	3	oij oij	2025-12-22 19:43:18.138226+01	text	\N	\N	\N	\N
328	2	3	oij oij	2025-12-22 19:43:28.058039+01	text	\N	\N	\N	\N
329	2	3	pok pok po k	2025-12-22 19:45:45.099632+01	text	\N	\N	\N	\N
330	2	3	kkkkkk	2025-12-22 19:45:50.521092+01	text	\N	\N	\N	\N
331	2	3	pok pko	2025-12-22 19:46:17.850572+01	text	\N	\N	\N	\N
332	2	3	popjo pojpo j	2025-12-22 19:48:13.409624+01	text	\N	\N	\N	\N
333	2	1	poj poj	2025-12-22 19:48:24.474542+01	text	\N	\N	\N	\N
334	2	3	pjp pjpoj poj	2025-12-22 19:53:30.850674+01	text	\N	\N	\N	\N
335	2	3	poj poj po j	2025-12-22 19:54:42.712259+01	text	\N	\N	\N	\N
336	2	3	pokpokpok	2025-12-22 19:57:25.037773+01	text	\N	\N	\N	\N
337	2	3	';l';l	2025-12-22 20:03:16.571318+01	text	\N	\N	\N	\N
338	2	1	oij oij oi	2025-12-22 20:03:43.127554+01	text	\N	\N	\N	\N
339	2	3	pok pok pok	2025-12-22 20:09:12.258356+01	text	\N	\N	\N	\N
340	2	1	pok pok	2025-12-22 20:09:34.610765+01	text	\N	\N	\N	\N
341	2	1	opkpoko	2025-12-22 20:09:57.848818+01	text	\N	\N	\N	\N
342	5	3	[po[p[po[po	2025-12-22 20:12:37.189796+01	text	\N	\N	\N	\N
343	5	3	[po[po	2025-12-22 20:12:46.787957+01	text	\N	\N	\N	\N
344	2	1	pokpok	2025-12-22 20:12:59.24102+01	text	\N	\N	\N	\N
345	2	1	pppppppppppppppp	2025-12-22 20:13:08.960164+01	text	\N	\N	\N	\N
346	2	3	oijoijoij	2025-12-22 20:17:13.785812+01	text	\N	\N	\N	\N
347	2	3	[pl[lp[l	2025-12-22 20:19:26.078433+01	text	\N	\N	\N	\N
348	2	3	[pl[pl	2025-12-22 20:19:31.017547+01	text	\N	\N	\N	\N
349	2	1	oijoijoij	2025-12-22 20:19:38.749809+01	text	\N	\N	\N	\N
350	2	1	oijoijoji	2025-12-22 20:19:45.44323+01	text	\N	\N	\N	\N
351	5	3	oijoijoij	2025-12-22 20:19:56.443813+01	text	\N	\N	\N	\N
352	2	3	pokpokok	2025-12-22 20:20:10.232671+01	text	\N	\N	\N	\N
353	2	3	pokpokok	2025-12-22 20:20:24.840535+01	text	\N	\N	\N	\N
354	2	1	oijoij	2025-12-22 20:20:36.327556+01	text	\N	\N	\N	\N
355	2	1	oijoijoij	2025-12-22 20:20:40.127126+01	text	\N	\N	\N	\N
356	2	1	oijoijoij	2025-12-22 20:20:44.257383+01	text	\N	\N	\N	\N
357	5	3	oijoijoij	2025-12-22 20:20:48.977733+01	text	\N	\N	\N	\N
358	5	3	oijoijoij	2025-12-22 20:20:55.521495+01	text	\N	\N	\N	\N
359	2	1	kpokpok	2025-12-22 20:21:44.825596+01	text	\N	\N	\N	\N
360	2	1	kkkkkkkkkkkkkkkkkkk	2025-12-22 20:21:56.536915+01	text	\N	\N	\N	\N
361	2	1	pokpokpok	2025-12-22 20:22:22.215762+01	text	\N	\N	\N	\N
362	2	3	pokpokpok	2025-12-22 20:22:31.880804+01	text	\N	\N	\N	\N
363	2	3	pokpok	2025-12-22 20:22:41.689809+01	text	\N	\N	\N	\N
364	2	1	pokpokpk	2025-12-22 20:22:55.545603+01	text	\N	\N	\N	\N
365	2	1	oijoijoij	2025-12-22 20:23:08.752372+01	text	\N	\N	\N	\N
366	2	3	;lk;lk;lk	2025-12-22 20:24:34.441215+01	text	\N	\N	\N	\N
367	2	1	pojpojpo	2025-12-22 20:25:07.583853+01	text	\N	\N	\N	\N
368	2	1	pokpokok	2025-12-22 20:25:22.599496+01	text	\N	\N	\N	\N
369	2	1	pokpokpo	2025-12-22 20:25:35.674257+01	text	\N	\N	\N	\N
370	2	1	iiiii	2025-12-22 20:25:56.52673+01	text	\N	\N	\N	\N
371	2	3	iiii	2025-12-22 20:26:07.032538+01	text	\N	\N	\N	\N
372	2	3	iiii	2025-12-22 20:26:12.368652+01	text	\N	\N	\N	\N
373	2	3	oijoijoij	2025-12-22 20:41:48.374126+01	text	\N	\N	\N	\N
374	2	3	iiiiiiiiiii	2025-12-22 20:41:56.252862+01	text	\N	\N	\N	\N
375	2	3	oijoijoij	2025-12-22 20:49:14.25554+01	text	\N	\N	\N	\N
376	2	1	oijoijoij	2025-12-22 20:49:25.850329+01	text	\N	\N	\N	\N
377	2	3	ojioijoij	2025-12-22 20:49:42.218202+01	text	\N	\N	\N	\N
378	2	3	oijoijij	2025-12-22 20:49:58.103318+01	text	\N	\N	\N	\N
379	2	3	ojoijoijoij	2025-12-22 20:50:42.503123+01	text	\N	\N	\N	\N
380	2	3	joijoijoij	2025-12-22 20:50:49.583382+01	text	\N	\N	\N	\N
381	2	1	oijoijoij	2025-12-22 20:51:00.520978+01	text	\N	\N	\N	\N
382	2	1	ojoijoioijoij	2025-12-22 20:51:08.484691+01	text	\N	\N	\N	\N
383	2	1	oijoijoij	2025-12-22 20:51:15.884359+01	text	\N	\N	\N	\N
384	2	3	lkjlkjlj	2025-12-22 21:29:50.133356+01	text	\N	\N	\N	\N
385	2	3	lkjlkjkj	2025-12-22 21:29:58.547915+01	text	\N	\N	\N	\N
386	2	3	kkkkk	2025-12-22 21:30:10.230832+01	text	\N	\N	\N	\N
387	2	1	lkjlkj	2025-12-22 21:30:28.597069+01	text	\N	\N	\N	\N
388	2	1	kkkkk	2025-12-22 21:30:35.709957+01	text	\N	\N	\N	\N
389	2	1	lkjlkjlkjklj	2025-12-22 21:30:43.627807+01	text	\N	\N	\N	\N
390	2	3	lkjlklkj	2025-12-22 21:34:46.598517+01	text	\N	\N	\N	\N
391	2	1	lkjlkjlkj	2025-12-22 21:34:55.568395+01	text	\N	\N	\N	\N
392	2	3	oijojoijio	2025-12-22 21:35:03.120721+01	text	\N	\N	\N	\N
393	5	1	iuhiuiuh	2025-12-22 21:35:14.088225+01	text	\N	\N	\N	\N
394	5	1	hihiuh	2025-12-22 21:35:38.415399+01	text	\N	\N	\N	\N
395	2	1	oijoioijiooj	2025-12-22 21:35:47.955268+01	text	\N	\N	\N	\N
396	5	3	oijoijoij	2025-12-22 21:36:02.575548+01	text	\N	\N	\N	\N
397	5	3	oijoijoij	2025-12-22 21:36:15.432354+01	text	\N	\N	\N	\N
398	5	3	oijoij	2025-12-22 21:37:17.463557+01	text	\N	\N	\N	\N
399	5	3	oijoioij	2025-12-22 21:37:28.550211+01	text	\N	\N	\N	\N
400	2	3	ojijoijo ij	2025-12-23 09:09:38.638422+01	text	\N	\N	\N	\N
401	2	1	oi joijio j	2025-12-23 09:09:57.979746+01	text	\N	\N	\N	\N
402	2	3	xgfxgfxgfx	2025-12-23 09:10:14.196076+01	text	\N	\N	\N	\N
403	2	1	09u09u09u	2025-12-23 09:11:28.120617+01	text	\N	\N	\N	\N
404	2	1	09u09u09u	2025-12-23 09:11:40.901881+01	text	\N	\N	\N	\N
405	2	1	09u09u09u	2025-12-23 09:11:52.928985+01	text	\N	\N	\N	\N
406	2	1	iuh iuhiu h	2025-12-23 09:26:21.729312+01	text	\N	\N	\N	\N
407	2	3	iu hiu h	2025-12-23 09:26:38.342052+01	text	\N	\N	\N	\N
408	2	3	iuh ih	2025-12-23 09:26:54.566141+01	text	\N	\N	\N	\N
409	2	3	jhvjhv	2025-12-23 09:28:51.349318+01	text	\N	\N	\N	\N
410	2	1	oiiojioj	2025-12-23 09:30:13.315571+01	text	\N	\N	\N	\N
411	5	3	oioijoij	2025-12-23 09:30:20.412847+01	text	\N	\N	\N	\N
412	2	3	iuhiuhiuhiuh	2025-12-23 09:30:38.476387+01	text	\N	\N	\N	\N
413	2	1	pojpo jpoj	2025-12-23 09:50:42.044402+01	text	\N	\N	\N	\N
414	2	3	poj poj	2025-12-23 09:50:57.75086+01	text	\N	\N	\N	\N
415	2	3	hoihoih	2025-12-23 09:51:14.67057+01	text	\N	\N	\N	\N
416	5	3	oihoih oih	2025-12-23 09:51:24.253637+01	text	\N	\N	\N	\N
417	2	3	pok pok	2025-12-23 09:53:57.046354+01	text	\N	\N	\N	\N
418	2	1	[po[po	2025-12-23 10:06:18.776556+01	text	\N	\N	\N	\N
419	2	1	opkpok	2025-12-23 10:06:43.449484+01	text	\N	\N	\N	\N
420	5	3	oijoijoijoi	2025-12-23 10:07:02.163079+01	text	\N	\N	\N	\N
421	5	3	oijoij	2025-12-23 10:07:20.07504+01	text	\N	\N	\N	\N
422	2	3	09u90nu0nu	2025-12-26 11:25:45.308823+01	text	\N	\N	\N	\N
423	2	1	09un09u0nu009un	2025-12-26 11:26:14.91543+01	text	\N	\N	\N	\N
424	2	3	0u909u0n9u	2025-12-26 11:26:36.662456+01	text	\N	\N	\N	\N
425	2	3	khjh kjh kjh	2025-12-26 11:39:40.939029+01	text	\N	\N	\N	\N
426	2	3	oijoijoij	2025-12-26 11:41:18.706381+01	text	\N	\N	\N	\N
427	2	1	oijoijoij	2025-12-26 11:41:32.688737+01	text	\N	\N	\N	\N
428	2	3	99999	2025-12-26 11:41:48.538694+01	text	\N	\N	\N	\N
429	2	3	0990009	2025-12-26 11:42:01.410794+01	text	\N	\N	\N	\N
430	2	3	oiioioioii	2025-12-26 11:48:22.232976+01	text	\N	\N	\N	\N
431	2	3	09u09u09u	2025-12-26 11:53:13.875647+01	text	\N	\N	\N	\N
432	2	1	76r76r76r	2025-12-26 11:53:30.999472+01	text	\N	\N	\N	\N
433	5	1	-----	2025-12-26 11:53:42.661543+01	text	\N	\N	\N	\N
434	2	3	poipipoi	2025-12-26 11:54:21.139195+01	text	\N	\N	\N	\N
435	2	1	uuoiuoiu	2025-12-26 11:54:39.639133+01	text	\N	\N	\N	\N
436	2	3	oiuoiu	2025-12-26 11:55:13.221186+01	text	\N	\N	\N	\N
437	2	1	oiouoiu	2025-12-26 11:55:18.760726+01	text	\N	\N	\N	\N
438	2	1	oiuoiu	2025-12-26 11:55:26.074021+01	text	\N	\N	\N	\N
439	2	3	oiu oiu oiu	2025-12-26 11:56:15.142883+01	text	\N	\N	\N	\N
440	2	3	98y98y98y	2025-12-26 11:56:42.036765+01	text	\N	\N	\N	\N
441	2	3	98y98y89y	2025-12-26 11:56:49.764107+01	text	\N	\N	\N	\N
442	2	3	yyyyyy	2025-12-26 11:56:55.958802+01	text	\N	\N	\N	\N
443	2	3	8y8y8y	2025-12-26 11:57:08.28362+01	text	\N	\N	\N	\N
444	2	3	poipoi	2025-12-26 12:00:13.706504+01	text	\N	\N	\N	\N
445	2	3	poipoipoi	2025-12-26 12:00:24.834839+01	text	\N	\N	\N	\N
446	5	3	poipoi	2025-12-26 12:01:15.852965+01	text	\N	\N	\N	\N
447	5	3	-0i-0i	2025-12-26 12:01:38.61041+01	text	\N	\N	\N	\N
448	5	3	oiuoiu	2025-12-26 12:11:46.283484+01	text	\N	\N	\N	\N
449	5	3	poipoipoi	2025-12-26 12:16:05.738067+01	text	\N	\N	\N	\N
450	2	1	poipoipoi	2025-12-26 12:16:15.431265+01	text	\N	\N	\N	\N
451	2	1	poipoipoi	2025-12-26 12:16:33.3763+01	text	\N	\N	\N	\N
452	5	3	poipoipio	2025-12-26 12:16:40.272702+01	text	\N	\N	\N	\N
453	5	3	pipoipoi	2025-12-26 12:16:52.073295+01	text	\N	\N	\N	\N
454	5	1	poipoioi	2025-12-26 12:17:05.057328+01	text	\N	\N	\N	\N
455	2	3	098098098	2025-12-26 12:17:31.024689+01	text	\N	\N	\N	\N
456	2	3	00000000000000000000	2025-12-26 12:17:39.935996+01	text	\N	\N	\N	\N
457	2	3	opipoi	2025-12-26 12:22:00.413015+01	text	\N	\N	\N	\N
458	2	3	oiuoiuoiu	2025-12-26 12:22:14.214561+01	text	\N	\N	\N	\N
459	2	3	iuiuiuiu	2025-12-26 12:23:10.358407+01	text	\N	\N	\N	\N
460	2	1	iuiuiu	2025-12-26 12:23:17.587809+01	text	\N	\N	\N	\N
461	2	3	iuiuiu	2025-12-26 12:23:23.624778+01	text	\N	\N	\N	\N
462	2	3	jojooijo	2025-12-26 12:27:56.803866+01	text	\N	\N	\N	\N
463	2	3	poipoipoipoi	2025-12-26 12:28:30.734657+01	text	\N	\N	\N	\N
464	2	3	oihoihoih	2025-12-26 12:34:00.219506+01	text	\N	\N	\N	\N
465	2	3	oijoijoij	2025-12-26 12:34:10.823491+01	text	\N	\N	\N	\N
466	2	1	oiuoiu	2025-12-26 12:37:10.376268+01	text	\N	\N	\N	\N
467	2	3	oiuoiuoiuiou	2025-12-26 12:37:21.000892+01	text	\N	\N	\N	\N
468	2	3	jpojpojpoj	2025-12-26 12:37:37.184455+01	text	\N	\N	\N	\N
469	2	3	oihoihoih	2025-12-26 12:39:19.096828+01	text	\N	\N	\N	\N
470	2	3	oijoijioj	2025-12-26 12:40:26.4246+01	text	\N	\N	\N	\N
471	2	1	lkjlkj	2025-12-26 16:59:22.390935+01	text	\N	\N	\N	\N
472	2	3	oiuoiuoiu	2025-12-26 16:59:32.790782+01	text	\N	\N	\N	\N
473	2	3	[pk[pkpk	2025-12-26 17:00:28.042458+01	text	\N	\N	\N	\N
474	2	3	[k[p k[p k[p k	2025-12-26 17:00:45.773412+01	text	\N	\N	\N	\N
475	2	3	poipoipoi	2025-12-26 17:01:27.847063+01	text	\N	\N	\N	\N
476	2	3	oijoijoij	2025-12-26 17:02:12.295499+01	text	\N	\N	\N	\N
477	2	3	pkpokpok	2025-12-26 17:05:53.764565+01	text	\N	\N	\N	\N
478	2	1	pokpokpok	2025-12-26 17:06:05.340814+01	text	\N	\N	\N	\N
479	2	3	oijoijij	2025-12-26 17:10:34.152549+01	text	\N	\N	\N	\N
480	2	3	oijoijioj	2025-12-26 17:11:00.474859+01	text	\N	\N	\N	\N
481	2	1	iojoij	2025-12-26 17:11:13.023939+01	text	\N	\N	\N	\N
482	2	3	poipoipoi	2025-12-26 17:12:17.496118+01	text	\N	\N	\N	\N
483	2	3	poipoi	2025-12-26 17:12:28.288384+01	text	\N	\N	\N	\N
484	2	1	poipoipoi	2025-12-26 17:12:40.095177+01	text	\N	\N	\N	\N
485	2	3	poipipoi	2025-12-26 17:12:44.593274+01	text	\N	\N	\N	\N
486	2	3	iuhiuhiuhuih	2025-12-26 17:12:56.168484+01	text	\N	\N	\N	\N
487	2	3	jlkjlkjlkj	2025-12-26 17:16:14.25557+01	text	\N	\N	\N	\N
488	2	3	oihoihoih	2025-12-26 17:16:22.670798+01	text	\N	\N	\N	\N
489	2	3	oiuoiuoiu	2025-12-26 17:16:39.84822+01	text	\N	\N	\N	\N
490	2	3	oiuoiuiou	2025-12-26 17:16:52.474099+01	text	\N	\N	\N	\N
491	2	3	oiuoiuoiu	2025-12-26 17:16:59.643749+01	text	\N	\N	\N	\N
492	2	3	iiiii	2025-12-26 17:17:03.664379+01	text	\N	\N	\N	\N
493	2	3	oiuoiuoiu	2025-12-26 17:18:27.392818+01	text	\N	\N	\N	\N
494	2	1	98y98y98y98y	2025-12-26 17:19:04.455491+01	text	\N	\N	\N	\N
495	2	1	98y98y89y	2025-12-26 17:19:24.140548+01	text	\N	\N	\N	\N
496	2	1	98y98y98y8y9	2025-12-26 17:19:30.896226+01	text	\N	\N	\N	\N
497	5	3	98y9y98y98y	2025-12-26 17:19:41.303017+01	text	\N	\N	\N	\N
498	2	1	pjpojpojpojopj	2025-12-26 17:45:50.927698+01	text	\N	\N	\N	\N
499	5	3	;lk;lk;lk	2025-12-26 17:46:40.046959+01	text	\N	\N	\N	\N
500	2	3	ipo ipi poipoi	2025-12-26 17:47:03.104888+01	text	\N	\N	\N	\N
501	5	1	ipoipoipoipoi	2025-12-26 17:48:04.350086+01	text	\N	\N	\N	\N
502	5	1	opjpjpo	2025-12-26 17:49:06.967149+01	text	\N	\N	\N	\N
503	5	1	asasd	2025-12-26 17:49:07.752691+01	text	\N	\N	\N	\N
504	5	1	da	2025-12-26 17:49:08.784702+01	text	\N	\N	\N	\N
505	5	1	as	2025-12-26 17:49:09.532658+01	text	\N	\N	\N	\N
506	5	1	s	2025-12-26 17:49:10.129049+01	text	\N	\N	\N	\N
507	5	1	asd	2025-12-26 17:49:10.780932+01	text	\N	\N	\N	\N
508	5	1	as	2025-12-26 17:49:11.373431+01	text	\N	\N	\N	\N
509	5	1	da	2025-12-26 17:49:12.461743+01	text	\N	\N	\N	\N
510	5	1	a	2025-12-26 17:49:13.089592+01	text	\N	\N	\N	\N
511	5	1	ADa	2025-12-26 17:49:13.684963+01	text	\N	\N	\N	\N
512	5	1	s	2025-12-26 17:49:14.268955+01	text	\N	\N	\N	\N
513	5	1	asdADa	2025-12-26 17:49:14.720059+01	text	\N	\N	\N	\N
514	5	1	asas	2025-12-26 17:49:15.223066+01	text	\N	\N	\N	\N
515	5	1	as	2025-12-26 17:49:15.687805+01	text	\N	\N	\N	\N
516	5	1	sd	2025-12-26 17:49:16.17749+01	text	\N	\N	\N	\N
517	2	1	iugih iuh iuh i	2025-12-26 17:49:39.964427+01	text	\N	\N	\N	\N
518	2	1	oi oiu oiuou oi	2025-12-26 17:49:42.33689+01	text	\N	\N	\N	\N
519	2	3	09u09u09u0u0u9	2025-12-26 17:50:23.186309+01	text	\N	\N	\N	\N
520	2	3	joi joi joij	2025-12-26 17:57:11.982852+01	text	\N	\N	\N	\N
521	2	3	kjhkkjh	2025-12-26 18:55:48.908772+01	text	\N	\N	\N	\N
522	2	3	oijoiuoiu	2025-12-26 18:56:03.488658+01	text	\N	\N	\N	\N
523	2	3	iiiii	2025-12-26 18:56:14.372793+01	text	\N	\N	\N	\N
524	2	3	pokpokpok	2025-12-26 18:57:39.003124+01	text	\N	\N	\N	\N
525	3	1	pokpokpok	2025-12-26 18:57:50.860033+01	text	\N	\N	\N	\N
526	2	3	oioiuou	2025-12-26 19:03:11.328634+01	text	\N	\N	\N	\N
527	2	3	iuy iuy iu y	2025-12-26 19:09:11.299226+01	text	\N	\N	\N	\N
528	2	1	iuyiuy i y	2025-12-26 19:09:23.547912+01	text	\N	\N	\N	\N
529	2	3	iuyiu y	2025-12-26 19:09:33.748285+01	text	\N	\N	\N	\N
530	2	3	iuyiuy iuy	2025-12-26 19:09:56.172283+01	text	\N	\N	\N	\N
531	2	3	oiu oiuo u	2025-12-26 19:11:21.055142+01	text	\N	\N	\N	\N
532	2	1	oiu oiu oiu	2025-12-26 19:11:28.924536+01	text	\N	\N	\N	\N
533	2	3	oiu oiu oiu oi u	2025-12-26 19:11:48.402827+01	text	\N	\N	\N	\N
534	2	1	oiu oiu oiu	2025-12-26 19:11:56.21215+01	text	\N	\N	\N	\N
535	2	3	oiu oiu oiu oiu	2025-12-26 19:12:07.06863+01	text	\N	\N	\N	\N
536	2	1	kjhkjh	2025-12-26 19:19:12.205169+01	text	\N	\N	\N	\N
537	2	1	poi poi poi	2025-12-26 19:19:27.466137+01	text	\N	\N	\N	\N
538	5	3	;;;;;	2025-12-26 19:19:36.329421+01	text	\N	\N	\N	\N
539	5	3	p uoup upou	2025-12-26 19:19:46.177558+01	text	\N	\N	\N	\N
540	2	1	pou po u	2025-12-26 19:19:53.681393+01	text	\N	\N	\N	\N
541	2	3	90u09u 0u 09u	2025-12-26 19:28:34.199523+01	text	\N	\N	\N	\N
542	2	3	poipoipoi	2025-12-26 19:30:21.480709+01	text	\N	\N	\N	\N
543	2	1	poipoipoi	2025-12-26 19:30:31.015182+01	text	\N	\N	\N	\N
544	2	3	poipoipoi	2025-12-26 19:30:39.576333+01	text	\N	\N	\N	\N
545	2	3	poipoipoi	2025-12-26 19:30:54.282178+01	text	\N	\N	\N	\N
546	2	3	iiiiiiiiiii	2025-12-26 19:31:01.496653+01	text	\N	\N	\N	\N
547	2	3	poipoipoi	2025-12-26 19:32:30.93666+01	text	\N	\N	\N	\N
548	5	1	iyiuyiuy	2025-12-26 19:33:29.998034+01	text	\N	\N	\N	\N
549	5	1	iyiuyiuyiuy	2025-12-26 19:33:46.71167+01	text	\N	\N	\N	\N
550	5	3	iuyiuyiuy	2025-12-26 19:33:57.794768+01	text	\N	\N	\N	\N
551	5	3	tttt	2025-12-26 19:34:09.172391+01	text	\N	\N	\N	\N
552	5	3	ttttt	2025-12-26 19:34:14.330671+01	text	\N	\N	\N	\N
553	5	3	;lk;lk	2025-12-26 19:37:39.44824+01	text	\N	\N	\N	\N
554	2	3	oiuoiuoiu	2025-12-26 19:47:47.489744+01	text	\N	\N	\N	\N
555	2	3	kjhkjhkjh	2025-12-26 19:48:29.352457+01	text	\N	\N	\N	\N
556	2	3	[po[po[po[op	2025-12-26 19:53:08.336148+01	text	\N	\N	\N	\N
557	2	3	0990909090	2025-12-26 19:53:21.946048+01	text	\N	\N	\N	\N
558	2	1	oiuoiuoiu	2025-12-26 20:25:43.669684+01	text	\N	\N	\N	\N
559	2	1	iuyiuyiuy	2025-12-26 20:26:00.083663+01	text	\N	\N	\N	\N
560	2	1	iuyiuyiuy	2025-12-26 20:26:07.455169+01	text	\N	\N	\N	\N
561	2	1	iuyiuiuy	2025-12-26 20:26:20.055476+01	text	\N	\N	\N	\N
562	2	3	iuyiuyiuy	2025-12-26 20:26:32.465993+01	text	\N	\N	\N	\N
563	2	3	iuyiuyiuy	2025-12-26 20:26:37.60709+01	text	\N	\N	\N	\N
564	8	1	iuyiuy	2025-12-26 20:26:44.649206+01	text	\N	\N	\N	\N
565	2	1	ytrytrytr	2025-12-26 20:29:02.111016+01	text	\N	\N	\N	\N
566	2	1	ytrytr	2025-12-26 20:29:22.545184+01	text	\N	\N	\N	\N
567	2	1	ytrytrrt	2025-12-26 20:29:27.553297+01	text	\N	\N	\N	\N
568	2	1	oiuoiuoiu	2025-12-26 20:30:06.435476+01	text	\N	\N	\N	\N
569	2	3	oiuoioiu	2025-12-26 20:30:18.075756+01	text	\N	\N	\N	\N
570	2	3	pokpokpo	2025-12-26 20:30:50.523861+01	text	\N	\N	\N	\N
571	2	3	pkopokpok	2025-12-26 20:31:02.097522+01	text	\N	\N	\N	\N
572	2	3	poooopipoipoi	2025-12-26 20:33:02.538634+01	text	\N	\N	\N	\N
573	2	3	oiuouoi	2025-12-26 20:35:30.288995+01	text	\N	\N	\N	\N
574	2	3	oiuoiuoiu	2025-12-26 20:35:46.241175+01	text	\N	\N	\N	\N
575	2	1	oiuoiu	2025-12-26 20:35:58.719306+01	text	\N	\N	\N	\N
576	2	1	oioiuoiu	2025-12-26 20:36:08.407369+01	text	\N	\N	\N	\N
577	2	1	pipoipoi	2025-12-26 20:37:13.135465+01	text	\N	\N	\N	\N
578	5	3	iyiuyiyiuy	2025-12-26 20:38:00.535298+01	text	\N	\N	\N	\N
579	5	3	iuyiuy	2025-12-26 20:38:11.254689+01	text	\N	\N	\N	\N
580	2	3	poipoipoi	2025-12-26 20:51:34.544599+01	text	\N	\N	\N	\N
581	5	3	poipopoi	2025-12-26 20:52:13.358803+01	text	\N	\N	\N	\N
582	2	22	iojojoijoij	2025-12-26 20:52:24.97339+01	text	\N	\N	\N	\N
583	2	22	ioooo	2025-12-26 20:52:29.813422+01	text	\N	\N	\N	\N
584	2	1	09u09u0u	2025-12-26 21:58:57.942272+01	text	\N	\N	\N	\N
585	3	21	oijoijoij	2025-12-26 22:10:42.071649+01	text	\N	\N	\N	\N
586	3	21	oijiojoij	2025-12-26 22:10:51.204928+01	text	\N	\N	\N	\N
587	3	21	lkjlkjkj	2025-12-26 22:11:05.92935+01	text	\N	\N	\N	\N
588	2	1	lkjlkjlkj	2025-12-26 22:11:22.073085+01	text	\N	\N	\N	\N
589	5	1	lkjlkjlkj	2025-12-26 22:11:42.033646+01	text	\N	\N	\N	\N
590	5	1	lkjlkjlkj	2025-12-26 22:11:47.872865+01	text	\N	\N	\N	\N
591	7	1	lkjlkjlkj	2025-12-26 22:11:56.266641+01	text	\N	\N	\N	\N
593	2	1	iuhiuhiuh	2025-12-28 09:54:19.453649+01	text	\N	\N	\N	\N
594	2	3	iiiii	2025-12-28 10:35:17.681391+01	text	\N	\N	\N	\N
595	2	1	iuy iuy iu y	2025-12-30 09:42:41.081648+01	text	\N	\N	\N	\N
596	2	1	oijoijoij	2025-12-30 09:46:54.490598+01	text	\N	\N	\N	\N
597	2	1	poj pj poj	2025-12-30 09:51:40.577276+01	text	\N	\N	\N	\N
598	2	1	poj poj poj	2025-12-30 09:51:53.895893+01	text	\N	\N	\N	\N
599	2	1	oiu oiuoi uoiu	2025-12-30 09:56:04.423986+01	text	\N	\N	\N	\N
600	2	22	hiuhiu h	2025-12-30 10:11:41.623513+01	text	\N	\N	\N	\N
601	2	1	iu hiuhiuh	2025-12-30 10:25:25.617339+01	text	\N	\N	\N	\N
602	2	22	iuh ih	2025-12-30 10:25:54.347626+01	text	\N	\N	\N	\N
603	2	1	8888	2025-12-30 10:26:56.203892+01	text	\N	\N	\N	\N
604	2	3	yuyuy	2026-01-01 21:30:41.350188+01	text	\N	\N	\N	\N
605	2	3	jljlkj	2026-01-01 21:31:04.826401+01	text	\N	\N	\N	\N
606	5	3	oij oij o	2026-01-01 21:39:31.771005+01	text	\N	\N	\N	\N
607	2	1	oijoij	2026-01-01 22:17:15.347719+01	text	\N	\N	\N	\N
608	2	1	ihiuh	2026-01-01 22:17:59.480287+01	text	\N	\N	\N	\N
609	2	1	\N	2026-01-02 19:42:27.502047+01	poll	{"question": "Zajtra trening", "allow_multi": false}	\N	\N	\N
610	2	3	\N	2026-01-02 19:44:13.910594+01	video	\N	https://d3gdgwfjk7nizh.cloudfront.net/talker/rooms/2/media/beee18d354d74c2396dc90be2334af48_8fed08259aec43cb8b7c29e36d0fa0da_66d6d971fb673f142012ef49_68410bc6617e7ac784c6995a_c5fe08ca-7270-4a84-844a-6367c5035dec-transcode.mp4	video/mp4	3715564
611	2	1	\N	2026-01-02 19:48:38.573858+01	poll	{"question": "Zajtra trening od 17.00 do 18.30", "allow_multi": false}	\N	\N	\N
612	2	1	\N	2026-01-02 19:59:47.219095+01	poll	{"question": "trening zajtra", "allow_multi": false}	\N	\N	\N
613	2	1	https://www.youtube.com/watch?v=xOtaHHkpkwk	2026-01-02 20:23:28.071702+01	text	\N	\N	\N	\N
614	2	1	https://www.facebook.com/fcslovanmodra	2026-01-02 20:24:00.678246+01	text	\N	\N	\N	\N
615	2	1	\N	2026-01-02 20:24:25.862312+01	poll	{"question": "Zajtra trening???", "allow_multi": false}	\N	\N	\N
616	2	3	\N	2026-01-02 20:26:11.309809+01	image	\N	https://d3gdgwfjk7nizh.cloudfront.net/talker/rooms/2/media/fd78ca5717c54cccb4d120ae46a15ff9_fc961880a9764e3ca064c41ad507503f_610a609f661b486881bc04ee28cdf291_68410e495ca39e6b8af76b53_e3a59815-3966-449e-8e52-8bca91d4b6f8.webp	image/webp	848210
618	2	3	\N	2026-01-03 10:22:27.717734+01	file	\N	https://d3gdgwfjk7nizh.cloudfront.net/talker/rooms/2/media/2ada5ba43b084ca38e21e25dea2bdf7f_b94a9b3a793b4397a8a3a40d2b7b9788_Prihlaska_za_clena_OZ-4.pdf	application/pdf	530043
625	2	1	\N	2026-01-03 11:21:11.931169+01	file	\N	https://d3gdgwfjk7nizh.cloudfront.net/talker/rooms/2/media/62db8396b8b147b4b0362d8fe5a4cc88_Oktober-2025.pdf	application/pdf	10552572
626	2	1	jiojoij	2026-01-03 11:34:39.492177+01	text	\N	\N	\N	\N
627	2	1	joijoij	2026-01-03 11:34:42.000879+01	text	\N	\N	\N	\N
629	2	1	98u98u8u	2026-01-03 12:38:07.75167+01	text	\N	\N	\N	\N
630	2	1	uuuu	2026-01-03 12:38:10.456912+01	text	\N	\N	\N	\N
631	2	1	88	2026-01-03 12:38:14.92445+01	text	\N	\N	\N	\N
632	2	1	98u98u98u	2026-01-03 12:38:31.212468+01	text	\N	\N	\N	\N
633	2	1	9999	2026-01-03 12:38:41.314085+01	text	\N	\N	\N	\N
634	2	3	oiioioio	2026-01-03 12:41:46.523584+01	text	\N	\N	\N	\N
635	2	3	pokpok	2026-01-03 12:42:18.570198+01	text	\N	\N	\N	\N
636	2	1	hihiuh	2026-01-03 13:02:39.049584+01	text	\N	\N	\N	\N
637	2	1	iuhiuhuh	2026-01-03 13:02:51.065996+01	text	\N	\N	\N	\N
638	2	1	iuhiuhiuh	2026-01-03 13:03:08.848945+01	text	\N	\N	\N	\N
639	2	1	iuhiuhhu	2026-01-03 13:03:12.200379+01	text	\N	\N	\N	\N
640	2	3	iuhiuh	2026-01-03 13:03:23.343783+01	text	\N	\N	\N	\N
641	2	3	hiuhiuh	2026-01-03 13:03:28.447418+01	text	\N	\N	\N	\N
642	2	3	iuiuiuh	2026-01-03 13:03:43.65551+01	text	\N	\N	\N	\N
643	2	1	oioiu	2026-01-03 13:04:04.542973+01	text	\N	\N	\N	\N
644	2	1	oooo	2026-01-03 13:04:08.839148+01	text	\N	\N	\N	\N
645	2	1	oiuoiu	2026-01-03 13:04:15.400598+01	text	\N	\N	\N	\N
646	2	3	iuyiuy	2026-01-03 13:04:39.968905+01	text	\N	\N	\N	\N
647	2	3	iuiiiu	2026-01-03 13:04:55.161514+01	text	\N	\N	\N	\N
648	2	22	hiuhiuh	2026-01-03 13:05:13.607682+01	text	\N	\N	\N	\N
649	2	22	iuhiuhiuhiuh	2026-01-03 13:05:18.483897+01	text	\N	\N	\N	\N
650	2	3	oihoih	2026-01-03 17:23:45.228925+01	text	\N	\N	\N	\N
651	2	3	oioioi	2026-01-03 17:23:52.620828+01	text	\N	\N	\N	\N
652	2	3	hhh	2026-01-03 17:23:59.413572+01	text	\N	\N	\N	\N
653	2	3	iuhiuh	2026-01-03 17:24:45.73214+01	text	\N	\N	\N	\N
654	2	3	iuhiuhuih	2026-01-03 17:25:46.859436+01	text	\N	\N	\N	\N
655	2	1	lll	2026-01-05 08:48:35.72296+01	text	\N	\N	\N	\N
\.


--
-- Data for Name: talk_poll; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.talk_poll (id, message_id, question, allow_multi, expires_at) FROM stdin;
1	609	Zajtra trening	f	\N
2	611	Zajtra trening od 17.00 do 18.30	f	\N
3	612	trening zajtra	f	\N
4	615	Zajtra trening???	f	\N
\.


--
-- Data for Name: talk_poll_option; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.talk_poll_option (id, poll_id, text, order_index) FROM stdin;
1	1	Áno	0
2	1	Nie	1
3	1	Neviem	2
4	2	Áno	0
5	2	Nie	1
6	2	Možno	2
7	3	ano	0
8	3	nie	1
9	4	ano	0
10	4	nie	1
\.


--
-- Data for Name: talk_poll_vote; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.talk_poll_vote (id, poll_id, option_id, user_id, created_at) FROM stdin;
1	2	4	1	2026-01-02 19:48:44.410401+01
4	3	7	1	2026-01-02 20:04:04.742622+01
5	3	8	1	2026-01-02 20:04:08.513022+01
6	2	6	1	2026-01-02 20:04:32.569775+01
7	3	8	3	2026-01-02 20:09:38.067002+01
11	4	9	3	2026-01-02 20:25:03.220048+01
17	4	9	1	2026-01-03 09:55:20.807287+01
\.


--
-- Data for Name: talk_room; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.talk_room (id, name, team_id, created_by_user_id, created_at) FROM stdin;
2	A team	1	1	2025-12-14 17:14:16.208176+01
3	U19	2	1	2025-12-14 17:16:22.953112+01
5	U15	4	1	2025-12-16 21:18:27.803616+01
6	U13	5	1	2025-12-16 21:18:32.634929+01
7	U11	6	1	2025-12-16 21:18:40.965381+01
8	U9	7	1	2025-12-16 21:18:45.541117+01
\.


--
-- Data for Name: talk_room_members; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.talk_room_members (room_id, user_id, is_admin, joined_at) FROM stdin;
\.


--
-- Data for Name: talk_room_read_state; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.talk_room_read_state (id, user_id, room_id, last_read_message_id, updated_at) FROM stdin;
17	22	2	654	2026-01-04 11:35:57.405398+01
16	1	2	655	2026-01-05 08:48:35.805955+01
\.


--
-- Data for Name: team; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.team (id, name, score_scrap, player_list_scrap, main_league, events_results_scrap, events_program_scrap) FROM stdin;
7	U9				\N	\N
6	U11	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/u11-m-a/tabulky/#/?competitionId=684c50cbe7ee690eb42219bc	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/u11-m-a/hraci/	BFZ - PRÍPRAVKA U11 - PK (PRPK)	\N	\N
4	U15	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55099/tabulky/?partId=&sutaz=629b6f5d7163293609fb0ab7	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55099/hraci/?partId=&sutaz=629b6f5d7163293609fb0ab7	II. liga SŽ	https://sutaze.api.sportnet.online/api/v2/futbalnet/matches?playerAppSpace=fc-slovan-modra.futbalnet.sk&teamId=68610c035a52cdc943f78f99	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/u15-m-a/program/
2	U19	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55092/tabulky/?partId=&sutaz=62a82e3e71632936092991de	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55092/hraci/?partId=&sutaz=62a82e3e71632936092991de	IV. liga dorast (SD4V)	https://sutaze.api.sportnet.online/api/v2/futbalnet/matches?playerAppSpace=fc-slovan-modra.futbalnet.sk&teamId=685cca695a52cdc943e28360	\N
5	U13	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55102/tabulky/?partId=&sutaz=629b6f827163293609fb32fe	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/55102/hraci/?partId=&sutaz=629b6f827163293609fb32fe	II. liga MŽ	https://sutaze.api.sportnet.online/api/v2/futbalnet/matches?playerAppSpace=fc-slovan-modra.futbalnet.sk&teamId=685cca7a5a52cdc943e29d3f	\N
1	A team	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/53930/tabulky/?partId=&sutaz=629b6e797163293609f9fa26	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/53930/hraci/?partId=&sutaz=629b6e797163293609f9fa26	FUTBALSERVIS V. liga BFZ	https://sutaze.api.sportnet.online/api/v2/futbalnet/matches?playerAppSpace=fc-slovan-modra.futbalnet.sk&teamId=685bb1705a52cdc94319e046	https://sportnet.sme.sk/futbalnet/k/fc-slovan-modra/tim/dospeli-m-a/program/
\.


--
-- Data for Name: team_lineup_slots; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.team_lineup_slots (id, lineup_id, player_id, is_starter, order_index, "position") FROM stdin;
22	1	693	f	10	3
23	1	694	f	11	3
12	1	683	f	5	3
10	1	681	t	3	2
15	1	686	f	6	3
20	1	691	f	1	2
11	1	682	t	1	2
7	1	678	t	2	2
2	1	673	f	12	4
17	1	688	t	10	2
19	1	690	f	2	3
24	1	695	t	9	1
25	2	649	t	0	1
26	2	650	t	1	1
27	2	651	t	2	2
28	2	652	t	3	2
29	2	653	t	4	2
30	2	654	t	5	2
31	2	655	t	6	2
32	2	656	t	7	2
33	2	657	t	8	2
34	2	658	t	9	2
35	2	659	t	10	2
36	2	660	f	0	2
37	2	661	f	1	3
38	2	662	f	2	3
3	1	674	f	9	3
39	2	663	f	3	3
40	2	664	f	4	3
41	2	665	f	5	3
42	2	666	f	6	4
43	2	667	f	7	4
44	2	668	f	8	4
45	2	669	f	9	4
46	2	670	f	10	4
47	2	671	f	11	4
18	1	689	t	5	2
9	1	680	f	3	3
13	1	684	t	4	1
6	1	677	f	8	3
16	1	687	t	7	2
5	1	676	f	7	3
65	5	478	t	0	1
66	5	479	t	1	1
67	5	480	t	2	2
68	5	481	t	3	2
69	5	482	t	4	2
70	5	483	t	5	2
71	5	484	t	6	2
72	5	485	t	7	3
73	5	486	t	8	3
74	5	487	t	9	3
75	5	488	t	10	3
76	5	489	f	0	4
77	5	490	f	1	4
78	5	491	f	2	4
79	5	492	f	3	4
80	5	493	f	4	4
81	6	626	t	0	1
82	6	627	t	1	2
83	6	628	t	2	2
84	6	629	t	3	2
85	6	630	t	4	2
86	6	631	t	5	2
87	6	632	t	6	2
88	6	633	t	7	2
89	6	634	t	8	3
90	6	635	t	9	3
91	6	636	t	10	3
92	6	637	f	0	3
93	6	638	f	1	3
94	6	639	f	2	3
95	6	640	f	3	3
96	6	641	f	4	4
97	6	642	f	5	4
98	6	643	f	6	4
99	6	644	f	7	4
100	6	645	f	8	4
101	6	646	f	9	4
102	6	647	f	10	4
103	6	648	f	11	4
1	1	672	t	0	2
4	1	675	f	0	2
21	1	692	t	8	2
8	1	679	f	4	3
14	1	685	t	6	2
104	7	516	t	0	1
105	7	517	t	1	1
106	7	518	t	2	1
107	7	525	t	3	2
108	7	519	t	4	2
109	7	520	t	5	2
110	7	521	t	6	2
111	7	522	t	7	2
112	7	523	t	8	2
113	7	524	t	9	2
114	7	526	t	10	3
115	7	527	f	0	3
116	7	528	f	1	3
117	7	529	f	2	3
118	7	530	f	3	3
119	7	531	f	4	3
120	7	532	f	5	3
121	7	533	f	6	3
122	7	534	f	7	4
123	7	535	f	8	4
124	7	536	f	9	4
125	7	537	f	10	4
\.


--
-- Data for Name: team_lineups; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.team_lineups (id, team_id, formation, updated_at) FROM stdin;
2	2	4-3-3	2025-12-30 11:42:45.260747
4	7	4-3-3	2025-12-30 12:51:51.384385
5	5	4-3-3	2025-12-30 12:54:12.00798
6	6	4-3-3	2025-12-30 12:58:00.364059
1	1	4-1-4-1	2025-12-30 14:47:33.294191
7	4	4-3-3	2026-01-01 17:16:00.999256
\.


--
-- Data for Name: teams_members; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.teams_members (member_id, team_id) FROM stdin;
7	1
6	1
4	1
4	2
14	6
14	4
14	2
15	2
15	5
15	1
3	4
3	1
11	1
\.


--
-- Data for Name: type_product_variant; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.type_product_variant (id, name, operation) FROM stdin;
2	default	select
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public."user" (id, uuid, username, email, image_file, password, confirm, active, confirmed_at, fs_uniquifier) FROM stdin;
4	9c37ff6c-272f-480e-be39-8f7d88ab0a1f	stefanmatas	stefanmatas@fcsm.sk	default.jpg	$2b$12$dMj7R0YenqmdOlgNZ5lTDO7HmjGlBvig93L2xsFFY5SlBfxvX61CK	f	t	\N	9c37ff6c-272f-480e-be39-8f7d88ab0a1f
6	76a15f81-3a3b-41d6-b3e2-8606428ff6c9	fero	ferodolutovsky@fcsm.sk	default.jpg	$2b$12$nlxNZej1pni89liBOEnwDObK3er3rCFVxtkzHY/glr27/EHbAJF5.	f	t	\N	76a15f81-3a3b-41d6-b3e2-8606428ff6c9
7	2be0d46a-abf4-408f-8a6a-b13cdc6c9c91	jano	janvislocky@fcsm.sk	default.jpg	$2b$12$6iDtza/BgG8cBa227.MJm.HyA4vds4ImuzV7L4DePJFWr2bnWC/hS	f	t	\N	2be0d46a-abf4-408f-8a6a-b13cdc6c9c91
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
3	ba4ed929-d4e6-46cf-9748-d8f5d5b8529c	messi	info@appdesign.sk	default.jpg	$2b$12$5IxmS6.KlVy4wcZ3c3GPXe2ffJvuEqoGLWPv88dYgIOr/TPDYx.mO	t	t	\N	ba4ed929-d4e6-46cf-9748-d8f5d5b8529c
8	98e41192-874a-4dc3-b397-b203eecf9dff	Mito		default.jpg	$2b$12$QIl0miaTdXyz/WcHkOEp/u8dq1XvU53rrRKNfAEkq/7u9WS4r9Dr6	f	t	\N	98e41192-874a-4dc3-b397-b203eecf9dff
22	a2665d0f-54d3-4dea-8a22-c1c6e7e02746	Marco Van Basten	office@appdesign.sk	default.jpg	$2b$12$5IxmS6.KlVy4wcZ3c3GPXe2ffJvuEqoGLWPv88dYgIOr/TPDYx.mO	t	t	\N	\N
21	0526d01d-3e1d-41e3-bf7e-29d3a0c98913	fanusik2	martis@gasparikmasovyroba.sk	default.jpg	$2b$12$5IxmS6.KlVy4wcZ3c3GPXe2ffJvuEqoGLWPv88dYgIOr/TPDYx.mO	t	t	\N	0526d01d-3e1d-41e3-bf7e-29d3a0c98913
1	be026d3b-cc56-41fa-97f7-8ee1f871e29d	admin	milanmartis@gmail.com	ea46f20747b448b081903b83101325e6.png	$2b$12$jZOlyG5wyogd8G1JGn1LLe53iEcpQON.mNifYnOiMFvNe5BDuvZbW	t	t	2025-12-09 21:42:27.944414	be026d3b-cc56-41fa-97f7-8ee1f871e29d
\.


--
-- Data for Name: variant_products; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.variant_products (product_id, variant_id, variant_text, variant_image) FROM stdin;
19	5	140	
19	5	141	
19	5	149	
19	6	Black	C:\\fakepath\\660ad3b2c3b0437f97f1d62dabe9bcd4_astrobotic-peregrine-pyld-ps-10 (2).jpg
19	6	White	C:\\fakepath\\660ad3b2c3b0437f97f1d62dabe9bcd4_astrobotic-peregrine-pyld-ps-10 (2).jpg
19	6	Yellow	C:\\fakepath\\660ad3b2c3b0437f97f1d62dabe9bcd4_astrobotic-peregrine-pyld-ps-10 (2).jpg
20	5	138	
20	5	140	
20	6	Blue	
\.


--
-- Data for Name: webpush_subscription; Type: TABLE DATA; Schema: public; Owner: fuma_user
--

COPY public.webpush_subscription (id, user_id, endpoint, p256dh, auth, device, platform, created_at, last_seen_at) FROM stdin;
\.


--
-- Name: category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.category_id_seq', 10, true);


--
-- Name: club_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.club_id_seq', 1, false);


--
-- Name: event_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.event_category_id_seq', 1, false);


--
-- Name: event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.event_id_seq', 1423, true);


--
-- Name: member_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.member_id_seq', 15, true);


--
-- Name: order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.order_id_seq', 2, true);


--
-- Name: player_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.player_id_seq', 695, true);


--
-- Name: position_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.position_id_seq', 1, false);


--
-- Name: post_gallery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.post_gallery_id_seq', 105, true);


--
-- Name: post_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.post_id_seq', 89, true);


--
-- Name: product_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.product_category_id_seq', 1, false);


--
-- Name: product_gallery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.product_gallery_id_seq', 42, true);


--
-- Name: product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.product_id_seq', 21, true);


--
-- Name: product_variant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.product_variant_id_seq', 8, true);


--
-- Name: push_token_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.push_token_id_seq', 42, true);


--
-- Name: role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.role_id_seq', 5, true);


--
-- Name: score_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.score_table_id_seq', 1210, true);


--
-- Name: sponsors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.sponsors_id_seq', 10, true);


--
-- Name: talk_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.talk_message_id_seq', 655, true);


--
-- Name: talk_poll_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.talk_poll_id_seq', 4, true);


--
-- Name: talk_poll_option_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.talk_poll_option_id_seq', 10, true);


--
-- Name: talk_poll_vote_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.talk_poll_vote_id_seq', 17, true);


--
-- Name: talk_room_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.talk_room_id_seq', 11, true);


--
-- Name: talk_room_read_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.talk_room_read_state_id_seq', 17, true);


--
-- Name: team_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.team_id_seq', 9, true);


--
-- Name: team_lineup_slots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.team_lineup_slots_id_seq', 125, true);


--
-- Name: team_lineups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.team_lineups_id_seq', 7, true);


--
-- Name: type_product_variant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.type_product_variant_id_seq', 2, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.user_id_seq', 22, true);


--
-- Name: webpush_subscription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fuma_user
--

SELECT pg_catalog.setval('public.webpush_subscription_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: category category_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_pkey PRIMARY KEY (id);


--
-- Name: club club_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.club
    ADD CONSTRAINT club_pkey PRIMARY KEY (id);


--
-- Name: club club_subdomain_key; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.club
    ADD CONSTRAINT club_subdomain_key UNIQUE (subdomain);


--
-- Name: event_category event_category_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.event_category
    ADD CONSTRAINT event_category_pkey PRIMARY KEY (id);


--
-- Name: event event_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id);


--
-- Name: member member_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.member
    ADD CONSTRAINT member_pkey PRIMARY KEY (id);


--
-- Name: order order_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pkey PRIMARY KEY (id);


--
-- Name: player player_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.player
    ADD CONSTRAINT player_pkey PRIMARY KEY (id);


--
-- Name: position position_name_key; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."position"
    ADD CONSTRAINT position_name_key UNIQUE (name);


--
-- Name: position position_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."position"
    ADD CONSTRAINT position_pkey PRIMARY KEY (id);


--
-- Name: post_gallery post_gallery_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.post_gallery
    ADD CONSTRAINT post_gallery_pkey PRIMARY KEY (id);


--
-- Name: post post_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.post
    ADD CONSTRAINT post_pkey PRIMARY KEY (id);


--
-- Name: product_category product_category_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product_category
    ADD CONSTRAINT product_category_pkey PRIMARY KEY (id);


--
-- Name: product_gallery product_gallery_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product_gallery
    ADD CONSTRAINT product_gallery_pkey PRIMARY KEY (id);


--
-- Name: product product_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pkey PRIMARY KEY (id);


--
-- Name: product_variant product_variant_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product_variant
    ADD CONSTRAINT product_variant_pkey PRIMARY KEY (id);


--
-- Name: push_token push_token_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.push_token
    ADD CONSTRAINT push_token_pkey PRIMARY KEY (id);


--
-- Name: push_token push_token_token_key; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.push_token
    ADD CONSTRAINT push_token_token_key UNIQUE (token);


--
-- Name: role role_name_key; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_name_key UNIQUE (name);


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: score_table score_table_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.score_table
    ADD CONSTRAINT score_table_pkey PRIMARY KEY (id);


--
-- Name: sponsors sponsors_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.sponsors
    ADD CONSTRAINT sponsors_pkey PRIMARY KEY (id);


--
-- Name: talk_message talk_message_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_message
    ADD CONSTRAINT talk_message_pkey PRIMARY KEY (id);


--
-- Name: talk_poll talk_poll_message_id_key; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll
    ADD CONSTRAINT talk_poll_message_id_key UNIQUE (message_id);


--
-- Name: talk_poll_option talk_poll_option_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll_option
    ADD CONSTRAINT talk_poll_option_pkey PRIMARY KEY (id);


--
-- Name: talk_poll talk_poll_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll
    ADD CONSTRAINT talk_poll_pkey PRIMARY KEY (id);


--
-- Name: talk_poll_vote talk_poll_vote_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll_vote
    ADD CONSTRAINT talk_poll_vote_pkey PRIMARY KEY (id);


--
-- Name: talk_room_members talk_room_members_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room_members
    ADD CONSTRAINT talk_room_members_pkey PRIMARY KEY (room_id, user_id);


--
-- Name: talk_room talk_room_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room
    ADD CONSTRAINT talk_room_pkey PRIMARY KEY (id);


--
-- Name: talk_room_read_state talk_room_read_state_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room_read_state
    ADD CONSTRAINT talk_room_read_state_pkey PRIMARY KEY (id);


--
-- Name: team_lineup_slots team_lineup_slots_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.team_lineup_slots
    ADD CONSTRAINT team_lineup_slots_pkey PRIMARY KEY (id);


--
-- Name: team_lineups team_lineups_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.team_lineups
    ADD CONSTRAINT team_lineups_pkey PRIMARY KEY (id);


--
-- Name: team team_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.team
    ADD CONSTRAINT team_pkey PRIMARY KEY (id);


--
-- Name: type_product_variant type_product_variant_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.type_product_variant
    ADD CONSTRAINT type_product_variant_pkey PRIMARY KEY (id);


--
-- Name: team_lineup_slots uq_lineup_player; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.team_lineup_slots
    ADD CONSTRAINT uq_lineup_player UNIQUE (lineup_id, player_id);


--
-- Name: talk_poll_vote uq_poll_user_option; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll_vote
    ADD CONSTRAINT uq_poll_user_option UNIQUE (poll_id, user_id, option_id);


--
-- Name: talk_room_read_state uq_user_room_read; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room_read_state
    ADD CONSTRAINT uq_user_room_read UNIQUE (user_id, room_id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_fs_uniquifier_key; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_fs_uniquifier_key UNIQUE (fs_uniquifier);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- Name: webpush_subscription webpush_subscription_endpoint_key; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.webpush_subscription
    ADD CONSTRAINT webpush_subscription_endpoint_key UNIQUE (endpoint);


--
-- Name: webpush_subscription webpush_subscription_pkey; Type: CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.webpush_subscription
    ADD CONSTRAINT webpush_subscription_pkey PRIMARY KEY (id);


--
-- Name: idx_post_published_at; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX idx_post_published_at ON public.post USING btree (published_at DESC);


--
-- Name: idx_post_views; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX idx_post_views ON public.post USING btree (views DESC);


--
-- Name: ix_post_slug; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX ix_post_slug ON public.post USING btree (slug);


--
-- Name: ix_push_token_user_id; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX ix_push_token_user_id ON public.push_token USING btree (user_id);


--
-- Name: ix_talk_poll_option_poll_id; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX ix_talk_poll_option_poll_id ON public.talk_poll_option USING btree (poll_id);


--
-- Name: ix_talk_poll_vote_option_id; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX ix_talk_poll_vote_option_id ON public.talk_poll_vote USING btree (option_id);


--
-- Name: ix_talk_poll_vote_poll_id; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX ix_talk_poll_vote_poll_id ON public.talk_poll_vote USING btree (poll_id);


--
-- Name: ix_talk_poll_vote_user_id; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX ix_talk_poll_vote_user_id ON public.talk_poll_vote USING btree (user_id);


--
-- Name: ix_team_lineup_slots_lineup_id; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX ix_team_lineup_slots_lineup_id ON public.team_lineup_slots USING btree (lineup_id);


--
-- Name: ix_team_lineup_slots_player_id; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX ix_team_lineup_slots_player_id ON public.team_lineup_slots USING btree (player_id);


--
-- Name: ix_team_lineups_team_id; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX ix_team_lineups_team_id ON public.team_lineups USING btree (team_id);


--
-- Name: ix_webpush_subscription_user_id; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE INDEX ix_webpush_subscription_user_id ON public.webpush_subscription USING btree (user_id);


--
-- Name: ux_post_slug; Type: INDEX; Schema: public; Owner: fuma_user
--

CREATE UNIQUE INDEX ux_post_slug ON public.post USING btree (slug);


--
-- Name: event event_event_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_event_category_id_fkey FOREIGN KEY (event_category_id) REFERENCES public.event_category(id);


--
-- Name: event event_event_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_event_team_id_fkey FOREIGN KEY (event_team_id) REFERENCES public.team(id);


--
-- Name: event event_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: talk_poll_vote fk_talk_poll_vote_user; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll_vote
    ADD CONSTRAINT fk_talk_poll_vote_user FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: member member_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.member
    ADD CONSTRAINT member_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: order order_produc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_produc_id_fkey FOREIGN KEY (produc_id) REFERENCES public.product(id);


--
-- Name: order order_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: player player_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.player
    ADD CONSTRAINT player_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.team(id);


--
-- Name: positions_members positions_members_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.positions_members
    ADD CONSTRAINT positions_members_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.member(id);


--
-- Name: positions_members positions_members_position_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.positions_members
    ADD CONSTRAINT positions_members_position_id_fkey FOREIGN KEY (position_id) REFERENCES public."position"(id);


--
-- Name: post post_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.post
    ADD CONSTRAINT post_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.category(id);


--
-- Name: post_gallery post_gallery_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.post_gallery
    ADD CONSTRAINT post_gallery_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.post(id);


--
-- Name: post post_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.post
    ADD CONSTRAINT post_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: product_gallery product_gallery_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product_gallery
    ADD CONSTRAINT product_gallery_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: product product_product_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_product_category_id_fkey FOREIGN KEY (product_category_id) REFERENCES public.product_category(id);


--
-- Name: product product_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: product_variant_product product_variant_product_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product_variant_product
    ADD CONSTRAINT product_variant_product_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: product_variant_product product_variant_product_product_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product_variant_product
    ADD CONSTRAINT product_variant_product_product_variant_id_fkey FOREIGN KEY (product_variant_id) REFERENCES public.product_variant(id);


--
-- Name: product_variant product_variant_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.product_variant
    ADD CONSTRAINT product_variant_type_fkey FOREIGN KEY (type) REFERENCES public.type_product_variant(id);


--
-- Name: push_token push_token_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.push_token
    ADD CONSTRAINT push_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: roles_users roles_users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.roles_users
    ADD CONSTRAINT roles_users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(id);


--
-- Name: roles_users roles_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.roles_users
    ADD CONSTRAINT roles_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: score_table score_table_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.score_table
    ADD CONSTRAINT score_table_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.team(id);


--
-- Name: talk_message talk_message_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_message
    ADD CONSTRAINT talk_message_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.talk_room(id);


--
-- Name: talk_message talk_message_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_message
    ADD CONSTRAINT talk_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: talk_poll talk_poll_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll
    ADD CONSTRAINT talk_poll_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.talk_message(id) ON DELETE CASCADE;


--
-- Name: talk_poll_option talk_poll_option_poll_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll_option
    ADD CONSTRAINT talk_poll_option_poll_id_fkey FOREIGN KEY (poll_id) REFERENCES public.talk_poll(id) ON DELETE CASCADE;


--
-- Name: talk_poll_vote talk_poll_vote_option_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll_vote
    ADD CONSTRAINT talk_poll_vote_option_id_fkey FOREIGN KEY (option_id) REFERENCES public.talk_poll_option(id) ON DELETE CASCADE;


--
-- Name: talk_poll_vote talk_poll_vote_poll_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll_vote
    ADD CONSTRAINT talk_poll_vote_poll_id_fkey FOREIGN KEY (poll_id) REFERENCES public.talk_poll(id) ON DELETE CASCADE;


--
-- Name: talk_poll_vote talk_poll_vote_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_poll_vote
    ADD CONSTRAINT talk_poll_vote_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: talk_room talk_room_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room
    ADD CONSTRAINT talk_room_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public."user"(id);


--
-- Name: talk_room_members talk_room_members_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room_members
    ADD CONSTRAINT talk_room_members_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.talk_room(id);


--
-- Name: talk_room_members talk_room_members_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room_members
    ADD CONSTRAINT talk_room_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: talk_room_read_state talk_room_read_state_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room_read_state
    ADD CONSTRAINT talk_room_read_state_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.talk_room(id);


--
-- Name: talk_room_read_state talk_room_read_state_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room_read_state
    ADD CONSTRAINT talk_room_read_state_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: talk_room talk_room_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.talk_room
    ADD CONSTRAINT talk_room_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.team(id);


--
-- Name: team_lineup_slots team_lineup_slots_lineup_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.team_lineup_slots
    ADD CONSTRAINT team_lineup_slots_lineup_id_fkey FOREIGN KEY (lineup_id) REFERENCES public.team_lineups(id);


--
-- Name: team_lineup_slots team_lineup_slots_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.team_lineup_slots
    ADD CONSTRAINT team_lineup_slots_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.player(id);


--
-- Name: team_lineups team_lineups_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.team_lineups
    ADD CONSTRAINT team_lineups_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.team(id);


--
-- Name: teams_members teams_members_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.teams_members
    ADD CONSTRAINT teams_members_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.member(id);


--
-- Name: teams_members teams_members_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.teams_members
    ADD CONSTRAINT teams_members_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.team(id);


--
-- Name: variant_products variant_products_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.variant_products
    ADD CONSTRAINT variant_products_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: variant_products variant_products_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.variant_products
    ADD CONSTRAINT variant_products_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES public.product_variant(id);


--
-- Name: webpush_subscription webpush_subscription_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fuma_user
--

ALTER TABLE ONLY public.webpush_subscription
    ADD CONSTRAINT webpush_subscription_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO fuma_user;


--
-- PostgreSQL database dump complete
--

