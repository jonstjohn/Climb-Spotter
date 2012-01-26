ALTER TABLE role ENGINE=INNODB;
CREATE TABLE invite (id char(32) primary key, email varchar(100), created datetime) engine = innodb;
CREATE TABLE invite_role (id char(32), role_id int, primary key(id, role_id), INDEX(role_id), FOREIGN KEY (id) REFERENCES invite(id) ON DELETE CASCADE, FOREIGN KEY(role_id) REFERENCES role(role_id) ON DELETE CASCADE) engine = innodb;
