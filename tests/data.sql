INSERT INTO user (username, password,authority)
VALUES
  ('auth1', 'pbkdf2:sha256:600000$4gcJFiQDB4le8AnW$a02a2ecfa8692cf7b5c8eb03b31203ec3c42efb224fe74633ed9a3ac9fa87b2d',1),
  ('auth5', 'pbkdf2:sha256:600000$0Pgv6bYmYnsfExX6$9ed2ebb19a537dc91755a3e0ec0998c703853a63a82b2798a64e4d565ad13aa1',5),
  ('auth10','pbkdf2:sha256:600000$0GOAww6uih1IVdJb$82afd7042c96738d7c2d668459d8192548b4dba9e38e305c062b2d235d2eae00',10);

INSERT INTO post (title, body, author_id, created)
VALUES
  ('test 1', 'test', 2, '2018-01-01 00:00:00'),
  ('test 2', 'test' || x'0a' || 'body', 3, '2018-01-02 00:00:00');