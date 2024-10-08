PGDMP      8                |            agent_writer    14.12 (Homebrew)    16.3 @    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    25409    agent_writer    DATABASE     n   CREATE DATABASE agent_writer WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C';
    DROP DATABASE agent_writer;
                phuongpd    false                        2615    2200    public    SCHEMA     2   -- *not* creating schema, since initdb creates it
 2   -- *not* dropping schema, since initdb creates it
                phuongpd    false            �           0    0    SCHEMA public    ACL     Q   REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;
                   phuongpd    false    5            �            1255    25410    set_gmt7_timestamps()    FUNCTION     +  CREATE FUNCTION public.set_gmt7_timestamps() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.created_at = NEW.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh';
    NEW.updated_at = NEW.updated_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh';
    RETURN NEW;
END;
$$;
 ,   DROP FUNCTION public.set_gmt7_timestamps();
       public          phuongpd    false    5            �            1255    25411    update_transcripts()    FUNCTION     �  CREATE FUNCTION public.update_transcripts() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Cập nhật hoặc chèn bản ghi vào bảng transcripts
    INSERT INTO transcripts (conversation_id, user_id, session_id, total_token, bot_id, transcripts)
    VALUES (
        NEW.conversation_id,
        NEW.user_id,
        NEW.session_id,
        NEW.total_token,
        NEW.bot_id,
        jsonb_build_array(
            jsonb_build_object('messageId', NEW.message_id, 'text', NEW.inputs, 'role', 'user', 'timestamp', NEW.timestamp),
            jsonb_build_object('messageId', NEW.message_id, 'text', NEW.outputs, 'role', 'bot', 'timestamp', NEW.timestamp, 'domain', 'Domain 1')
        )
    )
    ON CONFLICT (conversation_id)
    DO UPDATE SET 
        total_token = transcripts.total_token + EXCLUDED.total_token,
        transcripts = transcripts.transcripts ||
                      jsonb_build_object('messageId', NEW.message_id, 'text', NEW.inputs, 'role', 'user', 'timestamp', NEW.timestamp) ||
                      jsonb_build_object('messageId', NEW.message_id, 'text', NEW.outputs, 'role', 'bot', 'timestamp', NEW.timestamp, 'domain', 'Domain 1'),
        bot_id = EXCLUDED.bot_id,
        updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;
 +   DROP FUNCTION public.update_transcripts();
       public          phuongpd    false    5            �            1255    25412    update_user_cost()    FUNCTION     �  CREATE FUNCTION public.update_user_cost() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Cập nhật hoặc chèn bản ghi vào bảng user_cost
    INSERT INTO user_cost (user_id, session_id, total_token)
    VALUES (NEW.user_id, NEW.session_id, NEW.total_token)
    ON CONFLICT (user_id, session_id)
    DO UPDATE SET total_token = user_cost.total_token + EXCLUDED.total_token;
    RETURN NEW;
