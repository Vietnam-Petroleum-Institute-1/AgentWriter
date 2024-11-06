--
-- PostgreSQL database dump
--

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
-- TOC entry 867 (class 1247 OID 17093)
-- Name: file_extension_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.file_extension_enum AS ENUM (
    'pdf',
    'docx',
    'txt'
);


ALTER TYPE public.file_extension_enum OWNER TO postgres;

--
-- TOC entry 855 (class 1247 OID 17055)
-- Name: user_role_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_role_enum AS ENUM (
    'admin',
    'user'
);


ALTER TYPE public.user_role_enum OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 215 (class 1259 OID 17044)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 17049)
-- Name: bot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bot (
    bot_id character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(100) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.bot OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 17128)
-- Name: chunk; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chunk (
    chunk_id character varying(100) NOT NULL,
    content text NOT NULL,
    fk_chunk_file_id character varying(100) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.chunk OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 17099)
-- Name: file; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.file (
    file_id character varying(100) NOT NULL,
    fk_file_notebook_id character varying(100) NOT NULL,
    file_name character varying(255) NOT NULL,
    extension public.file_extension_enum NOT NULL,
    summary text,
    content text,
    file_path character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.file OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 17140)
-- Name: message_feedback; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.message_feedback (
    feedback_id character varying(100) NOT NULL,
    fk_feedback_user_id character varying(100) NOT NULL,
    fk_feedback_message_id character varying(100) NOT NULL,
    fk_feedback_notebook_id character varying(100) NOT NULL,
    content text NOT NULL,
    seen boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.message_feedback OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 17111)
-- Name: message_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.message_log (
    message_id character varying(100) NOT NULL,
    fk_message_notebook_id character varying(100) NOT NULL,
    fk_message_bot_id character varying(100) NOT NULL,
    content text NOT NULL,
    from_user boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.message_log OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 17162)
-- Name: note; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.note (
    note_id character varying(100) NOT NULL,
    fk_note_notebook_id character varying(100) NOT NULL,
    fk_note_chunk_id character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    content text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.note OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 17070)
-- Name: notebook; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notebook (
    notebook_id character varying(100) NOT NULL,
    fk_notebook_user_id character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.notebook OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 17080)
-- Name: systemfeedback; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.systemfeedback (
    feedback_id character varying(100) NOT NULL,
    fk_sysfeedback_user_id character varying(100) NOT NULL,
    content text NOT NULL,
    seen boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.systemfeedback OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 17059)
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    user_id character varying(100) NOT NULL,
    username character varying(100) NOT NULL,
    full_name character varying(255),
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    role public.user_role_enum NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- TOC entry 4429 (class 0 OID 17044)
-- Dependencies: 215
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
8d675daa3dad
\.


