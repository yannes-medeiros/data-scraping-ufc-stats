
import pyodbc #SQL

conn = pyodbc.connect('Driver={SQL Server};Server=localhost\SQLEXPRESS01;Database=master2;Trusted_Connection=True')
cursor = conn.cursor()



querry='CREATE TABLE ufc_all_fight_details (event_id nvarchar(50), fight_date date, fight_id nvarchar(50), wldnc nvarchar(50), weight_class nvarchar(400), method nvarchar(400), round int, fight_time DOUBLE PRECISION, winner nvarchar(400), kd_win int, str_win int, td_win int, sub_win int, vol_str_win int, vol_td_win int, rev_win int, ctrl_win DOUBLE PRECISION, vol_str_head_win int, vol_str_body_win int, vol_str_leg_win  int, vol_str_dist_win  int, vol_str_clinch_win  int, vol_str_ground_win int, sig_str_head_win int, sig_str_body_win int, sig_str_leg_win  int, sig_str_dist_win  int, sig_str_clinch_win  int, sig_str_ground_win  int, losser nvarchar(400), kd_loss int, str_loss int, td_loss int, sub_loss int, vol_str_loss int, vol_td_loss int, rev_loss int, ctrl_loss DOUBLE PRECISION, vol_str_head_loss int, vol_str_body_loss int, vol_str_leg_loss  int, vol_str_dist_loss  int, vol_str_clinch_loss  int, vol_str_ground_loss int, sig_str_head_loss int, sig_str_body_loss int, sig_str_leg_loss  int, sig_str_dist_loss  int, sig_str_clinch_loss  int, sig_str_ground_loss  int)'
querry2='CREATE TABLE ufc_events_tb2 (event_id nvarchar(50), event_date date, event_name nvarchar(100), location nvarchar(100))'


cursor.execute(querry)
cursor.execute(querry2)

#salve alterations
conn.commit()


