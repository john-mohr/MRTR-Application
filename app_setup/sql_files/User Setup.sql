INSERT INTO auth_group(id, name)
VALUES 
    (1, 'Admin'),
	(2, 'House Manager')
;

UPDATE custom_user_user
SET first_name = 'Erik', last_name = 'Gray', assoc_resident_id = 7
WHERE email = 'e.gray@mrtr.com';

UPDATE mrtr_house
SET manager_id = 7
WHERE name = '277';

UPDATE custom_user_user
SET first_name = 'Fritz', last_name = 'Schuppe', assoc_resident_id = 3
WHERE email = 'test@gmail.com';

UPDATE mrtr_house
SET manager_id = 3
WHERE name = '278';

UPDATE custom_user_user
SET first_name = 'Brian', last_name = 'Chesley', assoc_resident_id = 14
WHERE email = 'b.chesley@mrtr.com';

UPDATE mrtr_house
SET manager_id = 14
WHERE name = '620';

INSERT INTO custom_user_user_groups(user_id, group_id)
VALUES
	(1, 1),
    (2, 2),
    (3, 2),
    (4, 2)
;
