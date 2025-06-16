-- 1. Создание функции триггера
CREATE OR REPLACE FUNCTION log_status_change_action()
RETURNS TRIGGER AS $$
DECLARE
    status_change_action_id INTEGER;
BEGIN
    -- Получение ID типа действия 'Изменение статуса'
    SELECT ActionTypeId INTO status_change_action_id 
    FROM ActionType WHERE Name = 'Изменение статуса';
    
    -- Если статус изменен
    IF NEW.Status IS DISTINCT FROM OLD.Status THEN
        INSERT INTO Action (
            ActionedPerson, 
            ActionType, 
            ActionDate
        ) VALUES (
            NEW.PersonId, 
            status_change_action_id, 
            NOW()
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Создание триггера
CREATE TRIGGER person_status_change_trigger
AFTER UPDATE OF Status ON Person
FOR EACH ROW
EXECUTE FUNCTION log_status_change_action();

-- 3. Инициализация данных
INSERT INTO ActionType (Name) 
VALUES ('Изменение статуса') 
ON CONFLICT (Name) DO NOTHING;  



-- Тип состояния инициализации
INSERT INTO Status (Name) VALUES ('Здоровый'), ('Лечение');

-- Создание тестового персонажа
INSERT INTO Person (Name, Status) 
SELECT 'Флойд', StatusId FROM Status WHERE Name = 'Здоровый';

-- Обновление записи действия триггера статуса
UPDATE Person SET Status = (
    SELECT StatusId FROM Status WHERE Name = 'Лечение'
) WHERE Name = 'Флойд';

-- Проверьте результаты
SELECT p.Name, s.Name AS Status, a.ActionDate 
FROM Person p
JOIN Status s ON s.StatusId = p.Status
JOIN Action a ON a.ActionedPerson = p.PersonId;