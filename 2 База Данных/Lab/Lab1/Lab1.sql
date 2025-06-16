CREATE TABLE IF NOT EXISTS ProfessionType(
	ProfessionId SERIAL PRIMARY KEY,
	Name VARCHAR(25) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS Status (
	StatusId SERIAL PRIMARY KEY,
	Name VARCHAR(20) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS Person(
	PersonId SERIAL PRIMARY KEY,
	Name VARCHAR(50) UNIQUE NOT NULL,
	Profession INTEGER REFERENCES ProfessionType(ProfessionId),
	Status INTEGER REFERENCES Status(StatusId)
);
CREATE TABLE IF NOT EXISTS Location(
	LocationId SERIAL PRIMARY KEY,
	Name VARCHAR(25) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS MoveType(
	MoveTypeId SERIAL PRIMARY KEY,
	Name VARCHAR(50) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS Move(
	MovedPerson INTEGER REFERENCES Person(PersonId),
	MoveType INTEGER REFERENCES MoveType(MoveTypeId),
	StartLocation INTEGER REFERENCES Location(LocationId),
    EndLocation INTEGER REFERENCES Location(LocationId),
    MoveDate TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS ActionType(
    ActionTypeId SERIAL PRIMARY KEY,
    Name VARCHAR(25) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS Action(
    ActionId SERIAL PRIMARY KEY,
    ActionedPerson INTEGER REFERENCES Person(PersonId),
    ActionType INTEGER REFERENCES ActionType(ActionTypeId),
    ActionDate TIMESTAMP NOT NULL
);

INSERT INTO ProfessionType(
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
INSERT INTO MoveType(
    Name
)
VALUES
('выплыть'),
('бегать'),
('Ходить');
INSERT INTO ActionType(
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
    ActionedPerson,
    ActionType,
    ActionDate
)
VALUES
(1,3,'2012-05-12 12:08:25'),
(2,1,'2012-05-12 12:06:16'),
(3,1,'2012-05-12 12:04:31');
INSERT INTO Move(
    MovedPerson,
    MoveType,
    StartLocation,
    EndLocation,
    MoveDate
)
VALUES
(1,1,1,2,'2012-05-12 12:05:11'),
(2,2,2,1,'2012-05-12 13:09:54'),
(3,3,2,3,'2012-05-12 13:16:33');

SELECT 
    p.Name AS "name",
    mt.Name AS "moveType",
    l_start.Name AS "startLocation",
    l_end.Name AS "endLocation",
    m.MoveDate AS "time"
FROM Person p
JOIN Move m ON p.PersonId = m.MovedPerson
JOIN MoveType mt ON m.MoveType = mt.MoveTypeId
JOIN Location l_start ON m.StartLocation = l_start.LocationId
JOIN Location l_end ON m.EndLocation = l_end.LocationId