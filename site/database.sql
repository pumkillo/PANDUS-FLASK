CREATE TABLE IF NOT EXISTS users (
    int_id INTEGER PRIMARY KEY NOT NULL,
    id_user text NOT NULL,
    name text NOT NULL,
    surname text DEFAULT NULL,
    email text NOT NULL,
    password text NOT NULL,
    avatar BLOB DEFAULT NULL,
    about text DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id_post INTEGER PRIMARY KEY NOT NULL,
    id_user text NOT NULL,
    title text NOT NULl,
    post_text text NOT NULL,
    time text NOT NULL,
    timeint integer NOT NULL,
    img BLOB DEFAULT NULL,
    FOREIGN KEY (id_user) REFERENCES users(id_user)
);

CREATE TABLE IF NOT EXISTS comments (
    id_comment INTEGER PRIMARY KEY NOT NULL,
    id_post INTEGER NOT NULL,
    id_user text NOT NULL,
    comment_text text NOT NULL,
    time text NOT NULL,
    timeint integer NOT NULL,
    FOREIGN KEY (id_user) REFERENCES users(id_user),
    FOREIGN KEY (id_post) REFERENCES posts(id_post)
)
