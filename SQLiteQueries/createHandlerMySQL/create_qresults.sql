CREATE TABLE IF NOT EXISTS qresults (
  q_uuid     CHAR(36) PRIMARY KEY,
  q_score    INT NOT NULL,
  q_year     INT,
  q_percent  TINYINT,  -- or SMALLINT if you prefer 0–1000 etc.
  q_resp     TEXT NOT NULL,
  n_correct  INT NOT NULL,
  n_wrong    INT NOT NULL,
  n_skip     INT NOT NULL,
  user_id    INT,
  start_ts   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finish_ts  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_qresults_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;
