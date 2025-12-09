CREATE TABLE IF NOT EXISTS documents (
  docu_id    INT PRIMARY KEY AUTO_INCREMENT,
  user_id    INT,
  visible    BOOLEAN NOT NULL DEFAULT FALSE,
  docname    VARCHAR(255),
  docurl     VARCHAR(512),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_documents_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;
