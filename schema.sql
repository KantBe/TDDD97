CREATE TABLE IF NOT EXISTS user(
    username    VARCHAR(50) NOT NULL,
    password    VARCHAR(255) NOT NULL,
    firstname   VARCHAR(255) NOT NULL,
    lastname    VARCHAR(255) NOT NULL,
    gender      TEXT CHECK( gender IN ('MALE', 'FEMALE', 'OTHER') ) DEFAULT 'OTHER',
    city        VARCHAR(255) NOT NULL,
    country     VARCHAR(255) NOT NULL,
    PRIMARY KEY(username)
);

CREATE TABLE IF NOT EXISTS post(
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    writer   VARCHAR(50),
    user     VARCHAR(50),
    posttext VARCHAR(255),
    FOREIGN KEY(writer) REFERENCES user(username)
    FOREIGN KEY(user)   REFERENCES user(username)
);

CREATE TABLE IF NOT EXISTS user_session(
    token   VARCHAR(20) NOT NULL,
    user    VARCHAR(50) NOT NULL,
    expires TEXT NOT NULL DEFAULT (strftime('%F %T', 'now', '+1 days')),
    PRIMARY KEY(token),
    FOREIGN KEY(user) REFERENCES user(username)
);
