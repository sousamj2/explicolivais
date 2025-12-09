CREATE TABLE IF NOT EXISTS personal (
  personal_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id     INT UNIQUE,
  address     VARCHAR(255) NOT NULL DEFAULT 'Unknown',
  number      VARCHAR(20) NOT NULL DEFAULT 'NA',
  floor       VARCHAR(20) NOT NULL DEFAULT 'NA',
  door        VARCHAR(20) NOT NULL DEFAULT 'NA',
  notes       TEXT,
  zip_code1   SMALLINT CHECK (zip_code1 > 0 AND zip_code1 <= 9999),
  zip_code2   TINYINT CHECK (zip_code2 > 0 AND zip_code2 <= 999),
  cell_phone  INT UNIQUE CHECK (cell_phone > 910000000 AND cell_phone <= 999999999),
  nfiscal     INT UNIQUE CHECK (nfiscal > 100000000 AND nfiscal <= 999999999),
  CONSTRAINT fk_personal_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;
