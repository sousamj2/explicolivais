CREATE TABLE IF NOT EXISTS iplist (
  ip_id      INT PRIMARY KEY AUTO_INCREMENT,
  user_id    INT,
  ip_value   VARCHAR(45),
  ip_valid   BOOLEAN NOT NULL DEFAULT TRUE,
  first_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  login_count INT NOT NULL DEFAULT 1,
  CONSTRAINT fk_iplist_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;
