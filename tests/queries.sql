/* @name insert_data */
INSERT INTO beatles (id, member) VALUES (:id, :member);

/* @name select_all_data */
SELECT * FROM beatles;





/* @name select_record_by_id */
SELECT * FROM beatles WHERE id = :id;
