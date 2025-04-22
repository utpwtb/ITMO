CREATE TABLE IF NOT EXISTS Profession_type(
	Profession_id SERIAL PRIMARY KEY,
	Name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS Status (
	Status_id SERIAL PRIMARY KEY,
	Name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS Person(
	Person_id SERIAL PRIMARY KEY,
	Name TEXT UNIQUE NOT NULL,
	Profession INTEGER REFERENCES Profession_type(Profession_id),
	Status INTEGER REFERENCES Status(Status_id)
);
CREATE TABLE IF NOT EXISTS Location(
	Location_id SERIAL PRIMARY KEY,
	Name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS Move_type(
	MoveType_id SERIAL PRIMARY KEY,
	Name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS Move(
	Moved_person INTEGER REFERENCES Person(Person_id),
	MoveType INTEGER REFERENCES Move_type(MoveType_id),
	Start_location INTEGER REFERENCES Location(Location_id),
    End_location INTEGER REFERENCES Location(Location_id)
);
CREATE TABLE IF NOT EXISTS Action_type(
    ActionType_id SERIAL PRIMARY KEY,
    Name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS Action(
    Action_id SERIAL PRIMARY KEY,
    Actioned_person INTEGER REFERENCES Person(Person_id),
    ActionType INTEGER REFERENCES Action_type(ActionType_id)
);

INSERT INTO Profession_type(
    Name
)
VALUES
('кибернетик'),
('доктор');
INSERT INTO Status(
    Name
)
VALUES
('неуклонность'),
('порадоваться');
INSERT INTO Location(
    Name
)
VALUES
('медотсек'),
('Д-6'),
('Д-4');
INSERT INTO Move_type(
    Name
)
VALUES
('выплыть'),
('бегать'),
('Ходить');
INSERT INTO Action_type(
    Name
)
VALUES
('взглянуть'),
('отвернуться'),
('наслаждаться'),
('Закрыть глаза');
INSERT INTO Person(
    Name,
    Profession,
    Status
)
VALUES
('Флойд',2,2),
('Чандра',1,1),
('Курноу',1,1);
INSERT INTO Action(
    Actioned_person,
    ActionType
)
VALUES
(1,3),
(2,1),
(3,1);
INSERT INTO Move(
    Moved_person,
    MoveType,
    Start_location,
    End_location
)
VALUES
(1,1,1,2),
(2,2,2,1),
(3,3,2,3);