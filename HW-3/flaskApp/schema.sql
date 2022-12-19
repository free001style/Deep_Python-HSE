drop table if exists passwods;
create table passwords
(
    login    text primary key,
    password text not null
);