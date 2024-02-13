LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/houses.csv"
INTO TABLE mrtr_house
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, name, address, city, state);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/beds.csv"
INTO TABLE mrtr_bed
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, name, house_id);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/residents.csv"
INTO TABLE mrtr_resident
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, first_name, last_name, phone, email, admit_date, rent, referral_info, notes, door_code, discharge_date, bed_id, submission_date);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/transactions.csv"
INTO TABLE mrtr_transaction
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, date, amount, type, method, notes, resident_id, submission_date);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/dtests.csv"
INTO TABLE mrtr_drug_test
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, result, date, notes, substances, resident_id, submission_date);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/check_ins.csv"
INTO TABLE mrtr_check_in
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, date, manager_id, resident_id, method, notes, submission_date);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/site_visits.csv"
INTO TABLE mrtr_site_visit
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, date, issues, explanation, manager_id, house_id, submission_date);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/house_meetings.csv"
INTO TABLE mrtr_house_meeting
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, date, issues, manager_id, house_id, submission_date);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/absentees.csv"
INTO TABLE mrtr_absentee
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, meeting_id, resident_id);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/anon_demo/shopping_trips.csv"
INTO TABLE mrtr_shopping_trip
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, date, amount, notes);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/anon_demo/supply_req.csv"
INTO TABLE mrtr_supply_request
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, products, other, fulfilled, submission_date, house_id, manager_id, trip_id);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/anon_demo/maint_req.csv"
INTO TABLE mrtr_maintenance_request
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id, issue, fulfilled, fulfillment_date, fulfillment_notes, fulfillment_cost, submission_date, house_id, manager_id);


UPDATE mrtr_resident
SET notes = REPLACE(notes, '"', '');

UPDATE mrtr_check_in
SET notes = REPLACE(notes, '"', '');

UPDATE mrtr_house_meeting
SET issues = REPLACE(issues, '"', '');
