CREATE TABLE role (role_id int primary key, name varchar(25) NOT NULL);
INSERT INTO role(role_id, name) values (1, 'Administrator'), (2, 'Moderator'), (3, 'Bolter'), (4, 'Viewer');
CREATE TABLE privilege (privilege_id int primary key, name varchar(25) NOT NULL);
INSERT INTO privilege(privilege_id, name) VALUES (1, 'Manage Users'), (2, 'Submit Routes'), (3, 'View Routes');
CREATE TABLE role_privilege(role_id int not null, privilege_id int not null, primary key(role_id, privilege_id));
INSERT INTO role_privilege (role_id, privilege_id) VALUES (2, 1), (2, 2), (2, 3), (3, 2), (3,3), (4, 3);
CREATE TABLE user_role (user_id int, role_id int, primary key (user_id, role_id));
