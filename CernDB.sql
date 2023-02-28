CREATE TABLE ip_ranges (
      	ip_range VARCHAR ( 50 ) UNIQUE PRIMARY KEY
);

CREATE TABLE ip (
      	ip VARCHAR ( 50 ) UNIQUE PRIMARY KEY,
      	ip_range VARCHAR ( 50 ) NOT NULL,
          is_alive BOOLEAN NOT NULL,
          last_check TIMESTAMP NOT NULL,
          FOREIGN KEY (ip_range)
              REFERENCES ip_ranges (ip_range)
);

CREATE TABLE dns (
      	id serial PRIMARY KEY,
      	domain_name VARCHAR ( 255 ) NOT NULL,
          hostname_name VARCHAR ( 255 ) NOT NULL
);

CREATE TABLE ip_dns (
      	dns_id INT NOT NULL ,
      	ip VARCHAR ( 50 ) NOT NULL,
      	PRIMARY KEY (dns_id, ip),
      	FOREIGN KEY (dns_id)
              REFERENCES dns(id),
          FOREIGN KEY (ip)
              REFERENCES ip(ip)
):

CREATE TABLE ports (
      	id serial PRIMARY KEY,
      	ip VARCHAR ( 50 ) NOT NULL,
      	port_number INT NOT NULL,
      	port_type VARCHAR(20) NOT NULL,
      	information VARCHAR(255),
      	FOREIGN KEY (ip)
      	    REFERENCES ip(ip)
);