END;
$$;
 )   DROP FUNCTION public.update_user_cost();
       public          phuongpd    false    5            �            1259    25416    conversation_logs    TABLE     �  CREATE TABLE public.conversation_logs (
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
 %   DROP TABLE public.conversation_logs;
       public         heap    phuongpd    false    5            �            1259    25424    conversations    TABLE     /  CREATE TABLE public.conversations (
    conversation_id character varying(36) NOT NULL,
    session_id character varying(50),
    user_id character varying(36),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
 !   DROP TABLE public.conversations;
       public         heap    phuongpd    false    5            �            1259    25429 
   error_logs    TABLE     �  CREATE TABLE public.error_logs (
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
    DROP TABLE public.error_logs;
       public         heap    phuongpd    false    5            �            1259    25435    error_logs_error_id_seq    SEQUENCE     �   CREATE SEQUENCE public.error_logs_error_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.error_logs_error_id_seq;
       public          phuongpd    false    211    5            �           0    0    error_logs_error_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.error_logs_error_id_seq OWNED BY public.error_logs.error_id;
          public          phuongpd    false    212            �            1259    25436    feedback    TABLE     �  CREATE TABLE public.feedback (
    feedback_id integer NOT NULL,
    user_id character varying(255) NOT NULL,
    session_id character varying(255) NOT NULL,
    message_id character varying(255) NOT NULL,
    feedback_type character varying(50) NOT NULL,
    feedback_text text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.feedback;
       public         heap    phuongpd    false    5            �            1259    25443    feedback_feedback_id_seq    SEQUENCE     �   CREATE SEQUENCE public.feedback_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.feedback_feedback_id_seq;
       public          phuongpd    false    5    213            �           0    0    feedback_feedback_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.feedback_feedback_id_seq OWNED BY public.feedback.feedback_id;
          public          phuongpd    false    214            �            1259    25444    sessions    TABLE     ^  CREATE TABLE public.sessions (
    session_id character varying(36) NOT NULL,
    user_id character varying(36),
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.sessions;
       public         heap    phuongpd    false    5            �            1259    25449    transcripts    TABLE     q  CREATE TABLE public.transcripts (
    conversation_id character varying(36) NOT NULL,
    user_id character varying(50),
    session_id character varying(50),
    total_token integer,
    transcripts jsonb DEFAULT '[]'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.transcripts;
       public         heap    phuongpd    false    5            �            1259    25624    upload_files    TABLE     �  CREATE TABLE public.upload_files (
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
     DROP TABLE public.upload_files;
       public         heap    phuongpd    false    5            �            1259    25465    users    TABLE        CREATE TABLE public.users (
    user_id character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.users;
       public         heap    phuongpd    false    5            �           2604    25472    error_logs error_id    DEFAULT     z   ALTER TABLE ONLY public.error_logs ALTER COLUMN error_id SET DEFAULT nextval('public.error_logs_error_id_seq'::regclass);
 B   ALTER TABLE public.error_logs ALTER COLUMN error_id DROP DEFAULT;
       public          phuongpd    false    212    211            �           2604    25473    feedback feedback_id    DEFAULT     |   ALTER TABLE ONLY public.feedback ALTER COLUMN feedback_id SET DEFAULT nextval('public.feedback_feedback_id_seq'::regclass);
 C   ALTER TABLE public.feedback ALTER COLUMN feedback_id DROP DEFAULT;
       public          phuongpd    false    214    213            �          0    25416    conversation_logs 
   TABLE DATA           �   COPY public.conversation_logs (message_id, session_id, user_id, inputs, token_input, outputs, token_output, total_token, "timestamp", created_at, updated_at, conversation_id, domain, file_id) FROM stdin;
    public          phuongpd    false    209   �a       �          0    25424    conversations 
   TABLE DATA           e   COPY public.conversations (conversation_id, session_id, user_id, created_at, updated_at) FROM stdin;
    public          phuongpd    false    210   �a       �          0    25429 
   error_logs 
   TABLE DATA           �   COPY public.error_logs (error_id, "timestamp", user_id, session_id, conversation_id, input_message, error_message, error_code, created_at, updated_at) FROM stdin;
    public          phuongpd    false    211   �a       �          0    25436    feedback 
   TABLE DATA           �   COPY public.feedback (feedback_id, user_id, session_id, message_id, feedback_type, feedback_text, created_at, updated_at) FROM stdin;
    public          phuongpd    false    213   �a       �          0    25444    sessions 
   TABLE DATA           e   COPY public.sessions (session_id, user_id, start_time, end_time, created_at, updated_at) FROM stdin;
    public          phuongpd    false    215    b       �          0    25449    transcripts 
   TABLE DATA           }   COPY public.transcripts (conversation_id, user_id, session_id, total_token, transcripts, created_at, updated_at) FROM stdin;
    public          phuongpd    false    216   b       �          0    25624    upload_files 
   TABLE DATA           �   COPY public.upload_files (file_id, user_id, session_id, conversation_id, file_name, file_path, file_size, mime_type, created_at, created_by, updated_at, updated_by) FROM stdin;
    public          phuongpd    false    218   :b       �          0    25465    users 
   TABLE DATA           F   COPY public.users (user_id, name, created_at, updated_at) FROM stdin;
    public          phuongpd    false    217   Wb       �           0    0    error_logs_error_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.error_logs_error_id_seq', 1, false);
          public          phuongpd    false    212            �           0    0    feedback_feedback_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.feedback_feedback_id_seq', 50, true);
          public          phuongpd    false    214            �           2606    25494 (   conversation_logs conversation_logs_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT conversation_logs_pkey PRIMARY KEY (message_id);
 R   ALTER TABLE ONLY public.conversation_logs DROP CONSTRAINT conversation_logs_pkey;
       public            phuongpd    false    209            �           2606    25496     conversations conversations_pkey 
   CONSTRAINT     k   ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (conversation_id);
 J   ALTER TABLE ONLY public.conversations DROP CONSTRAINT conversations_pkey;
       public            phuongpd    false    210            �           2606    25498    error_logs error_logs_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.error_logs
    ADD CONSTRAINT error_logs_pkey PRIMARY KEY (error_id);
 D   ALTER TABLE ONLY public.error_logs DROP CONSTRAINT error_logs_pkey;
       public            phuongpd    false    211            �           2606    25500    feedback feedback_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (feedback_id);
 @   ALTER TABLE ONLY public.feedback DROP CONSTRAINT feedback_pkey;
       public            phuongpd    false    213            �           2606    25502    sessions sessions_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (session_id);
 @   ALTER TABLE ONLY public.sessions DROP CONSTRAINT sessions_pkey;
       public            phuongpd    false    215            �           2606    25504    transcripts transcripts_pkey 
   CONSTRAINT     g   ALTER TABLE ONLY public.transcripts
    ADD CONSTRAINT transcripts_pkey PRIMARY KEY (conversation_id);
 F   ALTER TABLE ONLY public.transcripts DROP CONSTRAINT transcripts_pkey;
       public            phuongpd    false    216            �           2606    25506    transcripts unique_session_id 
   CONSTRAINT     ^   ALTER TABLE ONLY public.transcripts
    ADD CONSTRAINT unique_session_id UNIQUE (session_id);
 G   ALTER TABLE ONLY public.transcripts DROP CONSTRAINT unique_session_id;
       public            phuongpd    false    216            �           2606    25632    upload_files upload_files_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY public.upload_files
    ADD CONSTRAINT upload_files_pkey PRIMARY KEY (file_id);
 H   ALTER TABLE ONLY public.upload_files DROP CONSTRAINT upload_files_pkey;
       public            phuongpd    false    218            �           2606    25510    users users_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            phuongpd    false    217            �           2620    25511 0   conversation_logs after_insert_conversation_logs    TRIGGER     �   CREATE TRIGGER after_insert_conversation_logs AFTER INSERT ON public.conversation_logs FOR EACH ROW EXECUTE FUNCTION public.update_transcripts();
 I   DROP TRIGGER after_insert_conversation_logs ON public.conversation_logs;
       public          phuongpd    false    223    209            �           2620    25512 0   conversation_logs trg_set_gmt7_conversation_logs    TRIGGER     �   CREATE TRIGGER trg_set_gmt7_conversation_logs BEFORE INSERT OR UPDATE ON public.conversation_logs FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();
 I   DROP TRIGGER trg_set_gmt7_conversation_logs ON public.conversation_logs;
       public          phuongpd    false    209    219            �           2620    25513 (   conversations trg_set_gmt7_conversations    TRIGGER     �   CREATE TRIGGER trg_set_gmt7_conversations BEFORE INSERT OR UPDATE ON public.conversations FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();
 A   DROP TRIGGER trg_set_gmt7_conversations ON public.conversations;
       public          phuongpd    false    219    210                        2620    25514 "   error_logs trg_set_gmt7_error_logs    TRIGGER     �   CREATE TRIGGER trg_set_gmt7_error_logs BEFORE INSERT OR UPDATE ON public.error_logs FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();
 ;   DROP TRIGGER trg_set_gmt7_error_logs ON public.error_logs;
       public          phuongpd    false    211    219                       2620    25515    feedback trg_set_gmt7_feedback    TRIGGER     �   CREATE TRIGGER trg_set_gmt7_feedback BEFORE INSERT OR UPDATE ON public.feedback FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();
 7   DROP TRIGGER trg_set_gmt7_feedback ON public.feedback;
       public          phuongpd    false    213    219                       2620    25516    sessions trg_set_gmt7_sessions    TRIGGER     �   CREATE TRIGGER trg_set_gmt7_sessions BEFORE INSERT OR UPDATE ON public.sessions FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();
 7   DROP TRIGGER trg_set_gmt7_sessions ON public.sessions;
       public          phuongpd    false    215    219                       2620    25517 $   transcripts trg_set_gmt7_transcripts    TRIGGER     �   CREATE TRIGGER trg_set_gmt7_transcripts BEFORE INSERT OR UPDATE ON public.transcripts FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();
 =   DROP TRIGGER trg_set_gmt7_transcripts ON public.transcripts;
       public          phuongpd    false    219    216                       2620    25519    users trg_set_gmt7_users    TRIGGER     �   CREATE TRIGGER trg_set_gmt7_users BEFORE INSERT OR UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.set_gmt7_timestamps();
 1   DROP TRIGGER trg_set_gmt7_users ON public.users;
       public          phuongpd    false    219    217            �           2606    25648 3   conversation_logs conversation_logs_session_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT conversation_logs_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(session_id);
 ]   ALTER TABLE ONLY public.conversation_logs DROP CONSTRAINT conversation_logs_session_id_fkey;
       public          phuongpd    false    209    215    3558            �           2606    25659 0   conversation_logs conversation_logs_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT conversation_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 Z   ALTER TABLE ONLY public.conversation_logs DROP CONSTRAINT conversation_logs_user_id_fkey;
       public          phuongpd    false    217    3564    209            �           2606    25530 !   feedback feedback_message_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.conversation_logs(message_id);
 K   ALTER TABLE ONLY public.feedback DROP CONSTRAINT feedback_message_id_fkey;
       public          phuongpd    false    3550    213    209            �           2606    25535 !   feedback feedback_session_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(session_id);
 K   ALTER TABLE ONLY public.feedback DROP CONSTRAINT feedback_session_id_fkey;
       public          phuongpd    false    213    215    3558            �           2606    25540    feedback feedback_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 H   ALTER TABLE ONLY public.feedback DROP CONSTRAINT feedback_user_id_fkey;
       public          phuongpd    false    213    217    3564            �           2606    25565 &   conversation_logs fk_conversation_logs    FK CONSTRAINT     �   ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT fk_conversation_logs FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id);
 P   ALTER TABLE ONLY public.conversation_logs DROP CONSTRAINT fk_conversation_logs;
       public          phuongpd    false    209    210    3552            �           2606    25570 (   transcripts fk_transcripts_conversations    FK CONSTRAINT     �   ALTER TABLE ONLY public.transcripts
    ADD CONSTRAINT fk_transcripts_conversations FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id);
 R   ALTER TABLE ONLY public.transcripts DROP CONSTRAINT fk_transcripts_conversations;
       public          phuongpd    false    3552    216    210            �           2606    25575    error_logs fkey_conversations    FK CONSTRAINT     �   ALTER TABLE ONLY public.error_logs
    ADD CONSTRAINT fkey_conversations FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id) NOT VALID;
 G   ALTER TABLE ONLY public.error_logs DROP CONSTRAINT fkey_conversations;
       public          phuongpd    false    211    210    3552            �           2606    25580    error_logs fkey_sessions    FK CONSTRAINT     �   ALTER TABLE ONLY public.error_logs
    ADD CONSTRAINT fkey_sessions FOREIGN KEY (session_id) REFERENCES public.sessions(session_id) NOT VALID;
 B   ALTER TABLE ONLY public.error_logs DROP CONSTRAINT fkey_sessions;
       public          phuongpd    false    215    211    3558            �           2606    25585    error_logs fkey_users    FK CONSTRAINT     �   ALTER TABLE ONLY public.error_logs
    ADD CONSTRAINT fkey_users FOREIGN KEY (user_id) REFERENCES public.users(user_id) NOT VALID;
 ?   ALTER TABLE ONLY public.error_logs DROP CONSTRAINT fkey_users;
       public          phuongpd    false    211    217    3564            �           2606    25590    sessions sessions_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 H   ALTER TABLE ONLY public.sessions DROP CONSTRAINT sessions_user_id_fkey;
       public          phuongpd    false    3564    217    215            �           2606    25643 .   upload_files upload_files_conversation_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.upload_files
    ADD CONSTRAINT upload_files_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id);
 X   ALTER TABLE ONLY public.upload_files DROP CONSTRAINT upload_files_conversation_id_fkey;
       public          phuongpd    false    3552    218    210            �           2606    25638 )   upload_files upload_files_session_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.upload_files
    ADD CONSTRAINT upload_files_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(session_id);
 S   ALTER TABLE ONLY public.upload_files DROP CONSTRAINT upload_files_session_id_fkey;
       public          phuongpd    false    3558    215    218            �           2606    25633 &   upload_files upload_files_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.upload_files
    ADD CONSTRAINT upload_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 P   ALTER TABLE ONLY public.upload_files DROP CONSTRAINT upload_files_user_id_fkey;
       public          phuongpd    false    218    3564    217            �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �   �   x��RKn� ]�)���0�p�n�e7��p�j��)�/���U%/ؼ��>Fx�d���@� (4ޢ7��!��$���rn6C
���i��#�8��f8My�x��c3���z�������̜�S̷7V�K���Š'���;7;�L%�>�Ju�ޮI<�.��q/֮�^��[��h���vG�S��^���\v��$6�kI9p����:����n�(     