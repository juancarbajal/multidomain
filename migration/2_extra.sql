DELIMITER //

drop trigger if exists tg_upd_domains //

create trigger tg_upd_domains before update on domains
for each row
begin
	set NEW.updated_at = now();
	if (NEW.status = 100) then 
		 set NEW.release_date = now();
	end if;
end //

DELIMITER ;

drop table if exists md_domain;
drop table if exists md_domain_log;
