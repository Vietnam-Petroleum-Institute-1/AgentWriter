--
-- PostgreSQL database dump
--

-- Dumped from database version 14.12 (Homebrew)
-- Dumped by pg_dump version 16.3

-- Started on 2024-09-25 18:18:03 +07

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

--
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: phuongpd
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO phuongpd;

--
-- TOC entry 219 (class 1255 OID 25410)
-- Name: set_gmt7_timestamps(); Type: FUNCTION; Schema: public; Owner: phuongpd
--

CREATE FUNCTION public.set_gmt7_timestamps() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.created_at = NEW.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh';
    NEW.updated_at = NEW.updated_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh';
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.set_gmt7_timestamps() OWNER TO phuongpd;

--
-- TOC entry 231 (class 1255 OID 25411)
-- Name: update_transcripts(); Type: FUNCTION; Schema: public; Owner: phuongpd
--

CREATE FUNCTION public.update_transcripts() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Cập nhật hoặc chèn bản ghi vào bảng transcripts
    INSERT INTO transcripts (conversation_id, user_id, session_id, total_token, transcripts)
    VALUES (
        NEW.conversation_id,
        NEW.user_id,
        NEW.session_id,
        NEW.total_token,
        jsonb_build_array(
            jsonb_build_object('messageId', NEW.message_id, 'text', NEW.inputs, 'role', 'user', 'timestamp', NEW.timestamp),
            jsonb_build_object('messageId', NEW.message_id, 'text', NEW.outputs, 'role', 'bot', 'timestamp', NEW.timestamp)
        )
    )
    ON CONFLICT (conversation_id)
    DO UPDATE SET 
        total_token = transcripts.total_token + EXCLUDED.total_token,
        transcripts = transcripts.transcripts ||
                      jsonb_build_object('messageId', NEW.message_id, 'text', NEW.inputs, 'role', 'user', 'timestamp', NEW.timestamp) ||
                      jsonb_build_object('messageId', NEW.message_id, 'text', NEW.outputs, 'role', 'bot', 'timestamp', NEW.timestamp),
        updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_transcripts() OWNER TO phuongpd;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 209 (class 1259 OID 25416)
-- Name: conversation_logs; Type: TABLE; Schema: public; Owner: phuongpd
--

CREATE TABLE public.conversation_logs (
    message_id character varying(36) NOT NULL,
    session_id character varying(36),
    user_id character varying(36),
    inputs text NOT NULL,
    token_input integer NOT NULL,
    outputs text NOT NULL,
    token_output integer NOT NULL,
    total_token integer NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    conversation_id character varying(36) NOT NULL,
    domain character varying(36),
    file_id character varying[]
);


ALTER TABLE public.conversation_logs OWNER TO phuongpd;

--
-- TOC entry 210 (class 1259 OID 25424)
-- Name: conversations; Type: TABLE; Schema: public; Owner: phuongpd
--