--
-- TOC entry 4430 (class 0 OID 17049)
-- Dependencies: 216
-- Data for Name: bot; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bot (bot_id, name, type, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4436 (class 0 OID 17128)
-- Dependencies: 222
-- Data for Name: chunk; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chunk (chunk_id, content, fk_chunk_file_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4434 (class 0 OID 17099)
-- Dependencies: 220
-- Data for Name: file; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.file (file_id, fk_file_notebook_id, file_name, extension, summary, content, file_path, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4437 (class 0 OID 17140)
-- Dependencies: 223
-- Data for Name: message_feedback; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.message_feedback (feedback_id, fk_feedback_user_id, fk_feedback_message_id, fk_feedback_notebook_id, content, seen, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4435 (class 0 OID 17111)
-- Dependencies: 221
-- Data for Name: message_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.message_log (message_id, fk_message_notebook_id, fk_message_bot_id, content, from_user, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4438 (class 0 OID 17162)
-- Dependencies: 224
-- Data for Name: note; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.note (note_id, fk_note_notebook_id, fk_note_chunk_id, title, content, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4432 (class 0 OID 17070)
-- Dependencies: 218
-- Data for Name: notebook; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notebook (notebook_id, fk_notebook_user_id, title, created_at, updated_at) FROM stdin;
notebook-f2a239d3-a7c3-42b7-8733-293901700458	user-3350dd6c-9ce6-48fe-984c-162e220e4f9f	Notebook dau tien	2024-10-31 16:20:06.787075+00	2024-10-31 16:20:06.787261+00
\.


--
-- TOC entry 4433 (class 0 OID 17080)
-- Dependencies: 219
-- Data for Name: systemfeedback; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.systemfeedback (feedback_id, fk_sysfeedback_user_id, content, seen, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4431 (class 0 OID 17059)
-- Dependencies: 217
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."user" (user_id, username, full_name, email, password, role, created_at, updated_at) FROM stdin;
user-d86fb3b9-da50-491d-a0fe-f3fb3582f313	test01	Test01	test01@gmail.com	$2b$12$GM2JMemvQ7UJz3tzGc3AiuR.N6QBq5U/8Lq/LdNyZHZFUYT8UO5/2	user	2024-10-31 16:04:42.07812+00	2024-10-31 16:04:42.078225+00
user-0de73685-ca2d-4339-9e04-29571269822b	test02	Test02	test02@gmail.com	$2b$12$d5BVJUpwnkxiWrtT6W/ZX.qpQShzTFSE//fE8t4qIk6nPvRJpv8qa	user	2024-10-31 16:42:00.548522+00	2024-10-31 16:42:00.548635+00
user-3350dd6c-9ce6-48fe-984c-162e220e4f9f	admin	Admin	admin@gmail.com	$2b$12$ORYSrDOsP6VWo41gf8ivD.Mo/JhWVeN2GD4yoGcE15ojiTfZBqXdi	admin	2024-10-31 15:40:22.277254+00	2024-11-06 01:19:56.522806+00
\.


--
-- TOC entry 4252 (class 2606 OID 17048)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4254 (class 2606 OID 17053)
-- Name: bot bot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bot
    ADD CONSTRAINT bot_pkey PRIMARY KEY (bot_id);


--
-- TOC entry 4270 (class 2606 OID 17134)
-- Name: chunk chunk_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chunk
    ADD CONSTRAINT chunk_pkey PRIMARY KEY (chunk_id);


--
-- TOC entry 4266 (class 2606 OID 17105)
-- Name: file file_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file
    ADD CONSTRAINT file_pkey PRIMARY KEY (file_id);


--
-- TOC entry 4272 (class 2606 OID 17146)
-- Name: message_feedback message_feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_feedback
    ADD CONSTRAINT message_feedback_pkey PRIMARY KEY (feedback_id);


--
-- TOC entry 4268 (class 2606 OID 17117)
-- Name: message_log message_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_log
    ADD CONSTRAINT message_log_pkey PRIMARY KEY (message_id);


--
-- TOC entry 4274 (class 2606 OID 17168)
-- Name: note note_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.note
    ADD CONSTRAINT note_pkey PRIMARY KEY (note_id);


--
-- TOC entry 4262 (class 2606 OID 17074)
-- Name: notebook notebook_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notebook
    ADD CONSTRAINT notebook_pkey PRIMARY KEY (notebook_id);


--
-- TOC entry 4264 (class 2606 OID 17086)
-- Name: systemfeedback systemfeedback_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.systemfeedback
    ADD CONSTRAINT systemfeedback_pkey PRIMARY KEY (feedback_id);


--
-- TOC entry 4256 (class 2606 OID 17067)
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- TOC entry 4258 (class 2606 OID 17065)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (user_id);


--
-- TOC entry 4260 (class 2606 OID 17069)
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- TOC entry 4280 (class 2606 OID 17135)
-- Name: chunk chunk_fk_chunk_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chunk
    ADD CONSTRAINT chunk_fk_chunk_file_id_fkey FOREIGN KEY (fk_chunk_file_id) REFERENCES public.file(file_id) ON DELETE CASCADE;


--
-- TOC entry 4277 (class 2606 OID 17106)
-- Name: file file_fk_file_notebook_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file
    ADD CONSTRAINT file_fk_file_notebook_id_fkey FOREIGN KEY (fk_file_notebook_id) REFERENCES public.notebook(notebook_id) ON DELETE CASCADE;


--
-- TOC entry 4281 (class 2606 OID 17147)
-- Name: message_feedback message_feedback_fk_feedback_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_feedback
    ADD CONSTRAINT message_feedback_fk_feedback_message_id_fkey FOREIGN KEY (fk_feedback_message_id) REFERENCES public.message_log(message_id) ON DELETE CASCADE;


--
-- TOC entry 4282 (class 2606 OID 17152)
-- Name: message_feedback message_feedback_fk_feedback_notebook_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_feedback
    ADD CONSTRAINT message_feedback_fk_feedback_notebook_id_fkey FOREIGN KEY (fk_feedback_notebook_id) REFERENCES public.notebook(notebook_id) ON DELETE CASCADE;


--
-- TOC entry 4283 (class 2606 OID 17157)
-- Name: message_feedback message_feedback_fk_feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_feedback
    ADD CONSTRAINT message_feedback_fk_feedback_user_id_fkey FOREIGN KEY (fk_feedback_user_id) REFERENCES public."user"(user_id) ON DELETE CASCADE;


--
-- TOC entry 4278 (class 2606 OID 17118)
-- Name: message_log message_log_fk_message_bot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_log
    ADD CONSTRAINT message_log_fk_message_bot_id_fkey FOREIGN KEY (fk_message_bot_id) REFERENCES public.bot(bot_id) ON DELETE CASCADE;


--
-- TOC entry 4279 (class 2606 OID 17123)
-- Name: message_log message_log_fk_message_notebook_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_log
    ADD CONSTRAINT message_log_fk_message_notebook_id_fkey FOREIGN KEY (fk_message_notebook_id) REFERENCES public.notebook(notebook_id) ON DELETE CASCADE;


--
-- TOC entry 4284 (class 2606 OID 17169)
-- Name: note note_fk_note_chunk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.note
    ADD CONSTRAINT note_fk_note_chunk_id_fkey FOREIGN KEY (fk_note_chunk_id) REFERENCES public.chunk(chunk_id) ON DELETE CASCADE;


--
-- TOC entry 4285 (class 2606 OID 17174)
-- Name: note note_fk_note_notebook_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.note
    ADD CONSTRAINT note_fk_note_notebook_id_fkey FOREIGN KEY (fk_note_notebook_id) REFERENCES public.notebook(notebook_id) ON DELETE CASCADE;


--
-- TOC entry 4275 (class 2606 OID 17075)
-- Name: notebook notebook_fk_notebook_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notebook
    ADD CONSTRAINT notebook_fk_notebook_user_id_fkey FOREIGN KEY (fk_notebook_user_id) REFERENCES public."user"(user_id) ON DELETE CASCADE;


--
-- TOC entry 4276 (class 2606 OID 17087)
-- Name: systemfeedback systemfeedback_fk_sysfeedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.systemfeedback
    ADD CONSTRAINT systemfeedback_fk_sysfeedback_user_id_fkey FOREIGN KEY (fk_sysfeedback_user_id) REFERENCES public."user"(user_id) ON DELETE CASCADE;


-- Completed on 2024-11-06 03:15:12

--
-- PostgreSQL database dump complete
--

