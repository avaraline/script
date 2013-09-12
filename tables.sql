CREATE TABLE users (
	id integer primary key,
	nickname text not null unique,
	password text not null,
	name text not null default '',
	email text not null default '',
	sms_email text not null default '',
	can_op boolean not null default 0,
	auto_op boolean not null default 0
);

CREATE TABLE hosts (
	user_id integer not null,
	host text not null unique,
	date_registered datetime not null
);