CREATE TABLE public.conversations (
    conversation_id character varying(36) NOT NULL,
    session_id character varying(50),
    user_id character varying(36),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.conversations OWNER TO phuongpd;

--
-- TOC entry 211 (class 1259 OID 25429)
-- Name: error_logs; Type: TABLE; Schema: public; Owner: phuongpd
--

CREATE TABLE public.error_logs (
    error_id integer NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_id character varying(36) NOT NULL,
    session_id character varying(36) NOT NULL,
    conversation_id character varying(36) NOT NULL,
    input_message text NOT NULL,
    error_message text NOT NULL,
    error_code character varying(36) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.error_logs OWNER TO phuongpd;

--
-- TOC entry 212 (class 1259 OID 25435)
-- Name: error_logs_error_id_seq; Type: SEQUENCE; Schema: public; Owner: phuongpd
--

CREATE SEQUENCE public.error_logs_error_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.error_logs_error_id_seq OWNER TO phuongpd;

--
-- TOC entry 3743 (class 0 OID 0)
-- Dependencies: 212
-- Name: error_logs_error_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: phuongpd
--

ALTER SEQUENCE public.error_logs_error_id_seq OWNED BY public.error_logs.error_id;


--
-- TOC entry 213 (class 1259 OID 25436)
-- Name: feedback; Type: TABLE; Schema: public; Owner: phuongpd
--

CREATE TABLE public.feedback (
    feedback_id integer NOT NULL,
    user_id character varying(255) NOT NULL,
    session_id character varying(255) NOT NULL,
    message_id character varying(255) NOT NULL,
    feedback_type character varying(50) NOT NULL,
    feedback_text text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.feedback OWNER TO phuongpd;

--
-- TOC entry 214 (class 1259 OID 25443)
-- Name: feedback_feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: phuongpd
--

CREATE SEQUENCE public.feedback_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.feedback_feedback_id_seq OWNER TO phuongpd;

--
-- TOC entry 3744 (class 0 OID 0)
-- Dependencies: 214
-- Name: feedback_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: phuongpd
--

ALTER SEQUENCE public.feedback_feedback_id_seq OWNED BY public.feedback.feedback_id;


--
-- TOC entry 215 (class 1259 OID 25444)
-- Name: sessions; Type: TABLE; Schema: public; Owner: phuongpd
--

CREATE TABLE public.sessions (
    session_id character varying(36) NOT NULL,
    user_id character varying(36),
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.sessions OWNER TO phuongpd;

--
-- TOC entry 216 (class 1259 OID 25449)
-- Name: transcripts; Type: TABLE; Schema: public; Owner: phuongpd
--

CREATE TABLE public.transcripts (
    conversation_id character varying(36) NOT NULL,
    user_id character varying(50),
    session_id character varying(50),
    total_token integer,
    transcripts jsonb DEFAULT '[]'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.transcripts OWNER TO phuongpd;

--
-- TOC entry 218 (class 1259 OID 25624)
-- Name: upload_files; Type: TABLE; Schema: public; Owner: phuongpd
--

CREATE TABLE public.upload_files (
    file_id uuid NOT NULL,
    user_id character varying(36),
    session_id character varying(36),
    conversation_id character varying(36),
    file_name character varying(255),
    file_path text,
    file_size integer,
    mime_type character varying(36),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(36),
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_by character varying(36)
);


ALTER TABLE public.upload_files OWNER TO phuongpd;

--
-- TOC entry 217 (class 1259 OID 25465)
-- Name: users; Type: TABLE; Schema: public; Owner: phuongpd
--

CREATE TABLE public.users (
    user_id character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO phuongpd;

--
-- TOC entry 3534 (class 2604 OID 25472)
-- Name: error_logs error_id; Type: DEFAULT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.error_logs ALTER COLUMN error_id SET DEFAULT nextval('public.error_logs_error_id_seq'::regclass);


--
-- TOC entry 3536 (class 2604 OID 25473)
-- Name: feedback feedback_id; Type: DEFAULT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.feedback ALTER COLUMN feedback_id SET DEFAULT nextval('public.feedback_feedback_id_seq'::regclass);


--
-- TOC entry 3727 (class 0 OID 25416)
-- Dependencies: 209
-- Data for Name: conversation_logs; Type: TABLE DATA; Schema: public; Owner: phuongpd
--

COPY public.conversation_logs (message_id, session_id, user_id, inputs, token_input, outputs, token_output, total_token, "timestamp", created_at, updated_at, conversation_id, domain, file_id) FROM stdin;
\.


--
-- TOC entry 3728 (class 0 OID 25424)
-- Dependencies: 210
-- Data for Name: conversations; Type: TABLE DATA; Schema: public; Owner: phuongpd
--

COPY public.conversations (conversation_id, session_id, user_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3729 (class 0 OID 25429)
-- Dependencies: 211
-- Data for Name: error_logs; Type: TABLE DATA; Schema: public; Owner: phuongpd
--

COPY public.error_logs (error_id, "timestamp", user_id, session_id, conversation_id, input_message, error_message, error_code, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3731 (class 0 OID 25436)
-- Dependencies: 213
-- Data for Name: feedback; Type: TABLE DATA; Schema: public; Owner: phuongpd
--

COPY public.feedback (feedback_id, user_id, session_id, message_id, feedback_type, feedback_text, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3733 (class 0 OID 25444)
-- Dependencies: 215
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: phuongpd
--

COPY public.sessions (session_id, user_id, start_time, end_time, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3734 (class 0 OID 25449)
-- Dependencies: 216
-- Data for Name: transcripts; Type: TABLE DATA; Schema: public; Owner: phuongpd
--

COPY public.transcripts (conversation_id, user_id, session_id, total_token, transcripts, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3736 (class 0 OID 25624)
-- Dependencies: 218
-- Data for Name: upload_files; Type: TABLE DATA; Schema: public; Owner: phuongpd
--

COPY public.upload_files (file_id, user_id, session_id, conversation_id, file_name, file_path, file_size, mime_type, created_at, created_by, updated_at, updated_by) FROM stdin;
\.


--
-- TOC entry 3735 (class 0 OID 25465)
-- Dependencies: 217
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: phuongpd
--

COPY public.users (user_id, name, created_at, updated_at) FROM stdin;
anhln	anhln	2024-06-20 21:32:12.514436	2024-06-20 21:32:12.514436
ducbq	ducbq	2024-06-14 00:11:25.085305	2024-06-14 00:11:25.085305
ducna	ducna	2024-06-20 21:32:12.514436	2024-06-20 21:32:12.514436
phuongpd	phuongpd	2024-06-04 21:53:37.602236	2024-06-04 21:53:37.602236
sonnt	Nguyen Trung Son	2024-06-20 22:43:41.727599	2024-06-20 22:43:41.727599
tungtk	tungtk	2024-06-20 21:32:12.514436	2024-06-20 21:32:12.514436
vyvt	vyvt	2024-06-20 21:32:12.514436	2024-06-20 21:32:12.514436
giangdh	giangdh	2024-07-08 18:33:01.449356	2024-07-08 18:33:01.449356
hanhdh	hanhdh	2024-07-08 18:33:01.449356	2024-07-08 18:33:01.449356
quyetdt	quyetdt	2024-07-08 18:33:01.449356	2024-07-08 18:33:01.449356
tuanna	tuanna	2024-07-08 18:33:01.449356	2024-07-08 18:33:01.449356
\.


--
-- TOC entry 3745 (class 0 OID 0)
-- Dependencies: 212
-- Name: error_logs_error_id_seq; Type: SEQUENCE SET; Schema: public; Owner: phuongpd
--

SELECT pg_catalog.setval('public.error_logs_error_id_seq', 1, false);


--
-- TOC entry 3746 (class 0 OID 0)
-- Dependencies: 214
-- Name: feedback_feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: phuongpd
--

SELECT pg_catalog.setval('public.feedback_feedback_id_seq', 50, true);


--
-- TOC entry 3549 (class 2606 OID 25494)
-- Name: conversation_logs conversation_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT conversation_logs_pkey PRIMARY KEY (message_id);


--
-- TOC entry 3551 (class 2606 OID 25496)
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (conversation_id);


--
-- TOC entry 3553 (class 2606 OID 25498)
-- Name: error_logs error_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.error_logs
    ADD CONSTRAINT error_logs_pkey PRIMARY KEY (error_id);


--
-- TOC entry 3555 (class 2606 OID 25500)
-- Name: feedback feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (feedback_id);


--
-- TOC entry 3557 (class 2606 OID 25502)
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (session_id);


--
-- TOC entry 3559 (class 2606 OID 25504)
-- Name: transcripts transcripts_pkey; Type: CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.transcripts
    ADD CONSTRAINT transcripts_pkey PRIMARY KEY (conversation_id);


--
-- TOC entry 3561 (class 2606 OID 25506)
-- Name: transcripts unique_session_id; Type: CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.transcripts
    ADD CONSTRAINT unique_session_id UNIQUE (session_id);


--
-- TOC entry 3565 (class 2606 OID 25632)
-- Name: upload_files upload_files_pkey; Type: CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.upload_files
    ADD CONSTRAINT upload_files_pkey PRIMARY KEY (file_id);


--
-- TOC entry 3563 (class 2606 OID 25510)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- TOC entry 3580 (class 2620 OID 25511)
-- Name: conversation_logs after_insert_conversation_logs; Type: TRIGGER; Schema: public; Owner: phuongpd
--

CREATE TRIGGER after_insert_conversation_logs AFTER INSERT ON public.conversation_logs FOR EACH ROW EXECUTE FUNCTION public.update_transcripts();


--
-- TOC entry 3581 (class 2620 OID 25512)
-- Name: conversation_logs trg_set_gmt7_conversation_logs; Type: TRIGGER; Schema: public; Owner: phuongpd
--

CREATE TRIGGER trg_set_gmt7_conversation_logs BEFORE INSERT OR UPDATE ON public.conversation_logs FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();


--
-- TOC entry 3582 (class 2620 OID 25513)
-- Name: conversations trg_set_gmt7_conversations; Type: TRIGGER; Schema: public; Owner: phuongpd
--

CREATE TRIGGER trg_set_gmt7_conversations BEFORE INSERT OR UPDATE ON public.conversations FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();


--
-- TOC entry 3583 (class 2620 OID 25514)
-- Name: error_logs trg_set_gmt7_error_logs; Type: TRIGGER; Schema: public; Owner: phuongpd
--

CREATE TRIGGER trg_set_gmt7_error_logs BEFORE INSERT OR UPDATE ON public.error_logs FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();


--
-- TOC entry 3584 (class 2620 OID 25515)
-- Name: feedback trg_set_gmt7_feedback; Type: TRIGGER; Schema: public; Owner: phuongpd
--

CREATE TRIGGER trg_set_gmt7_feedback BEFORE INSERT OR UPDATE ON public.feedback FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();


--
-- TOC entry 3585 (class 2620 OID 25516)
-- Name: sessions trg_set_gmt7_sessions; Type: TRIGGER; Schema: public; Owner: phuongpd
--

CREATE TRIGGER trg_set_gmt7_sessions BEFORE INSERT OR UPDATE ON public.sessions FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();


--
-- TOC entry 3586 (class 2620 OID 25517)
-- Name: transcripts trg_set_gmt7_transcripts; Type: TRIGGER; Schema: public; Owner: phuongpd
--

CREATE TRIGGER trg_set_gmt7_transcripts BEFORE INSERT OR UPDATE ON public.transcripts FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();


--
-- TOC entry 3587 (class 2620 OID 25519)
-- Name: users trg_set_gmt7_users; Type: TRIGGER; Schema: public; Owner: phuongpd
--

CREATE TRIGGER trg_set_gmt7_users BEFORE INSERT OR UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();


--
-- TOC entry 3566 (class 2606 OID 25648)
-- Name: conversation_logs conversation_logs_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT conversation_logs_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(session_id);


--
-- TOC entry 3567 (class 2606 OID 25659)
-- Name: conversation_logs conversation_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT conversation_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 3572 (class 2606 OID 25530)
-- Name: feedback feedback_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.conversation_logs(message_id);


--
-- TOC entry 3573 (class 2606 OID 25535)
-- Name: feedback feedback_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(session_id);


--
-- TOC entry 3574 (class 2606 OID 25540)
-- Name: feedback feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 3568 (class 2606 OID 25565)
-- Name: conversation_logs fk_conversation_logs; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT fk_conversation_logs FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id);


--
-- TOC entry 3576 (class 2606 OID 25570)
-- Name: transcripts fk_transcripts_conversations; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.transcripts
    ADD CONSTRAINT fk_transcripts_conversations FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id);


--
-- TOC entry 3569 (class 2606 OID 25575)
-- Name: error_logs fkey_conversations; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.error_logs
    ADD CONSTRAINT fkey_conversations FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id) NOT VALID;


--
-- TOC entry 3570 (class 2606 OID 25580)
-- Name: error_logs fkey_sessions; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.error_logs
    ADD CONSTRAINT fkey_sessions FOREIGN KEY (session_id) REFERENCES public.sessions(session_id) NOT VALID;


--
-- TOC entry 3571 (class 2606 OID 25585)
-- Name: error_logs fkey_users; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.error_logs
    ADD CONSTRAINT fkey_users FOREIGN KEY (user_id) REFERENCES public.users(user_id) NOT VALID;


--
-- TOC entry 3575 (class 2606 OID 25590)
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 3577 (class 2606 OID 25643)
-- Name: upload_files upload_files_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.upload_files
    ADD CONSTRAINT upload_files_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id);


--
-- TOC entry 3578 (class 2606 OID 25638)
-- Name: upload_files upload_files_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.upload_files
    ADD CONSTRAINT upload_files_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(session_id);


--
-- TOC entry 3579 (class 2606 OID 25633)
-- Name: upload_files upload_files_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: phuongpd
--

ALTER TABLE ONLY public.upload_files
    ADD CONSTRAINT upload_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 3742 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: phuongpd
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2024-09-25 18:18:03 +07

--
-- PostgreSQL database dump complete
--

