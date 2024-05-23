CREATE DATABASE fitness_center;
USE fitness_center;

CREATE TABLE Members (
	member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE,
    phone VARCHAR(16),
    membership_start_date DATE NOT NULL,
    membership_end_date DATE
);

-- Duration in minutes
CREATE TABLE Sessions (
	session_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    date DATE NOT NULL,
    duration INT,
    FOREIGN KEY(member_id) REFERENCES Members(member_id) 
);
