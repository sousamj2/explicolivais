CREATE TABLE IF NOT EXISTS classes (
  classes_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id    INT,
  year       INT NOT NULL,
  child_name VARCHAR(255) NOT NULL,
  first_class DATETIME DEFAULT NULL,
  first_contact DATETIME DEFAULT NULL,
  course     VARCHAR(100) NOT NULL DEFAULT 'Matematica',
  CONSTRAINT fk_classes_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;
